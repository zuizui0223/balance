"""Direct comparison of the shared and differentiated optimized worldlines."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math

from .boundary import (
    DEFAULT_BOUNDARY_TOLERANCE,
    classify_two_margin_point,
    two_margin_middle_position,
)


@dataclass(frozen=True)
class WorldlineComparison:
    shared_optimum_fitness: float
    differentiated_optimum_fitness: float
    conflict_load: float
    direct_worldline_gap: float
    direct_reserve: float | None
    direct_middle_position: float | None
    direct_two_sided_depth: float | None
    decomposed_gap: float | None
    decomposed_reserve: float | None
    decomposed_middle_position: float | None
    parallel_world_residual: float | None
    bridge_consistent: bool | None
    state: str


def _finite_fraction_output(value: Fraction, name: str) -> float:
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} is not float-representable; rescale fitness units") from exc
    if not math.isfinite(out):
        raise ValueError(f"{name} is not float-representable; rescale fitness units")
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision; rescale fitness units")
    return out


def compare_worldlines(
    shared_optimum_fitness: float,
    differentiated_optimum_fitness: float,
    conflict_load: float,
    *,
    decoupling: float | None = None,
    architecture_cost: float | None = None,
    tolerance: float = DEFAULT_BOUNDARY_TOLERANCE,
) -> WorldlineComparison:
    """Compare the two optimized worldlines on one fitness scale.

    ``direct_worldline_gap = W_D* - W_S*``.

    A direct BALANCE receipt (``L>0`` and ``W_D*<W_S*``) has an empirically
    observed reserve

        rho_direct = W_S* - W_D* = -Delta_W,

    and therefore supports Chapter-2 interior coordinates without requiring a
    prior Chapter-3 ``s,K`` decomposition:

        xi_direct = L / (L + rho_direct)
        d_B,direct = min(L, rho_direct).

    Direct state classification and the optional decomposed BALANCE coordinate
    both use the canonical two-margin boundary primitive. Representation-specific
    signs are converted once: ``rho_direct=-Delta_W`` and
    ``rho_decomposed=K-sL=-(sL-K)``.

    When ``decoupling`` and ``architecture_cost`` are also supplied, the
    function checks the programme-level bridge identity

        W_D* - W_S* = sL - K,

    reports

        delta_parallel = (W_D* - W_S*) - (sL - K),

    and computes the decomposed reserve/position. Under a consistent bridge,
    the direct and decomposed interior coordinates are identical.

    A non-zero residual is a *candidate* parallel-world shift, not proof of
    one. Scale mismatch, context mismatch, cost-definition mismatch and
    omitted ecological channels must be excluded first.
    """
    Ws = float(shared_optimum_fitness)
    Wd = float(differentiated_optimum_fitness)
    L = float(conflict_load)
    tol = float(tolerance)
    if not all(math.isfinite(x) for x in (Ws, Wd, L, tol)):
        raise ValueError("inputs must be finite")
    if L < 0:
        raise ValueError("conflict_load must be non-negative")
    if tol <= 0:
        raise ValueError("tolerance must be positive")

    ws_q = Fraction.from_float(Ws)
    wd_q = Fraction.from_float(Wd)
    l_q = Fraction.from_float(L)
    tol_q = Fraction.from_float(tol)
    direct_q = wd_q - ws_q
    direct = _finite_fraction_output(direct_q, "direct worldline gap")
    direct_reserve_margin = -direct
    direct_point = classify_two_margin_point(L, direct_reserve_margin, tolerance=tol)

    decomposed = None
    residual = None
    consistent = None
    decomposed_reserve = None
    decomposed_position = None

    if (decoupling is None) != (architecture_cost is None):
        raise ValueError("decoupling and architecture_cost must be supplied together")
    if decoupling is not None and architecture_cost is not None:
        s = float(decoupling)
        K = float(architecture_cost)
        if not math.isfinite(s) or not math.isfinite(K):
            raise ValueError("decomposition inputs must be finite")
        if not 0 <= s <= 1:
            raise ValueError("decoupling must lie in [0,1]")
        if K < 0:
            raise ValueError("architecture_cost must be non-negative")
        decomposed_q = Fraction.from_float(s) * l_q - Fraction.from_float(K)
        decomposed = _finite_fraction_output(decomposed_q, "decomposed worldline gap")
        residual_q = direct_q - decomposed_q
        residual = _finite_fraction_output(residual_q, "parallel-world residual")
        consistent = abs(residual_q) <= tol_q
        decomposed_margin = _finite_fraction_output(-decomposed_q, "decomposed reserve")
        decomposed_point = classify_two_margin_point(L, decomposed_margin, tolerance=tol)
        if decomposed_point.middle_active:
            decomposed_reserve = decomposed_margin
            decomposed_position = two_margin_middle_position(L, decomposed_reserve)

    if not direct_point.conflict_active:
        if direct_point.reserve_position == "NEGATIVE":
            state = "OUTSIDE_REGISTERED_SCH_CONFLICT"
        else:
            state = "SCH_NO_CONFLICT_WORLD"
    elif direct_point.reserve_position == "POSITIVE":
        state = "BALANCE_MIDDLE_WORLD"
    elif direct_point.reserve_position == "INTERFACE":
        state = "ARCHITECTURE_CRITICAL_INTERFACE"
    else:
        state = "BITA_DIFFERENTIATION_WORLD"

    if direct_point.middle_active:
        direct_reserve = direct_reserve_margin
        direct_position = two_margin_middle_position(L, direct_reserve)
        direct_depth = min(L, direct_reserve)
    else:
        direct_reserve = None
        direct_position = None
        direct_depth = None

    return WorldlineComparison(
        shared_optimum_fitness=Ws,
        differentiated_optimum_fitness=Wd,
        conflict_load=L,
        direct_worldline_gap=direct,
        direct_reserve=direct_reserve,
        direct_middle_position=direct_position,
        direct_two_sided_depth=direct_depth,
        decomposed_gap=decomposed,
        decomposed_reserve=decomposed_reserve,
        decomposed_middle_position=decomposed_position,
        parallel_world_residual=residual,
        bridge_consistent=consistent,
        state=state,
    )

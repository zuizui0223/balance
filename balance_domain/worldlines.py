"""Direct comparison of the shared and differentiated optimized worldlines."""

from __future__ import annotations

from dataclasses import dataclass
import math


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


def compare_worldlines(
    shared_optimum_fitness: float,
    differentiated_optimum_fitness: float,
    conflict_load: float,
    *,
    decoupling: float | None = None,
    architecture_cost: float | None = None,
    tolerance: float = 1e-9,
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

    direct = Wd - Ws
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
        decomposed = s * L - K
        residual = direct - decomposed
        consistent = abs(residual) <= tol
        if L > tol and decomposed < -tol:
            decomposed_reserve = -decomposed
            decomposed_position = L / (L + decomposed_reserve)

    if L <= tol:
        if direct > tol:
            state = "OUTSIDE_REGISTERED_SCH_CONFLICT"
        else:
            state = "SCH_NO_CONFLICT_WORLD"
    elif direct < -tol:
        state = "BALANCE_MIDDLE_WORLD"
    elif abs(direct) <= tol:
        state = "ARCHITECTURE_CRITICAL_INTERFACE"
    else:
        state = "BITA_DIFFERENTIATION_WORLD"

    if state == "BALANCE_MIDDLE_WORLD":
        direct_reserve = -direct
        direct_position = L / (L + direct_reserve)
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

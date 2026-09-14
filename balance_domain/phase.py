"""Dimensionless phase coordinates for the BALANCE middle world."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
import math

from .boundary import classify_two_margin_point, two_margin_middle_position


@dataclass(frozen=True)
class NormalizedPhasePoint:
    normalized_conflict: float
    decoupling: float
    recoverable_cost_ratio: float
    middle_position: float | None
    state: str
    balance_subregion: str | None
    critical_conflict_ratio: float | None
    deepest_ridge_ratio: float | None


def _finite_fraction_to_float(value: F, name: str) -> float:
    """Convert an exact finite phase quantity without inventing 0/inf."""
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale inputs"
        ) from exc
    if not math.isfinite(out):
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale inputs"
        )
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision; rescale inputs")
    return out


def normalized_phase_point(
    conflict_load: float,
    decoupling: float,
    architecture_cost: float,
    *,
    tolerance: float = 1e-12,
) -> NormalizedPhasePoint:
    """Map one context into the dimensionless ``(L/K, s)`` phase plane.

    ``K`` must be positive for this normalized representation. Let

        c = L/K
        q = sL/K = sc
        rho/K = 1-q.

    The static architecture boundary is ``q=1`` or ``c=1/s`` when ``s>0``.
    Inside BALANCE, the equal-margin/deepest ridge is

        c = 1/(1+s).

    ``tolerance`` is dimensionless and is applied to the normalized conflict
    margin ``c`` and normalized reserve margin ``1-q``. This preserves the
    defining scale invariance of the phase representation even near a boundary.
    Contexts below the deepest ridge are closer to the SCH-facing conflict
    boundary; contexts above it are closer to the BITA-facing architecture
    boundary in the common fitness-margin geometry.

    All derived phase coordinates are evaluated exactly at the supplied-float
    level before conversion back to float. ``s=0`` is the sole structural case
    with no finite architecture boundary. When ``s>0``, a mathematically finite
    critical boundary or phase coordinate that cannot be represented faithfully
    by the float-valued API fails closed rather than appearing as ``inf``, zero,
    or a rounded structural boundary value.
    """
    if any(isinstance(value, bool) for value in (conflict_load, decoupling, architecture_cost, tolerance)):
        raise ValueError("phase numeric inputs must not be boolean")
    L = float(conflict_load)
    s = float(decoupling)
    K = float(architecture_cost)
    tol = float(tolerance)
    if not all(math.isfinite(x) for x in (L, s, K, tol)):
        raise ValueError("inputs must be finite")
    if L < 0:
        raise ValueError("conflict_load must be non-negative")
    if not 0 <= s <= 1:
        raise ValueError("decoupling must lie in [0,1]")
    if K <= 0:
        raise ValueError("architecture_cost must be positive for normalized phase coordinates")
    if tol <= 0:
        raise ValueError("tolerance must be positive")

    l_q = F.from_float(L)
    s_q = F.from_float(s)
    k_q = F.from_float(K)
    tol_q = F.from_float(tol)
    one = F(1, 1)

    c_q = l_q / k_q
    q_q = s_q * c_q
    reserve_q = one - q_q
    ridge_q = one / (one + s_q)
    critical_q = None if s == 0 else one / s_q

    c = _finite_fraction_to_float(c_q, "normalized conflict ratio")
    q = _finite_fraction_to_float(q_q, "recoverable cost ratio")
    normalized_reserve = _finite_fraction_to_float(
        reserve_q, "normalized reserve margin"
    )
    if critical_q is None:
        critical = None
    else:
        critical = _finite_fraction_to_float(
            critical_q, "critical conflict ratio"
        )
    ridge = _finite_fraction_to_float(ridge_q, "deepest ridge ratio")
    if s > 0 and ridge == 1.0:
        raise ValueError(
            "deepest ridge ratio collapses to the s=0 boundary at float precision; rescale representation"
        )

    point = classify_two_margin_point(c, normalized_reserve, tolerance=tol)

    if not point.conflict_active:
        state = "SCH_NO_CONFLICT_WORLD"
        xi = None
        subregion = None
    elif point.reserve_position == "INTERFACE":
        state = "BALANCE_BITA_INTERFACE"
        xi = None
        subregion = None
    elif point.reserve_position == "POSITIVE":
        state = "BALANCE_MIDDLE_WORLD"
        # xi = L/(L+K-sL); divide both margins by K.
        xi = two_margin_middle_position(c, normalized_reserve)
        if abs(c_q - ridge_q) <= tol_q:
            subregion = "DEEPEST_BALANCE_RIDGE"
        elif c_q < ridge_q:
            subregion = "SCH_BOUNDARY_LIMITED_BALANCE"
        else:
            subregion = "BITA_BOUNDARY_LIMITED_BALANCE"
    else:
        state = "BITA_DIFFERENTIATION_WORLD"
        xi = None
        subregion = None

    return NormalizedPhasePoint(
        normalized_conflict=c,
        decoupling=s,
        recoverable_cost_ratio=q,
        middle_position=xi,
        state=state,
        balance_subregion=subregion,
        critical_conflict_ratio=critical,
        deepest_ridge_ratio=ridge,
    )

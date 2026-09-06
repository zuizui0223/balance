"""Dimensionless phase coordinates for the BALANCE middle world."""

from __future__ import annotations

from dataclasses import dataclass
import math


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
        q = sL/K = sc.

    The static architecture boundary is ``q=1`` or ``c=1/s`` when ``s>0``.
    Inside BALANCE, the equal-margin/deepest ridge is

        c = 1/(1+s).

    Contexts below that ridge are closer to the SCH-facing conflict boundary;
    contexts above it are closer to the BITA-facing architecture boundary in
    the common fitness-margin geometry.
    """
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

    c = L / K
    q = s * c
    critical = None if s == 0 else 1.0 / s
    ridge = 1.0 / (1.0 + s)

    if L <= tol:
        state = "SCH_NO_CONFLICT_WORLD"
        xi = None
        subregion = None
    elif abs(q - 1.0) <= tol:
        state = "BALANCE_BITA_INTERFACE"
        xi = None
        subregion = None
    elif q < 1.0:
        state = "BALANCE_MIDDLE_WORLD"
        # xi = L/(L+K-sL); divide numerator and denominator by K.
        xi = c / (c + 1.0 - s * c)
        if abs(c - ridge) <= tol:
            subregion = "DEEPEST_BALANCE_RIDGE"
        elif c < ridge:
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

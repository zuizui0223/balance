from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math


@dataclass(frozen=True)
class AccessibilityScopeBounds:
    classification: str
    conflict_load: float
    reserve_lower: float
    reserve_upper: float
    scope_fragility: float
    signed_margin_lower: float
    signed_margin_upper: float
    depth_lower: float | None
    depth_upper: float | None


def _finite_difference(upper: float, lower: float, name: str) -> float:
    exact = Fraction.from_float(upper) - Fraction.from_float(lower)
    try:
        out = float(exact)
    except OverflowError as exc:
        raise ValueError(f"{name} must remain finite; rescale fitness units") from exc
    if not math.isfinite(out):
        raise ValueError(f"{name} must remain finite; rescale fitness units")
    return out


def accessibility_scope_bounds(
    *,
    conflict_load: float,
    reserve_definite: float,
    reserve_possible: float,
) -> AccessibilityScopeBounds:
    """Classify BALANCE under nested definite/possible accessibility scopes.

    ``reserve_possible`` is the lower reserve obtained by comparing against all
    plausibly accessible alternatives; ``reserve_definite`` is the upper
    reserve obtained using only definitely accessible alternatives.

    ``depth_lower``/``depth_upper`` are emitted only when BALANCE is robust
    over the whole declared accessibility set. Outside that case the function
    returns signed minimum margins instead of silently calling them depth.
    """
    conflict = float(conflict_load)
    definite = float(reserve_definite)
    possible = float(reserve_possible)
    if not all(math.isfinite(value) for value in (conflict, definite, possible)):
        raise ValueError("conflict and reserve bounds must be finite")
    if conflict < 0:
        raise ValueError("conflict_load must be non-negative")
    if possible > definite:
        raise ValueError("reserve_possible cannot exceed reserve_definite")

    fragility = _finite_difference(definite, possible, "scope fragility")
    signed_lower = min(conflict, possible)
    signed_upper = min(conflict, definite)

    if conflict == 0:
        classification = "NO_POSITIVE_CONFLICT"
        depth_lower = None
        depth_upper = None
    elif possible > 0:
        classification = "ROBUST_BALANCE"
        depth_lower = signed_lower
        depth_upper = signed_upper
    elif definite <= 0:
        classification = "ROBUST_NON_BALANCE"
        depth_lower = None
        depth_upper = None
    else:
        classification = "ACCESSIBILITY_SCOPE_UNRESOLVED"
        depth_lower = None
        depth_upper = None

    return AccessibilityScopeBounds(
        classification=classification,
        conflict_load=conflict,
        reserve_lower=possible,
        reserve_upper=definite,
        scope_fragility=fragility,
        signed_margin_lower=signed_lower,
        signed_margin_upper=signed_upper,
        depth_lower=depth_lower,
        depth_upper=depth_upper,
    )

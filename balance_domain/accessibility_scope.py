from __future__ import annotations

from dataclasses import dataclass


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

    if reserve_possible > reserve_definite:
        raise ValueError("reserve_possible cannot exceed reserve_definite")

    fragility = reserve_definite - reserve_possible
    signed_lower = min(conflict_load, reserve_possible)
    signed_upper = min(conflict_load, reserve_definite)

    if conflict_load <= 0:
        classification = "NO_POSITIVE_CONFLICT"
        depth_lower = None
        depth_upper = None
    elif reserve_possible > 0:
        classification = "ROBUST_BALANCE"
        depth_lower = signed_lower
        depth_upper = signed_upper
    elif reserve_definite <= 0:
        classification = "ROBUST_NON_BALANCE"
        depth_lower = None
        depth_upper = None
    else:
        classification = "ACCESSIBILITY_SCOPE_UNRESOLVED"
        depth_lower = None
        depth_upper = None

    return AccessibilityScopeBounds(
        classification=classification,
        conflict_load=conflict_load,
        reserve_lower=reserve_possible,
        reserve_upper=reserve_definite,
        scope_fragility=fragility,
        signed_margin_lower=signed_lower,
        signed_margin_upper=signed_upper,
        depth_lower=depth_lower,
        depth_upper=depth_upper,
    )

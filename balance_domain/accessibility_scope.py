from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccessibilityScopeBounds:
    classification: str
    conflict_load: float
    reserve_lower: float
    reserve_upper: float
    scope_fragility: float
    depth_lower: float
    depth_upper: float


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
    """

    if reserve_possible > reserve_definite:
        raise ValueError("reserve_possible cannot exceed reserve_definite")

    fragility = reserve_definite - reserve_possible
    depth_lower = min(conflict_load, reserve_possible)
    depth_upper = min(conflict_load, reserve_definite)

    if conflict_load <= 0:
        classification = "NO_POSITIVE_CONFLICT"
    elif reserve_possible > 0:
        classification = "ROBUST_BALANCE"
    elif reserve_definite <= 0:
        classification = "ROBUST_NON_BALANCE"
    else:
        classification = "ACCESSIBILITY_SCOPE_UNRESOLVED"

    return AccessibilityScopeBounds(
        classification=classification,
        conflict_load=conflict_load,
        reserve_lower=reserve_possible,
        reserve_upper=reserve_definite,
        scope_fragility=fragility,
        depth_lower=depth_lower,
        depth_upper=depth_upper,
    )

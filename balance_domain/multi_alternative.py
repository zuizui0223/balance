from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence


@dataclass(frozen=True)
class MultiAlternativeState:
    conflict_margin: float
    alternative_reserves: tuple[float, ...]
    envelope_reserve: float
    fitness_depth: float
    threatening_alternatives: tuple[int, ...]
    state: str


def classify_multi_alternative_middle_world(
    conflict_margin: float,
    alternative_reserves: Sequence[float],
    *,
    atol: float = 1e-12,
) -> MultiAlternativeState:
    """Classify the shared architecture against all accessible alternatives.

    ``atol`` defines the numerical boundary band consistently for both status
    margins and for ties among the alternatives that attain the reserve
    envelope.  A margin whose absolute value is at most ``atol`` is therefore
    treated as lying on its registered boundary rather than as signed evidence
    for one side.
    """
    if not alternative_reserves:
        raise ValueError("at least one alternative architecture is required")

    conflict = float(conflict_margin)
    reserves = tuple(float(x) for x in alternative_reserves)
    tol = float(atol)
    if not math.isfinite(conflict) or not all(math.isfinite(x) for x in reserves):
        raise ValueError("conflict margin and alternative reserves must be finite")
    if not math.isfinite(tol) or tol < 0:
        raise ValueError("atol must be finite and nonnegative")

    envelope_reserve = min(reserves)
    threatening = tuple(
        i for i, value in enumerate(reserves)
        if abs(value - envelope_reserve) <= tol
    )

    if conflict <= tol:
        state = "NO_SHARED_CONFLICT"
        fitness_depth = 0.0
    elif envelope_reserve > tol:
        state = "MULTI_ALTERNATIVE_BALANCE"
        fitness_depth = min(conflict, envelope_reserve)
    elif envelope_reserve < -tol:
        state = "ALTERNATIVE_ARCHITECTURE_SIDE"
        fitness_depth = 0.0
    else:
        state = "ARCHITECTURE_ENVELOPE_BOUNDARY"
        fitness_depth = 0.0

    return MultiAlternativeState(
        conflict_margin=conflict,
        alternative_reserves=reserves,
        envelope_reserve=envelope_reserve,
        fitness_depth=fitness_depth,
        threatening_alternatives=threatening,
        state=state,
    )

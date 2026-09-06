from __future__ import annotations

from dataclasses import dataclass
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
    if not alternative_reserves:
        raise ValueError("at least one alternative architecture is required")
    reserves = tuple(float(x) for x in alternative_reserves)
    envelope_reserve = min(reserves)
    threatening = tuple(
        i for i, value in enumerate(reserves)
        if abs(value - envelope_reserve) <= atol
    )

    if conflict_margin <= 0:
        state = "NO_SHARED_CONFLICT"
        fitness_depth = 0.0
    elif envelope_reserve > 0:
        state = "MULTI_ALTERNATIVE_BALANCE"
        fitness_depth = min(conflict_margin, envelope_reserve)
    elif envelope_reserve < 0:
        state = "ALTERNATIVE_ARCHITECTURE_SIDE"
        fitness_depth = 0.0
    else:
        state = "ARCHITECTURE_ENVELOPE_BOUNDARY"
        fitness_depth = 0.0

    return MultiAlternativeState(
        conflict_margin=float(conflict_margin),
        alternative_reserves=reserves,
        envelope_reserve=envelope_reserve,
        fitness_depth=fitness_depth,
        threatening_alternatives=threatening,
        state=state,
    )

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

from .boundary import classify_two_margin_point


@dataclass(frozen=True)
class MultiAlternativeState:
    conflict_margin: float
    alternative_reserves: tuple[float, ...]
    envelope_reserve: float
    fitness_depth: float
    threatening_alternatives: tuple[int, ...]
    state: str


def _finite_input(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be finite numeric evidence, not boolean")
    try:
        out = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite numeric evidence") from exc
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite numeric evidence")
    return out


def classify_multi_alternative_middle_world(
    conflict_margin: float,
    alternative_reserves: Sequence[float],
    *,
    atol: float = 1e-12,
) -> MultiAlternativeState:
    """Classify the shared architecture against all accessible alternatives.

    ``atol`` defines the numerical boundary band consistently for both status
    margins and for ties among the alternatives that attain the reserve
    envelope. A margin whose absolute value is at most ``atol`` is therefore
    treated as lying on its registered boundary rather than as signed evidence
    for one side.

    The envelope reserve is passed to the same two-margin classifier used by
    the single-alternative BALANCE routes.
    """
    if not alternative_reserves:
        raise ValueError("at least one alternative architecture is required")

    conflict = _finite_input(conflict_margin, "conflict_margin")
    reserves = tuple(
        _finite_input(value, f"alternative_reserves[{index}]")
        for index, value in enumerate(alternative_reserves)
    )
    tol = _finite_input(atol, "atol")
    if tol < 0:
        raise ValueError("atol must be finite and nonnegative")

    envelope_reserve = min(reserves)
    threatening = tuple(
        i for i, value in enumerate(reserves)
        if abs(value - envelope_reserve) <= tol
    )
    point = classify_two_margin_point(conflict, envelope_reserve, tolerance=tol)

    if not point.conflict_active:
        state = "NO_SHARED_CONFLICT"
        fitness_depth = 0.0
    elif point.reserve_position == "POSITIVE":
        state = "MULTI_ALTERNATIVE_BALANCE"
        fitness_depth = min(conflict, envelope_reserve)
    elif point.reserve_position == "NEGATIVE":
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

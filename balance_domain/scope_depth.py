from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ScopeDepthComparison:
    old_reserve: float
    new_reserve: float
    old_fitness_depth: float
    new_fitness_depth: float
    old_balance: bool
    new_balance: bool


@dataclass(frozen=True)
class MarginalScopeShock:
    old_bottleneck: float
    new_alternative_reserve: float
    new_bottleneck: float
    depth_loss: float
    classification: str


def envelope_reserve(reserves: Iterable[float]) -> float:
    values = tuple(float(x) for x in reserves)
    if not values:
        raise ValueError("at least one alternative reserve is required")
    return min(values)


def fitness_depth(conflict_margin: float, reserves: Iterable[float]) -> float:
    return min(float(conflict_margin), envelope_reserve(reserves))


def is_balance(conflict_margin: float, reserves: Iterable[float]) -> bool:
    return float(conflict_margin) > 0.0 and envelope_reserve(reserves) > 0.0


def compare_nested_scopes(
    conflict_margin: float,
    old_reserves: Iterable[float],
    added_reserves: Iterable[float],
) -> ScopeDepthComparison:
    old_values = tuple(float(x) for x in old_reserves)
    added_values = tuple(float(x) for x in added_reserves)
    if not old_values:
        raise ValueError("old scope must contain at least one alternative")

    old_reserve = envelope_reserve(old_values)
    new_reserve = envelope_reserve(old_values + added_values)
    old_depth = min(float(conflict_margin), old_reserve)
    new_depth = min(float(conflict_margin), new_reserve)

    if new_reserve > old_reserve + 1e-12:
        raise AssertionError("nested-scope reserve monotonicity violated")
    if new_depth > old_depth + 1e-12:
        raise AssertionError("nested-scope fitness-depth monotonicity violated")

    return ScopeDepthComparison(
        old_reserve=old_reserve,
        new_reserve=new_reserve,
        old_fitness_depth=old_depth,
        new_fitness_depth=new_depth,
        old_balance=float(conflict_margin) > 0.0 and old_reserve > 0.0,
        new_balance=float(conflict_margin) > 0.0 and new_reserve > 0.0,
    )


def marginal_scope_shock(
    conflict_margin: float,
    old_reserves: Iterable[float],
    new_alternative_reserve: float,
) -> MarginalScopeShock:
    """Exact pointwise bottleneck update after adding one alternative."""
    old_values = tuple(float(x) for x in old_reserves)
    if not old_values:
        raise ValueError("old scope must contain at least one alternative")
    old_bottleneck = min(float(conflict_margin), envelope_reserve(old_values))
    r = float(new_alternative_reserve)
    new_bottleneck = min(old_bottleneck, r)
    depth_loss = old_bottleneck - new_bottleneck

    if r >= old_bottleneck:
        classification = "IRRELEVANT_OR_TIED_ADDITION"
    elif r > 0.0:
        classification = "DEPTH_REDUCING_BALANCE_PERSISTS"
    else:
        classification = "STATE_DESTROYING_ALTERNATIVE"

    return MarginalScopeShock(
        old_bottleneck=old_bottleneck,
        new_alternative_reserve=r,
        new_bottleneck=new_bottleneck,
        depth_loss=depth_loss,
        classification=classification,
    )


def metric_scope_depth(boundary_distances: Iterable[float]) -> float:
    values = tuple(float(x) for x in boundary_distances)
    if not values:
        raise ValueError("at least one boundary distance is required")
    if any(x < 0.0 for x in values):
        raise ValueError("boundary distances must be nonnegative")
    return min(values)

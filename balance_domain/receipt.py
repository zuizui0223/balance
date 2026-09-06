"""Bounded empirical receipts shared by SCH, BALANCE, and BITA."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Interval:
    lower: float
    upper: float

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError("interval lower bound must not exceed upper bound")

    def contains(self, value: float) -> bool:
        return self.lower <= value <= self.upper


@dataclass(frozen=True)
class MiddleWorldReceipt:
    context_id: str
    fitness_scale_id: str
    conflict_load: Interval
    shared_optimum_fitness: Interval
    differentiated_optimum_fitness: Interval
    direct_gap: Interval
    direct_state: str
    decoupling: Interval | None
    architecture_cost: Interval | None
    decomposed_gap: Interval | None
    bridge_residual: Interval | None
    bridge_zero_compatible: bool | None


def _sub(a: Interval, b: Interval) -> Interval:
    return Interval(a.lower - b.upper, a.upper - b.lower)


def _mul_nonnegative(a: Interval, b: Interval) -> Interval:
    if min(a.lower, b.lower) < 0:
        raise ValueError("non-negative interval multiplication received a negative bound")
    return Interval(a.lower * b.lower, a.upper * b.upper)


def classify_bounded_receipt(
    *,
    context_id: str,
    fitness_scale_id: str,
    conflict_load: Interval,
    shared_optimum_fitness: Interval,
    differentiated_optimum_fitness: Interval,
    decoupling: Interval | None = None,
    architecture_cost: Interval | None = None,
) -> MiddleWorldReceipt:
    """Classify a matched empirical receipt without hiding uncertainty.

    Strong direct BALANCE evidence requires both:

    - the SCH conflict interval is strictly above zero;
    - the entire direct architecture-gap interval ``W_D* - W_S*`` is below zero.

    Strong direct BITA-side evidence requires a positive SCH conflict and the
    entire direct architecture-gap interval above zero.  Any interval crossing
    zero is returned as unresolved rather than forced into a state.

    ``decoupling`` and ``architecture_cost`` are optional.  When supplied,
    they generate an interval for ``sL-K`` and an interval bridge residual
    ``Delta_W-(sL-K)``.
    """
    if not context_id.strip() or not fitness_scale_id.strip():
        raise ValueError("context_id and fitness_scale_id are required")
    if conflict_load.lower < 0:
        raise ValueError("conflict-load interval must be non-negative")

    direct = _sub(differentiated_optimum_fitness, shared_optimum_fitness)
    conflict_positive = conflict_load.lower > 0
    conflict_absent = conflict_load.upper <= 0

    if conflict_positive and direct.upper < 0:
        state = "BALANCE_IDENTIFIED"
    elif conflict_positive and direct.lower > 0:
        state = "BITA_SIDE_IDENTIFIED"
    elif conflict_positive and direct.lower <= 0 <= direct.upper:
        state = "ARCHITECTURE_ORDER_UNRESOLVED"
    elif conflict_absent:
        state = "SCH_CONFLICT_NOT_ESTABLISHED"
    else:
        state = "SCH_CONFLICT_UNRESOLVED"

    if (decoupling is None) != (architecture_cost is None):
        raise ValueError("decoupling and architecture_cost must be supplied together")

    decomposed = None
    residual = None
    zero_compatible = None
    if decoupling is not None and architecture_cost is not None:
        if decoupling.lower < 0 or decoupling.upper > 1:
            raise ValueError("decoupling interval must lie in [0,1]")
        if architecture_cost.lower < 0:
            raise ValueError("architecture-cost interval must be non-negative")
        recoverable = _mul_nonnegative(decoupling, conflict_load)
        decomposed = _sub(recoverable, architecture_cost)
        residual = _sub(direct, decomposed)
        zero_compatible = residual.contains(0.0)

    return MiddleWorldReceipt(
        context_id=context_id,
        fitness_scale_id=fitness_scale_id,
        conflict_load=conflict_load,
        shared_optimum_fitness=shared_optimum_fitness,
        differentiated_optimum_fitness=differentiated_optimum_fitness,
        direct_gap=direct,
        direct_state=state,
        decoupling=decoupling,
        architecture_cost=architecture_cost,
        decomposed_gap=decomposed,
        bridge_residual=residual,
        bridge_zero_compatible=zero_compatible,
    )

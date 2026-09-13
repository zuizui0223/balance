"""Bounded empirical receipts shared by SCH, BALANCE, and BITA."""

from __future__ import annotations

from dataclasses import dataclass
import math


_MISSING_IDENTIFIERS = {"none", "null", "nan", "required_before_use"}


def _required_identifier(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a non-empty string identifier")
    out = value.strip()
    if not out or out.casefold() in _MISSING_IDENTIFIERS:
        raise ValueError(f"{name} must be a frozen non-missing identifier")
    return out


@dataclass(frozen=True)
class Interval:
    lower: float
    upper: float

    def __post_init__(self) -> None:
        try:
            lower = float(self.lower)
            upper = float(self.upper)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("interval bounds must be numeric and float-representable") from exc
        if not math.isfinite(lower) or not math.isfinite(upper):
            raise ValueError("bounded empirical interval endpoints must be finite")
        if lower > upper:
            raise ValueError("interval lower bound must not exceed upper bound")
        object.__setattr__(self, "lower", lower)
        object.__setattr__(self, "upper", upper)

    def contains(self, value: float) -> bool:
        try:
            value = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("interval membership value must be numeric and float-representable") from exc
        if not math.isfinite(value):
            raise ValueError("interval membership value must be finite")
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
    context_id = _required_identifier(context_id, "context_id")
    fitness_scale_id = _required_identifier(fitness_scale_id, "fitness_scale_id")
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

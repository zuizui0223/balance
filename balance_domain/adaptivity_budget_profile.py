"""Executable budget profile for the BALANCE branch-invariance control.

This module promotes the independent Bellman check from the regression test into
an optional diagnostic API.  It compares outcome-dependent choices of the next
DIRECTION with the existing exact allocation of forward/reverse query counts.
Midpoint query LOCATIONS remain adaptive in both classes.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from typing import Sequence

from .bounded_switching_design import BoundedSwitchingReceipt, _q
from .budgeted_switching_design import plan_budgeted_reset_refinement


@dataclass(frozen=True)
class BalanceAdaptivityBudgetRow:
    budget: int
    fixed_allocation_worst_span_exact: str
    adaptive_direction_worst_span_exact: str
    fixed_minus_adaptive_span_exact: str


@dataclass(frozen=True)
class BalanceAdaptivityBudgetProfile:
    rows: tuple[BalanceAdaptivityBudgetRow, ...]
    positive_adaptive_gain_budgets: tuple[int, ...]
    branch_invariance_certified_on_declared_budgets: bool
    scope: str = (
        "Cartesian_threshold_span_midpoint_resets_fixed_directional_errors_"
        "adaptive_direction_choice_vs_optimal_count_allocation"
    )


def _count(value: int, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _adaptive_direction_value(wf: F, wr: F, ef: F, er: F,
                              cf: int, cr: int, budget: int) -> F:
    """Exact Bellman value when next direction may depend on prior outcomes.

    At a minimax midpoint query, stay and switch outcomes have different interval
    locations but the SAME future span ``min(w, w/2+e)``.  Therefore the future
    value state is only ``(wf,wr,budget)`` under the declared fixed errors/costs.
    """
    @lru_cache(None)
    def value(f: F, r: F, b: int) -> F:
        choices = [f + r]
        if cf <= b:
            choices.append(value(min(f, f/2 + ef), r, b-cf))
        if cr <= b:
            choices.append(value(f, min(r, r/2 + er), b-cr))
        return min(choices)
    return value(wf, wr, budget)


def balance_adaptivity_budget_profile(
    receipt: BoundedSwitchingReceipt,
    *,
    budgets: Sequence[int],
    forward_query_error: object,
    reverse_query_error: object,
    matched_reset_available_declared: bool,
    forward_cost: int = 1,
    reverse_cost: int = 1,
) -> BalanceAdaptivityBudgetProfile:
    """Compare adaptive direction choice with the existing allocation optimum.

    A positive ``fixed_minus_adaptive_span`` would mean outcome-contingent
    direction choice improved the worst-case width-span objective.  Under this
    declared Cartesian midpoint model the exact Bellman and count-allocation
    solutions must coincide; a mismatch raises rather than being described as a
    scientific discovery.
    """
    values = tuple(budgets)
    if not values or any(type(b) is not int or b < 0 for b in values):
        raise ValueError("budgets must be a nonempty sequence of nonnegative integers")
    if len(set(values)) != len(values):
        raise ValueError("budgets must be unique")
    if matched_reset_available_declared is not True:
        raise ValueError("matched resets must be declared available")
    values = tuple(sorted(values))
    cf = _count(forward_cost, "forward cost", 1)
    cr = _count(reverse_cost, "reverse cost", 1)
    ef, er = _q(forward_query_error), _q(reverse_query_error)
    if min(ef, er) < 0:
        raise ValueError("query errors must be nonnegative")
    fb, rb = receipt.forward_cost_over_horizon, receipt.reverse_cost_over_horizon
    if fb.exact_upper is None or rb.exact_upper is None:
        raise ValueError("finite forward and reverse threshold brackets are required")
    wf = F(fb.exact_upper) - F(fb.exact_lower)
    wr = F(rb.exact_upper) - F(rb.exact_lower)

    fixed = plan_budgeted_reset_refinement(
        receipt,
        budget=max(values),
        forward_query_error=ef,
        reverse_query_error=er,
        matched_reset_available_declared=True,
        forward_cost=cf,
        reverse_cost=cr,
    )
    fixed_by_budget = {
        row.budget_cap: F(row.width_worst_span_exact)
        for row in fixed.frontier
    }
    rows = []
    positive = []
    for budget in values:
        adaptive = _adaptive_direction_value(wf, wr, ef, er, cf, cr, budget)
        fixed_value = fixed_by_budget[budget]
        gain = fixed_value - adaptive
        if gain < 0:
            raise ArithmeticError("adaptive direction Bellman is worse than the feasible fixed allocation")
        if gain != 0:
            positive.append(budget)
        rows.append(BalanceAdaptivityBudgetRow(
            budget, str(fixed_value), str(adaptive), str(gain)
        ))
    if positive:
        raise ArithmeticError(
            "branch-invariant BALANCE control produced an unexpected adaptive direction gain"
        )
    return BalanceAdaptivityBudgetProfile(tuple(rows), (), True)

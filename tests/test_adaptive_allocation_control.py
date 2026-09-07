"""Negative control: routing has no extra minimax gain in the existing model.

Midpoint LOCATIONS remain adaptive. This audit only compares adaptive choices
of direction with the existing optimal fixed allocation of directional counts.
"""
from fractions import Fraction as F
from functools import lru_cache
import random

from balance_domain.bounded_switching_design import (
    BoundedSwitchingReceipt, _band,
)
from balance_domain.budgeted_switching_design import plan_budgeted_reset_refinement


def bellman_direction_control(wf, wr, ef, er, cf, cr, budget):
    # At each midpoint, both supported responses have the same outer span.
    # Hence a history-dependent direction planner has this span-state recursion.
    @lru_cache(None)
    def value(f, r, b):
        choices = [f+r]
        if cf <= b:
            choices.append(value(min(f, f/2+ef), r, b-cf))
        if cr <= b:
            choices.append(value(f, min(r, r/2+er), b-cr))
        return min(choices)
    return value(wf, wr, budget)


def make_receipt(wf, wr):
    f, r = _band(F(1), 1+wf), _band(F(1), 1+wr)
    return BoundedSwitchingReceipt(f, r, _band(F(2), 2+wf+wr), True, True,
                                   None, 'synthetic units', 'synthetic fixed context')


def test_extra_direction_adaptivity_cannot_improve_registered_frontier():
    wf, wr, e = F(3, 100), F(4, 100), F(1, 200)
    observed = []
    for budget in range(5):
        v = bellman_direction_control(wf, wr, e, e, 1, 1, budget)
        observed.append(v)
    assert observed == list(map(F, ('0.07', '0.055', '0.045', '0.0375', '0.0325')))


def test_direction_bellman_matches_count_allocation_across_seeded_contracts():
    rng = random.Random(20260907)
    for _ in range(200):
        wf, wr = (F(rng.randint(1, 30), 100) for _ in range(2))
        ef, er = (F(rng.randint(0, 20), 200) for _ in range(2))
        cf, cr, budget = rng.randint(1, 3), rng.randint(1, 3), rng.randint(0, 8)
        receipt = plan_budgeted_reset_refinement(make_receipt(wf, wr), budget=budget,
            forward_query_error=ef, reverse_query_error=er,
            forward_cost=cf, reverse_cost=cr, matched_reset_available_declared=True)
        assert F(receipt.optimal.width_worst_span_exact) == bellman_direction_control(
            wf, wr, ef, er, cf, cr, budget)


def test_initial_precision_below_query_error_is_not_widened_by_adaptive_planning():
    assert bellman_direction_control(F(1, 100), F(1, 50), F(1, 10), F(1, 10), 1, 1, 10) == F(3, 100)

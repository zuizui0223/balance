from fractions import Fraction as F
import random

from balance_domain.adaptivity_budget_profile import (
    _adaptive_direction_value,
    balance_adaptivity_budget_profile,
)
from balance_domain.bounded_switching_design import BoundedSwitchingReceipt, _band


def _receipt(wf, wr):
    f = _band(F(1), F(1) + wf)
    r = _band(F(1), F(1) + wr)
    return BoundedSwitchingReceipt(
        f,
        r,
        _band(F(2), F(2) + wf + wr),
        True,
        True,
        None,
        "synthetic units",
        "synthetic fixed context",
    )


def test_registered_budget_profile_has_zero_direction_adaptivity_gap():
    profile = balance_adaptivity_budget_profile(
        _receipt(F(3, 100), F(4, 100)),
        budgets=(0, 1, 2, 3, 4),
        forward_query_error=F(1, 200),
        reverse_query_error=F(1, 200),
        matched_reset_available_declared=True,
    )
    assert profile.branch_invariance_certified_on_declared_budgets
    assert profile.positive_adaptive_gain_budgets == ()
    expected = tuple(map(F, ("0.07", "0.055", "0.045", "0.0375", "0.0325")))
    observed = tuple(F(row.adaptive_direction_worst_span_exact) for row in profile.rows)
    assert observed == expected
    assert all(F(row.fixed_minus_adaptive_span_exact) == 0 for row in profile.rows)


def test_zero_gap_profile_matches_seeded_unequal_cost_contracts():
    rng = random.Random(202609071337)
    for _ in range(50):
        wf = F(rng.randint(1, 30), 100)
        wr = F(rng.randint(1, 30), 100)
        ef = F(rng.randint(0, 20), 200)
        er = F(rng.randint(0, 20), 200)
        cf, cr = rng.randint(1, 3), rng.randint(1, 3)
        budgets = tuple(range(rng.randint(0, 3), rng.randint(4, 8)))
        if not budgets:
            budgets = (0,)
        profile = balance_adaptivity_budget_profile(
            _receipt(wf, wr),
            budgets=budgets,
            forward_query_error=ef,
            reverse_query_error=er,
            forward_cost=cf,
            reverse_cost=cr,
            matched_reset_available_declared=True,
        )
        assert profile.positive_adaptive_gain_budgets == ()
        assert all(F(row.fixed_minus_adaptive_span_exact) == 0 for row in profile.rows)


def test_independent_bellman_has_no_python_recursion_depth_ceiling():
    # At these errors both spans are already at their query-error floors, so the
    # Bellman value is unchanged by any query. The point of the large budget is
    # to lock in iterative evaluation: the old recursive implementation would
    # exceed Python's recursion depth long before reaching 5000 units.
    value = _adaptive_direction_value(
        F(3, 100),
        F(4, 100),
        F(1),
        F(1),
        1,
        1,
        5000,
    )
    assert value == F(7, 100)


def test_profile_rejects_invalid_budget_vocabulary():
    kwargs = dict(
        receipt=_receipt(F(3, 100), F(4, 100)),
        forward_query_error=F(1, 200),
        reverse_query_error=F(1, 200),
        matched_reset_available_declared=True,
    )
    for budgets in ((), (1, 1), (-1, 0)):
        try:
            balance_adaptivity_budget_profile(budgets=budgets, **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid budget list should fail")

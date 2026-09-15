from dataclasses import replace

import pytest

from balance_domain.adaptivity_budget_profile import balance_adaptivity_budget_profile
from balance_domain.bounded_switching_design import (
    identify_bounded_switching,
    plan_reset_refinement,
)
from balance_domain.budgeted_switching_design import (
    condition_reset_outcome,
    plan_budgeted_reset_refinement,
)


UP = [("0.095", "0.105", "shared"), ("0.115", "0.125", "differentiated")]
DOWN = [("-0.055", "-0.045", "differentiated"), ("-0.085", "-0.075", "shared")]
KW = dict(
    common_phi_scale="synthetic",
    fixed_context="matched",
    latent_monotone_and_instantaneous_declared=True,
)


def _receipt():
    return identify_bounded_switching(UP, DOWN, **KW)


def _all_downstream_consumers_reject(receipt):
    with pytest.raises(ValueError):
        plan_reset_refinement(
            receipt,
            forward_query_error="0.005",
            reverse_query_error="0.005",
            matched_reset_available_declared=True,
        )
    with pytest.raises(ValueError):
        plan_budgeted_reset_refinement(
            receipt,
            budget=2,
            forward_query_error="0.005",
            reverse_query_error="0.005",
            matched_reset_available_declared=True,
        )
    with pytest.raises(ValueError):
        balance_adaptivity_budget_profile(
            receipt,
            budgets=(0, 1, 2),
            forward_query_error="0.005",
            reverse_query_error="0.005",
            matched_reset_available_declared=True,
        )
    with pytest.raises(ValueError):
        condition_reset_outcome(
            receipt,
            direction="forward",
            query_phi="0.11",
            query_error="0.005",
            observed_state="shared",
            matched_reset_available_declared=True,
        )


def test_downstream_planners_reject_forged_display_vs_exact_threshold_band():
    receipt = _receipt()
    forged_band = replace(
        receipt.forward_cost_over_horizon,
        lower=receipt.forward_cost_over_horizon.lower + 0.001,
    )
    forged = replace(receipt, forward_cost_over_horizon=forged_band)
    _all_downstream_consumers_reject(forged)


def test_downstream_planners_reject_forged_exact_text_and_closure_semantics():
    receipt = _receipt()
    forged_exact = replace(receipt.forward_cost_over_horizon, exact_lower="0")
    _all_downstream_consumers_reject(
        replace(receipt, forward_cost_over_horizon=forged_exact)
    )

    forged_closure = replace(receipt.forward_cost_over_horizon, upper_closed=True)
    _all_downstream_consumers_reject(
        replace(receipt, forward_cost_over_horizon=forged_closure)
    )


def test_receipt_rejects_width_band_inconsistent_with_component_thresholds():
    receipt = _receipt()
    forged = replace(receipt, hysteresis_width=receipt.forward_cost_over_horizon)
    _all_downstream_consumers_reject(forged)


def test_receipt_rejects_non_boolean_or_inconsistent_switch_flags():
    receipt = _receipt()
    _all_downstream_consumers_reject(replace(receipt, forward_switch_observed=1))
    _all_downstream_consumers_reject(replace(receipt, forward_switch_observed=False))


def test_receipt_rejects_noncanonical_provenance_and_scope():
    receipt = _receipt()
    _all_downstream_consumers_reject(
        replace(receipt, common_phi_scale=" synthetic ")
    )
    _all_downstream_consumers_reject(
        replace(receipt, fixed_context="REQUIRED_BEFORE_USE")
    )
    _all_downstream_consumers_reject(replace(receipt, scope="forged_scope"))


def test_total_cost_boundedness_must_match_width_boundedness_when_present():
    receipt = identify_bounded_switching(UP, DOWN, **KW, horizon_bounds=(10, 10))
    assert receipt.total_cost is not None
    forged_cost = replace(receipt.total_cost, upper=None, exact_upper=None, upper_closed=False)
    forged = replace(receipt, total_cost=forged_cost)
    _all_downstream_consumers_reject(forged)


def test_valid_receipt_remains_usable_across_reset_budget_and_adaptivity_routes():
    receipt = _receipt()
    reset = plan_reset_refinement(
        receipt,
        forward_query_error="0.005",
        reverse_query_error="0.005",
        matched_reset_available_declared=True,
    )
    budgeted = plan_budgeted_reset_refinement(
        receipt,
        budget=2,
        forward_query_error="0.005",
        reverse_query_error="0.005",
        matched_reset_available_declared=True,
    )
    adaptive = balance_adaptivity_budget_profile(
        receipt,
        budgets=(0, 1, 2),
        forward_query_error="0.005",
        reverse_query_error="0.005",
        matched_reset_available_declared=True,
    )
    updated = condition_reset_outcome(
        receipt,
        direction="forward",
        query_phi="0.11",
        query_error="0.005",
        observed_state="shared",
        matched_reset_available_declared=True,
    )

    assert reset.best_directions == ("reverse",)
    assert budgeted.optimal.budget_cap == 2
    assert adaptive.branch_invariance_certified_on_declared_budgets
    assert updated.forward_cost_over_horizon.exact_lower == "21/200"

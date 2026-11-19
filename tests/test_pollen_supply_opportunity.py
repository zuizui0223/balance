"""Regression tests for purely synthetic supply and visitor-order predictions."""
from math import inf, nan

import pytest

from balance_domain.pollen_supply_opportunity import (
    build_synthetic_gate_and_order_scenarios,
    build_closed_stock_parameter_sweep,
    service_gated_output,
    simulate_visitor_order,
)


def test_low_visitation_can_remain_pollen_limited_but_buffer_source_depletion():
    out = build_synthetic_gate_and_order_scenarios()
    low = out["supply_by_visits"]["2"]
    assert low["baseline"]["visit_pickup_capacity"] == 20
    assert low["source_reduced"]["source_pollen_after_reduction"] == 50
    assert low["baseline"]["bounded_female_output_proxy"] == pytest.approx(
        3.2967995396436067
    )
    assert low["source_reduction_effect_on_output_proxy"] == pytest.approx(0.0)
    assert low["direct_hand_supplementation_gain"] == pytest.approx(
        2.2099108191841776
    )


def test_higher_legitimate_opportunity_exposes_source_supply_constraint():
    high = build_synthetic_gate_and_order_scenarios()["supply_by_visits"]["7"]
    assert high["baseline"]["donor_export_proxy"] == 70
    assert high["source_reduced"]["donor_export_proxy"] == 50
    assert high["source_reduction_effect_on_output_proxy"] == pytest.approx(
        1.212824772298359
    )
    assert high["direct_hand_supplementation_gain"] > 0


def test_visitor_order_reverses_relative_value_of_delayed_pollen_presentation():
    out = build_synthetic_gate_and_order_scenarios()
    early_thief = out["visitor_sequence"]["TLL"]
    early_legitimate = out["visitor_sequence"]["LTL"]
    assert early_thief["delayed_minus_burst_under_theft"] == pytest.approx(12.75)
    assert early_legitimate["delayed_minus_burst_under_theft"] == pytest.approx(-12.75)
    assert early_thief["delayed_minus_burst_under_sham"] == pytest.approx(0)
    assert early_legitimate["delayed_minus_burst_under_sham"] == pytest.approx(-10.5)
    assert early_thief["thief_specific_difference_in_stage_advantage"] == pytest.approx(12.75)
    assert early_legitimate["thief_specific_difference_in_stage_advantage"] == pytest.approx(-2.25)
    assert out["thief_specific_three_way_interaction_proxy"] == pytest.approx(15.0)


def test_donor_stock_conservation_with_two_programmes_and_all_three_orders():
    for order in ("TLL", "LTL", "LLT"):
        for delayed_fraction in (0.0, 0.25, 0.5, 1.0):
            for thief_fraction in (0.0, 0.2, 0.5, 1.0):
                trial = simulate_visitor_order(
                    event_order=order,
                    initial_pollen_total=123.0,
                    delayed_release_fraction=delayed_fraction,
                    legitimate_removal_fraction=0.3,
                    thief_removal_fraction=thief_fraction,
                    effective_transfer_fraction=0.75,
                )
                assert trial["conservation_residual"] == pytest.approx(0, abs=1e-9)
                assert (trial["total_legitimate_pollen_removed"] +
                        trial["total_pollen_stolen"] +
                        trial["remaining_pollen"]) == pytest.approx(123.0)
                assert trial["effective_export_proxy"] <= (
                    trial["total_legitimate_pollen_removed"] + 1e-9
                )
                assert len(trial["visitor_trace"]) == 3


def test_post_service_thief_cannot_undo_prior_export_in_closed_model():
    early = simulate_visitor_order(
        event_order="LLT", initial_pollen_total=100,
        delayed_release_fraction=0, legitimate_removal_fraction=0.3,
        thief_removal_fraction=0.5,
    )
    sham = simulate_visitor_order(
        event_order="LLT", initial_pollen_total=100,
        delayed_release_fraction=0, legitimate_removal_fraction=0.3,
        thief_removal_fraction=0,
    )
    assert early["effective_export_proxy"] == pytest.approx(51)
    assert sham["effective_export_proxy"] == pytest.approx(51)
    assert early["total_pollen_stolen"] > 0


@pytest.mark.parametrize("invalid", (-0.01, 1.01, nan, inf, -inf, True, "0.5"))
def test_invalid_thief_fraction_fails_closed(invalid):
    with pytest.raises(ValueError):
        simulate_visitor_order(
            event_order="TLL", initial_pollen_total=100,
            delayed_release_fraction=.5, legitimate_removal_fraction=.3,
            thief_removal_fraction=invalid,
        )


@pytest.mark.parametrize("order", ("T", "LTT", "LLL", "TTT", "TLX", "", None))
def test_wrong_visitor_schedule_rejected(order):
    with pytest.raises(ValueError, match="event_order"):
        simulate_visitor_order(
            event_order=order, initial_pollen_total=100,
            delayed_release_fraction=.5,
            legitimate_removal_fraction=.3,
            thief_removal_fraction=.5,
        )


@pytest.mark.parametrize("count", (1.5, -1, True, "2", None))
def test_noninteger_or_invalid_legitimate_visits_fails_closed(count):
    with pytest.raises(ValueError, match="legitimate_visits"):
        service_gated_output(
            initial_source_pollen=100, source_removal_fraction=.5,
            legitimate_visits=count, pickup_capacity_per_visit=10,
            transfer_success_fraction=1, response_scale=50, output_ceiling=10,
        )


def test_no_biological_outcome_or_architecture_promotion():
    result = build_synthetic_gate_and_order_scenarios()
    assert result["status"] == "SYNTHETIC_PROSPECTIVE_MODEL_ONLY"
    assert result["data_used_for_model_calibration"] is False
    assert result["empirical_fitness_or_paternity_inferred"] is False
    assert result["architecture_fitness_comparison_performed"] is False


def test_fixed_81_scenario_grid_shows_model_only_order_reversal():
    result = build_closed_stock_parameter_sweep()
    assert result["parameter_combinations"] == 81
    assert result["positive_delayed_advantage_if_thief_first"] == 81
    assert result["negative_delayed_advantage_if_legitimate_first"] == 81
    assert result["positive_thief_adjusted_triple_contrast"] == 81
    assert result["minimum_thief_adjusted_triple_contrast"] == pytest.approx(0.25)
    assert result["maximum_thief_adjusted_triple_contrast"] == pytest.approx(72.0)
    assert result["empirical_studies_counted"] == 0
    assert result["status"] == "ALL_SYNTHETIC_SAME_CLOSED_STOCK_MECHANISM"

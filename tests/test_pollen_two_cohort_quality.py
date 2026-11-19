"""Independent regression guards for the hypothetical two-cohort quality model."""
import pytest

from balance_domain.pollen_supply_opportunity import simulate_visitor_order
from balance_domain.pollen_two_cohort_quality import (
    quality_threshold_sweep,
    scenario_with_quality,
    track_two_pollen_cohorts,
)


def test_equal_quality_matches_frozen_original_model_for_all_orders_and_release_schedules():
    for order in ("TLL", "LTL", "LLT"):
        for d in (0, 0.25, 0.5, 0.75, 1.0):
            for b in (0, 0.2, 0.5, 0.9, 1.0):
                current = track_two_pollen_cohorts(
                    order=order, total_pollen=100.0,
                    delayed_fraction=d, legitimate_pickup_fraction=0.3,
                    thief_pickup_fraction=b, late_relative_effective_contribution=1.0,
                    legitimate_transfer_efficiency=0.75,
                )
                previous = simulate_visitor_order(
                    event_order=order, initial_pollen_total=100.0,
                    delayed_release_fraction=d,
                    legitimate_removal_fraction=0.3,
                    thief_removal_fraction=b, effective_transfer_fraction=0.75,
                )
                assert current["quality_weighted_export_proxy"] == pytest.approx(
                    previous["effective_export_proxy"]
                )
                assert current["pollen_leftover"] == pytest.approx(
                    previous["remaining_pollen"]
                )
                assert current["thief_pollen_removed"] == pytest.approx(
                    previous["total_pollen_stolen"]
                )
                assert current["physical_mass_balance_residual"] == pytest.approx(
                    0, abs=1e-9
                )


def test_early_thief_delayed_release_requires_quality_above_one_minus_theft_fraction():
    examples = quality_threshold_sweep()
    assert examples["threshold_q_at_b_half"] == pytest.approx(0.5)
    assert examples["number_positive_delayed_effect_thief_first"] == 2
    assert examples["number_negative_delayed_effect_thief_first"] == 2
    assert examples["number_zero_delayed_effect_thief_first"] == 1
    assert examples["source_experimental_data_rows_used"] == 0
    assert [x["raw_delayed_advantage_thief_first"] for x in examples["scenarios"]] == pytest.approx(
        [-12.75, -6.375, 0, 6.375, 12.75]
    )


def test_threshold_closed_form_exactly_pins_sign_at_multiple_thief_levels():
    for b in (0.1, 0.3, 0.5, 0.8):
        theta = 1-b
        gap_equal = scenario_with_quality(b=b, q=theta)
        assert gap_equal["raw_delayed_advantage_thief_first"] == pytest.approx(0, abs=1e-9)
        if theta >= 0.1:
            below = scenario_with_quality(b=b, q=theta-0.05)
            assert below["raw_delayed_advantage_thief_first"] < 0
        above = scenario_with_quality(b=b, q=theta + min(b/2, 0.05))
        assert above["raw_delayed_advantage_thief_first"] > 0


def test_sham_adjusted_triple_interaction_remains_positive_while_raw_sign_changes():
    for q, gamma in [(0.0, 7.5), (0.25, 9.375), (0.5, 11.25), (0.75, 13.125), (1.0, 15.0)]:
        case = scenario_with_quality(q=q)
        assert case["sham_adjusted_three_way_interaction"] == pytest.approx(gamma)
        assert case["closed_form_interaction"] == pytest.approx(gamma)
        assert case["raw_delayed_advantage_legitimate_first"] < 0
    assert scenario_with_quality(q=0.25)["raw_delayed_advantage_thief_first"] < 0
    assert scenario_with_quality(q=1.0)["raw_delayed_advantage_thief_first"] > 0


def test_quality_reweighting_changes_siring_proxy_not_physical_pollen_accounting():
    for q in (0.0, 0.2, 0.4, 0.8, 1.0):
        out = track_two_pollen_cohorts(
            order="TLL", total_pollen=100.0,
            delayed_fraction=0.5,
            legitimate_pickup_fraction=0.3,
            thief_pickup_fraction=0.5,
            late_relative_effective_contribution=q,
        )
        assert out["legitimate_pollen_removed_total"] == pytest.approx(38.25)
        assert out["thief_pollen_removed"] == pytest.approx(25)
        assert out["pollen_leftover"] == pytest.approx(36.75)
        assert out["physical_mass_balance_residual"] == pytest.approx(0)
        assert 0 <= out["quality_weighted_export_proxy"] <= 38.25
        assert "not_genetic_siring" in out["claim_ceiling"]


@pytest.mark.parametrize("invalid", (-1, 1.01, float("nan"), float("inf"), True, "0.5"))
def test_quality_out_of_range_fails_closed(invalid):
    with pytest.raises(ValueError):
        scenario_with_quality(q=invalid)


def test_zero_effect_parameters_are_not_called_an_identified_threshold():
    with pytest.raises(ValueError, match="positive P"):
        scenario_with_quality(P=0, q=1)
    with pytest.raises(ValueError, match="positive P"):
        scenario_with_quality(d=0, q=1)
    with pytest.raises(ValueError, match="positive P"):
        scenario_with_quality(a=0, q=1)
    with pytest.raises(ValueError, match="positive P"):
        scenario_with_quality(b=0, q=1)

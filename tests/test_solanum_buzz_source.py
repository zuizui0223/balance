"""Regress one-study Solanum buzzer kinetics without inventing original data."""
import json
from math import exp, log

import pytest

from balance_domain.solanum_buzz_source import (
    SOURCE, TIMES_SECONDS, build_solanum_published_kinetics_audit,
    pollen_release_curve, source_readout,
)


def test_published_study_grain_and_nonindependence_explicit():
    out = build_solanum_published_kinetics_audit()
    assert out["sampling_grain"] == {
        "flowers": 80,
        "bees": 13,
        "colonies": 1,
        "buzzes_nested_not_independent": 2101,
        "independent_research_programmes": 1,
        "independent_evolutionary_transition_replications": 0,
    }
    assert out["independent_species_level_replication_added_to_U3"] is False
    assert out["new_original_biological_effects_estimated"] == 0
    assert out["q_threshold_and_thief_order_tested"] is False


def test_two_published_source_rate_models_reproduce_predicted_buzz_dose_curves():
    readout = build_solanum_published_kinetics_audit()
    fits = readout["published_model_predictions"]
    assert set(fits) == {"original_nonlinear_fit", "bee_mixed_log_linear_fit"}
    assert fits["original_nonlinear_fit"]["source_fitted_rate_per_buzz_second"] == 0.027
    assert fits["bee_mixed_log_linear_fit"]["source_fitted_rate_per_buzz_second"] == 0.036
    assert fits["original_nonlinear_fit"]["half_life_using_rounded_r_seconds"] == pytest.approx(
        log(2)/0.027
    )
    assert fits["bee_mixed_log_linear_fit"]["half_life_using_rounded_r_seconds"] == pytest.approx(
        log(2)/0.036
    )
    for fit in fits.values():
        arr = fit["predictions_at_prespecified_buzz_duration_seconds"]
        assert [x["cumulative_buzz_seconds"] for x in arr] == list(TIMES_SECONDS)
        assert arr[0]["fraction_released"] == pytest.approx(0)
        assert all(
            arr[i]["fraction_released"] < arr[i+1]["fraction_released"]
            for i in range(len(arr)-1)
        )
        assert all(
            a["pollen_remaining_model"] + a["pollen_released_model"]
            == pytest.approx(fit["source_fitted_available_pollen_A0"])
            for a in arr
        )


def test_mean_buzz_time_is_model_conditional_not_mean_empirical_release():
    fits = build_solanum_published_kinetics_audit()["published_model_predictions"]
    avg_duration_index = 1
    lower = fits["original_nonlinear_fit"][
        "predictions_at_prespecified_buzz_duration_seconds"
    ][avg_duration_index]["fraction_released"]
    upper = fits["bee_mixed_log_linear_fit"][
        "predictions_at_prespecified_buzz_duration_seconds"
    ][avg_duration_index]["fraction_released"]
    assert lower == pytest.approx(1-exp(-0.027*0.748))
    assert upper == pytest.approx(1-exp(-0.036*0.748))
    assert lower == pytest.approx(0.01999342680678673)
    assert upper == pytest.approx(0.026568673943260568)


def test_mixed_A0_table_vs_prose_difference_must_not_be_silently_resolved():
    out = build_solanum_published_kinetics_audit()
    assert out["text_table_pollen_A0_conflict"] == {
        "table1_A0": 352284,
        "results_prose_A0": 352384,
        "difference_grains": 100,
        "state": "SOURCE_DISCREPANCY_UNRESOLVED_NOT_SILENTLY_CORRECTED",
    }
    assert out["pollen_available_fraction_alternative_assumptions"] == {
        "using_mean_control_total": 0.955,
        "using_maximum_pollen_remaining": 0.537,
        "different_denominators_not_a_statistical_confidence_interval": True,
    }


@pytest.mark.parametrize("r,t,p", [
    (float("nan"), 1, 100), (float("inf"), 1, 100),
    (0, 1, 100), (0.03, -1, 100), (0.03, 1, 0),
    (0.03, 1, -1), (0.03, 1, True), ("0.03", 1, 100),
])
def test_illegal_source_rate_inputs_fail_closed(r,t,p):
    with pytest.raises(ValueError):
        pollen_release_curve(
            rate_per_buzz_second=r,
            cumulative_buzz_seconds=t,
            available_pollen_grains=p,
        )


def test_disallowed_raw_data_or_male_fitness_upgrade_fails_closed(tmp_path):
    orig = json.loads(SOURCE.read_text(encoding="utf-8"))
    orig["archive"]["original_csv_independently_refitted"] = True
    path = tmp_path / "wrong_source.json"
    path.write_text(json.dumps(orig), encoding="utf-8")
    with pytest.raises(ValueError, match="new model fits"):
        source_readout(path)


def test_same_taxon_U3_prior_record_cannot_be_renamed_independent_evolution(tmp_path):
    orig = json.loads(SOURCE.read_text(encoding="utf-8"))
    orig["biological_inference_boundaries"][
        "not_independent_evolutionary_lineage_from_prior_U3_S_rostratum"
    ] = False
    path = tmp_path / "wrong_species_independence.json"
    path.write_text(json.dumps(orig), encoding="utf-8")
    with pytest.raises(ValueError, match="Same-taxon U3 dependence"):
        source_readout(path)

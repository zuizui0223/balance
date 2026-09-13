import json
import math
from pathlib import Path

import pytest

from balance_domain.peucedanum_proxy import analyze_peucedanum_proxy_criticality


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "empirical" / "peucedanum" / "PEUCEDANUM_ANTAGONIST_PROXY_CRITICALITY_INPUT_V1.json"


def _config():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    # Keep the regression test fast while preserving the registered seed/model.
    config["registered_sensitivity_model"]["draws"] = 5000
    return config


def _run():
    return analyze_peucedanum_proxy_criticality(_config())


def test_peucedanum_proxy_analysis_preserves_observational_claim_ceiling():
    result = _run()
    assert result["classification"] == "SAME_NUMERIC_PROXY_CRITICAL_CONTEXT_COMPATIBLE"
    assert result["common_conditional_95_interval"] is not None
    lo, hi = result["common_conditional_95_interval"]
    assert 1.9 < lo < 2.2
    assert 2.3 < hi < 2.6
    assert "not_direct_middle_world_receipt" in result["claim_ceiling"]
    assert "not_causal_architecture_threshold" in result["claim_ceiling"]


def test_proxy_point_estimates_match_registered_published_summary_inputs():
    result = _run()
    points = {
        key: value["point_critical_proxy"]
        for key, value in result["definitions"].items()
    }
    assert math.isclose(points["final_fruit_selection_gradient_beta"], 2.422539682539682)
    assert math.isclose(points["final_fruit_selection_differential_S"], 2.24)
    assert math.isclose(points["female_gain_exponent_b_minus_1"], 1.9507142857142856)
    assert result["point_estimate_spread_fraction_of_observed_bracket"] > 0.3


def test_gain_shape_definition_is_less_sign_stable_than_selection_definitions():
    result = _run()
    beta = result["definitions"]["final_fruit_selection_gradient_beta"]["sign_consistent_draw_fraction"]
    differential = result["definitions"]["final_fruit_selection_differential_S"]["sign_consistent_draw_fraction"]
    gain = result["definitions"]["female_gain_exponent_b_minus_1"]["sign_consistent_draw_fraction"]
    assert beta > 0.95
    assert differential > 0.99
    assert 0.65 < gain < 0.85


def test_monte_carlo_draw_count_and_seed_must_be_exact_finite_integers():
    config = _config()
    config["registered_sensitivity_model"]["draws"] = 5000.5
    with pytest.raises(ValueError, match="integer-valued"):
        analyze_peucedanum_proxy_criticality(config)

    config = _config()
    config["registered_sensitivity_model"]["random_seed"] = math.nan
    with pytest.raises(ValueError, match="integer-valued"):
        analyze_peucedanum_proxy_criticality(config)


def test_definition_means_and_standard_errors_must_be_finite():
    for field, bad in (("left_se", math.nan), ("right_se", math.inf), ("left_mean", math.nan)):
        config = _config()
        definition = config["definitions"]["final_fruit_selection_gradient_beta"]
        definition[field] = bad
        with pytest.raises(ValueError, match="must be finite"):
            analyze_peucedanum_proxy_criticality(config)


def test_proxy_axis_must_have_a_finite_nonzero_span_and_distinct_contexts():
    config = _config()
    config["proxy_axis"]["left_value"] = -1e308
    config["proxy_axis"]["right_value"] = 1e308
    with pytest.raises(ValueError, match="finite nonzero span"):
        analyze_peucedanum_proxy_criticality(config)

    config = _config()
    config["proxy_axis"]["right_context"] = config["proxy_axis"]["left_context"]
    with pytest.raises(ValueError, match="contexts must be distinct"):
        analyze_peucedanum_proxy_criticality(config)


def test_proxy_analysis_requires_at_least_one_definition_and_zero_semantics():
    config = _config()
    config["definitions"] = {}
    with pytest.raises(ValueError, match="non-empty mapping"):
        analyze_peucedanum_proxy_criticality(config)

    config = _config()
    config["definitions"]["final_fruit_selection_gradient_beta"]["zero_semantics"] = ""
    with pytest.raises(ValueError, match="zero_semantics must be non-empty"):
        analyze_peucedanum_proxy_criticality(config)

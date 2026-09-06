import json
import math
from pathlib import Path

from balance_domain.peucedanum_proxy import analyze_peucedanum_proxy_criticality


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "empirical" / "peucedanum" / "PEUCEDANUM_ANTAGONIST_PROXY_CRITICALITY_INPUT_V1.json"


def _run():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    # Keep the regression test fast while preserving the registered seed/model.
    config["registered_sensitivity_model"]["draws"] = 5000
    return analyze_peucedanum_proxy_criticality(config)


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

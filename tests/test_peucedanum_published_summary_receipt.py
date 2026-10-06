import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "empirical" / "peucedanum"
RECEIPT = BASE / "PEUCEDANUM_2025_PUBLISHED_SUMMARY_RECEIPT_V1.json"
CRITICAL = BASE / "PEUCEDANUM_CRITICAL_DEFINITIONS_V1.json"
LONGITUDINAL = BASE / "PEUCEDANUM_LONGITUDINAL_MOSAIC_INPUT_V2.json"
PROXY = BASE / "PEUCEDANUM_ANTAGONIST_PROXY_CRITICALITY_INPUT_V1.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_direct_source_receipt_matches_all_registered_peucedanum_point_estimates():
    receipt = _load(RECEIPT)
    critical = _load(CRITICAL)
    longitudinal = _load(LONGITUDINAL)

    contexts = receipt["ordered_contexts"]
    s = receipt["final_fruit_set_rate"]["linear_selection_differential_S"]
    beta = receipt["final_fruit_set_rate"]["linear_selection_gradient_beta"]
    b = receipt["female_gain_exponent_b"]

    assert critical["ordered_contexts"] == contexts
    assert {
        context: s[context]["estimate"] for context in contexts
    } == critical["definitions"]["final_fruit_selection_differential_S"]
    assert {
        context: beta[context]["estimate"] for context in contexts
    } == critical["definitions"]["final_fruit_selection_gradient_beta"]
    assert {
        context: round(b[context]["estimate"] - 1.0, 2) for context in contexts
    } == critical["definitions"]["female_gain_exponent_minus_one"]
    assert {
        context: beta[context]["estimate"] for context in contexts
    } == longitudinal["source_layers"]["2025_selection_mosaic"][
        "final_fruit_selection_gradient_beta"
    ]


def test_proxy_hl_hc_uncertainty_is_exactly_the_direct_source_receipt():
    receipt = _load(RECEIPT)
    proxy = _load(PROXY)["definitions"]

    s = receipt["final_fruit_set_rate"]["linear_selection_differential_S"]
    beta = receipt["final_fruit_set_rate"]["linear_selection_gradient_beta"]
    b = receipt["female_gain_exponent_b"]

    assert proxy["final_fruit_selection_differential_S"] == {
        "left_mean": s["HL"]["estimate"],
        "left_se": s["HL"]["se"],
        "right_mean": s["HC"]["estimate"],
        "right_se": s["HC"]["se"],
        "zero_semantics": (
            "no univariate standardized selection differential on perfect-flower "
            "production for final fruit-set rate"
        ),
    }
    assert proxy["final_fruit_selection_gradient_beta"] == {
        "left_mean": beta["HL"]["estimate"],
        "left_se": beta["HL"]["se"],
        "right_mean": beta["HC"]["estimate"],
        "right_se": beta["HC"]["se"],
        "zero_semantics": (
            "no direct standardized selection gradient on perfect-flower production "
            "for final fruit-set rate"
        ),
    }
    assert proxy["female_gain_exponent_b_minus_1"] == {
        "left_mean": round(b["HL"]["estimate"] - 1.0, 2),
        "left_se": b["HL"]["se"],
        "right_mean": round(b["HC"]["estimate"] - 1.0, 2),
        "right_se": b["HC"]["se"],
        "zero_semantics": "female-gain exponent b equals one",
    }


def test_direct_source_receipt_freezes_current_corrected_article_surface():
    receipt = _load(RECEIPT)
    assert receipt["status"] == "DIRECT_PRIMARY_SOURCE_VERIFIED"
    assert receipt["source"]["doi"] == "10.1111/1365-2745.70130"
    assert receipt["source"]["table"] == "Table 3"
    assert receipt["source"]["source_verification_date"] == "2026-10-06"
    assert "2025-09-02" in receipt["source"]["correction_note"]
    assert receipt["verified_regime_pattern"]["coarse_transition_bracket"] == [
        "HL",
        "HC",
    ]
    assert receipt["existing_balance_fixture_crosscheck"] == {
        "final_fruit_selection_differential_all_five_estimates_match": True,
        "final_fruit_selection_gradient_all_five_estimates_match": True,
        "female_gain_exponent_all_five_estimates_match": True,
        "no_numeric_fixture_correction_required": True,
    }

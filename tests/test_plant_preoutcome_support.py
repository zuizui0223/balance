import json
from pathlib import Path

from balance_domain.plant_preoutcome_support import build_preoutcome_predictor_support


ROOT = Path(__file__).resolve().parents[1]
U2_CONFLICT = ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv"
U2_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U6_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
FREEZE = ROOT / "data" / "BALANCE_PLANT_PREOUTCOME_PREDICTOR_SUPPORT_V1.json"


def test_preoutcome_predictor_support_recomputes_v3_freeze():
    out = build_preoutcome_predictor_support(U2_CONFLICT, U2_RECEIPTS, U6_RECEIPTS)
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))

    assert out["n_groups"] == 29
    assert out["universe_counts"] == {"U2": 8, "U6": 21}
    assert out["module_opportunity2_counts"] == {"MODULAR": 3, "SINGLE": 26}
    assert out["temporal_exposure3_counts"] == {
        "ORDERED_OR_ALTERNATING": 5,
        "SIMULTANEOUS": 21,
        "VARIABLE_CONTEXT": 3,
    }
    assert out["spatial_exposure2_counts"] == {
        "DISTRIBUTED": 1,
        "SAME_UNIT": 28,
    }
    assert out["axis_support_sufficient_for_primary_joint_model"] == {
        "module_opportunity2": True,
        "temporal_exposure3": True,
        "spatial_exposure2": False,
    }
    assert out["recommended_primary_axes"] == [
        "module_opportunity2",
        "temporal_exposure3",
    ]
    assert out["secondary_due_support_axis"] == "spatial_exposure2"
    assert out["architecture_outcomes_used"] is False

    assert frozen["n_source_screened_conflict_positive_groups"] == out["n_groups"]
    assert frozen["universe_counts"] == out["universe_counts"]
    assert frozen["primary_contrast_support"]["module_opportunity2"] == out["module_opportunity2_counts"]
    assert frozen["primary_contrast_support"]["temporal_exposure3"] == out["temporal_exposure3_counts"]
    assert frozen["primary_contrast_support"]["spatial_exposure2"] == out["spatial_exposure2_counts"]
    assert frozen["decision"] == "DEMOTE_SPATIAL_FROM_PRIMARY_FIXED_EFFECT_BEFORE_OUTCOME_CODING"

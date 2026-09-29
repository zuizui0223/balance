from pathlib import Path

from balance_domain.plant_preoutcome_generality import (
    build_preoutcome_generality_audit,
)


ROOT = Path(__file__).resolve().parents[1]
U2_CONFLICT = ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv"
U2_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U6_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"


def test_only_timing_simultaneous_vs_ordered_is_cross_universe_replicated_preoutcome():
    out = build_preoutcome_generality_audit(
        U2_CONFLICT,
        U2_RECEIPTS,
        U6_RECEIPTS,
    )

    assert out["universe_counts"] == {"U2": 8, "U6": 21}
    assert out["predictor_counts_by_universe"]["U2"] == {
        "module_opportunity2": {"MODULAR": 3, "SINGLE": 5},
        "temporal_exposure3": {
            "ORDERED_OR_ALTERNATING": 2,
            "SIMULTANEOUS": 3,
            "VARIABLE_CONTEXT": 3,
        },
        "spatial_exposure2": {"DISTRIBUTED": 1, "SAME_UNIT": 7},
    }
    assert out["predictor_counts_by_universe"]["U6"] == {
        "module_opportunity2": {"SINGLE": 21},
        "temporal_exposure3": {
            "ORDERED_OR_ALTERNATING": 3,
            "SIMULTANEOUS": 18,
        },
        "spatial_exposure2": {"SAME_UNIT": 21},
    }
    assert out["shared_predictor_levels"] == {
        "module_opportunity2": ["SINGLE"],
        "temporal_exposure3": ["ORDERED_OR_ALTERNATING", "SIMULTANEOUS"],
        "spatial_exposure2": ["SAME_UNIT"],
    }
    assert out["cross_universe_replicated_contrasts"] == {
        "module_SINGLE_vs_MODULAR": False,
        "timing_SIMULTANEOUS_vs_ORDERED": True,
        "timing_VARIABLE_CONTEXT_contrast": False,
        "spatial_SAME_UNIT_vs_DISTRIBUTED": False,
    }
    assert out["only_current_cross_universe_two_level_contrast"] == (
        "timing_SIMULTANEOUS_vs_ORDERED"
    )
    assert out["sampling_universe_adjustment_recommended"] is True
    assert out["architecture_outcomes_used"] is False



def test_cross_universe_timing_marginal_replication_lacks_common_module_support():
    out = build_preoutcome_generality_audit(
        U2_CONFLICT,
        U2_RECEIPTS,
        U6_RECEIPTS,
    )
    assert out["module_timing_joint_counts_by_universe"]["U2"] == {
        "SINGLE__SIMULTANEOUS": 1,
        "SINGLE__ORDERED_OR_ALTERNATING": 2,
        "SINGLE__VARIABLE_CONTEXT": 2,
        "MODULAR__SIMULTANEOUS": 2,
        "MODULAR__ORDERED_OR_ALTERNATING": 0,
        "MODULAR__VARIABLE_CONTEXT": 1,
    }
    assert out["module_timing_joint_counts_by_universe"]["U6"] == {
        "SINGLE__SIMULTANEOUS": 18,
        "SINGLE__ORDERED_OR_ALTERNATING": 3,
        "SINGLE__VARIABLE_CONTEXT": 0,
        "MODULAR__SIMULTANEOUS": 0,
        "MODULAR__ORDERED_OR_ALTERNATING": 0,
        "MODULAR__VARIABLE_CONTEXT": 0,
    }
    assert out["shared_module_levels"] == ["SINGLE"]
    assert out["temporal_common_support_module_strata"] == []
    assert out["temporal_cross_universe_common_support_ready"] is False

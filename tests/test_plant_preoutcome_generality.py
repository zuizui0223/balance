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
    assert out["u2_complete_outcome_independent_predictor_groups"] == 8
    assert out["u2_complete_predictor_groups_equal_source_positive"] is True
    assert (
        out["final_u2_licensed_rows_are_subset_only_under_frozen_receipts"]
        is True
    )
    assert (
        out[
            "temporal_common_support_reachable_without_predictor_receipt_expansion"
        ]
        is False
    )
    assert out["temporal_common_support_reachability_shortfall"] == {
        "SINGLE": {
            "U2": {
                "SIMULTANEOUS": 1,
                "ORDERED_OR_ALTERNATING": 0,
            },
            "U6": {
                "SIMULTANEOUS": 0,
                "ORDERED_OR_ALTERNATING": 0,
            },
        }
    }



def test_v4_main_predictor_design_is_full_rank_even_though_generality_gate_is_not_ready():
    out = build_preoutcome_generality_audit(
        U2_CONFLICT,
        U2_RECEIPTS,
        U6_RECEIPTS,
    )
    assert out["v4_preoutcome_slope_design_rank"] == 3
    assert out["v4_preoutcome_slope_design_column_count"] == 3
    assert out["v4_preoutcome_slope_design_full_rank"] is True
    assert out["v4_preoutcome_full_design_rank"] == 5
    assert out["v4_preoutcome_full_design_column_count"] == 5
    assert out["v4_preoutcome_full_design_full_rank"] is True
    assert out["v4_main_predictor_design_viable"] is True
    assert out["temporal_cross_universe_common_support_ready"] is False



def test_strict_temporal_generality_cannot_be_repaired_by_final_u2_subsetting():
    out = build_preoutcome_generality_audit(
        U2_CONFLICT,
        U2_RECEIPTS,
        U6_RECEIPTS,
    )
    assert out["temporal_cross_universe_common_support_ready"] is False
    assert (
        out["temporal_common_support_reachable_without_predictor_receipt_expansion"]
        is False
    )
    assert "final adjudication alone cannot increase" in (
        out["prospective_reopening_rule"]
    )

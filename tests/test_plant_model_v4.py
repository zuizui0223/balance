import pytest

from balance_domain.plant_model_v4 import build_v4_estimability_report


def _row(universe, group, mode, module, timing, spatial="SAME_UNIT", *, block=None):
    return {
        "universe_id": universe,
        "dependency_group": group,
        "dependence_block": block or group,
        "architecture_mode": mode,
        "module_substrate": module,
        "conflict_timing_geometry": timing,
        "conflict_spatial_geometry": spatial,
    }


def _ready_rows():
    u2 = "U2_BARRETT_2002"
    u6 = "U6_POLLEN_THEFT_HARGREAVES_2009"
    return [
        _row(u2, "u2_s1", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row(u2, "u2_s2", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _row(u2, "u2_n1", "TEMPORAL_SEPARATION", "SERIAL_WITHIN_FLOWER", "SEASONALLY_ALTERNATING"),
        _row(u2, "u2_n2", "SPATIAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row(u2, "u2_n3", "TEMPORAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _row(u2, "u2_d1", "WITHIN_FLOWER_DIVISION_OF_LABOUR", "REPEATED_FLOWERS", "CONTEXT_DEPENDENT"),
        _row(u2, "u2_m1", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "MIXED", "BETWEEN_MODULES"),
        _row(u6, "u6_s1", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row(u6, "u6_n1", "TEMPORAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _row(u6, "u6_n2", "SPATIAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row(u6, "u6_d1", "AMONG_FLOWER_MODULE_DIVISION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row(u6, "u6_m1", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEASONALLY_ALTERNATING"),
    ]


def test_v4_primary_and_cross_universe_timing_generality_can_both_pass():
    out = build_v4_estimability_report(_ready_rows())
    assert out["primary_universe_dependence_block_counts"] == {
        "U2_BARRETT_2002": 7,
        "U6_POLLEN_THEFT_HARGREAVES_2009": 5,
    }
    assert out["response_class_dependence_block_counts"] == {
        "SHARED": 3,
        "NONSTRUCTURAL_SEPARATION": 5,
        "STRUCTURAL_MODULE_DIVISION": 2,
        "MOSAIC": 2,
    }
    assert out["module_level_dependence_block_counts"] == {
        "SINGLE": 10,
        "MODULAR": 2,
    }
    assert out["temporal_level_dependence_block_counts"] == {
        "SIMULTANEOUS": 5,
        "ORDERED_OR_ALTERNATING": 5,
        "VARIABLE_CONTEXT": 2,
    }
    assert out["temporal_cross_universe_support"] == {
        "U2_BARRETT_2002": {
            "SIMULTANEOUS": 2,
            "ORDERED_OR_ALTERNATING": 3,
        },
        "U6_POLLEN_THEFT_HARGREAVES_2009": {
            "SIMULTANEOUS": 3,
            "ORDERED_OR_ALTERNATING": 2,
        },
    }
    assert out["temporal_cross_universe_marginal_replication_ready"] is True
    assert out["shared_module_levels_across_universes"] == ["SINGLE"]
    assert out["temporal_common_support_module_strata"] == ["SINGLE"]
    assert out["temporal_cross_universe_common_support_ready"] is True
    assert out["temporal_cross_universe_outcome_support"] == {
        "U2_BARRETT_2002": {
            "NONSTRUCTURAL_SEPARATION": 3,
            "OTHER_ARCHITECTURE": 4,
        },
        "U6_POLLEN_THEFT_HARGREAVES_2009": {
            "NONSTRUCTURAL_SEPARATION": 2,
            "OTHER_ARCHITECTURE": 3,
        },
    }
    assert out["temporal_cross_universe_outcome_support_ready"] is True
    assert out["temporal_cross_universe_generality_ready"] is True
    assert out["module_timing_joint_support_by_universe"]["U2_BARRETT_2002"] == {
        "SINGLE__SIMULTANEOUS": 2,
        "SINGLE__ORDERED_OR_ALTERNATING": 2,
        "MODULAR__SIMULTANEOUS": 0,
        "MODULAR__ORDERED_OR_ALTERNATING": 1,
    }
    assert out["module_timing_joint_support_by_universe"]["U6_POLLEN_THEFT_HARGREAVES_2009"] == {
        "SINGLE__SIMULTANEOUS": 3,
        "SINGLE__ORDERED_OR_ALTERNATING": 2,
        "MODULAR__SIMULTANEOUS": 0,
        "MODULAR__ORDERED_OR_ALTERNATING": 0,
    }
    assert out["spatial_secondary_dependence_block_counts"] == {
        "SAME_UNIT": 11,
        "DISTRIBUTED": 1,
    }
    assert out["spatial_secondary_estimable"] is False
    assert out["slope_design_full_rank"] is True
    assert out["full_design_full_rank"] is True
    assert out["blockers"] == []
    assert out["ready_for_primary_fit"] is True


def test_v4_generality_can_fail_without_blocking_primary_fit():
    rows = _ready_rows()
    row = next(row for row in rows if row["dependency_group"] == "u6_m1")
    row["conflict_timing_geometry"] = "SIMULTANEOUS"

    out = build_v4_estimability_report(rows)
    assert out["temporal_cross_universe_support"]["U6_POLLEN_THEFT_HARGREAVES_2009"] == {
        "SIMULTANEOUS": 4,
        "ORDERED_OR_ALTERNATING": 1,
    }
    assert out["temporal_cross_universe_marginal_replication_ready"] is False
    assert out["temporal_cross_universe_common_support_ready"] is False
    assert out["temporal_cross_universe_generality_ready"] is False
    assert out["ready_for_primary_fit"] is True


def test_v4_generality_outcome_support_can_fail_without_blocking_main_fit():
    rows = _ready_rows()
    row = next(row for row in rows if row["dependency_group"] == "u6_n2")
    row["architecture_mode"] = "SHARED_INTEGRATED"

    out = build_v4_estimability_report(rows)
    assert out["temporal_cross_universe_marginal_replication_ready"] is True
    assert out["temporal_cross_universe_common_support_ready"] is True
    assert out["temporal_cross_universe_outcome_support"]["U6_POLLEN_THEFT_HARGREAVES_2009"] == {
        "NONSTRUCTURAL_SEPARATION": 1,
        "OTHER_ARCHITECTURE": 4,
    }
    assert out["temporal_cross_universe_outcome_support_ready"] is False
    assert out["temporal_cross_universe_generality_ready"] is False
    assert out["ready_for_primary_fit"] is True


def test_v4_rejects_nonprimary_universe():
    rows = _ready_rows()
    rows[0]["universe_id"] = "U1_HAAS_LORTIE_2020"
    with pytest.raises(ValueError, match="accepts U2/U6 only"):
        build_v4_estimability_report(rows)


def test_v4_missing_primary_universe_is_a_fit_blocker():
    rows = [row for row in _ready_rows() if row["universe_id"] == "U2_BARRETT_2002"]
    out = build_v4_estimability_report(rows)
    assert any(
        blocker.startswith("primary_universe_support_below_2_dependence_blocks")
        for blocker in out["blockers"]
    )
    assert out["ready_for_primary_fit"] is False


def test_v4_detects_common_slope_rank_deficiency():
    rows = _ready_rows()
    # Force module status to equal VARIABLE_CONTEXT membership.
    for row in rows:
        row["module_substrate"] = (
            "SERIAL_WITHIN_FLOWER"
            if row["conflict_timing_geometry"] in {"MIXED", "CONTEXT_DEPENDENT"}
            else "SINGLE_OR_CONTINUOUS"
        )

    out = build_v4_estimability_report(rows)
    assert out["slope_design_full_rank"] is False
    assert "primary_common_slope_design_matrix_rank_deficient" in out["blockers"]
    assert out["ready_for_primary_fit"] is False



def test_v4_detects_predictor_universe_confounding_even_when_slope_rank_is_full():
    rows = _ready_rows()
    for row in rows:
        row["module_substrate"] = (
            "SERIAL_WITHIN_FLOWER"
            if row["universe_id"] == "U2_BARRETT_2002"
            else "SINGLE_OR_CONTINUOUS"
        )

    out = build_v4_estimability_report(rows)
    assert out["slope_design_full_rank"] is True
    assert out["full_design_full_rank"] is False
    assert "primary_universe_stratified_design_matrix_rank_deficient" in out["blockers"]
    assert out["ready_for_primary_fit"] is False

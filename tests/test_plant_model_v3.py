from balance_domain.plant_model_v3 import build_v3_estimability_report


def _row(group, mode, module, timing, spatial, *, block=None):
    return {
        "dependency_group": group,
        "dependence_block": block or group,
        "architecture_mode": mode,
        "module_substrate": module,
        "conflict_timing_geometry": timing,
        "conflict_spatial_geometry": spatial,
    }


def _ready_rows():
    return [
        _row("s1", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS", "SAME_UNIT"),
        _row("s2", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "MIXED", "SAME_UNIT"),
        _row("n1", "TEMPORAL_SEPARATION", "SERIAL_WITHIN_FLOWER", "SEQUENTIAL_WITHIN_UNIT", "SAME_UNIT"),
        _row("n2", "SPATIAL_SEPARATION", "REPEATED_FLOWERS", "SEASONALLY_ALTERNATING", "SAME_UNIT"),
        _row("d1", "WITHIN_FLOWER_DIVISION_OF_LABOUR", "SERIAL_WITHIN_FLOWER", "SIMULTANEOUS", "SAME_UNIT"),
        _row("d2", "AMONG_FLOWER_MODULE_DIVISION", "REPEATED_FLOWERS", "CONTEXT_DEPENDENT", "SAME_UNIT"),
        _row("m1", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT", "SAME_UNIT"),
        _row("m2", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEASONALLY_ALTERNATING", "BETWEEN_MODULES"),
    ]


def test_v3_primary_can_be_estimable_while_spatial_secondary_is_not():
    out = build_v3_estimability_report(_ready_rows())
    assert out["response_class_dependence_block_counts"] == {
        "SHARED": 2,
        "NONSTRUCTURAL_SEPARATION": 2,
        "STRUCTURAL_MODULE_DIVISION": 2,
        "MOSAIC": 2,
    }
    assert out["module_level_dependence_block_counts"] == {
        "SINGLE": 4,
        "MODULAR": 4,
    }
    assert out["temporal_level_dependence_block_counts"] == {
        "SIMULTANEOUS": 2,
        "ORDERED_OR_ALTERNATING": 4,
        "VARIABLE_CONTEXT": 2,
    }
    assert out["spatial_secondary_dependence_block_counts"] == {
        "SAME_UNIT": 7,
        "DISTRIBUTED": 1,
    }
    assert out["spatial_secondary_estimable"] is False
    assert out["design_full_rank"] is True
    assert out["blockers"] == []
    assert out["ready_for_primary_fit"] is True


def test_v3_fails_when_primary_predictor_level_has_only_one_dependence_block():
    rows = _ready_rows()
    for row in rows:
        if row["module_substrate"] != "SINGLE_OR_CONTINUOUS":
            row["module_substrate"] = "SINGLE_OR_CONTINUOUS"
    rows[4]["module_substrate"] = "SERIAL_WITHIN_FLOWER"

    out = build_v3_estimability_report(rows)
    assert out["module_level_dependence_block_counts"]["MODULAR"] == 1
    assert any(
        blocker.startswith("module_level_support_below_2_dependence_blocks")
        for blocker in out["blockers"]
    )
    assert out["ready_for_primary_fit"] is False


def test_v3_fails_when_variable_context_temporal_level_is_missing():
    rows = _ready_rows()
    for row in rows:
        if row["conflict_timing_geometry"] in {"MIXED", "CONTEXT_DEPENDENT"}:
            row["conflict_timing_geometry"] = "SIMULTANEOUS"

    out = build_v3_estimability_report(rows)
    assert out["temporal_level_dependence_block_counts"]["VARIABLE_CONTEXT"] == 0
    assert any(
        blocker.startswith("temporal_level_support_below_2_dependence_blocks")
        for blocker in out["blockers"]
    )
    assert out["ready_for_primary_fit"] is False


def test_v3_detects_primary_rank_deficiency_without_using_spatial_to_rescue_fit():
    rows = [
        _row("s1", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS", "SAME_UNIT"),
        _row("s2", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS", "BETWEEN_MODULES"),
        _row("n1", "TEMPORAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT", "SAME_UNIT"),
        _row("n2", "SPATIAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEASONALLY_ALTERNATING", "SAME_UNIT"),
        _row("d1", "WITHIN_FLOWER_DIVISION_OF_LABOUR", "SERIAL_WITHIN_FLOWER", "SIMULTANEOUS", "SAME_UNIT"),
        _row("d2", "AMONG_FLOWER_MODULE_DIVISION", "REPEATED_FLOWERS", "SIMULTANEOUS", "SAME_UNIT"),
        _row("m1", "POLYMORPHIC_OR_MOSAIC", "SERIAL_WITHIN_FLOWER", "CONTEXT_DEPENDENT", "SAME_UNIT"),
        _row("m2", "POLYMORPHIC_OR_MOSAIC", "REPEATED_FLOWERS", "MIXED", "SAME_UNIT"),
    ]
    out = build_v3_estimability_report(rows)
    # module status is perfectly determined by the temporal contrast in this construction.
    assert out["design_full_rank"] is False
    assert "primary_design_matrix_rank_deficient" in out["blockers"]
    assert out["failure_action"] == "DO_NOT_FIT_OR_DROP_TERMS_POST_HOC"

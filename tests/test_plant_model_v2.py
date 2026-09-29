from balance_domain.plant_model_v2 import build_v2_estimability_report


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
        _row("s2", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS", "SAME_UNIT"),
        _row("n1", "TEMPORAL_SEPARATION", "SERIAL_WITHIN_FLOWER", "SEQUENTIAL_WITHIN_UNIT", "SAME_UNIT"),
        _row("n2", "SPATIAL_SEPARATION", "REPEATED_FLOWERS", "SEASONALLY_ALTERNATING", "SAME_UNIT"),
        _row("d1", "WITHIN_FLOWER_DIVISION_OF_LABOUR", "SERIAL_WITHIN_FLOWER", "SIMULTANEOUS", "BETWEEN_MODULES"),
        _row("d2", "AMONG_FLOWER_MODULE_DIVISION", "REPEATED_FLOWERS", "SIMULTANEOUS", "AMONG_INDIVIDUALS"),
        _row("m1", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT", "AMONG_POPULATIONS"),
        _row("m2", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEASONALLY_ALTERNATING", "ENVIRONMENTAL_MOSAIC"),
    ]


def test_v2_estimability_ready_when_class_support_contrasts_and_rank_all_pass():
    out = build_v2_estimability_report(_ready_rows())
    assert out["response_class_dependence_block_counts"] == {
        "SHARED": 2,
        "NONSTRUCTURAL_SEPARATION": 2,
        "STRUCTURAL_MODULE_DIVISION": 2,
        "MOSAIC": 2,
    }
    assert all(out["planned_contrast_support"].values())
    assert out["design_full_rank"] is True
    assert out["blockers"] == []
    assert out["ready_for_primary_fit"] is True


def test_v2_estimability_fails_when_one_response_class_has_only_one_block():
    rows = _ready_rows()[:-1]
    out = build_v2_estimability_report(rows)
    assert out["response_class_dependence_block_counts"]["MOSAIC"] == 1
    assert any(
        blocker.startswith("response_class_support_below_2_dependence_blocks")
        for blocker in out["blockers"]
    )
    assert out["ready_for_primary_fit"] is False


def test_v2_estimability_detects_rank_deficiency_without_dropping_terms():
    rows = [
        _row("s1", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS", "SAME_UNIT"),
        _row("s2", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS", "SAME_UNIT"),
        _row("n1", "TEMPORAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT", "SAME_UNIT"),
        _row("n2", "SPATIAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT", "SAME_UNIT"),
        _row("d1", "WITHIN_FLOWER_DIVISION_OF_LABOUR", "SERIAL_WITHIN_FLOWER", "SIMULTANEOUS", "BETWEEN_MODULES"),
        _row("d2", "AMONG_FLOWER_MODULE_DIVISION", "REPEATED_FLOWERS", "SIMULTANEOUS", "BETWEEN_MODULES"),
        _row("m1", "POLYMORPHIC_OR_MOSAIC", "SERIAL_WITHIN_FLOWER", "SEQUENTIAL_WITHIN_UNIT", "AMONG_POPULATIONS"),
        _row("m2", "POLYMORPHIC_OR_MOSAIC", "REPEATED_FLOWERS", "SEQUENTIAL_WITHIN_UNIT", "ENVIRONMENTAL_MOSAIC"),
    ]
    out = build_v2_estimability_report(rows)
    assert all(out["planned_contrast_support"].values())
    assert out["design_full_rank"] is False
    assert "primary_design_matrix_rank_deficient" in out["blockers"]
    assert out["failure_action"] == "DO_NOT_FIT_OR_DROP_TERMS_POST_HOC"


def test_v2_variable_context_adds_registered_temporal_column():
    rows = _ready_rows() + [
        _row("v1", "SHARED_INTEGRATED", "SERIAL_WITHIN_FLOWER", "CONTEXT_DEPENDENT", "SAME_UNIT"),
        _row("v2", "NONSTRUCTURAL_SEPARATION" if False else "TEMPORAL_SEPARATION", "REPEATED_FLOWERS", "MIXED", "BETWEEN_MODULES"),
    ]
    out = build_v2_estimability_report(rows)
    assert "VARIABLE_CONTEXT" in out["temporal_levels_observed"]
    assert "temporal_VARIABLE_CONTEXT" in out["design_columns"]

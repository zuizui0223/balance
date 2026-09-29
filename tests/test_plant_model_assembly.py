import pytest

from balance_domain.plant_model_assembly import (
    build_model_assembly_readout,
    validate_model_assembly_rows,
)


def _row(row_id, universe, group, block, mode, module, timing, spatial, family):
    return {
        "analysis_row_id": row_id,
        "universe_id": universe,
        "dependency_group": group,
        "dependence_block": block,
        "system_taxon": group.replace("_", " "),
        "conflict_family": family,
        "conflict_receipt_status": "ADJUDICATED_POSITIVE",
        "architecture_mode": mode,
        "module_substrate": module,
        "conflict_timing_geometry": timing,
        "conflict_spatial_geometry": spatial,
        "architecture_adjudication_status": "ADJUDICATED",
        "predictor_receipt_status": "THREE_ADJUDICATED_OUTCOME_INDEPENDENT",
        "source_basis": "synthetic_test",
        "claim_ceiling": "comparative_only",
    }


def _ready_rows():
    return [
        _row("r1", "U2_BARRETT_2002", "s1", "b1", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS", "SAME_UNIT", "SEXUAL_INTERFERENCE"),
        _row("r2", "U6_POLLEN_THEFT_HARGREAVES_2009", "s2", "b2", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "MIXED", "SAME_UNIT", "POLLEN_REWARD_GAMETE"),
        _row("r3", "U2_BARRETT_2002", "n1", "b3", "TEMPORAL_SEPARATION", "SERIAL_WITHIN_FLOWER", "SEQUENTIAL_WITHIN_UNIT", "SAME_UNIT", "SEXUAL_INTERFERENCE"),
        _row("r4", "U6_POLLEN_THEFT_HARGREAVES_2009", "n2", "b4", "SPATIAL_SEPARATION", "REPEATED_FLOWERS", "SEASONALLY_ALTERNATING", "SAME_UNIT", "POLLEN_REWARD_GAMETE"),
        _row("r5", "U6_POLLEN_THEFT_HARGREAVES_2009", "d1", "b5", "WITHIN_FLOWER_DIVISION_OF_LABOUR", "SERIAL_WITHIN_FLOWER", "SIMULTANEOUS", "BETWEEN_MODULES", "POLLEN_REWARD_GAMETE"),
        _row("r6", "U6_POLLEN_THEFT_HARGREAVES_2009", "d2", "b6", "AMONG_FLOWER_MODULE_DIVISION", "REPEATED_FLOWERS", "CONTEXT_DEPENDENT", "AMONG_INDIVIDUALS", "POLLEN_REWARD_GAMETE"),
        _row("r7", "U2_BARRETT_2002", "m1", "b7", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT", "AMONG_POPULATIONS", "SEXUAL_INTERFERENCE"),
        _row("r8", "U6_POLLEN_THEFT_HARGREAVES_2009", "m2", "b8", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEASONALLY_ALTERNATING", "ENVIRONMENTAL_MOSAIC", "POLLEN_REWARD_GAMETE"),
    ]


def test_primary_model_assembly_accepts_only_fully_licensed_rows():
    rows = validate_model_assembly_rows(_ready_rows())
    assert len(rows) == 8


def test_primary_model_assembly_rejects_u1_and_u3_denominator_leaks():
    for universe in ("U1_HAAS_LORTIE_2020", "U3_HETERANTHERY_CASE_CONTROL"):
        rows = _ready_rows()
        rows[0]["universe_id"] = universe
        with pytest.raises(ValueError, match="not licensed for the primary confirmatory denominator"):
            validate_model_assembly_rows(rows)


def test_primary_model_assembly_rejects_predictor_without_independent_receipts():
    rows = _ready_rows()
    rows[0]["predictor_receipt_status"] = "SCREENED_ONLY"
    with pytest.raises(ValueError, match="lacks three adjudicated outcome-independent predictors"):
        validate_model_assembly_rows(rows)


def test_primary_model_assembly_runs_v4_estimability_after_licensing():
    out = build_model_assembly_readout(_ready_rows())
    assert out["n_rows"] == 8
    assert out["architecture_class_counts"] == {
        "MOSAIC": 2,
        "NONSTRUCTURAL_SEPARATION": 2,
        "SHARED": 2,
        "STRUCTURAL_MODULE_DIVISION": 2,
    }
    assert out["v4_estimability"]["ready_for_primary_fit"] is True
    assert out["ready_for_primary_fit"] is True
    assert out["u1_u3_u4_primary_denominator_allowed"] is False


def test_duplicate_dependence_block_can_reduce_class_support_without_row_deletion():
    rows = _ready_rows()
    rows[1]["dependence_block"] = rows[0]["dependence_block"]
    out = build_model_assembly_readout(rows)
    assert out["n_rows"] == 8
    assert out["n_dependence_blocks"] == 7
    assert out["v4_estimability"]["response_class_dependence_block_counts"]["SHARED"] == 1
    assert out["ready_for_primary_fit"] is False

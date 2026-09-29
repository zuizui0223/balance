import pytest

from balance_domain.plant_assembly_builder import (
    build_u2_licensed_rows,
    build_u6_licensed_rows,
    build_v4_licensed_assembly,
)


def _receipt(group, predictor, value):
    return {
        "receipt_id": f"{group}_{predictor}",
        "cluster_id": group,
        "predictor": predictor,
        "reported_value": value,
        "source_id": "source",
        "evidence_type": "PRE_OUTCOME_MEASUREMENT",
        "outcome_independence": "TRUE",
        "adjudication_status": "ADJUDICATED",
        "notes": "",
    }


def _receipts(group, module, timing, spatial):
    return [
        _receipt(group, "module_substrate", module),
        _receipt(group, "conflict_timing_geometry", timing),
        _receipt(group, "conflict_spatial_geometry", spatial),
    ]


def test_u2_builder_keeps_only_adjudicated_conflict_positive_rows():
    positive = {
        "cluster_id": "Campsis_radicans",
        "conflict_status": "POSITIVE",
        "architecture_mode": "SHARED_INTEGRATED",
        "module_substrate": "SINGLE_OR_CONTINUOUS",
        "conflict_timing_geometry": "SIMULTANEOUS",
        "conflict_spatial_geometry": "SAME_UNIT",
        "adjudication_status": "ADJUDICATED",
        "adjudication_basis": "SOURCE_REVIEW",
        "notes": "resolved",
    }
    negative = {
        **positive,
        "cluster_id": "Narcissus_assoanus",
        "conflict_status": "NO_DEMONSTRATED_CONFLICT",
    }
    sources = [
        {
            "dependency_group": "Campsis_radicans",
            "taxon_raw": "Campsis radicans",
            "primary_source_id": "Bertin & Sullivan 1988",
            "primary_source_doi": "10.1002/example",
        },
        {
            "dependency_group": "Narcissus_assoanus",
            "taxon_raw": "Narcissus assoanus",
            "primary_source_id": "Baker et al. 2000",
            "primary_source_doi": "",
        },
    ]
    rows = build_u2_licensed_rows(
        adjudication_rows=[positive, negative],
        predictor_receipts=_receipts(
            "Campsis_radicans",
            "SINGLE_OR_CONTINUOUS",
            "SIMULTANEOUS",
            "SAME_UNIT",
        ),
        source_packet_rows=sources,
    )
    assert len(rows) == 1
    row = rows[0]
    assert row["analysis_row_id"] == "U2::Campsis_radicans"
    assert row["universe_id"] == "U2_BARRETT_2002"
    assert row["dependence_block"] == "U2::Campsis_radicans"
    assert row["conflict_receipt_status"] == "ADJUDICATED_POSITIVE"
    assert row["predictor_receipt_status"] == "THREE_ADJUDICATED_OUTCOME_INDEPENDENT"


def test_u2_builder_rejects_predictor_receipt_mismatch():
    row = {
        "cluster_id": "Campsis_radicans",
        "conflict_status": "POSITIVE",
        "architecture_mode": "SHARED_INTEGRATED",
        "module_substrate": "SINGLE_OR_CONTINUOUS",
        "conflict_timing_geometry": "SIMULTANEOUS",
        "conflict_spatial_geometry": "SAME_UNIT",
        "adjudication_status": "ADJUDICATED",
        "adjudication_basis": "SOURCE_REVIEW",
        "notes": "resolved",
    }
    receipts = _receipts(
        "Campsis_radicans",
        "SERIAL_WITHIN_FLOWER",
        "SIMULTANEOUS",
        "SAME_UNIT",
    )
    with pytest.raises(ValueError, match="adjudication/receipt mismatch"):
        build_u2_licensed_rows(
            adjudication_rows=[row],
            predictor_receipts=receipts,
            source_packet_rows=[{
                "dependency_group": "Campsis_radicans",
                "taxon_raw": "Campsis radicans",
                "primary_source_id": "source",
                "primary_source_doi": "",
            }],
        )


def test_u6_builder_preserves_frozen_dependence_block():
    group = "Melastoma_affine"
    adjudication = [{
        "dependency_group": group,
        "architecture_mode": "WITHIN_FLOWER_DIVISION_OF_LABOUR",
        "module_substrate": "SINGLE_OR_CONTINUOUS",
        "conflict_timing_geometry": "SIMULTANEOUS",
        "conflict_spatial_geometry": "SAME_UNIT",
        "adjudication_status": "ADJUDICATED",
        "adjudication_basis": "SOURCE_REVIEW",
        "notes": "resolved",
    }]
    dependence = [{
        "u6_dependency_group": group,
        "overlap_universe": "U3",
        "overlap_record_id": "U3_PAIR_MELMA_001",
        "dependence_block": "U6_DEP_MELASTOMA_U3_01",
        "analysis_action": "SHARED_TAXON_CONCEPT_BLOCK",
        "notes": "conservative",
    }]
    source = [{
        "dependency_group": group,
        "plant_taxon": "Melastoma_affine",
        "admission_reference_ids": "U6_REF_046",
        "admission_primary_source_basis": "Gross & Mackay 1998",
        "supplemental_primary_source_ids": "DOI:10.17660/example",
        "source_recovery_status": "RESOLVED",
        "coder_instruction": "blinded",
    }]
    rows = build_u6_licensed_rows(
        adjudication_rows=adjudication,
        predictor_receipts=_receipts(
            group,
            "SINGLE_OR_CONTINUOUS",
            "SIMULTANEOUS",
            "SAME_UNIT",
        ),
        dependence_rows=dependence,
        frozen_source_packet_rows=source,
    )
    assert len(rows) == 1
    row = rows[0]
    assert row["universe_id"] == "U6_POLLEN_THEFT_HARGREAVES_2009"
    assert row["dependence_block"] == "U6_DEP_MELASTOMA_U3_01"
    assert row["conflict_family"] == "POLLEN_REWARD_GAMETE"


def test_combined_builder_returns_only_current_primary_universes():
    u2_adj = [{
        "cluster_id": "Campsis_radicans",
        "conflict_status": "POSITIVE",
        "architecture_mode": "SHARED_INTEGRATED",
        "module_substrate": "SINGLE_OR_CONTINUOUS",
        "conflict_timing_geometry": "SIMULTANEOUS",
        "conflict_spatial_geometry": "SAME_UNIT",
        "adjudication_status": "ADJUDICATED",
        "adjudication_basis": "SOURCE_REVIEW",
        "notes": "resolved",
    }]
    u6_adj = [{
        "dependency_group": "Hamelia_patens",
        "architecture_mode": "TEMPORAL_SEPARATION",
        "module_substrate": "SINGLE_OR_CONTINUOUS",
        "conflict_timing_geometry": "SEQUENTIAL_WITHIN_UNIT",
        "conflict_spatial_geometry": "SAME_UNIT",
        "adjudication_status": "ADJUDICATED",
        "adjudication_basis": "SOURCE_REVIEW",
        "notes": "resolved",
    }]
    rows = build_v4_licensed_assembly(
        u2_adjudication_rows=u2_adj,
        u2_predictor_receipts=_receipts(
            "Campsis_radicans",
            "SINGLE_OR_CONTINUOUS",
            "SIMULTANEOUS",
            "SAME_UNIT",
        ),
        u2_source_packet_rows=[{
            "dependency_group": "Campsis_radicans",
            "taxon_raw": "Campsis radicans",
            "primary_source_id": "source-u2",
            "primary_source_doi": "",
        }],
        u6_adjudication_rows=u6_adj,
        u6_predictor_receipts=_receipts(
            "Hamelia_patens",
            "SINGLE_OR_CONTINUOUS",
            "SEQUENTIAL_WITHIN_UNIT",
            "SAME_UNIT",
        ),
        u6_dependence_rows=[{
            "u6_dependency_group": "Hamelia_patens",
            "overlap_universe": "NONE",
            "overlap_record_id": "NONE",
            "dependence_block": "U6_DEP_HAMELIA_01",
            "analysis_action": "U6_ONLY",
            "notes": "none",
        }],
        u6_frozen_source_packet_rows=[{
            "dependency_group": "Hamelia_patens",
            "plant_taxon": "Hamelia_patens",
            "admission_reference_ids": "U6_REF_102",
            "admission_primary_source_basis": "Paciorek et al. 1995",
            "supplemental_primary_source_ids": "NONE_AFTER_REGISTERED_GENERIC_SEARCH",
            "source_recovery_status": "EVIDENCE_CEILING",
            "coder_instruction": "blinded",
        }],
    )
    assert {row["universe_id"] for row in rows} == {
        "U2_BARRETT_2002",
        "U6_POLLEN_THEFT_HARGREAVES_2009",
    }
    assert {row["analysis_row_id"] for row in rows} == {
        "U2::Campsis_radicans",
        "U6::Hamelia_patens",
    }


def test_combined_builder_refuses_empty_pending_state():
    with pytest.raises(ValueError, match="no licensed U2/U6 rows"):
        build_v4_licensed_assembly(
            u2_adjudication_rows=[],
            u2_predictor_receipts=[],
            u2_source_packet_rows=[],
            u6_adjudication_rows=[],
            u6_predictor_receipts=[],
            u6_dependence_rows=[],
            u6_frozen_source_packet_rows=[],
        )

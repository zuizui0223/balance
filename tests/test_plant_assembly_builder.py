from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

from balance_domain.plant_assembly_builder import (
    build_u2_licensed_rows,
    build_u6_licensed_rows,
    build_v4_licensed_assembly,
    build_v4_licensed_assembly_from_files,
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


def _u2_complete_fixture():
    rows = []
    sources = []
    receipts = []
    for i in range(20):
        group = f"U2_test_{i:02d}"
        positive = i == 0
        rows.append({
            "cluster_id": group,
            "conflict_status": "POSITIVE" if positive else "NO_DEMONSTRATED_CONFLICT",
            "architecture_mode": "SHARED_INTEGRATED" if positive else "UNRESOLVED",
            "module_substrate": "SINGLE_OR_CONTINUOUS" if positive else "UNRESOLVED",
            "conflict_timing_geometry": "SIMULTANEOUS" if positive else "UNRESOLVED",
            "conflict_spatial_geometry": "SAME_UNIT" if positive else "UNRESOLVED",
            "adjudication_status": "ADJUDICATED",
            "adjudication_basis": "SOURCE_REVIEW",
            "notes": "resolved",
        })
        sources.append({
            "dependency_group": group,
            "taxon_raw": group.replace("_", " "),
            "primary_source_id": f"source-{i}",
            "primary_source_doi": "",
        })
        if positive:
            receipts.extend(_receipts(
                group,
                "SINGLE_OR_CONTINUOUS",
                "SIMULTANEOUS",
                "SAME_UNIT",
            ))
    return rows, receipts, sources


def _u6_complete_fixture():
    adjudication = []
    receipts = []
    dependence = []
    sources = []
    for i in range(21):
        group = f"U6_test_{i:02d}"
        mode = "WITHIN_FLOWER_DIVISION_OF_LABOUR" if i == 0 else "SHARED_INTEGRATED"
        adjudication.append({
            "dependency_group": group,
            "architecture_mode": mode,
            "module_substrate": "SINGLE_OR_CONTINUOUS",
            "conflict_timing_geometry": "SIMULTANEOUS",
            "conflict_spatial_geometry": "SAME_UNIT",
            "adjudication_status": "ADJUDICATED",
            "adjudication_basis": "SOURCE_REVIEW",
            "notes": "resolved",
        })
        receipts.extend(_receipts(
            group,
            "SINGLE_OR_CONTINUOUS",
            "SIMULTANEOUS",
            "SAME_UNIT",
        ))
        dependence.append({
            "u6_dependency_group": group,
            "overlap_universe": "NONE",
            "overlap_record_id": "NONE",
            "dependence_block": f"U6_DEP_{i:02d}",
            "analysis_action": "U6_ONLY",
            "notes": "none",
        })
        sources.append({
            "dependency_group": group,
            "plant_taxon": group,
            "admission_reference_ids": f"U6_REF_TEST_{i:02d}",
            "admission_primary_source_basis": f"source-{i}",
            "supplemental_primary_source_ids": "NONE_AFTER_REGISTERED_GENERIC_SEARCH",
            "source_recovery_status": "EVIDENCE_CEILING",
            "coder_instruction": "blinded",
        })
    return adjudication, receipts, dependence, sources


def test_u2_builder_keeps_only_adjudicated_conflict_positive_rows():
    adjudication, receipts, sources = _u2_complete_fixture()
    rows = build_u2_licensed_rows(
        adjudication_rows=adjudication,
        predictor_receipts=receipts,
        source_packet_rows=sources,
    )
    assert len(rows) == 1
    row = rows[0]
    assert row["analysis_row_id"] == "U2::U2_test_00"
    assert row["universe_id"] == "U2_BARRETT_2002"
    assert row["dependence_block"] == "U2::U2_test_00"
    assert row["conflict_receipt_status"] == "ADJUDICATED_POSITIVE"
    assert row["predictor_receipt_status"] == "THREE_ADJUDICATED_OUTCOME_INDEPENDENT"


def test_u2_builder_rejects_predictor_receipt_mismatch():
    adjudication, receipts, sources = _u2_complete_fixture()
    module_receipt = next(
        row for row in receipts
        if row["cluster_id"] == "U2_test_00" and row["predictor"] == "module_substrate"
    )
    module_receipt["reported_value"] = "SERIAL_WITHIN_FLOWER"
    with pytest.raises(ValueError, match="adjudication/receipt mismatch"):
        build_u2_licensed_rows(
            adjudication_rows=adjudication,
            predictor_receipts=receipts,
            source_packet_rows=sources,
        )


def test_u2_builder_refuses_partial_adjudication():
    adjudication, receipts, sources = _u2_complete_fixture()
    with pytest.raises(ValueError, match="all 20 frozen reliability adjudication rows"):
        build_u2_licensed_rows(
            adjudication_rows=adjudication[:-1],
            predictor_receipts=receipts,
            source_packet_rows=sources[:-1],
        )


def test_u6_builder_preserves_frozen_dependence_block():
    adjudication, receipts, dependence, sources = _u6_complete_fixture()
    dependence[0] = {
        **dependence[0],
        "overlap_universe": "U3",
        "overlap_record_id": "U3_PAIR_TEST",
        "dependence_block": "U6_DEP_SHARED_TAXON_TEST",
        "analysis_action": "SHARED_TAXON_CONCEPT_BLOCK",
    }
    rows = build_u6_licensed_rows(
        adjudication_rows=adjudication,
        predictor_receipts=receipts,
        dependence_rows=dependence,
        frozen_source_packet_rows=sources,
    )
    assert len(rows) == 21
    row = next(row for row in rows if row["dependency_group"] == "U6_test_00")
    assert row["universe_id"] == "U6_POLLEN_THEFT_HARGREAVES_2009"
    assert row["dependence_block"] == "U6_DEP_SHARED_TAXON_TEST"
    assert row["conflict_family"] == "POLLEN_REWARD_GAMETE"


def test_u6_builder_refuses_pending_adjudication():
    adjudication, receipts, dependence, sources = _u6_complete_fixture()
    adjudication[0]["adjudication_status"] = "PENDING"
    with pytest.raises(ValueError, match="cannot omit pending adjudication rows"):
        build_u6_licensed_rows(
            adjudication_rows=adjudication,
            predictor_receipts=receipts,
            dependence_rows=dependence,
            frozen_source_packet_rows=sources,
        )


def test_combined_builder_returns_only_current_primary_universes():
    u2_adj, u2_receipts, u2_sources = _u2_complete_fixture()
    u6_adj, u6_receipts, u6_dependence, u6_sources = _u6_complete_fixture()
    rows = build_v4_licensed_assembly(
        u2_adjudication_rows=u2_adj,
        u2_predictor_receipts=u2_receipts,
        u2_source_packet_rows=u2_sources,
        u6_adjudication_rows=u6_adj,
        u6_predictor_receipts=u6_receipts,
        u6_dependence_rows=u6_dependence,
        u6_frozen_source_packet_rows=u6_sources,
    )
    assert {row["universe_id"] for row in rows} == {
        "U2_BARRETT_2002",
        "U6_POLLEN_THEFT_HARGREAVES_2009",
    }
    assert len(rows) == 22  # one U2 positive + all 21 U6 conflict-first groups


def test_combined_builder_refuses_empty_pending_state():
    with pytest.raises(ValueError, match="all 20 frozen reliability adjudication rows"):
        build_v4_licensed_assembly(
            u2_adjudication_rows=[],
            u2_predictor_receipts=[],
            u2_source_packet_rows=[],
            u6_adjudication_rows=[],
            u6_predictor_receipts=[],
            u6_dependence_rows=[],
            u6_frozen_source_packet_rows=[],
        )



def test_canonical_file_assembly_is_blocked_while_independent_coding_is_blank():
    with pytest.raises(ValueError, match="must be frozen"):
        build_v4_licensed_assembly_from_files(
            u2_sample_path=ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv",
            u2_coding_path=ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
            u2_adjudication_path=ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
            u2_predictor_receipts_path=ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
            u2_source_packet_path=ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv",
            u6_freeze_path=ROOT / "data" / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json",
            u6_coding_path=ROOT / "data" / "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv",
            u6_adjudication_path=ROOT / "data" / "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv",
            u6_predictor_receipts_path=ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
            u6_dependence_path=ROOT / "data" / "BALANCE_PLANT_U6_CROSS_UNIVERSE_DEPENDENCE_V1.csv",
            u6_source_recovery_path=ROOT / "data" / "BALANCE_PLANT_U6_PASS2_SOURCE_RECOVERY_FRAME_V1.csv",
            u6_frozen_source_packet_path=ROOT / "data" / "BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv",
        )

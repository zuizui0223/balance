from pathlib import Path
import csv
import pytest

from balance_domain.plant_u1_double_code import (
    build_u1_double_code_handoff,
    load_u1_adjudication,
    load_u1_blank_worksheet,
    load_u1_source_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"
RESOLUTION = ROOT / "data" / "BALANCE_PLANT_U1_SOURCE_RESOLUTION_V1.csv"
PACKET = ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SOURCE_PACKET_V1.csv"
WORKSHEET = ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv"
ADJUDICATION = ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv"


def _rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_u1_blinded_source_packet_matches_frozen_first20():
    sample = {r["universe_record_id"]: r for r in _rows(SAMPLE)}
    packet = load_u1_source_packet(PACKET)
    assert len(packet) == 20
    for row in packet:
        assert row["universe_record_id"] in sample
        assert row["dependency_group"] == sample[row["universe_record_id"]]["dependency_group"]
        assert row["taxon_raw"] == sample[row["universe_record_id"]]["taxon_raw"]
        assert row["primary_source_id"]
        assert row["coder_instruction"] == (
            "CODE_FROM_PRIMARY_SOURCE_ONLY_DO_NOT_USE_U1_SCREENING_OR_SOURCE_EVIDENCE_NOTES"
        )
        assert "conflict_status" not in row
        assert "architecture_mode" not in row
        assert "evidence_surface" not in row


def test_u1_blank_worksheet_has_two_empty_coder_rows_per_group():
    sample_groups = {r["dependency_group"] for r in _rows(SAMPLE)}
    worksheet = load_u1_blank_worksheet(WORKSHEET)
    assert len(worksheet) == 40
    assert {r["cluster_id"] for r in worksheet} == sample_groups
    for dep in sample_groups:
        rows = [r for r in worksheet if r["cluster_id"] == dep]
        assert {r["coder_id"] for r in rows} == {"CODER_A", "CODER_B"}
        for row in rows:
            assert not row["conflict_status"]
            assert not row["architecture_mode"]
            assert not row["module_substrate"]
            assert not row["conflict_timing_geometry"]
            assert not row["conflict_spatial_geometry"]


def test_u1_double_code_handoff_is_ready_and_blinded():
    out = build_u1_double_code_handoff(SAMPLE, RESOLUTION, PACKET, WORKSHEET)
    assert out["n_sampled_groups"] == 20
    assert out["n_source_packet_groups"] == 20
    assert out["n_blank_worksheet_rows"] == 40
    assert out["all_sampled_sources_resolved"] is True
    assert out["source_packet_excludes_screening_and_evidence_surface"] is True
    assert out["two_independent_coder_slots_per_group"] is True
    assert out["independent_double_coding_ready"] is True



def test_u1_adjudication_template_remains_pending_before_double_coding():
    sample = _rows(SAMPLE)
    rows = load_u1_adjudication(ADJUDICATION, sample)
    assert len(rows) == 20
    assert all(row["adjudication_status"] == "PENDING" for row in rows)
    assert all(row["adjudication_basis"] == "AWAITING_INDEPENDENT_DOUBLE_CODING" for row in rows)
    assert all(row["conflict_status"] == "UNRESOLVED" for row in rows)
    assert all(row["architecture_mode"] == "UNRESOLVED" for row in rows)
    assert all(row["module_substrate"] == "UNRESOLVED" for row in rows)
    assert all(row["conflict_timing_geometry"] == "UNRESOLVED" for row in rows)
    assert all(row["conflict_spatial_geometry"] == "UNRESOLVED" for row in rows)


def test_u1_adjudication_cannot_preempt_two_completed_coders(tmp_path):
    source = ADJUDICATION.read_text(encoding="utf-8")
    source = source.replace(
        ",UNRESOLVED,UNRESOLVED,UNRESOLVED,UNRESOLVED,UNRESOLVED,PENDING,AWAITING_INDEPENDENT_DOUBLE_CODING,",
        ",NO_DEMONSTRATED_CONFLICT,UNRESOLVED,UNRESOLVED,UNRESOLVED,UNRESOLVED,ADJUDICATED,SOURCE_REVIEW,preemptive",
        1,
    )
    path = tmp_path / "bad_u1_adjudication.csv"
    path.write_text(source, encoding="utf-8")
    with pytest.raises(ValueError, match="before two completed coder rows exist"):
        load_u1_adjudication(path, _rows(SAMPLE))

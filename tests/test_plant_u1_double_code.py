from pathlib import Path
import csv

from balance_domain.plant_u1_double_code import (
    build_u1_double_code_handoff,
    load_u1_blank_worksheet,
    load_u1_source_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"
RESOLUTION = ROOT / "data" / "BALANCE_PLANT_U1_SOURCE_RESOLUTION_V1.csv"
PACKET = ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SOURCE_PACKET_V1.csv"
WORKSHEET = ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv"


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

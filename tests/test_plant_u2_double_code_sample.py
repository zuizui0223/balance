from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "data" / "BALANCE_PLANT_U2_BARRETT_REVIEW_UNIVERSE_V1.csv"
SAMPLE = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"
SOURCE_PACKET = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv"
WORKSHEET = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv"


def _rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_u2_double_code_sample_is_first20_frozen_record_ids():
    rows = _rows(SAMPLE)
    assert len(rows) == 20
    assert [r["sample_order"] for r in rows] == [str(i) for i in range(1, 21)]
    assert [r["universe_record_id"] for r in rows] == [
        f"U2_{i:03d}" for i in range(1, 21)
    ]
    assert all(
        r["selection_rule"] == "FIRST_20_DEPENDENCY_GROUPS_BY_FROZEN_U2_RECORD_ID"
        for r in rows
    )
    assert all(r["source_resolution_status"] == "RESOLVED_PRIMARY" for r in rows)
    assert all(
        r["double_code_status"] == "READY_FOR_INDEPENDENT_DOUBLE_CODING"
        for r in rows
    )


def test_u2_double_code_sample_matches_universe_without_outcome_fields():
    universe = {r["universe_record_id"]: r for r in _rows(UNIVERSE)}
    sample = _rows(SAMPLE)
    for row in sample:
        source = universe[row["universe_record_id"]]
        assert row["dependency_group"] == source["dependency_group"]
        assert row["taxon_raw"] == source["taxon_raw"]
        assert row["source_resolution_status"] == source["source_resolution_status"]


def test_u2_source_packet_matches_sample_and_hides_screening_fields():
    sample = {r["universe_record_id"]: r for r in _rows(SAMPLE)}
    packet = _rows(SOURCE_PACKET)
    assert len(packet) == 20
    for row in packet:
        assert row["universe_record_id"] in sample
        assert row["dependency_group"] == sample[row["universe_record_id"]]["dependency_group"]
        assert row["taxon_raw"] == sample[row["universe_record_id"]]["taxon_raw"]
        assert row["primary_source_id"]
        assert row["coder_instruction"] == (
            "CODE_FROM_PRIMARY_SOURCE_ONLY_DO_NOT_USE_U2_EVIDENCE_FAMILY_OR_REVIEW_NOTES"
        )
        assert "conflict_status" not in row
        assert "architecture_mode" not in row
        assert "evidence_family" not in row


def test_u2_blank_worksheet_has_two_coders_per_sample_cluster():
    sample = _rows(SAMPLE)
    worksheet = _rows(WORKSHEET)
    assert len(worksheet) == 40
    sample_groups = {r["dependency_group"] for r in sample}
    assert {r["cluster_id"] for r in worksheet} == sample_groups

    for dep in sample_groups:
        rows = [r for r in worksheet if r["cluster_id"] == dep]
        assert {r["coder_id"] for r in rows} == {"CODER_A", "CODER_B"}
        assert all(not r["conflict_status"] for r in rows)
        assert all(not r["architecture_mode"] for r in rows)
        assert all(not r["module_substrate"] for r in rows)


def test_u2_records_21_22_are_not_in_reliability_sample():
    sample_ids = {r["universe_record_id"] for r in _rows(SAMPLE)}
    assert "U2_021" not in sample_ids
    assert "U2_022" not in sample_ids

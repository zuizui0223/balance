from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "data" / "BALANCE_PLANT_U2_BARRETT_REVIEW_UNIVERSE_V1.csv"
SAMPLE = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"
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
    assert all(r["double_code_status"] == "READY_FOR_INDEPENDENT_CODING" for r in rows)


def test_u2_double_code_sample_matches_universe_without_outcome_fields():
    universe = {r["universe_record_id"]: r for r in _rows(UNIVERSE)}
    sample = _rows(SAMPLE)
    for row in sample:
        source = universe[row["universe_record_id"]]
        assert row["dependency_group"] == source["dependency_group"]
        assert row["taxon_raw"] == source["taxon_raw"]
        assert row["primary_source_id"] == source["primary_source_id"]
        assert row["primary_source_doi"] == source["primary_source_doi"]


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


def test_u2_records_21_22_are_not_in_reliability_sample():
    sample_ids = {r["universe_record_id"] for r in _rows(SAMPLE)}
    assert "U2_021" not in sample_ids
    assert "U2_022" not in sample_ids

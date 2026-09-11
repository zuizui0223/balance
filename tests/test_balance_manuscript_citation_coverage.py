import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATTERN = ROOT / "data" / "BALANCE_PATTERN_LEDGER_V1.csv"
CITATIONS = ROOT / "data" / "BALANCE_MANUSCRIPT_CITATION_LEDGER_V1.csv"
MAP = ROOT / "data" / "BALANCE_PATTERN_CLUSTER_CITATION_MAP_V1.csv"


def _rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_every_pattern_cluster_has_exactly_one_primary_manuscript_citation_key():
    pattern_ids = {r["cluster_id"] for r in _rows(PATTERN)}
    mapped = _rows(MAP)
    mapped_ids = [r["cluster_id"] for r in mapped]
    assert set(mapped_ids) == pattern_ids
    assert len(mapped_ids) == len(set(mapped_ids)) == 17


def test_all_cluster_citation_keys_exist_in_citation_ledger():
    citation_keys = {r["citation_key"] for r in _rows(CITATIONS)}
    for row in _rows(MAP):
        assert row["citation_key"] in citation_keys


def test_citation_ledger_preserves_claim_ceiling_for_every_entry():
    rows = _rows(CITATIONS)
    assert rows
    assert all(r["claim_ceiling"].strip() for r in rows)
    assert all(r["sections_supported"].strip() for r in rows)

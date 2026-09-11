import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "data" / "BALANCE_THEORY_EMPIRICAL_LAYER_MAP_V1.csv"


def _rows():
    with MAP.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_direct_worldline_remains_unidentified():
    rows = {r["theory_object"]: r for r in _rows()}
    direct = rows["shared_vs_differentiated_worldline"]
    assert direct["status"] == "NOT_IDENTIFIED"
    assert direct["empirical_layer"] == "DIRECT_WORLDLINE_RESERVE"
    assert direct["current_evidence"].startswith("0_direct_matched_receipts")


def test_q1b_is_precondition_evidence_not_direct_occupancy():
    rows = {r["theory_object"]: r for r in _rows()}
    q1b = rows["conflict_active_shared_coordinate"]
    assert q1b["empirical_layer"] == "STRICT_Q1B_POSITIVE"
    assert "direct_BALANCE_occupancy" in q1b["prohibited_inference"]
    assert "recurs" in q1b["allowed_inference"]


def test_boundary_and_attribution_layers_remain_separate():
    rows = {r["theory_object"]: r for r in _rows()}
    assert rows["estimand_boundary"]["status"] == "SEPARATE_ESTIMANDS_ACTIVE"
    assert rows["mechanism_attribution_boundary"]["status"] == "MECHANISM_NOT_IDENTIFIED"


def test_pattern_ledger_supports_recurrence_not_prevalence():
    rows = {r["theory_object"]: r for r in _rows()}
    middle = rows["middle_regime_persistence"]
    assert "17_independent_clusters" in middle["current_evidence"]
    assert "9_middle_regime_signatures" in middle["current_evidence"]
    assert "natural_prevalence" in middle["prohibited_inference"]

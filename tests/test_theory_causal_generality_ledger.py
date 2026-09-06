import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "THEORY_CAUSAL_GENERALITY_LEDGER_V1.csv"


def _rows():
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_layers_are_separated():
    rows = _rows()
    assert [row["stage"] for row in rows] == [
        "T1", "T2", "T3", "T4", "C0", "C1", "C2", "C3", "C4", "G0", "G1", "G2", "G3"
    ]
    assert {row["layer"] for row in rows[:4]} == {"theory"}
    assert {row["layer"] for row in rows[4:9]} == {"causal"}
    assert {row["layer"] for row in rows[9:]} == {"generality"}


def test_observational_anchor_is_not_promoted_to_direct_balance():
    by_stage = {row["stage"]: row for row in _rows()}
    assert by_stage["G1"]["status"] == "POSITIVE_OBSERVATIONAL_ANCHOR_DIRECT_WORLDLINE_NOT_IDENTIFIED"
    assert "NOT_YET_EXECUTED" in by_stage["G0"]["status"]


def test_payoff_frequency_feedback_is_outside_balance_spine():
    text = (ROOT / "docs" / "THEORY_CAUSAL_GENERALITY_RECOVERY_V1.md").read_text(encoding="utf-8")
    assert "PAYOFF frequency dependence" in text
    assert "outside this spine" in text

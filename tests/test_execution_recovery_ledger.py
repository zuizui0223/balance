import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "empirical" / "BALANCE_EXECUTION_RECOVERY_LEDGER_V1.csv"


def _rows():
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_pedicularis_functional_and_structural_worldlines_are_not_conflated():
    rows = _rows()
    functional = next(r for r in rows if r["system"] == "Pedicularis_rex" and r["target"] == "shared_vs_water_state_worldline")
    structural = next(r for r in rows if r["system"] == "Pedicularis_rex" and r["target"] == "shared_vs_structural_y_worldline")
    assert functional["empirical_execution_status"] == "NOT_YET_EXECUTED"
    assert "functional_state_middle_world_only" in functional["claim_ceiling"]
    assert structural["evidence_status"] == "NOT_YET_RECOVERED"
    assert structural["empirical_execution_status"] == "NOT_YET_EXECUTED"
    assert "architecture_middle_world" in structural["claim_ceiling"]


def test_peucedanum_is_observational_anchor_not_direct_middle_world_receipt():
    rows = _rows()
    anchor = next(r for r in rows if r["system"] == "Peucedanum_multivittatum" and r["target"] == "multiple_definition_critical_region")
    worldline = next(r for r in rows if r["system"] == "Peucedanum_multivittatum" and r["target"] == "matched_WS_WD_same_fitness_scale")
    assert anchor["empirical_execution_status"] == "EXISTING_OBSERVATIONAL_SELECTION_DATA"
    assert "not_BALANCE_worldline" in anchor["claim_ceiling"]
    assert worldline["evidence_status"] == "NOT_IDENTIFIED"


def test_no_empirical_row_claims_historical_transition():
    for row in _rows():
        assert "historical_transition_identified" not in row["claim_ceiling"]

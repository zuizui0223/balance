import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "empirical" / "BALANCE_EXECUTION_RECOVERY_LEDGER_V2.csv"


def _rows():
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_pedicularis_is_not_silently_promoted_to_empirical_success() -> None:
    rows = [row for row in _rows() if row["system"] == "Pedicularis_rex"]
    assert rows
    forbidden = {"EMPIRICALLY_IDENTIFIED", "EXECUTED_POSITIVE", "CAUSAL_CHAIN_COMPLETE"}
    assert all(row["empirical_status"] not in forbidden for row in rows)
    assert any(row["empirical_status"] == "NOT_YET_EXECUTED" for row in rows)


def test_software_interface_and_power_are_distinguished_from_biology() -> None:
    rows = _rows()
    interface = next(row for row in rows if row["target"] == "context_and_fitness_scale_lock")
    assert interface["software_status"].startswith("MAIN_GREEN")
    assert interface["empirical_status"] == "SYNTHETIC_ONLY"
    powers = [row for row in rows if row["layer"] == "power"]
    assert {row["software_status"] for row in powers} == {"PR22_GREEN_NOT_MERGED", "PR182_GREEN_NOT_MERGED"}
    assert all(row["empirical_status"] == "PLANNING_ONLY" for row in powers)


def test_peucedanum_positive_anchor_keeps_direct_worldline_unidentified() -> None:
    rows = [row for row in _rows() if row["system"] == "Peucedanum_multivittatum"]
    longitudinal = next(row for row in rows if row["target"] == "longitudinal_selection_mosaic")
    direct = next(row for row in rows if row["target"] == "matched_WS_WD_common_scale")
    raw = next(row for row in rows if row["target"] == "individual_level_reproduction_and_LOO")
    assert longitudinal["evidence_status"] == "LONGITUDINAL_MOSAIC_CONCORDANT"
    assert direct["evidence_status"] == "NOT_IDENTIFIED"
    assert raw["empirical_status"] == "RAW_BINARY_NOT_ACQUIRED"

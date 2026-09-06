import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "comparative" / "BALANCE_GENERALITY_SIGNATURE_MATRIX_V1.csv"


def _rows():
    with MATRIX.open(encoding="utf-8", newline="") as handle:
        return {row["system"]: row for row in csv.DictReader(handle)}


def test_peucedanum_stays_observational_without_direct_worldline():
    rows = _rows()
    assert rows["Peucedanum_multivittatum"]["middle_world_status"] == "OBSERVATIONAL_TRANSITION_ANCHOR_ONLY"
    assert rows["Peucedanum_multivittatum"]["alternative_worldline_status"] == "NO_MATCHED_DIRECT_WS_WD"


def test_pedicularis_direct_balance_is_not_marked_executed():
    rows = _rows()
    assert rows["Pedicularis_rex"]["middle_world_status"] == "DIRECT_BALANCE_NOT_YET_EXECUTED"


def test_cross_domain_anchor_is_not_a_balance_receipt():
    rows = _rows()
    assert "NOT_BALANCE_RECEIPT" in rows["Cichlid_jaw_systems"]["middle_world_status"]


def test_hisa_trpf_is_boundary_candidate_not_direct_balance_receipt():
    rows = _rows()
    item = rows["Salmonella_HisA_TrpF"]
    assert item["program_role"] == "G3_CROSS_DOMAIN_ARCHITECTURE_BOUNDARY_CANDIDATE"
    assert item["middle_world_status"] == "DIRECT_BALANCE_WORLDLINE_NOT_IDENTIFIED"

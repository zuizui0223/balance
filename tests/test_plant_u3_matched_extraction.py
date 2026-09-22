from pathlib import Path

from balance_domain.plant_u3_matched_extraction import (
    build_u3_matched_extraction_readout,
    load_u3_matched_extraction,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
ADJ = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv"
EXTRACT = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv"


def test_matched_extraction_covers_only_two_pass_pairs():
    rows = load_u3_matched_extraction(EXTRACT, ADJ, PAIRS, CASES, U3)
    assert len(rows) == 4
    assert {r["pair_id"] for r in rows} == {
        "U3_PAIR_SOLRO_001",
        "U3_PAIR_MELMA_001",
    }


def test_current_matched_lane_is_not_conflict_estimand_ready():
    out = build_u3_matched_extraction_readout(EXTRACT, ADJ, PAIRS, CASES, U3)
    assert out["n_pairs"] == 2
    assert out["case_conflict_status_counts"] == {"POSITIVE": 2}
    assert out["control_conflict_status_counts"] == {"UNRESOLVED": 2}
    assert out["n_controls_with_resolved_conflict"] == 0
    assert out["matched_conflict_estimand_ready"] is False


def test_case_and_control_share_serial_module_substrate():
    rows = load_u3_matched_extraction(EXTRACT, ADJ, PAIRS, CASES, U3)
    assert {r["module_substrate"] for r in rows} == {"SERIAL_WITHIN_FLOWER"}

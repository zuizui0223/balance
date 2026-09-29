from pathlib import Path

from balance_domain.plant_u3_cases import build_u3_case_readout, load_u3_case_candidates


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"


def test_u3_case_candidates_map_only_to_registered_families():
    rows = load_u3_case_candidates(CASES, U3)
    assert len(rows) == 6
    assert {r["family"] for r in rows} == {
        "Fabaceae",
        "Melastomataceae",
        "Pontederiaceae",
        "Solanaceae",
    }


def test_u3_case_candidates_are_not_yet_case_control_ready():
    readout = build_u3_case_readout(CASES, U3)
    assert readout["n_source_resolved_cases"] == 6
    assert readout["n_families_represented"] == 4
    assert readout["n_direct_conflict_cases"] == 3
    assert readout["n_partial_conflict_cases"] == 3
    assert readout["n_matched_control_cases"] == 0
    assert readout["confirmatory_case_control_ready"] is False

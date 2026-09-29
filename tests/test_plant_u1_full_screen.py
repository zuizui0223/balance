from pathlib import Path

from balance_domain.plant_u1_full_screen import build_u1_full47_conflict_screen


ROOT = Path(__file__).resolve().parents[1]
FIRST20 = ROOT / "data" / "BALANCE_PLANT_U1_BLIND_CONFLICT_SCREEN_V1.csv"
PRODUCTION27 = ROOT / "data" / "BALANCE_PLANT_U1_PRODUCTION_BLIND_CONFLICT_SCREEN_V1.csv"


def test_u1_full47_source_screen_is_complete_without_architecture_inference():
    out = build_u1_full47_conflict_screen(FIRST20, PRODUCTION27)
    assert out["n_records"] == 47
    assert out["n_dependency_groups"] == 47
    assert out["conflict_status_counts"] == {
        "ALIGNED_NO_CONFLICT": 1,
        "NO_DEMONSTRATED_CONFLICT": 46,
    }
    assert out["screen_decision_counts"] == {
        "FAIL_CONFLICT_GATE": 47,
    }
    assert out["n_positive_conflict"] == 0
    assert out["n_unresolved_candidate"] == 0
    assert out["positive_conflict_ids"] == []
    assert out["unresolved_candidate_ids"] == []
    assert out["architecture_inferred"] is False
    assert out["independent_reliability_completed"] is False

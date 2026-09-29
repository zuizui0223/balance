from pathlib import Path

from balance_domain.plant_u1_screen import (
    build_u1_blind_screen_readout,
    load_u1_blind_screen,
)


ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "data" / "BALANCE_PLANT_U1_BLIND_CONFLICT_SCREEN_V1.csv"


def test_u1_blind_screen_validates():
    rows = load_u1_blind_screen(SCREEN)
    assert len(rows) == 20
    assert [int(r["sample_order"]) for r in rows] == list(range(1, 21))


def test_u1_blind_screen_does_not_promote_interaction_to_conflict():
    readout = build_u1_blind_screen_readout(SCREEN)
    assert readout["n_positive_conflict"] == 0
    assert readout["n_aligned_no_conflict"] == 1
    assert readout["n_no_demonstrated_conflict"] == 19
    assert readout["n_unresolved_candidate"] == 0
    assert readout["screen_decision_counts"] == {
        "FAIL_CONFLICT_GATE": 20,
    }


def test_castilleja_is_retained_as_aligned_specificity_control():
    rows = load_u1_blind_screen(SCREEN)
    row = next(r for r in rows if r["taxon_raw"] == "Castilleja indivisa")
    assert row["conflict_status"] == "ALIGNED_NO_CONFLICT"
    assert row["same_coordinate_evidence"] == "YES"
    assert row["screen_decision"] == "FAIL_CONFLICT_GATE"


def test_brassica_nigra_primary_result_closes_no_tradeoff():
    rows = load_u1_blind_screen(SCREEN)
    row = next(r for r in rows if r["taxon_raw"] == "Brassica nigra")
    assert row["conflict_status"] == "NO_DEMONSTRATED_CONFLICT"
    assert row["opposing_demand_evidence"] == "NO"
    assert row["screen_decision"] == "FAIL_CONFLICT_GATE"
    assert row["reason_code"] == "PRIMARY_STUDY_REPORTS_NO_HERBIVORY_POLLINATION_TRADEOFF"


def test_architecture_is_not_inferred_from_conflict_screen():
    rows = load_u1_blind_screen(SCREEN)
    assert all(r["architecture_status"] == "NOT_IDENTIFIED" for r in rows)

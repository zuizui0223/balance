from pathlib import Path

from balance_domain.plant_u1_production_screen import (
    build_u1_production_blind_screen_readout,
    load_u1_production_blind_screen,
)


ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "data" / "BALANCE_PLANT_U1_PRODUCTION_BLIND_CONFLICT_SCREEN_V1.csv"


def test_u1_production_screen_covers_exactly_u1_021_to_u1_047():
    rows = load_u1_production_blind_screen(SCREEN)
    assert len(rows) == 27
    assert [row["universe_record_id"] for row in rows] == [
        f"U1_{i:03d}" for i in range(21, 48)
    ]
    assert [int(row["sample_order"]) for row in rows] == list(range(21, 48))


def test_u1_production_screen_has_no_positive_conflict_promotions():
    out = build_u1_production_blind_screen_readout(SCREEN)
    assert out["conflict_status_counts"] == {
        "NO_DEMONSTRATED_CONFLICT": 27,
    }
    assert out["screen_decision_counts"] == {
        "FAIL_CONFLICT_GATE": 27,
    }
    assert out["n_positive_conflict"] == 0
    assert out["n_no_demonstrated_conflict"] == 27
    assert out["n_unresolved_candidate"] == 0
    assert out["held_for_full_text_ids"] == []
    assert out["architecture_inferred"] is False


def test_u1_production_conflict_screen_never_infers_architecture():
    rows = load_u1_production_blind_screen(SCREEN)
    assert all(row["architecture_status"] == "NOT_IDENTIFIED" for row in rows)


def test_myrmecophila_primary_result_closes_no_conflict():
    rows = load_u1_production_blind_screen(SCREEN)
    row = next(row for row in rows if row["universe_record_id"] == "U1_032")
    assert row["taxon_raw"] == "Myrmecophila tibicinis"
    assert row["conflict_status"] == "NO_DEMONSTRATED_CONFLICT"
    assert row["same_coordinate_evidence"] == "PARTIAL"
    assert row["opposing_demand_evidence"] == "NO"
    assert row["screen_decision"] == "FAIL_CONFLICT_GATE"
    assert row["reason_code"] == "FLORAL_MORPHOLOGY_MANIPULATION_NULL_FOR_POLLINATION_SUCCESS"


def test_pastinaca_is_damage_mediated_pollination_cost_not_opposing_optimum():
    rows = load_u1_production_blind_screen(SCREEN)
    row = next(row for row in rows if row["universe_record_id"] == "U1_034")
    assert row["conflict_status"] == "NO_DEMONSTRATED_CONFLICT"
    assert row["screen_decision"] == "FAIL_CONFLICT_GATE"
    assert "10.2307/2426744" in row["source_basis"]

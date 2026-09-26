from pathlib import Path

from balance_domain.plant_u3_bixaceae_controls import (
    build_u3_bixaceae_control_search_readout,
    load_u3_bixaceae_control_search,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U3_BIXACEAE_CONTROL_SEARCH_V1.csv"


def test_bixaceae_search_keeps_nearest_tetraporum_open():
    rows = load_u3_bixaceae_control_search(LEDGER)
    tet = next(r for r in rows if r["candidate_control"] == "Cochlospermum tetraporum")
    assert tet["candidate_role"] == "INCUMBENT"
    assert tet["heteranthery_absence_status"] == "PASS"
    assert tet["phylogenetic_proximity_status"] == "PASS"
    assert tet["animal_pollination_status"] == "OPEN"
    assert tet["selection_status"] == "OPEN"


def test_farther_biologically_eligible_controls_cannot_jump_nearest_open_candidate():
    out = build_u3_bixaceae_control_search_readout(LEDGER)
    assert out["nearest_candidate"] == "Cochlospermum tetraporum"
    assert out["fallbacks_with_animal_pollination_pass"] == [
        "Cochlospermum orinocense",
        "Cochlospermum vitifolium",
    ]
    assert out["control_selected"] is False
    assert out["search_closed"] is False
    assert out["blocker"] == "CLOSEST_C_TETRAPORUM_ANIMAL_POLLINATION_ELIGIBILITY_OPEN"


def test_bixaceae_search_does_not_extract_conflict_or_routing_outcomes():
    rows = load_u3_bixaceae_control_search(LEDGER)
    forbidden = ("conflict", "routing", "architecture_mode")
    for row in rows:
        payload = " ".join([row["source_id"], row["blocker"], row["notes"]]).casefold()
        assert "conflict positive" not in payload
        assert "routing_mode" not in payload
        assert all(key not in row for key in forbidden)

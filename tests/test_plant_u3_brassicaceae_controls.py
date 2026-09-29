from pathlib import Path

from balance_domain.plant_u3_brassicaceae_controls import (
    build_u3_brassicaceae_control_search_readout,
    load_u3_brassicaceae_control_search,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U3_BRASSICACEAE_CONTROL_SEARCH_V1.csv"


def test_close_brassiceae_candidates_fail_negative_architecture_gate():
    rows = load_u3_brassicaceae_control_search(LEDGER)
    close = [r for r in rows if r["candidate_role"] == "NEAR_RELATIVE"]
    assert {r["candidate_control"] for r in close} == {
        "Brassica oleracea",
        "Brassica napus",
        "Diplotaxis erucoides",
        "Raphanus raphanistrum",
    }
    assert all(r["heteranthery_absence_status"] == "FAIL" for r in close)
    assert all(r["selection_status"] == "REJECTED" for r in close)


def test_family_level_equal_stamen_candidates_pass_biology_but_not_ranking():
    rows = load_u3_brassicaceae_control_search(LEDGER)
    family = [r for r in rows if r["candidate_role"] == "FAMILY_LEVEL_CANDIDATE"]
    assert {r["candidate_control"] for r in family} == {
        "Stanleya elata",
        "Stanleya pinnata",
    }
    assert all(r["heteranthery_absence_status"] == "PASS" for r in family)
    assert all(r["animal_pollination_status"] == "PASS" for r in family)
    assert all(r["phylogenetic_proximity_status"] == "OPEN" for r in family)
    assert all(r["selection_status"] == "OPEN" for r in family)


def test_brassicaceae_search_fails_closed_on_family_level_phylogenetic_ranking():
    out = build_u3_brassicaceae_control_search_readout(LEDGER)
    assert out["n_candidates"] == 6
    assert out["n_close_candidates_rejected_by_absence_gate"] == 4
    assert out["biologically_eligible_family_level_candidates"] == [
        "Stanleya elata",
        "Stanleya pinnata",
    ]
    assert out["control_selected"] is False
    assert out["search_closed"] is False
    assert out["blocker"] == (
        "FAMILY_LEVEL_EQUAL_STAMEN_CLOSEST_PHYLOGENETIC_RANKING_OPEN"
    )

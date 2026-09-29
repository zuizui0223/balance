from pathlib import Path
from balance_domain.plant_u3_lythraceae_controls import (
    build_u3_lythraceae_control_search_readout,
    load_u3_lythraceae_control_search,
)

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"data"/"BALANCE_PLANT_U3_LYTHRACEAE_CONTROL_SEARCH_V1.csv"

def test_close_lagerstroemia_candidates_fail_negative_architecture_gate():
    rows=load_u3_lythraceae_control_search(LEDGER)
    close=[r for r in rows if r["candidate_role"]=="NEAR_RELATIVE"]
    assert len(close)==4
    assert all(r["heteranthery_absence_status"]=="FAIL" for r in close)
    assert all(r["selection_status"]=="REJECTED" for r in close)

def test_monomorphic_family_candidates_are_retained_without_convenience_selection():
    rows=load_u3_lythraceae_control_search(LEDGER)
    candidates=[r for r in rows if r["candidate_role"]=="FAMILY_LEVEL_CANDIDATE"]
    assert {r["candidate_control"] for r in candidates}=={
        "Lagerstroemia parviflora","Lagerstroemia speciosa","Lagerstroemia macrocarpa"
    }
    assert all(r["heteranthery_absence_status"]=="PASS" for r in candidates)
    spec=next(r for r in candidates if r["candidate_control"]=="Lagerstroemia speciosa")
    assert spec["animal_pollination_status"]=="PASS"
    par=next(r for r in candidates if r["candidate_control"]=="Lagerstroemia parviflora")
    assert par["phylogenetic_proximity_status"]=="OPEN"
    assert all(r["selection_status"]=="OPEN" for r in candidates)

def test_lythraceae_search_fails_closed_on_unsampled_parviflora():
    out=build_u3_lythraceae_control_search_readout(LEDGER)
    assert out["n_candidates"]==7
    assert out["n_close_candidates_rejected_by_absence_gate"]==4
    assert out["family_level_candidates_with_animal_pollination_pass"]==["Lagerstroemia speciosa"]
    assert out["control_selected"] is False
    assert out["search_closed"] is False
    assert "L_PARVIFLORA" in out["blocker"]

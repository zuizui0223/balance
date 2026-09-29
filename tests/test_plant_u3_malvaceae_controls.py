from pathlib import Path
from balance_domain.plant_u3_malvaceae_controls import (
    build_u3_malvaceae_control_search_readout,
    load_u3_malvaceae_control_search,
)

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"data"/"BALANCE_PLANT_U3_MALVACEAE_CONTROL_SEARCH_V1.csv"

def test_four_source_resolved_congeners_fail_negative_architecture_gate():
    rows=load_u3_malvaceae_control_search(LEDGER)
    resolved=[r for r in rows if r["candidate_role"]=="RESOLVED_CONGENER"]
    assert {r["candidate_control"] for r in resolved}=={
        "Mollia speciosa","Mollia gracilis","Mollia tomentosa","Mollia longifolia"
    }
    assert all(r["heteranthery_absence_status"]=="FAIL" for r in resolved)
    assert all(r["selection_status"]=="REJECTED" for r in resolved)

def test_divergent_trimera_and_unscreened_remainder_prevent_convenience_widening():
    rows=load_u3_malvaceae_control_search(LEDGER)
    trimera=next(r for r in rows if r["candidate_control"]=="Mollia trimera")
    remainder=next(r for r in rows if r["candidate_role"]=="GENUS_REMAINDER")
    assert trimera["heteranthery_absence_status"]=="OPEN"
    assert trimera["phylogenetic_proximity_status"]=="OPEN"
    assert trimera["selection_status"]=="OPEN"
    assert remainder["selection_status"]=="OPEN"

def test_malvaceae_search_hits_registered_public_evidence_ceiling():
    out=build_u3_malvaceae_control_search_readout(LEDGER)
    assert out["n_receipts"]==6
    assert out["n_resolved_congener_morphology_failures"]==4
    assert out["open_congeneric_surfaces"]==[
        "Mollia spp. unresolved accepted remainder","Mollia trimera"
    ]
    assert out["control_selected"] is False
    assert out["search_closed"] is False
    assert "INTRAGENERIC_PHYLOGENY_OPEN" in out["blocker"]

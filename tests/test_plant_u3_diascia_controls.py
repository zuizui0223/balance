from pathlib import Path
from balance_domain.plant_u3_diascia_controls import (
    build_diascia_control_audit,load_diascia_control_audit
)

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"data"/"BALANCE_PLANT_U3_DIASCIA_CONTROL_AUDIT_V1.csv"

def test_diascia_audit_keeps_three_eligible_controls_open():
    rows=load_diascia_control_audit(AUDIT)
    out=build_diascia_control_audit(AUDIT)
    assert len(rows)==6
    assert out["decision_counts"]=={"OPEN":3,"REJECTED":3}
    assert out["open_candidates"]==[
        "Diascia barberae","Diascia cordata","Diascia integerrima"
    ]
    assert out["n_biologically_eligible_but_closest_open"]==3
    assert out["control_selected"] is False
    assert out["evidence_ceiling_blocked"] is True

def test_close_heterantherous_candidates_are_rejected_not_skipped():
    rows={r["candidate_control"]:r for r in load_diascia_control_audit(AUDIT)}
    for taxon in ("Diascia megathura","Diascia purpurea"):
        assert rows[taxon]["proximity_status"]=="PASS"
        assert rows[taxon]["heteranthery_absence_status"]=="FAIL"
        assert rows[taxon]["decision"]=="REJECTED"

def test_equal_or_single_set_candidates_are_not_selected_without_distance_closure():
    rows={r["candidate_control"]:r for r in load_diascia_control_audit(AUDIT)}
    for taxon in ("Diascia barberae","Diascia cordata","Diascia integerrima"):
        assert rows[taxon]["heteranthery_absence_status"]=="PASS"
        assert rows[taxon]["animal_pollination_status"]=="PASS"
        assert rows[taxon]["closest_eligible_status"]=="OPEN"
        assert rows[taxon]["decision"]=="OPEN"

from pathlib import Path
from balance_domain.plant_u3_routing_expansion import build_u3_routing_expansion_readout, load_u3_routing_expansion_queue

ROOT=Path(__file__).resolve().parents[1]
U3=ROOT/"data"/"BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
QUEUE=ROOT/"data"/"BALANCE_PLANT_U3_ROUTING_EXPANSION_QUEUE_V1.csv"

def test_routing_queue_retains_three_blocked_cases_and_activates_malvaceae():
    rows=load_u3_routing_expansion_queue(QUEUE,U3)
    assert [r["family"] for r in rows]==["Bixaceae","Brassicaceae","Lythraceae","Malvaceae"]
    assert [r["control_search_status"] for r in rows]==[
        "EVIDENCE_CEILING_BLOCKED","EVIDENCE_CEILING_BLOCKED",
        "EVIDENCE_CEILING_BLOCKED","IN_PROGRESS"
    ]

def test_next_active_case_is_mollia_without_dropping_blocked_families():
    out=build_u3_routing_expansion_readout(QUEUE,U3)
    assert out["next_active_case"]=="Mollia lepidota"
    assert out["n_evidence_ceiling_blocked"]==3
    assert out["n_control_search_not_started"]==0
    assert out["n_new_dependence_blocks"]==4

def test_queue_progression_remains_preoutcome():
    out=build_u3_routing_expansion_readout(QUEUE,U3)
    assert "advance_only_after_prior_case" in out["progression_rule"]
    assert "outcome_convenience" in out["progression_rule"]

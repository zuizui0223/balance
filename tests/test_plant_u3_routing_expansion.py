from pathlib import Path
import csv
import pytest
from balance_domain.plant_u3_routing_expansion import (
    FIELDS,
    build_u3_routing_expansion_readout,
    load_u3_routing_expansion_queue,
)

ROOT=Path(__file__).resolve().parents[1]
U3=ROOT/"data"/"BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
QUEUE=ROOT/"data"/"BALANCE_PLANT_U3_ROUTING_EXPANSION_QUEUE_V1.csv"

def test_routing_queue_is_exhausted_with_four_retained_blocked_cases():
    rows=load_u3_routing_expansion_queue(QUEUE,U3)
    assert [r["family"] for r in rows]==["Bixaceae","Brassicaceae","Lythraceae","Malvaceae"]
    assert all(r["control_search_status"]=="EVIDENCE_CEILING_BLOCKED" for r in rows)

def test_readout_reports_exhaustion_without_dropping_any_dependence_block():
    out=build_u3_routing_expansion_readout(QUEUE,U3)
    assert out["next_active_case"] is None
    assert out["prospective_queue_exhausted"] is True
    assert out["n_evidence_ceiling_blocked"]==4
    assert out["n_terminal_or_blocked"]==4
    assert out["n_control_search_not_started"]==0
    assert out["n_new_dependence_blocks"]==4

def test_no_active_case_cannot_hide_unstarted_row(tmp_path):
    with QUEUE.open(encoding="utf-8",newline="") as handle:
        rows=list(csv.DictReader(handle))
    rows[-1]["control_search_status"]="NOT_STARTED"
    path=tmp_path/"queue.csv"
    with path.open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError,match="cannot retain NOT_STARTED"):
        load_u3_routing_expansion_queue(path,U3)

def test_queue_progression_remains_preoutcome():
    out=build_u3_routing_expansion_readout(QUEUE,U3)
    assert "retain_blocked_cases_as_missing_dependence_blocks" in out["progression_rule"]
    assert "outcome_convenience" in out["progression_rule"]

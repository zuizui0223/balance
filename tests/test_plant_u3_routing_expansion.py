from pathlib import Path

from balance_domain.plant_u3_routing_expansion import (
    build_u3_routing_expansion_readout,
    load_u3_routing_expansion_queue,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
QUEUE = ROOT / "data" / "BALANCE_PLANT_U3_ROUTING_EXPANSION_QUEUE_V1.csv"


def test_routing_queue_retains_two_blocked_cases_and_activates_lythraceae():
    rows = load_u3_routing_expansion_queue(QUEUE, U3)
    assert [r["family"] for r in rows] == [
        "Bixaceae",
        "Brassicaceae",
        "Lythraceae",
        "Malvaceae",
    ]
    assert rows[0]["control_search_status"] == "EVIDENCE_CEILING_BLOCKED"
    assert rows[1]["control_search_status"] == "EVIDENCE_CEILING_BLOCKED"
    assert rows[2]["control_search_status"] == "IN_PROGRESS"
    assert rows[3]["control_search_status"] == "NOT_STARTED"


def test_next_active_case_is_lagerstroemia_without_dropping_blocked_families():
    out = build_u3_routing_expansion_readout(QUEUE, U3)
    assert out["n_queued_families"] == 4
    assert out["n_new_dependence_blocks"] == 4
    assert out["first_case_family"] == "Bixaceae"
    assert out["next_active_case"] == "Lagerstroemia indica"
    assert out["n_evidence_ceiling_blocked"] == 2
    assert out["n_control_search_not_started"] == 1
    assert out["queue_frozen_before_control_outcomes"] is True


def test_queue_progression_requires_frozen_preoutcome_receipts():
    out = build_u3_routing_expansion_readout(QUEUE, U3)
    assert "advance_only_after_prior_case" in out["progression_rule"]
    assert "retain_blocked_cases_as_missing_dependence_blocks" in out["progression_rule"]
    assert "outcome_convenience" in out["progression_rule"]

from pathlib import Path

from balance_domain.plant_u3_routing_expansion import (
    build_u3_routing_expansion_readout,
    load_u3_routing_expansion_queue,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
QUEUE = ROOT / "data" / "BALANCE_PLANT_U3_ROUTING_EXPANSION_QUEUE_V1.csv"


def test_routing_expansion_queue_preserves_blocked_bixaceae_and_activates_brassicaceae():
    rows = load_u3_routing_expansion_queue(QUEUE, U3)
    assert [r["family"] for r in rows] == [
        "Bixaceae",
        "Brassicaceae",
        "Lythraceae",
        "Malvaceae",
    ]
    assert rows[0]["control_search_status"] == "EVIDENCE_CEILING_BLOCKED"
    assert rows[1]["control_search_status"] == "IN_PROGRESS"
    assert all(r["control_search_status"] == "NOT_STARTED" for r in rows[2:])
    assert all(
        r["predictor_blinding_status"]
        == "FROZEN_BEFORE_CONTROL_CONFLICT_OR_ROUTING_EXTRACTION"
        for r in rows
    )


def test_next_active_case_is_brassica_rapa_without_dropping_bixaceae():
    out = build_u3_routing_expansion_readout(QUEUE, U3)
    assert out["n_queued_families"] == 4
    assert out["n_new_dependence_blocks"] == 4
    assert out["first_case_family"] == "Bixaceae"
    assert out["first_case_taxon"] == "Amoreuxia wrightii"
    assert out["next_active_case"] == "Brassica rapa"
    assert out["n_evidence_ceiling_blocked"] == 1
    assert out["n_control_search_not_started"] == 2
    assert out["queue_frozen_before_control_outcomes"] is True


def test_queue_progression_requires_frozen_preoutcome_receipt():
    out = build_u3_routing_expansion_readout(QUEUE, U3)
    assert "advance_only_after_prior_case" in out["progression_rule"]
    assert "retain_blocked_cases_as_missing_dependence_blocks" in out["progression_rule"]
    assert "outcome_convenience" in out["progression_rule"]

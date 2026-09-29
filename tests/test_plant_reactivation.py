import json
from pathlib import Path

from balance_domain.plant_reactivation import (
    evaluate_v4_reactivation_conditions,
    evaluate_v4_reactivation_gate,
    load_v4_reactivation_gate,
)


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "data" / "BALANCE_PLANT_V4_REACTIVATION_GATE_V1.json"


def test_current_v4_reactivation_gate_stays_dormant():
    data = load_v4_reactivation_gate(GATE)
    out = evaluate_v4_reactivation_gate(GATE)

    assert data["publication_status"] == "DORMANT_PAPER_BRANCH"
    assert data["active_publication_queue"] is False
    assert data["standalone_reactivation_eligible"] is False
    assert out["standalone_reactivation_eligible"] is False
    assert out["activation_action"] == "KEEP_DORMANT"
    assert "u2_independent_coding_and_adjudication_complete" in out["blockers"]
    assert "u6_independent_coding_and_adjudication_complete" in out["blockers"]
    assert "v4_primary_fit_complete" in out["blockers"]
    assert "directionally_concordant_across_u2_u6" in out["blockers"]


def test_v4_reactivation_requires_more_than_nonzero_pooled_effect():
    data = json.loads(GATE.read_text(encoding="utf-8"))
    conditions = dict(data["required_conditions"])
    conditions.update({
        "u2_independent_coding_and_adjudication_complete": True,
        "u6_independent_coding_and_adjudication_complete": True,
        "u2_u6_predictor_independence_adjudication_complete": True,
        "v4_primary_estimability_pass": True,
        "v4_primary_fit_complete": True,
        "temporal_generality_sensitivity_fit_complete": True,
        "u2_ordered_vs_simultaneous_direction_resolved": True,
        "u6_ordered_vs_simultaneous_direction_resolved": True,
        "directionally_concordant_across_u2_u6": False,
        "contradictory_universe_interaction_exceeds_practical_margin": False,
    })
    out = evaluate_v4_reactivation_conditions(conditions)
    assert out["standalone_reactivation_eligible"] is False
    assert out["blockers"] == ["directionally_concordant_across_u2_u6"]


def test_v4_reactivation_gate_can_become_evidence_eligible_without_auto_activation():
    data = json.loads(GATE.read_text(encoding="utf-8"))
    conditions = {
        key: True
        for key in (
            "u2_independent_coding_and_adjudication_complete",
            "u6_independent_coding_and_adjudication_complete",
            "u2_u6_predictor_independence_adjudication_complete",
            "v4_primary_estimability_pass",
            "v4_primary_fit_complete",
            "temporal_generality_sensitivity_fit_complete",
            "u2_ordered_vs_simultaneous_direction_resolved",
            "u6_ordered_vs_simultaneous_direction_resolved",
        )
    }
    conditions["directionally_concordant_across_u2_u6"] = True
    conditions["contradictory_universe_interaction_exceeds_practical_margin"] = False

    out = evaluate_v4_reactivation_conditions(conditions)
    assert out["standalone_reactivation_eligible"] is True
    assert out["publication_status_if_current"] == "DORMANT_PAPER_BRANCH"
    assert out["activation_action"] == "HUMAN_REVIEW_REQUIRED_BEFORE_PUBLICATION_STATUS_CHANGE"

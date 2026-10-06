import json
from pathlib import Path

from balance_domain.plant_reactivation import (
    _validated_generality_decision,
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
    assert data["posterior_decision_rules"] == (
        "data/BALANCE_PLANT_V4_POSTERIOR_DECISION_RULES_V1.json"
    )
    assert data["posterior_decision_evaluator"] == (
        "balance_domain.plant_v4_decision.temporal_generality_decision"
    )
    assert data["fit_execution_contract"] == (
        "data/BALANCE_PLANT_V4_FIT_EXECUTION_CONTRACT_V1.json"
    )
    assert data["fit_execution_runner"] == "scripts/run_plant_v4_cmdstan.py"
    assert data["reactivation_evidence_bridge"] == (
        "balance_domain.plant_reactivation.evaluate_v4_reactivation_evidence"
    )
    assert data["reactivation_evidence_cli"] == (
        "scripts/evaluate_plant_v4_reactivation.py"
    )
    assert "PASS diagnostics" in data["fit_diagnostic_requirement"]
    reachability = data["current_v4_generality_reachability"]
    assert (
        reachability[
            "strict_temporal_generality_reachable_without_predictor_receipt_expansion"
        ]
        is False
    )
    assert reachability["v2_expansion_route_registered"] is True
    assert reachability["v2_expansion_packet_generated"] is True
    assert reachability["v2_expansion_return_received"] is False
    assert reachability["constructive_mechanical_witness_registered"] is True
    assert reachability["reopening_route_mechanically_nonempty"] is True
    assert reachability["real_strict_generality_gate_ready"] is False
    assert reachability["current_state"] == (
        "V1_UNREACHABLE_V2_ROUTE_EXECUTED_AWAITING_REAL_RETURN"
    )
    assert out["standalone_reactivation_eligible"] is False
    assert out["activation_action"] == "KEEP_DORMANT"
    assert "u2_independent_coding_and_adjudication_complete" in out["blockers"]
    assert "u6_independent_coding_and_adjudication_complete" in out["blockers"]
    assert "v4_primary_fit_complete" in out["blockers"]
    assert "temporal_common_support_module_stratum_ready" in out["blockers"]
    assert "temporal_generality_outcome_support_ready" in out["blockers"]
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
        "temporal_common_support_module_stratum_ready": True,
        "temporal_generality_outcome_support_ready": True,
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
            "temporal_common_support_module_stratum_ready",
            "temporal_generality_outcome_support_ready",
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



def test_reactivation_semantic_check_does_not_count_zero_mass_as_negative():
    summary = {
        "standardization_module_strata": ["SINGLE"],
        "universe_contrasts": {
            universe: {
                prior: {
                    "p_positive": 0.03,
                    "p_negative": 0.90,
                }
                for prior in ("primary_prior", "sensitivity_prior")
            }
            for universe in (
                "U2_BARRETT_2002",
                "U6_POLLEN_THEFT_HARGREAVES_2009",
            )
        },
        "interaction_negative_margin_probability": {
            "primary_prior": 0.01,
            "sensitivity_prior": 0.01,
            "margin_log_odds": -1.0,
        },
    }
    estimability = {
        "temporal_common_support_module_strata": ["SINGLE"],
        "temporal_cross_universe_common_support_ready": True,
        "temporal_cross_universe_outcome_support_ready": True,
    }
    expected = _validated_generality_decision(
        summary={
            **summary,
            "decision": {
                "analysis": "balance_plant_v4_temporal_generality_decision",
                "u2_directional_label": "INCONCLUSIVE",
                "u6_directional_label": "INCONCLUSIVE",
                "interaction_label": "NO_PRACTICALLY_LARGE_CONTRADICTION",
                "cross_universe_generality_supported": False,
                "blockers": [
                    "U2_direction_inconclusive",
                    "U6_direction_inconclusive",
                ],
                "posterior_direction_threshold": 0.95,
                "practical_negative_interaction_margin_log_odds": -1.0,
                "claim_ceiling": "posterior_reporting_label_not_publication_decision",
            },
        },
        estimability=estimability,
    )
    assert expected["u2_directional_label"] == "INCONCLUSIVE"
    assert expected["u6_directional_label"] == "INCONCLUSIVE"

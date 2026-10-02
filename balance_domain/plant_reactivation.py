"""Fail-closed standalone-paper reactivation gate for BALANCE plant model v4."""
from __future__ import annotations

import json
from pathlib import Path


SCHEMA = "BALANCE_PLANT_V4_REACTIVATION_GATE_V1"
BOOLEAN_REQUIREMENTS = (
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


def load_v4_reactivation_gate(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != SCHEMA:
        raise ValueError("V4 reactivation gate schema mismatch")
    if data.get("publication_status") != "DORMANT_PAPER_BRANCH":
        raise ValueError("V4 reactivation gate must remain dormant before eligibility")
    if data.get("active_publication_queue") is not False:
        raise ValueError("V4 reactivation gate cannot activate publication queue prospectively")

    req = data.get("required_conditions")
    if not isinstance(req, dict):
        raise ValueError("V4 reactivation gate requires condition mapping")
    for key in BOOLEAN_REQUIREMENTS:
        if not isinstance(req.get(key), bool):
            raise ValueError(f"V4 reactivation condition {key!r} must be boolean")

    for key in (
        "directionally_concordant_across_u2_u6",
        "contradictory_universe_interaction_exceeds_practical_margin",
    ):
        if req.get(key) not in {True, False, None}:
            raise ValueError(f"V4 reactivation condition {key!r} must be true/false/null")

    if data.get("standalone_reactivation_eligible") is not False:
        raise ValueError("prospective V4 gate cannot pre-declare standalone eligibility")

    ceiling = data.get("current_frozen_v4_support_ceiling")
    required_ceiling = {
        "predictor_adjudication_policy": "FILTER_ONLY_ACCEPT_OR_REJECT_FROZEN_VALUES",
        "source_screen_is_maximal_predictor_support": True,
        "shared_module_strata": ["SINGLE"],
        "maximal_common_support_counts": {
            "U2": {
                "SINGLE_SIMULTANEOUS": 1,
                "SINGLE_ORDERED_OR_ALTERNATING": 2,
            },
            "U6": {
                "SINGLE_SIMULTANEOUS": 18,
                "SINGLE_ORDERED_OR_ALTERNATING": 3,
            },
        },
        "strict_temporal_generality_common_support_reachable_without_new_evidence": False,
        "consequence": (
            "CURRENT_V4_CRITERION_4_CANNOT_REACTIVATE_FROM_HUMAN_ADJUDICATION_ALONE"
        ),
        "required_if_generality_is_pursued": (
            "NEW_PROSPECTIVELY_FROZEN_PREDICTOR_UNIVERSE_EXPANSION_BEFORE_OUTCOME_INSPECTION"
        ),
        "prohibited_response": "DO_NOT_LOWER_COMMON_SUPPORT_THRESHOLD_POST_HOC",
    }
    if ceiling != required_ceiling:
        raise ValueError("V4 frozen generality support ceiling drifted")
    return data


def evaluate_v4_reactivation_conditions(conditions: dict[str, object]) -> dict:
    """Evaluate future completed evidence without changing publication status."""
    missing = [
        key for key in BOOLEAN_REQUIREMENTS
        if conditions.get(key) is not True
    ]
    concordant = conditions.get("directionally_concordant_across_u2_u6") is True
    contradictory = (
        conditions.get("contradictory_universe_interaction_exceeds_practical_margin")
        is True
    )

    blockers = list(missing)
    if not concordant:
        blockers.append("directionally_concordant_across_u2_u6")
    if contradictory:
        blockers.append("practically_large_contradictory_universe_interaction")

    eligible = not blockers
    return {
        "analysis": "balance_plant_v4_standalone_reactivation_gate",
        "standalone_reactivation_eligible": eligible,
        "blockers": blockers,
        "publication_status_if_current": "DORMANT_PAPER_BRANCH",
        "activation_action": (
            "HUMAN_REVIEW_REQUIRED_BEFORE_PUBLICATION_STATUS_CHANGE"
            if eligible
            else "KEEP_DORMANT"
        ),
        "claim_ceiling": "reactivation_gate_only_not_publication_decision",
    }


def evaluate_v4_reactivation_gate(path: Path) -> dict:
    data = load_v4_reactivation_gate(path)
    return evaluate_v4_reactivation_conditions(data["required_conditions"])



def derive_v4_reactivation_conditions(
    *,
    human_workspace_receipt: dict,
    assembly_readout: dict,
    fit_execution_receipt: dict,
    temporal_generality_postfit_summary: dict | None,
) -> dict[str, object]:
    """Derive the frozen reactivation evidence conditions from validated receipts.

    This function is deliberately read-only. It does not change publication status.
    A directional condition is true only when the preregistered positive timing
    direction is SUPPORTED under both priors; a merely resolved negative direction
    does not satisfy reactivation eligibility.
    """
    if (
        human_workspace_receipt.get("schema_version")
        != "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_V1"
    ):
        raise ValueError("V4 human-workspace receipt schema mismatch")
    if (
        human_workspace_receipt.get("analysis")
        != "balance_plant_v4_human_input_workspace"
    ):
        raise ValueError("V4 human-workspace receipt analysis mismatch")

    if human_workspace_receipt.get("primary_model_assembly_ready") is not True:
        raise ValueError("V4 human-workspace receipt is not primary-assembly ready")

    primary_open = human_workspace_receipt.get("primary_human_open_gates")
    if not isinstance(primary_open, dict):
        raise ValueError("V4 human-workspace receipt lacks primary human gates")

    required_gate_names = {
        "u2_independent_double_coding",
        "u2_post_coding_adjudication",
        "u6_independent_double_coding",
        "u6_post_coding_adjudication",
        "u2_predictor_independent_adjudication",
        "u6_predictor_independent_adjudication",
    }
    if set(primary_open) != required_gate_names:
        raise ValueError("V4 human-workspace primary human gate set drifted")
    if any(not isinstance(primary_open[name], bool) for name in required_gate_names):
        raise ValueError("V4 human-workspace primary human gates must be boolean")

    if (
        assembly_readout.get("analysis")
        != "balance_plant_confirmatory_model_assembly_v4"
    ):
        raise ValueError("V4 assembly readout analysis mismatch")
    estimability = assembly_readout.get("v4_estimability")
    if not isinstance(estimability, dict):
        raise ValueError("V4 assembly readout lacks estimability report")

    if (
        fit_execution_receipt.get("schema_version")
        != "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1"
    ):
        raise ValueError("V4 fit execution receipt schema mismatch")

    active_jobs = fit_execution_receipt.get("active_jobs")
    if not isinstance(active_jobs, list):
        raise ValueError("V4 fit execution receipt lacks active jobs")
    active_jobs = set(active_jobs)
    execution_complete = (
        fit_execution_receipt.get("execution_status") == "COMPLETE"
        and fit_execution_receipt.get("postfit_decision_allowed") is True
        and fit_execution_receipt.get("diagnostic_failures") == []
    )
    primary_fit_complete = execution_complete and {
        "PRIMARY",
        "PRIMARY_PRIOR_SENSITIVITY",
    } <= active_jobs

    generality_jobs = {
        "TEMPORAL_GENERALITY",
        "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY",
    }
    partial_generality_jobs = active_jobs & generality_jobs
    if partial_generality_jobs and partial_generality_jobs != generality_jobs:
        raise ValueError("V4 fit execution receipt contains an incomplete generality pair")

    assembly_generality_ready = (
        estimability.get("temporal_cross_universe_generality_ready") is True
    )
    receipt_generality_expected = fit_execution_receipt.get(
        "temporal_generality_expected_from_assembly"
    )
    if receipt_generality_expected is not assembly_generality_ready:
        raise ValueError(
            "V4 fit receipt generality expectation disagrees with assembly estimability"
        )
    generality_pair_active = generality_jobs <= active_jobs
    if generality_pair_active is not assembly_generality_ready:
        raise ValueError(
            "V4 fit active generality jobs disagree with assembly support gate"
        )
    generality_fit_complete = execution_complete and generality_pair_active

    u2_supported = False
    u6_supported = False
    contradictory = None
    if temporal_generality_postfit_summary is not None:
        if (
            temporal_generality_postfit_summary.get("analysis")
            != "balance_plant_v4_temporal_generality_postfit_summary"
        ):
            raise ValueError("V4 temporal-generality postfit summary analysis mismatch")
        decision = temporal_generality_postfit_summary.get("decision")
        if not isinstance(decision, dict):
            raise ValueError("V4 temporal-generality summary lacks decision")
        u2_label = decision.get("u2_directional_label")
        u6_label = decision.get("u6_directional_label")
        interaction_label = decision.get("interaction_label")
        if u2_label not in {"SUPPORTED", "CONTRADICTED", "INCONCLUSIVE"}:
            raise ValueError("invalid U2 temporal-generality directional label")
        if u6_label not in {"SUPPORTED", "CONTRADICTED", "INCONCLUSIVE"}:
            raise ValueError("invalid U6 temporal-generality directional label")
        if interaction_label not in {
            "PRACTICALLY_CONTRADICTORY",
            "NO_PRACTICALLY_LARGE_CONTRADICTION",
        }:
            raise ValueError("invalid temporal-generality interaction label")
        u2_supported = u2_label == "SUPPORTED"
        u6_supported = u6_label == "SUPPORTED"
        contradictory = interaction_label == "PRACTICALLY_CONTRADICTORY"
        expected_generality_supported = (
            u2_supported and u6_supported and not contradictory
        )
        if (
            decision.get("cross_universe_generality_supported")
            is not expected_generality_supported
        ):
            raise ValueError(
                "V4 temporal-generality decision fields are internally inconsistent"
            )

    return {
        "u2_independent_coding_and_adjudication_complete": (
            not primary_open["u2_independent_double_coding"]
            and not primary_open["u2_post_coding_adjudication"]
        ),
        "u6_independent_coding_and_adjudication_complete": (
            not primary_open["u6_independent_double_coding"]
            and not primary_open["u6_post_coding_adjudication"]
        ),
        "u2_u6_predictor_independence_adjudication_complete": (
            not primary_open["u2_predictor_independent_adjudication"]
            and not primary_open["u6_predictor_independent_adjudication"]
        ),
        "v4_primary_estimability_pass": (
            assembly_readout.get("ready_for_primary_fit") is True
        ),
        "v4_primary_fit_complete": primary_fit_complete,
        "temporal_generality_sensitivity_fit_complete": generality_fit_complete,
        "temporal_common_support_module_stratum_ready": (
            estimability.get("temporal_cross_universe_common_support_ready") is True
        ),
        "temporal_generality_outcome_support_ready": (
            estimability.get("temporal_cross_universe_outcome_support_ready") is True
        ),
        "u2_ordered_vs_simultaneous_direction_resolved": u2_supported,
        "u6_ordered_vs_simultaneous_direction_resolved": u6_supported,
        "directionally_concordant_across_u2_u6": (
            u2_supported and u6_supported
        ),
        "contradictory_universe_interaction_exceeds_practical_margin": contradictory,
    }


def evaluate_v4_reactivation_evidence(
    *,
    human_workspace_receipt: dict,
    assembly_readout: dict,
    fit_execution_receipt: dict,
    temporal_generality_postfit_summary: dict | None,
) -> dict:
    """Derive and evaluate V4 standalone evidence eligibility without activation."""
    conditions = derive_v4_reactivation_conditions(
        human_workspace_receipt=human_workspace_receipt,
        assembly_readout=assembly_readout,
        fit_execution_receipt=fit_execution_receipt,
        temporal_generality_postfit_summary=temporal_generality_postfit_summary,
    )
    gate = evaluate_v4_reactivation_conditions(conditions)
    return {
        "analysis": "balance_plant_v4_reactivation_evidence_bridge",
        "derived_conditions": conditions,
        "gate": gate,
        "publication_status_changed": False,
        "claim_ceiling": "evidence_eligibility_only_not_publication_decision",
    }

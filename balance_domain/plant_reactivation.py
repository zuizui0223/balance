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

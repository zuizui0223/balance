"""Prospective estimability gate for the Senna covesii routing assay.

Stage-0 data may estimate nuisance quantities only. The biologically meaningful
routing/equivalence margin must be frozen independently of the focal positional
contrast before any final power or classification analysis.
"""
from __future__ import annotations

from typing import Any


REQUIRED = "REQUIRED_BEFORE_USE"
READY_NUISANCE_STATUS = "SENCOV_STAGE0_NUISANCE_READY"
TARGET_ANALYSIS = "balance_u3_sencov_routing_power_targets_v1"
NUISANCE_ANALYSIS = "balance_u3_sencov_stage0_nuisance_v1"

FORBIDDEN_NUISANCE_KEYS = {
    "observed_delta_route_log_odds",
    "observed_position_treatment_effect",
    "observed_median_vs_abaxial_effect",
}


def _required_paths(value: Any, prefix: str = "") -> list[str]:
    missing: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            missing.extend(_required_paths(child, child_prefix))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            child_prefix = f"{prefix}[{idx}]"
            missing.extend(_required_paths(child, child_prefix))
    elif value == REQUIRED:
        missing.append(prefix)
    return missing


def classify_routing_interval(
    ci_low: float,
    ci_high: float,
    equivalence_margin_abs_log_odds: float,
) -> str:
    """Classify one frozen CI against a symmetric routing-equivalence band."""
    if ci_low > ci_high:
        raise ValueError("routing CI lower bound cannot exceed upper bound")
    margin = float(equivalence_margin_abs_log_odds)
    if margin <= 0:
        raise ValueError("routing equivalence margin must be positive")

    if ci_low > margin or ci_high < -margin:
        return "WITHIN_FLOWER_DIVISION_OF_LABOUR"
    if ci_low > -margin and ci_high < margin:
        return "SHARED_INTEGRATED"
    return "UNRESOLVED"


def prepare_sencov_routing_estimability(nuisance: dict, targets: dict) -> dict:
    errors: list[str] = []

    if nuisance.get("analysis") != NUISANCE_ANALYSIS:
        errors.append("wrong_nuisance_analysis_id")
    if nuisance.get("status") != READY_NUISANCE_STATUS:
        errors.append(
            f"nuisance_status_not_ready:{nuisance.get('status', 'MISSING')}"
        )
    for key in sorted(FORBIDDEN_NUISANCE_KEYS & set(nuisance)):
        errors.append(f"forbidden_stage0_effect_input:{key}")

    if targets.get("analysis") != TARGET_ANALYSIS:
        errors.append("wrong_target_analysis_id")
    errors.extend(
        f"unfrozen_target:{path}" for path in _required_paths(targets)
    )

    rule = str(targets.get("target_source_rule", ""))
    if (
        "Stage-0 positional effect estimates must not be used" not in rule
        or "independent" not in rule.casefold()
    ):
        errors.append("target_source_rule_missing_anticircularity_guard")

    estimand = targets.get("primary_estimand", {})
    if estimand.get("name") != "delta_route_log_odds":
        errors.append("wrong_primary_estimand")
    if estimand.get("comparison") != "abaxial_minus_median":
        errors.append("wrong_primary_estimand_comparison")

    margin = targets.get("equivalence_margin_abs_log_odds")
    if margin != REQUIRED:
        try:
            if float(margin) <= 0:
                errors.append("equivalence_margin_must_be_positive")
        except (TypeError, ValueError):
            errors.append("equivalence_margin_must_be_numeric")

    design = targets.get("design", {})
    if design.get("cluster_unit") != "plant_id":
        errors.append("plant_level_dependence_not_required")
    if design.get("source_assignment_unit") != "pollen_grain_or_validated_source_proxy":
        errors.append("source_resolved_pollen_not_required")
    if design.get("position_groups_frozen_before_outcomes") is not True:
        errors.append("position_groups_not_frozen_before_outcomes")
    if design.get("shared_integration_requires_equivalence") is not True:
        errors.append("shared_integration_equivalence_not_required")

    stopping = targets.get("precision_stopping_rule", {})
    if stopping.get("outcome_blinded_for_margin_selection") is not True:
        errors.append("margin_selection_not_outcome_blinded")
    if stopping.get("classification") != (
        "CI_outside_equivalence_band=>WITHIN_FLOWER_DIVISION_OF_LABOUR;"
        "CI_inside_equivalence_band=>SHARED_INTEGRATED;"
        "otherwise=>UNRESOLVED"
    ):
        errors.append("routing_classification_rule_drift")

    result = {
        "analysis": "balance_u3_sencov_routing_estimability_gate_v1",
        "status": (
            "SENCOV_ROUTING_CONFIG_READY_FOR_POWER"
            if not errors
            else "SENCOV_ROUTING_CONFIG_NOT_READY"
        ),
        "errors": errors,
        "primary_estimand": (
            "delta_route_log_odds="
            "logit(P(transfer_fate|abaxial_source))-"
            "logit(P(transfer_fate|median_source))"
        ),
        "classification_contract": {
            "WITHIN_FLOWER_DIVISION_OF_LABOUR": (
                "confidence interval entirely outside the frozen symmetric "
                "equivalence band"
            ),
            "SHARED_INTEGRATED": (
                "confidence interval entirely inside the frozen symmetric "
                "equivalence band"
            ),
            "UNRESOLVED": "confidence interval overlaps an equivalence boundary",
        },
        "anti_circularity_rule": (
            "Stage-0 estimates nuisance variation, recovery, clustering and attrition "
            "only; it cannot define the routing effect or equivalence margin"
        ),
        "claim_ceiling": (
            "prospective_estimability_and_power_input_gate_only_not_empirical_"
            "routing_result_not_architecture_assignment"
        ),
    }
    if not errors:
        result["power_contract"] = {
            "target_power": targets["target_power"],
            "alpha_two_sided": targets["alpha_two_sided"],
            "equivalence_margin_abs_log_odds": float(
                targets["equivalence_margin_abs_log_odds"]
            ),
            "cluster_unit": "plant_id",
            "position_groups": {
                "median": "four median fertile stamen positions",
                "abaxial": "three abaxial fertile stamen positions",
            },
            "choose_final_n_by": (
                "precision_or_power_for_both_division_and_equivalence_decisions_"
                "under_registered_nuisance_sensitivity"
            ),
        }
    return result

"""Prospective estimability gate for an Osbeckia chinensis pollen-fate assay.

The public-source ceiling leaves the control-side pollen-fate conflict
unresolved. This module defines a fail-closed empirical route: source-resolve
pollen removed from focal flowers into reward/grooming versus transfer fates.
Stage-0 may estimate nuisance quantities only; it may not choose convenient
biological thresholds from the focal fate proportions.
"""
from __future__ import annotations

from typing import Any


REQUIRED = "REQUIRED_BEFORE_USE"
TARGET_ANALYSIS = "balance_u3_osbeckia_conflict_power_targets_v1"
NUISANCE_ANALYSIS = "balance_u3_osbeckia_stage0_nuisance_v1"
READY_NUISANCE_STATUS = "OSBECKIA_STAGE0_NUISANCE_READY"

FORBIDDEN_NUISANCE_KEYS = {
    "observed_reward_fate_probability",
    "observed_transfer_fate_probability",
    "observed_transfer_to_reward_log_ratio",
    "observed_conflict_strength",
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


def classify_osbeckia_partition(
    reward_ci_low: float,
    transfer_ci_low: float,
    minimum_reward_fate_probability: float,
    minimum_transfer_fate_probability: float,
    source_misclassification_rate: float,
    maximum_source_misclassification_rate: float,
) -> str:
    """Return POSITIVE only when both competing fates clear frozen floors."""
    values = (
        reward_ci_low,
        transfer_ci_low,
        minimum_reward_fate_probability,
        minimum_transfer_fate_probability,
        source_misclassification_rate,
        maximum_source_misclassification_rate,
    )
    if any(not isinstance(x, (int, float)) or isinstance(x, bool) for x in values):
        raise ValueError("Osbeckia classification inputs must be numeric")
    if not 0 <= reward_ci_low <= 1 or not 0 <= transfer_ci_low <= 1:
        raise ValueError("fate-probability CI lower bounds must lie in [0,1]")
    if not 0 < minimum_reward_fate_probability < 1:
        raise ValueError("minimum reward-fate probability must lie in (0,1)")
    if not 0 < minimum_transfer_fate_probability < 1:
        raise ValueError("minimum transfer-fate probability must lie in (0,1)")
    if not 0 <= source_misclassification_rate < 1:
        raise ValueError("source misclassification rate must lie in [0,1)")
    if not 0 < maximum_source_misclassification_rate < 1:
        raise ValueError("maximum source misclassification rate must lie in (0,1)")

    if (
        reward_ci_low > minimum_reward_fate_probability
        and transfer_ci_low > minimum_transfer_fate_probability
        and source_misclassification_rate <= maximum_source_misclassification_rate
    ):
        return "POSITIVE"
    return "UNRESOLVED"


def prepare_osbeckia_conflict_estimability(nuisance: dict, targets: dict) -> dict:
    errors: list[str] = []

    if nuisance.get("analysis") != NUISANCE_ANALYSIS:
        errors.append("wrong_nuisance_analysis_id")
    if nuisance.get("status") != READY_NUISANCE_STATUS:
        errors.append(
            f"nuisance_status_not_ready:{nuisance.get('status', 'MISSING')}"
        )
    for key in sorted(FORBIDDEN_NUISANCE_KEYS & set(nuisance)):
        errors.append(f"forbidden_stage0_focal_output:{key}")

    if targets.get("analysis") != TARGET_ANALYSIS:
        errors.append("wrong_target_analysis_id")
    errors.extend(f"unfrozen_target:{p}" for p in _required_paths(targets))

    source_rule = str(targets.get("target_source_rule", ""))
    if (
        "Stage-0 focal fate proportions must not be used" not in source_rule
        or "independent" not in source_rule.casefold()
    ):
        errors.append("target_source_rule_missing_anticircularity_guard")

    estimand = targets.get("primary_estimand", {})
    if estimand.get("name") != "same_visit_source_resolved_pollen_fate_partition":
        errors.append("wrong_primary_estimand")
    if estimand.get("classification") != (
        "POSITIVE_only_if_simultaneous_lower_bounds_clear_both_frozen_fate_floors"
    ):
        errors.append("wrong_primary_classification_contract")

    design = targets.get("design", {})
    if design.get("cluster_unit") != "plant_id":
        errors.append("plant_level_dependence_not_required")
    if design.get("visit_unit") != "tracked_single_visitor_sequence":
        errors.append("single_visit_sequence_not_required")
    if design.get("source_assignment_required") is not True:
        errors.append("source_resolved_pollen_not_required")
    if design.get("reward_and_transfer_fates_mutually_exclusive_at_scoring_time") is not True:
        errors.append("fate_partition_not_mutually_exclusive")
    if design.get("unresolved_grains_retained_separately") is not True:
        errors.append("unresolved_grains_not_retained")

    stopping = targets.get("precision_stopping_rule", {})
    if stopping.get("outcome_blinded_for_threshold_selection") is not True:
        errors.append("threshold_selection_not_outcome_blinded")
    if stopping.get("negative_call_allowed") is not False:
        errors.append("negative_call_must_fail_closed")
    if stopping.get("classification") != (
        "both_simultaneous_CI_lower_bounds_above_frozen_floors_and_"
        "source_error_below_ceiling=>POSITIVE;otherwise=>UNRESOLVED"
    ):
        errors.append("classification_rule_drift")

    result = {
        "analysis": "balance_u3_osbeckia_conflict_estimability_gate_v1",
        "status": (
            "OSBECKIA_CONFLICT_CONFIG_READY_FOR_POWER"
            if not errors
            else "OSBECKIA_CONFLICT_CONFIG_NOT_READY"
        ),
        "errors": errors,
        "primary_estimand": (
            "source-resolved probabilities that pollen removed from a focal "
            "O. chinensis flower enters preregistered reward/grooming versus "
            "conspecific-transfer fates within one tracked visitor sequence"
        ),
        "positive_classification_contract": (
            "call POSITIVE only when simultaneous lower confidence bounds for "
            "both reward and transfer fate probabilities exceed independently "
            "frozen biological/assay floors and source misclassification is "
            "below its frozen ceiling"
        ),
        "negative_classification_contract": (
            "no NO_DEMONSTRATED_CONFLICT call is licensed by failure to clear "
            "the positive floors; insufficient precision remains UNRESOLVED"
        ),
        "anti_circularity_rule": (
            "Stage-0 estimates clustering, recovery, contamination, attrition "
            "and unresolved-fate nuisance only; focal fate proportions cannot "
            "set the biological floors used for final classification"
        ),
        "claim_ceiling": (
            "prospective_osbeckia_conflict_estimability_gate_only_not_empirical_"
            "conflict_result_not_strength_estimate_not_routing_assignment"
        ),
    }
    if not errors:
        result["power_contract"] = {
            "target_power": targets["target_power"],
            "alpha_familywise": targets["alpha_familywise"],
            "minimum_reward_fate_probability": float(
                targets["minimum_reward_fate_probability"]
            ),
            "minimum_transfer_fate_probability": float(
                targets["minimum_transfer_fate_probability"]
            ),
            "maximum_source_misclassification_rate": float(
                targets["maximum_source_misclassification_rate"]
            ),
            "cluster_unit": "plant_id",
            "choose_final_n_by": (
                "simultaneous_precision_for_both_fate_lower_bounds_across_"
                "registered_nuisance_sensitivity"
            ),
        }
    return result

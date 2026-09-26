import pytest

from balance_domain.plant_u3_osbeckia_estimability import (
    REQUIRED,
    classify_osbeckia_partition,
    prepare_osbeckia_conflict_estimability,
)


def _ready_nuisance():
    return {
        "analysis": "balance_u3_osbeckia_stage0_nuisance_v1",
        "status": "OSBECKIA_STAGE0_NUISANCE_READY",
        "allowed_outputs": {
            "plant_level_icc": 0.1,
        },
    }


def _ready_targets():
    return {
        "analysis": "balance_u3_osbeckia_conflict_power_targets_v1",
        "status": "READY",
        "target_power": 0.8,
        "alpha_familywise": 0.05,
        "target_source_rule": (
            "Thresholds use independent assay/biological justification. "
            "Stage-0 focal fate proportions must not be used to choose convenient "
            "thresholds; threshold justification is independent."
        ),
        "primary_estimand": {
            "name": "same_visit_source_resolved_pollen_fate_partition",
            "classification": (
                "POSITIVE_only_if_simultaneous_lower_bounds_clear_both_frozen_fate_floors"
            ),
        },
        "minimum_reward_fate_probability": 0.05,
        "minimum_reward_fate_probability_justification": "independent assay threshold",
        "minimum_transfer_fate_probability": 0.02,
        "minimum_transfer_fate_probability_justification": "independent assay threshold",
        "maximum_source_misclassification_rate": 0.01,
        "source_misclassification_ceiling_justification": "independent validation",
        "design": {
            "cluster_unit": "plant_id",
            "donor_unit": "single_focal_flower",
            "visit_unit": "tracked_single_visitor_sequence",
            "source_assignment_required": True,
            "donor_pollen_source_method": "validated marker",
            "recipient_sequence": "one registered recipient",
            "visitor_body_sector_map": "preregistered sectors",
            "reward_compartment_definition": "groomed or collected",
            "transfer_compartment_definition": "safe sector or recipient stigma",
            "reward_and_transfer_fates_mutually_exclusive_at_scoring_time": True,
            "unresolved_grains_retained_separately": True,
            "candidate_plants": 10,
            "tracked_visits_per_plant": 4,
            "allocation_rule": "balanced",
            "attrition_inflation_rule": "registered",
        },
        "nuisance_sensitivity": {
            "plant_level_icc_range": [0.05, 0.2],
            "visitor_class_heterogeneity_range": [0.0, 0.2],
            "source_label_recovery_rate_range": [0.8, 0.95],
            "background_contamination_rate_range": [0.0, 0.02],
            "source_misclassification_rate_range": [0.0, 0.01],
            "unresolved_or_lost_fate_fraction_range": [0.05, 0.2],
            "recipient_stigma_recovery_rate_range": [0.8, 0.95],
            "attrition_fraction_range": [0.05, 0.15],
        },
        "precision_stopping_rule": {
            "outcome_blinded_for_threshold_selection": True,
            "thresholds_frozen_before_focal_fate_proportions": True,
            "negative_call_allowed": False,
            "classification": (
                "both_simultaneous_CI_lower_bounds_above_frozen_floors_and_"
                "source_error_below_ceiling=>POSITIVE;otherwise=>UNRESOLVED"
            ),
            "final_scale_rule": "registered precision rule",
        },
        "fail_closed_rules": ["registered"],
        "claim_ceiling": "prospective target",
    }


def test_osbeckia_positive_requires_both_fates_and_source_quality():
    assert classify_osbeckia_partition(0.08, 0.04, 0.05, 0.02, 0.005, 0.01) == "POSITIVE"
    assert classify_osbeckia_partition(0.04, 0.04, 0.05, 0.02, 0.005, 0.01) == "UNRESOLVED"
    assert classify_osbeckia_partition(0.08, 0.01, 0.05, 0.02, 0.005, 0.01) == "UNRESOLVED"
    assert classify_osbeckia_partition(0.08, 0.04, 0.05, 0.02, 0.02, 0.01) == "UNRESOLVED"


def test_osbeckia_classifier_rejects_invalid_probability_inputs():
    with pytest.raises(ValueError):
        classify_osbeckia_partition(-0.1, 0.1, 0.05, 0.02, 0.0, 0.01)
    with pytest.raises(ValueError):
        classify_osbeckia_partition(True, 0.1, 0.05, 0.02, 0.0, 0.01)


def test_template_with_required_fields_is_not_ready():
    targets = _ready_targets()
    targets["minimum_transfer_fate_probability"] = REQUIRED
    out = prepare_osbeckia_conflict_estimability(_ready_nuisance(), targets)
    assert out["status"] == "OSBECKIA_CONFLICT_CONFIG_NOT_READY"
    assert any("unfrozen_target" in x for x in out["errors"])


def test_stage0_cannot_smuggle_focal_fate_effects_into_targets():
    nuisance = _ready_nuisance()
    nuisance["observed_reward_fate_probability"] = 0.4
    out = prepare_osbeckia_conflict_estimability(nuisance, _ready_targets())
    assert out["status"] == "OSBECKIA_CONFLICT_CONFIG_NOT_READY"
    assert "forbidden_stage0_focal_output:observed_reward_fate_probability" in out["errors"]


def test_ready_osbeckia_contract_preserves_positive_only_fail_closed_rule():
    out = prepare_osbeckia_conflict_estimability(_ready_nuisance(), _ready_targets())
    assert out["status"] == "OSBECKIA_CONFLICT_CONFIG_READY_FOR_POWER"
    assert out["power_contract"]["cluster_unit"] == "plant_id"
    assert "no NO_DEMONSTRATED_CONFLICT" in out["negative_classification_contract"]

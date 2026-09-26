from balance_domain.plant_u3_sencov_estimability import (
    classify_routing_interval,
    prepare_sencov_routing_estimability,
)


def _ready_nuisance():
    return {
        "analysis": "balance_u3_sencov_stage0_nuisance_v1",
        "status": "SENCOV_STAGE0_NUISANCE_READY",
        "plant_level_icc": 0.2,
        "source_label_recovery_rate": 0.8,
    }


def _ready_targets():
    return {
        "analysis": "balance_u3_sencov_routing_power_targets_v1",
        "status": "TARGETS_FROZEN",
        "target_power": 0.8,
        "alpha_two_sided": 0.05,
        "target_source_rule": (
            "The equivalence margin is independently justified. "
            "Stage-0 positional effect estimates must not be used to choose it."
        ),
        "primary_estimand": {
            "name": "delta_route_log_odds",
            "comparison": "abaxial_minus_median",
        },
        "equivalence_margin_abs_log_odds": 0.4,
        "design": {
            "cluster_unit": "plant_id",
            "source_assignment_unit": "pollen_grain_or_validated_source_proxy",
            "position_groups_frozen_before_outcomes": True,
            "shared_integration_requires_equivalence": True,
        },
        "precision_stopping_rule": {
            "outcome_blinded_for_margin_selection": True,
            "classification": (
                "CI_outside_equivalence_band=>WITHIN_FLOWER_DIVISION_OF_LABOUR;"
                "CI_inside_equivalence_band=>SHARED_INTEGRATED;"
                "otherwise=>UNRESOLVED"
            ),
        },
    }


def test_current_template_fails_closed_until_targets_and_nuisance_are_frozen():
    nuisance = {
        "analysis": "balance_u3_sencov_stage0_nuisance_v1",
        "status": "TEMPLATE_NOT_READY",
    }
    targets = {
        "analysis": "balance_u3_sencov_routing_power_targets_v1",
        "target_source_rule": (
            "independent target; Stage-0 positional effect estimates must not be used"
        ),
        "primary_estimand": {
            "name": "delta_route_log_odds",
            "comparison": "abaxial_minus_median",
        },
        "equivalence_margin_abs_log_odds": "REQUIRED_BEFORE_USE",
        "design": {
            "cluster_unit": "plant_id",
            "source_assignment_unit": "pollen_grain_or_validated_source_proxy",
            "position_groups_frozen_before_outcomes": True,
            "shared_integration_requires_equivalence": True,
            "candidate_plants": "REQUIRED_BEFORE_USE",
        },
        "precision_stopping_rule": {
            "outcome_blinded_for_margin_selection": True,
            "classification": (
                "CI_outside_equivalence_band=>WITHIN_FLOWER_DIVISION_OF_LABOUR;"
                "CI_inside_equivalence_band=>SHARED_INTEGRATED;"
                "otherwise=>UNRESOLVED"
            ),
        },
    }
    out = prepare_sencov_routing_estimability(nuisance, targets)
    assert out["status"] == "SENCOV_ROUTING_CONFIG_NOT_READY"
    assert any(e.startswith("unfrozen_target:") for e in out["errors"])
    assert any(e.startswith("nuisance_status_not_ready") for e in out["errors"])


def test_ready_configuration_requires_independent_margin_and_clustered_design():
    out = prepare_sencov_routing_estimability(_ready_nuisance(), _ready_targets())
    assert out["status"] == "SENCOV_ROUTING_CONFIG_READY_FOR_POWER"
    assert out["errors"] == []
    assert out["power_contract"]["equivalence_margin_abs_log_odds"] == 0.4
    assert out["power_contract"]["cluster_unit"] == "plant_id"


def test_stage0_focal_effect_cannot_enter_nuisance_receipt():
    nuisance = _ready_nuisance()
    nuisance["observed_delta_route_log_odds"] = 0.9
    out = prepare_sencov_routing_estimability(nuisance, _ready_targets())
    assert out["status"] == "SENCOV_ROUTING_CONFIG_NOT_READY"
    assert "forbidden_stage0_effect_input:observed_delta_route_log_odds" in out["errors"]


def test_interval_classification_is_symmetric_and_fail_closed():
    margin = 0.4
    assert classify_routing_interval(0.55, 0.9, margin) == (
        "WITHIN_FLOWER_DIVISION_OF_LABOUR"
    )
    assert classify_routing_interval(-0.9, -0.55, margin) == (
        "WITHIN_FLOWER_DIVISION_OF_LABOUR"
    )
    assert classify_routing_interval(-0.2, 0.25, margin) == "SHARED_INTEGRATED"
    assert classify_routing_interval(0.1, 0.55, margin) == "UNRESOLVED"
    assert classify_routing_interval(-0.55, -0.1, margin) == "UNRESOLVED"


def test_shared_integration_is_not_failure_to_reject_difference():
    margin = 0.4
    # A wide interval includes zero but also biologically meaningful differences.
    assert classify_routing_interval(-0.7, 0.7, margin) == "UNRESOLVED"

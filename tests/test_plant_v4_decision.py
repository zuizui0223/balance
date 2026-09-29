import pytest

from balance_domain.plant_v4_decision import (
    contradictory_interaction_label,
    directional_label,
    temporal_generality_decision,
)


def test_directional_label_requires_same_direction_under_both_registered_priors():
    assert directional_label(
        p_positive_primary=0.97,
        p_positive_sensitivity=0.96,
    ) == "SUPPORTED"
    assert directional_label(
        p_positive_primary=0.03,
        p_positive_sensitivity=0.04,
    ) == "CONTRADICTED"
    assert directional_label(
        p_positive_primary=0.98,
        p_positive_sensitivity=0.80,
    ) == "INCONCLUSIVE"


def test_interaction_label_fails_if_either_prior_supports_large_reverse_interaction():
    assert contradictory_interaction_label(
        p_gamma_below_negative_margin_primary=0.96,
        p_gamma_below_negative_margin_sensitivity=0.20,
    ) == "PRACTICALLY_CONTRADICTORY"
    assert contradictory_interaction_label(
        p_gamma_below_negative_margin_primary=0.10,
        p_gamma_below_negative_margin_sensitivity=0.20,
    ) == "NO_PRACTICALLY_LARGE_CONTRADICTION"


def test_temporal_generality_requires_support_gates_both_universes_and_no_contradiction():
    out = temporal_generality_decision(
        preoutcome_common_support_ready=True,
        per_universe_outcome_support_ready=True,
        u2_p_positive_primary=0.98,
        u2_p_positive_sensitivity=0.97,
        u6_p_positive_primary=0.97,
        u6_p_positive_sensitivity=0.96,
        p_gamma_below_negative_margin_primary=0.10,
        p_gamma_below_negative_margin_sensitivity=0.12,
    )
    assert out["cross_universe_generality_supported"] is True
    assert out["blockers"] == []
    assert out["u2_directional_label"] == "SUPPORTED"
    assert out["u6_directional_label"] == "SUPPORTED"


def test_pooled_direction_cannot_rescue_missing_common_support():
    out = temporal_generality_decision(
        preoutcome_common_support_ready=False,
        per_universe_outcome_support_ready=True,
        u2_p_positive_primary=0.99,
        u2_p_positive_sensitivity=0.99,
        u6_p_positive_primary=0.99,
        u6_p_positive_sensitivity=0.99,
        p_gamma_below_negative_margin_primary=0.01,
        p_gamma_below_negative_margin_sensitivity=0.01,
    )
    assert out["cross_universe_generality_supported"] is False
    assert out["blockers"] == ["shared_module_common_support"]


def test_generality_rejects_direction_discordance_even_without_large_interaction():
    out = temporal_generality_decision(
        preoutcome_common_support_ready=True,
        per_universe_outcome_support_ready=True,
        u2_p_positive_primary=0.98,
        u2_p_positive_sensitivity=0.98,
        u6_p_positive_primary=0.02,
        u6_p_positive_sensitivity=0.03,
        p_gamma_below_negative_margin_primary=0.10,
        p_gamma_below_negative_margin_sensitivity=0.10,
    )
    assert out["cross_universe_generality_supported"] is False
    assert out["u2_directional_label"] == "SUPPORTED"
    assert out["u6_directional_label"] == "CONTRADICTED"
    assert "U6_direction_contradicted" in out["blockers"]


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_posterior_probability_inputs_must_be_valid(value):
    with pytest.raises(ValueError, match=r"\[0,1\]"):
        directional_label(
            p_positive_primary=value,
            p_positive_sensitivity=0.95,
        )

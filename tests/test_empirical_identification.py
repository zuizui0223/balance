import pytest

from balance_domain.empirical_identification import (
    identify_switching_records,
    synthetic_example,
)


UP = [(0.05, "shared"), (0.1, "shared"), (0.12, "differentiated")]
DOWN = [(0.01, "differentiated"), (-0.05, "differentiated"), (-0.08, "shared")]
META = dict(
    common_phi_scale="matched payoff",
    fixed_context="same environment",
    instantaneous_rule_declared=True,
)


def test_exact_brackets_use_last_stay_and_preserve_strict_endpoints():
    result = identify_switching_records(UP, DOWN, **META, horizon_bounds=(10, 10))
    assert (result.forward_threshold.lower, result.forward_threshold.upper) == pytest.approx(
        (0.1, 0.12)
    )
    assert not result.forward_threshold.upper_closed
    assert not result.reverse_threshold.lower_closed
    assert (result.width.lower, result.width.upper) == pytest.approx((0.15, 0.2))
    assert (
        result.cost_shared_to_diff.lower,
        result.cost_shared_to_diff.upper,
    ) == pytest.approx((1, 1.2))
    assert (
        result.cost_diff_to_shared.lower,
        result.cost_diff_to_shared.upper,
    ) == pytest.approx((0.5, 0.8))
    assert (
        result.total_switching_cost.lower,
        result.total_switching_cost.upper,
    ) == pytest.approx((1.5, 2))


def test_unknown_horizon_does_not_create_absolute_costs():
    result = identify_switching_records(UP, DOWN, **META)
    assert result.cost_shared_to_diff is None
    assert result.total_switching_cost is None
    assert not result.cost_scale_identified
    assert 1.1 / 10 == pytest.approx(11 / 100)  # indistinguishable thresholds
    assert -0.6 / 10 == pytest.approx(-6 / 100)


def test_uncertain_horizon_propagates_instead_of_using_midpoint():
    result = identify_switching_records(UP, DOWN, **META, horizon_bounds=(8, 12))
    assert (
        result.total_switching_cost.lower,
        result.total_switching_cost.upper,
    ) == pytest.approx((1.2, 2.4))
    assert not result.cost_scale_identified


def test_censored_path_produces_unbounded_cost_not_zero_or_imputed_switch():
    result = identify_switching_records(UP[:2], DOWN, **META, horizon_bounds=(10, 10))
    assert not result.forward_switch_observed
    assert result.forward_threshold.upper is None
    assert result.total_switching_cost.upper is None
    assert result.width.lower == pytest.approx(0.15)


def test_nonnegative_cost_constraint_can_reject_seemingly_ordered_switches():
    # A forward switch at negative Phi requires negative forward switching cost.
    with pytest.raises(ValueError, match="incompatible"):
        identify_switching_records(
            [(-0.2, "shared"), (-0.1, "differentiated")],
            DOWN,
            **META,
        )


def test_monotonicity_and_recrossing_are_contract_requirements():
    with pytest.raises(ValueError, match="monotone"):
        identify_switching_records(
            [(0.1, "shared"), (0.05, "shared")],
            DOWN,
            **META,
        )
    with pytest.raises(ValueError, match="recrossing"):
        identify_switching_records(UP + [(0.13, "shared")], DOWN, **META)


@pytest.mark.parametrize("bounds", [(0, 1), (10, 9), (float("nan"), 1)])
def test_invalid_horizons(bounds):
    with pytest.raises(ValueError):
        identify_switching_records(UP, DOWN, **META, horizon_bounds=bounds)


def test_finite_thresholds_that_overflow_derived_width_fail_closed():
    upward = [(1.0e308, "shared"), (1.1e308, "differentiated")]
    downward = [(-1.0e308, "differentiated"), (-1.1e308, "shared")]
    with pytest.raises(ValueError, match="finite or None"):
        identify_switching_records(upward, downward, **META)


def test_finite_horizon_scaling_that_overflows_cost_interval_fails_closed():
    upward = [(1.0e100, "shared"), (1.1e100, "differentiated")]
    downward = [(-1.0e100, "differentiated"), (-1.1e100, "shared")]
    with pytest.raises(ValueError, match="finite or None"):
        identify_switching_records(
            upward,
            downward,
            **META,
            horizon_bounds=(1.0e308, 1.0e308),
        )


def test_example_label():
    assert synthetic_example()["data_kind"] == "synthetic_bracket_witness"

import math

import pytest

from balance_domain.hysteresis_interval import identify_hysteresis_interval


def test_true_width_is_bounded_by_observed_width_and_step_resolution():
    result = identify_hysteresis_interval(
        0.12,
        -0.08,
        max_up_step=0.02,
        max_down_step=0.03,
    )
    assert abs(result.forward_lower - 0.10) < 1e-12
    assert abs(result.forward_upper - 0.12) < 1e-12
    assert abs(result.reverse_lower + 0.08) < 1e-12
    assert abs(result.reverse_upper + 0.05) < 1e-12
    assert abs(result.observed_width - 0.20) < 1e-12
    assert abs(result.true_width_lower - 0.15) < 1e-12
    assert abs(result.true_width_upper - 0.20) < 1e-12


def test_known_horizon_turns_width_interval_into_switching_cost_sum_interval():
    result = identify_hysteresis_interval(
        0.12,
        -0.08,
        max_up_step=0.02,
        max_down_step=0.03,
        horizon=10.0,
    )
    assert abs(result.switching_cost_sum_lower - 1.5) < 1e-12
    assert abs(result.switching_cost_sum_upper - 2.0) < 1e-12


def test_conservative_bounds_survive_binary_floating_point_roundoff():
    # In exact decimal arithmetic the true width is 0.3 and the cost sum is 3.
    # Outward rounding must not exclude the true parameter.
    result = identify_hysteresis_interval(
        0.3,
        -0.2,
        max_up_step=0.1,
        max_down_step=0.1,
        horizon=10.0,
    )
    assert result.true_width_lower <= 0.3 <= result.true_width_upper
    assert result.switching_cost_sum_lower <= 3.0 <= result.switching_cost_sum_upper


def test_large_representable_hysteresis_width_stays_finite():
    result = identify_hysteresis_interval(
        8.0e307,
        -8.0e307,
        max_up_step=1.0e307,
        max_down_step=1.0e307,
    )
    assert math.isfinite(result.observed_width)
    assert result.observed_width == pytest.approx(1.6e308)
    assert math.isfinite(result.true_width_lower)
    assert math.isfinite(result.true_width_upper)
    assert result.true_width_lower <= result.observed_width <= result.true_width_upper


def test_unrepresentable_observed_hysteresis_width_fails_closed():
    with pytest.raises(ValueError, match="observed hysteresis width.*not representable"):
        identify_hysteresis_interval(
            1.0e308,
            -1.0e308,
            max_up_step=1.0e307,
            max_down_step=1.0e307,
        )


def test_unrepresentable_switching_cost_upper_bound_fails_closed():
    with pytest.raises(ValueError, match="switching cost sum upper bound.*not representable"):
        identify_hysteresis_interval(
            1.0e154,
            -1.0e154,
            max_up_step=1.0e154,
            max_down_step=1.0e154,
            horizon=1.0e154,
        )


def test_resolution_uncertainty_cannot_make_negative_true_width():
    result = identify_hysteresis_interval(
        0.02,
        -0.005,
        max_up_step=0.03,
        max_down_step=0.03,
    )
    assert result.forward_lower == 0.0
    assert result.reverse_upper == 0.0
    assert result.true_width_lower == 0.0
    assert abs(result.true_width_upper - 0.025) < 1e-12


def test_nonnegative_cost_sign_constraints_tighten_resolution_envelope():
    result = identify_hysteresis_interval(
        0.20,
        -0.01,
        max_up_step=0.05,
        max_down_step=0.10,
    )
    # Raw reverse resolution would extend to +0.09, but R=-C_DS/T <= 0.
    assert result.forward_lower == pytest.approx(0.15)
    assert result.reverse_upper == 0.0
    assert result.true_width_lower == pytest.approx(0.15)
    assert result.true_width_upper == pytest.approx(0.21)


def test_observed_strict_switches_require_positive_crossing_steps():
    with pytest.raises(ValueError, match="strictly positive step bounds"):
        identify_hysteresis_interval(
            0.1,
            -0.1,
            max_up_step=0.0,
            max_down_step=0.01,
        )
    with pytest.raises(ValueError, match="strictly positive step bounds"):
        identify_hysteresis_interval(
            0.1,
            -0.1,
            max_up_step=0.01,
            max_down_step=0.0,
        )


def test_observed_switch_signs_must_match_nonnegative_cost_model():
    with pytest.raises(ValueError, match="forward switch must be positive"):
        identify_hysteresis_interval(
            -0.1,
            -0.2,
            max_up_step=0.01,
            max_down_step=0.01,
        )
    with pytest.raises(ValueError, match="reverse switch must be negative"):
        identify_hysteresis_interval(
            0.2,
            0.1,
            max_up_step=0.01,
            max_down_step=0.01,
        )


def test_observed_threshold_order_must_be_consistent_with_hysteresis():
    # Sign-valid switch observations are automatically ordered around zero;
    # malformed cross-sign observations fail at the stronger sign contract.
    with pytest.raises(ValueError):
        identify_hysteresis_interval(
            -0.1,
            0.1,
            max_up_step=0.01,
            max_down_step=0.01,
        )

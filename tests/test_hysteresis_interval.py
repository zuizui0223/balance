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


def test_resolution_uncertainty_cannot_make_negative_true_width():
    result = identify_hysteresis_interval(
        0.02,
        0.00,
        max_up_step=0.03,
        max_down_step=0.03,
    )
    assert result.true_width_lower == 0.0
    assert abs(result.true_width_upper - 0.02) < 1e-12


def test_observed_threshold_order_must_be_consistent_with_hysteresis():
    try:
        identify_hysteresis_interval(
            -0.1,
            0.1,
            max_up_step=0.01,
            max_down_step=0.01,
        )
    except ValueError as exc:
        assert "forward" in str(exc)
    else:
        raise AssertionError("inconsistent observed switch order should fail")

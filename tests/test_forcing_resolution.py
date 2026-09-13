import pytest

from balance_domain.forcing_resolution import (
    downward_switch_resolution,
    hysteresis_resolution_audit,
    upward_switch_resolution,
)
from balance_domain.hysteresis_interval import identify_hysteresis_interval
from balance_domain.stepwise_hysteresis import (
    follow_switching_path,
    linear_small_step_path,
)


PARAMS = dict(
    horizon_per_step=10.0,
    cost_shared_to_diff=2.0,
    cost_diff_to_shared=1.0,
)


def _up(path, **overrides):
    params = {**PARAMS, **overrides}
    return follow_switching_path(path, initial_state="shared", **params)


def _down(path, **overrides):
    params = {**PARAMS, **overrides}
    return follow_switching_path(path, initial_state="differentiated", **params)


def test_switch_points_are_bracketed_by_crossing_step():
    up = upward_switch_resolution(
        _up((-0.2, -0.1, 0.0, 0.1, 0.2, 0.3))
    )
    down = downward_switch_resolution(
        _down((0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2))
    )

    assert abs(up.threshold - 0.2) < 1e-12
    assert abs(up.observed_switch_phi - 0.3) < 1e-12
    assert up.previous_phi <= up.threshold < up.observed_switch_phi
    assert up.absolute_error <= up.jump_bound + 1e-12

    assert abs(down.threshold + 0.1) < 1e-12
    assert abs(down.observed_switch_phi + 0.2) < 1e-12
    assert down.observed_switch_phi < down.threshold <= down.previous_phi
    assert down.absolute_error <= down.jump_bound + 1e-12


def test_observed_hysteresis_width_overestimates_by_at_most_two_crossing_jumps():
    audit = hysteresis_resolution_audit(
        _up((-0.2, -0.1, 0.0, 0.1, 0.2, 0.3)),
        _down((0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2)),
    )
    assert abs(audit.true_hysteresis_width - 0.3) < 1e-12
    assert abs(audit.observed_hysteresis_width - 0.5) < 1e-12
    assert abs(audit.width_overestimate - 0.2) < 1e-12
    assert audit.width_overestimate <= audit.overestimate_upper_bound + 1e-12


def test_path_refinement_shrinks_the_resolution_bound():
    coarse = hysteresis_resolution_audit(
        _up(linear_small_step_path(-0.2, 0.4, max_phi_jump=0.1)),
        _down(linear_small_step_path(0.4, -0.3, max_phi_jump=0.1)),
    )
    fine = hysteresis_resolution_audit(
        _up(linear_small_step_path(-0.2, 0.4, max_phi_jump=0.025)),
        _down(linear_small_step_path(0.4, -0.3, max_phi_jump=0.025)),
    )
    assert fine.overestimate_upper_bound < coarse.overestimate_upper_bound
    assert fine.overestimate_upper_bound <= 0.05 + 1e-12
    assert fine.width_overestimate <= fine.overestimate_upper_bound + 1e-12


def test_resolution_audit_rejects_splicing_different_switching_models():
    upward = _up((-0.2, -0.1, 0.0, 0.1, 0.2, 0.3))
    # Preserve the forward threshold F=0.2 while changing only the reverse
    # threshold from -0.1 to -0.3.  Looking only at the observed direction of
    # each sweep would splice a width of 0.5 from two different models.
    downward = _down(
        (0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.4),
        cost_diff_to_shared=3.0,
    )
    with pytest.raises(ValueError, match="same switching thresholds"):
        hysteresis_resolution_audit(upward, downward)


def test_resolution_audit_and_inverse_interval_share_one_identified_model():
    audit = hysteresis_resolution_audit(
        _up((-0.2, -0.1, 0.0, 0.1, 0.2, 0.3)),
        _down((0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2)),
    )
    interval = identify_hysteresis_interval(
        audit.observed_forward_switch,
        audit.observed_reverse_switch,
        max_up_step=audit.forward.jump_bound,
        max_down_step=audit.reverse.jump_bound,
        horizon=PARAMS["horizon_per_step"],
    )

    assert interval.forward_lower <= audit.true_forward_threshold <= interval.forward_upper
    assert interval.reverse_lower <= audit.true_reverse_threshold <= interval.reverse_upper
    assert interval.true_width_lower <= audit.true_hysteresis_width <= interval.true_width_upper

    true_cost_sum = PARAMS["cost_shared_to_diff"] + PARAMS["cost_diff_to_shared"]
    assert interval.switching_cost_sum_lower <= true_cost_sum <= interval.switching_cost_sum_upper

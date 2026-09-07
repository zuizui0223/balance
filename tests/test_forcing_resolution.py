from balance_domain.forcing_resolution import (
    downward_switch_resolution,
    hysteresis_resolution_audit,
    upward_switch_resolution,
)
from balance_domain.stepwise_hysteresis import (
    follow_switching_path,
    linear_small_step_path,
)


PARAMS = dict(
    horizon_per_step=10.0,
    cost_shared_to_diff=2.0,
    cost_diff_to_shared=1.0,
)


def _up(path):
    return follow_switching_path(path, initial_state="shared", **PARAMS)


def _down(path):
    return follow_switching_path(path, initial_state="differentiated", **PARAMS)


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

import pytest

from balance_domain.stepwise_hysteresis import (
    follow_switching_path,
    linear_small_step_path,
    max_path_jump,
    switch_points,
)


def test_small_step_constructor_respects_bound():
    path = linear_small_step_path(-1.0, 1.0, max_phi_jump=0.3)
    assert path[0] == -1.0
    assert path[-1] == 1.0
    assert max_path_jump(path) <= 0.3 + 1e-15


def test_declared_small_step_assumption_fails_closed():
    with pytest.raises(ValueError, match="violates declared max_phi_jump"):
        follow_switching_path(
            (-0.2, 0.8),
            initial_state="shared",
            horizon_per_step=1.0,
            cost_shared_to_diff=0.5,
            cost_diff_to_shared=0.5,
            max_phi_jump=0.2,
        )


def test_shared_switches_only_after_forward_threshold():
    result = follow_switching_path(
        (0.0, 0.4, 0.5, 0.6),
        initial_state="shared",
        horizon_per_step=1.0,
        cost_shared_to_diff=0.5,
        cost_diff_to_shared=0.5,
    )
    assert switch_points(result) == (0.6,)
    assert result.final_state == "differentiated"


def test_differentiated_switches_back_only_below_reverse_threshold():
    result = follow_switching_path(
        (0.2, 0.0, -0.4, -0.5, -0.6),
        initial_state="differentiated",
        horizon_per_step=1.0,
        cost_shared_to_diff=0.5,
        cost_diff_to_shared=0.5,
    )
    assert switch_points(result) == (-0.6,)
    assert result.final_state == "shared"


def test_same_phi_inside_band_retains_history():
    shared = follow_switching_path(
        (0.0,),
        initial_state="shared",
        horizon_per_step=1.0,
        cost_shared_to_diff=0.5,
        cost_diff_to_shared=0.5,
    )
    diff = follow_switching_path(
        (0.0,),
        initial_state="differentiated",
        horizon_per_step=1.0,
        cost_shared_to_diff=0.5,
        cost_diff_to_shared=0.5,
    )
    assert shared.final_state == "shared"
    assert diff.final_state == "differentiated"

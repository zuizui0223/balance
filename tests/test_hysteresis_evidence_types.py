import pytest

from balance_domain.dynamics import switching_cost_state
from balance_domain.forcing_resolution import (
    hysteresis_resolution_audit,
    upward_switch_resolution,
)
from balance_domain.hysteresis_interval import identify_hysteresis_interval
from balance_domain.stepwise_hysteresis import (
    PathStep,
    SwitchingPathResult,
    follow_switching_path,
    linear_small_step_path,
    max_path_jump,
)


def test_switching_cost_state_rejects_boolean_numeric_evidence():
    base = dict(phi=0.0, horizon=10.0, cost_shared_to_diff=1.0, cost_diff_to_shared=1.0)
    for field in base:
        malformed = dict(base)
        malformed[field] = True
        with pytest.raises(ValueError, match="boolean"):
            switching_cost_state(**malformed)


def test_stepwise_forcing_rejects_boolean_path_and_resolution_inputs():
    with pytest.raises(ValueError, match="boolean"):
        max_path_jump([0.0, True])
    with pytest.raises(ValueError, match="boolean"):
        linear_small_step_path(True, 1.0, max_phi_jump=0.1)
    with pytest.raises(ValueError, match="boolean"):
        linear_small_step_path(0.0, 1.0, max_phi_jump=True)
    with pytest.raises(ValueError, match="boolean"):
        follow_switching_path(
            [0.0, 0.2],
            initial_state="shared",
            horizon_per_step=10.0,
            cost_shared_to_diff=1.0,
            cost_diff_to_shared=1.0,
            max_phi_jump=True,
        )
    with pytest.raises(ValueError, match="boolean"):
        follow_switching_path(
            [0.0, True],
            initial_state="shared",
            horizon_per_step=10.0,
            cost_shared_to_diff=1.0,
            cost_diff_to_shared=1.0,
        )


def _valid_manual_upward() -> SwitchingPathResult:
    return SwitchingPathResult(
        initial_state="shared",
        final_state="differentiated",
        steps=(
            PathStep(0, 0.0, "shared", "shared", False, 0.1, -0.1),
            PathStep(1, 0.2, "shared", "differentiated", True, 0.1, -0.1),
        ),
        max_observed_phi_jump=0.2,
        declared_max_phi_jump=None,
    )


def test_forcing_resolution_rejects_forged_step_index_and_boolean_fields():
    valid = _valid_manual_upward()
    forged_index = SwitchingPathResult(
        initial_state=valid.initial_state,
        final_state=valid.final_state,
        steps=(valid.steps[0], PathStep(2, 0.2, "shared", "differentiated", True, 0.1, -0.1)),
        max_observed_phi_jump=0.2,
        declared_max_phi_jump=None,
    )
    with pytest.raises(ValueError, match="position"):
        upward_switch_resolution(forged_index)

    forged_bool_index = SwitchingPathResult(
        initial_state=valid.initial_state,
        final_state=valid.final_state,
        steps=(valid.steps[0], PathStep(True, 0.2, "shared", "differentiated", True, 0.1, -0.1)),
        max_observed_phi_jump=0.2,
        declared_max_phi_jump=None,
    )
    with pytest.raises(ValueError, match="integer"):
        upward_switch_resolution(forged_bool_index)

    forged_phi = SwitchingPathResult(
        initial_state=valid.initial_state,
        final_state=valid.final_state,
        steps=(valid.steps[0], PathStep(1, True, "shared", "differentiated", True, 0.1, -0.1)),
        max_observed_phi_jump=0.2,
        declared_max_phi_jump=None,
    )
    with pytest.raises(ValueError, match="boolean"):
        upward_switch_resolution(forged_phi)

    forged_threshold = SwitchingPathResult(
        initial_state=valid.initial_state,
        final_state=valid.final_state,
        steps=(valid.steps[0], PathStep(1, 0.2, "shared", "differentiated", True, True, -0.1)),
        max_observed_phi_jump=0.2,
        declared_max_phi_jump=None,
    )
    with pytest.raises(ValueError, match="boolean"):
        upward_switch_resolution(forged_threshold)


def test_inverse_hysteresis_identification_rejects_boolean_evidence():
    base = dict(
        observed_forward_switch=0.2,
        observed_reverse_switch=-0.2,
        max_up_step=0.1,
        max_down_step=0.1,
        horizon=10.0,
    )
    for field in base:
        malformed = dict(base)
        malformed[field] = True
        with pytest.raises(ValueError, match="boolean"):
            identify_hysteresis_interval(**malformed)


def test_valid_stepwise_resolution_chain_remains_unchanged_in_kind():
    upward = follow_switching_path(
        [-0.1, 0.0, 0.2],
        initial_state="shared",
        horizon_per_step=10.0,
        cost_shared_to_diff=1.0,
        cost_diff_to_shared=1.0,
    )
    downward = follow_switching_path(
        [0.2, 0.0, -0.2],
        initial_state="differentiated",
        horizon_per_step=10.0,
        cost_shared_to_diff=1.0,
        cost_diff_to_shared=1.0,
    )
    audit = hysteresis_resolution_audit(upward, downward)
    assert audit.true_forward_threshold == pytest.approx(0.1)
    assert audit.true_reverse_threshold == pytest.approx(-0.1)
    assert audit.true_hysteresis_width == pytest.approx(0.2)
    assert audit.observed_hysteresis_width == pytest.approx(0.4)
    assert audit.width_overestimate == pytest.approx(0.2)

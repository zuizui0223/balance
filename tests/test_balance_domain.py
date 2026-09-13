import math
import random

from balance_domain import analyze_balance_path, switching_cost_state


def test_monotone_path_has_single_balance_domain_and_no_reentry():
    result = analyze_balance_path(
        environment=[0, 1, 2, 3, 4],
        conflict_load=[0, 0.2, 0.5, 0.9, 1.3],
        decoupling=[0.2, 0.3, 0.4, 0.5, 0.6],
        architecture_cost=[0.45, 0.42, 0.38, 0.34, 0.30],
    )
    assert result.monotone_no_reentry_conditions_hold
    assert result.topology in {"SINGLE_BALANCE_DOMAIN", "NO_BALANCE"}
    assert len(result.balance_intervals) <= 1


def test_reentry_requires_registered_monotonicity_failure():
    result = analyze_balance_path(
        environment=[0, 1, 2, 3, 4],
        conflict_load=[0.2, 0.8, 1.1, 0.6, 0.5],
        decoupling=[0.5, 0.5, 0.5, 0.5, 0.5],
        architecture_cost=[0.4, 0.4, 0.4, 0.4, 0.4],
    )
    assert not result.monotone_no_reentry_conditions_hold
    assert result.topology == "REENTRANT_OR_MULTIPLE_BALANCE_DOMAINS"


def test_criticality_index_and_reserve_inside_balance():
    result = analyze_balance_path(
        environment=[0, 1, 2],
        conflict_load=[0.1, 0.2, 0.3],
        decoupling=[0.5, 0.5, 0.5],
        architecture_cost=[0.4, 0.4, 0.4],
    )
    assert all(state == "BALANCE" for state in result.states)
    assert all(0 < q < 1 for q in result.criticality_index if q is not None)
    assert all(r > 0 for r in result.reserve)
    assert math.isclose(result.criticality_index[1], 0.2 / (0.2 + 0.3))
    assert math.isclose(result.architecture_pressure_ratio[1], 0.1 / 0.4)
    assert math.isclose(result.balance_width, 2.0)


def test_conflict_loss_exit_uses_conflict_boundary_not_phi_extrapolation():
    result = analyze_balance_path(
        environment=[0, 1, 2],
        conflict_load=[2, 1, 0],
        decoupling=[0.5, 0.5, 0.5],
        architecture_cost=[2, 1, 1],
    )
    assert result.states == ("BALANCE", "BALANCE", "NO_CONFLICT")
    assert len(result.balance_intervals) == 1
    start, end = result.balance_intervals[0]
    assert math.isclose(start, 0.0, abs_tol=1e-9)
    assert math.isclose(end, 2.0, abs_tol=1e-9)
    assert math.isclose(result.balance_width, 2.0, abs_tol=1e-9)


def test_no_conflict_entry_interpolates_conflict_boundary():
    result = analyze_balance_path(
        environment=[0, 1, 2],
        conflict_load=[0, 1, 1],
        decoupling=[0.5, 0.5, 0.5],
        architecture_cost=[1, 1, 1],
    )
    assert result.states == ("NO_CONFLICT", "BALANCE", "BALANCE")
    start, end = result.balance_intervals[0]
    assert start < 1e-9
    assert math.isclose(end, 2.0)
    assert math.isclose(result.balance_width, 2.0, abs_tol=1e-9)


def test_integrated_reserve_is_clipped_to_balance_interval():
    result = analyze_balance_path(
        environment=[0, 1],
        conflict_load=[1, 1],
        decoupling=[1, 1],
        architecture_cost=[2, 0],
    )
    assert result.states == ("BALANCE", "DIFFERENTIATION")
    assert math.isclose(result.balance_width, 0.5, abs_tol=1e-9)
    assert math.isclose(result.integrated_reserve, 0.25, abs_tol=1e-9)


def test_balance_width_is_always_bounded_by_environment_span():
    rng = random.Random(20260913)
    environment = [0, 1, 2, 3, 4]
    span = environment[-1] - environment[0]
    for _ in range(250):
        conflict = [0.0 if rng.random() < 0.25 else rng.uniform(0.0, 2.0) for _ in environment]
        decoupling = [rng.random() for _ in environment]
        cost = [rng.uniform(0.0, 2.0) for _ in environment]
        result = analyze_balance_path(environment, conflict, decoupling, cost)
        assert -1e-12 <= result.balance_width <= span + 1e-12
        assert all(environment[0] - 1e-12 <= a <= b <= environment[-1] + 1e-12 for a, b in result.balance_intervals)


def test_switching_costs_create_history_dependent_band():
    result = switching_cost_state(
        phi=0.05,
        horizon=10,
        cost_shared_to_diff=1.0,
        cost_diff_to_shared=0.5,
    )
    assert math.isclose(result.forward_threshold, 0.1)
    assert math.isclose(result.reverse_threshold, -0.05)
    assert math.isclose(result.hysteresis_width, 0.15)
    assert result.history_dependent
    assert result.shared_stays
    assert result.differentiated_stays


def test_longer_context_shrinks_hysteresis_band():
    short = switching_cost_state(0.0, horizon=5, cost_shared_to_diff=1, cost_diff_to_shared=1)
    long = switching_cost_state(0.0, horizon=20, cost_shared_to_diff=1, cost_diff_to_shared=1)
    assert long.hysteresis_width < short.hysteresis_width

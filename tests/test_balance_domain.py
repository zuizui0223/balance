import math

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
    assert math.isclose(result.balance_width, 2.0)


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

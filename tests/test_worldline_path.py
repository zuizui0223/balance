import math

from balance_domain.worldline_path import analyze_worldline_path


def test_direct_worldline_path_maps_middle_world_without_s_k_decomposition():
    result = analyze_worldline_path(
        environment=[0, 1, 2, 3],
        shared_optimum_fitness=[10.0, 10.0, 10.0, 10.0],
        differentiated_optimum_fitness=[9.9, 9.8, 10.0, 10.2],
        conflict_load=[0.0, 0.2, 0.4, 0.5],
    )
    assert result.states == (
        "SCH_NO_CONFLICT_WORLD",
        "BALANCE_MIDDLE_WORLD",
        "ARCHITECTURE_CRITICAL_INTERFACE",
        "BITA_DIFFERENTIATION_WORLD",
    )
    assert result.critical_crossings == (2.0,)
    assert math.isclose(result.balance_intervals[0][0], 0.0, abs_tol=1e-8)
    assert math.isclose(result.balance_intervals[0][1], 2.0, abs_tol=1e-8)
    assert math.isclose(result.balance_width, 2.0, abs_tol=1e-8)


def test_multiple_middle_world_intervals_are_visible_in_direct_worldlines():
    result = analyze_worldline_path(
        environment=[0, 1, 2, 3, 4],
        shared_optimum_fitness=[10, 10, 10, 10, 10],
        differentiated_optimum_fitness=[9.8, 10.2, 9.7, 10.3, 10.4],
        conflict_load=[0.2, 0.3, 0.4, 0.5, 0.6],
    )
    assert len(result.balance_intervals) == 2
    assert len(result.critical_crossings) == 3


def test_no_conflict_positive_diff_gap_is_not_called_balance():
    result = analyze_worldline_path(
        environment=[0, 1],
        shared_optimum_fitness=[10.0, 10.0],
        differentiated_optimum_fitness=[10.1, 10.2],
        conflict_load=[0.0, 0.0],
    )
    assert all(state == "OUTSIDE_REGISTERED_SCH_CONFLICT" for state in result.states)
    assert result.balance_intervals == ()


def test_direct_worldline_conflict_loss_exit_stays_inside_path():
    result = analyze_worldline_path(
        environment=[0, 1, 2],
        shared_optimum_fitness=[10, 10, 10],
        differentiated_optimum_fitness=[9, 9.5, 9.75],
        conflict_load=[2, 1, 0],
    )
    assert result.states == (
        "BALANCE_MIDDLE_WORLD",
        "BALANCE_MIDDLE_WORLD",
        "SCH_NO_CONFLICT_WORLD",
    )
    assert math.isclose(result.balance_intervals[0][1], 2.0, abs_tol=1e-8)
    assert math.isclose(result.balance_width, 2.0, abs_tol=1e-8)


def test_direct_worldline_no_conflict_entry_uses_conflict_boundary():
    result = analyze_worldline_path(
        environment=[0, 1, 2],
        shared_optimum_fitness=[10, 10, 10],
        differentiated_optimum_fitness=[9.5, 9.5, 9.5],
        conflict_load=[0, 1, 1],
    )
    assert result.states == (
        "SCH_NO_CONFLICT_WORLD",
        "BALANCE_MIDDLE_WORLD",
        "BALANCE_MIDDLE_WORLD",
    )
    assert result.balance_intervals[0][0] < 1e-8
    assert math.isclose(result.balance_width, 2.0, abs_tol=1e-8)

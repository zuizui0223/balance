import math

import pytest

from balance_domain.worldlines import compare_worldlines


def test_direct_worldlines_identify_middle_world_and_internal_coordinates():
    result = compare_worldlines(
        shared_optimum_fitness=10.0,
        differentiated_optimum_fitness=9.8,
        conflict_load=0.4,
    )
    assert result.state == "BALANCE_MIDDLE_WORLD"
    assert math.isclose(result.direct_worldline_gap, -0.2)
    assert math.isclose(result.direct_reserve, 0.2)
    assert math.isclose(result.direct_middle_position, 2.0 / 3.0)
    assert math.isclose(result.direct_two_sided_depth, 0.2)
    assert result.decomposed_middle_position is None
    assert result.parallel_world_residual is None


def test_direct_worldline_crossing_identifies_architecture_interface():
    result = compare_worldlines(10.0, 10.0, 0.4)
    assert result.state == "ARCHITECTURE_CRITICAL_INTERFACE"
    assert result.direct_middle_position is None
    assert result.direct_two_sided_depth is None


def test_decomposed_bridge_must_match_direct_worldline_gap_and_position():
    # sL-K = 0.5*0.4-0.4 = -0.2 = W_D*-W_S*
    result = compare_worldlines(
        10.0,
        9.8,
        0.4,
        decoupling=0.5,
        architecture_cost=0.4,
    )
    assert result.bridge_consistent
    assert math.isclose(result.decomposed_gap, result.direct_worldline_gap)
    assert math.isclose(result.parallel_world_residual, 0.0, abs_tol=1e-12)
    assert math.isclose(result.decomposed_reserve, result.direct_reserve)
    assert math.isclose(result.decomposed_middle_position, result.direct_middle_position)


def test_scale_or_model_mismatch_is_exposed_as_parallel_world_residual_and_coordinate_mismatch():
    result = compare_worldlines(
        10.0,
        9.8,
        0.4,
        decoupling=0.5,
        architecture_cost=0.2,
    )
    assert result.bridge_consistent is False
    assert not math.isclose(result.decomposed_gap, result.direct_worldline_gap)
    assert math.isclose(result.parallel_world_residual, -0.2)
    assert result.direct_middle_position is not None
    assert result.decomposed_middle_position is None  # decomposed gap is at the critical boundary here


def test_differentiation_without_registered_sch_conflict_is_outside_bridge():
    result = compare_worldlines(10.0, 10.2, 0.0)
    assert result.state == "OUTSIDE_REGISTERED_SCH_CONFLICT"
    assert result.direct_reserve is None


def test_partial_decomposition_input_fails_closed():
    with pytest.raises(ValueError):
        compare_worldlines(10.0, 9.8, 0.4, decoupling=0.5)


def test_nonfinite_inputs_fail_closed():
    with pytest.raises(ValueError):
        compare_worldlines(float("nan"), 9.8, 0.4)

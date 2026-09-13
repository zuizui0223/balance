import math

import pytest

from balance_domain.depth_path import deepest_middle_point


def test_piecewise_linear_equal_margin_point_has_xi_half_and_max_depth():
    e = [0.0, 1.0, 2.0, 3.0]
    L = [0.1, 0.4, 0.8, 1.2]
    rho = [1.0, 0.7, 0.5, 0.2]
    point = deepest_middle_point(e, L, rho)
    assert 1.0 < point.environment < 2.0
    assert abs(point.conflict_load - point.reserve) < 1e-12
    assert abs(point.xi - 0.5) < 1e-12

    sampled_depths = [min(l, r) for l, r in zip(L, rho)]
    assert point.depth >= max(sampled_depths)


def test_common_positive_fitness_rescaling_preserves_location_and_xi():
    e = [0.0, 1.0, 2.0, 3.0]
    L = [0.1, 0.4, 0.8, 1.2]
    rho = [1.0, 0.7, 0.5, 0.2]
    first = deepest_middle_point(e, L, rho)
    for scale in (1e-16, 17.0, 1e16):
        second = deepest_middle_point(
            e,
            [scale * x for x in L],
            [scale * x for x in rho],
        )
        assert math.isclose(first.environment, second.environment, rel_tol=1e-14, abs_tol=1e-14)
        assert math.isclose(first.xi, second.xi, rel_tol=1e-14, abs_tol=1e-14)
        assert math.isclose(second.depth, scale * first.depth, rel_tol=1e-14, abs_tol=0.0)


def test_small_units_do_not_turn_crossing_endpoints_into_exact_equalities():
    point = deepest_middle_point(
        [0.0, 1.0],
        [1e-13, 2e-13],
        [2e-13, 1e-13],
    )
    assert math.isclose(point.environment, 0.5, abs_tol=1e-15)
    assert point.interpolation_interval == (0, 1)
    assert math.isclose(point.xi, 0.5, abs_tol=1e-15)
    assert math.isclose(point.depth, 1.5e-13, rel_tol=1e-14)


def test_large_finite_crossing_does_not_overflow_fraction_or_interpolation():
    point = deepest_middle_point(
        [-1e308, 1e308],
        [0.0, 1e308],
        [1e308, 0.0],
    )
    assert math.isfinite(point.environment)
    assert point.environment == 0.0
    assert point.interpolation_interval == (0, 1)
    assert point.xi == 0.5
    assert point.depth == 5e307


def test_exact_equal_margin_sample_is_used_directly():
    point = deepest_middle_point(
        [0.0, 1.0, 2.0],
        [0.1, 0.5, 0.9],
        [0.9, 0.5, 0.1],
    )
    assert point.environment == 1.0
    assert point.interpolation_interval == (1, 1)
    assert point.xi == 0.5


def test_nonmonotone_path_fails_closed_for_this_theorem():
    with pytest.raises(ValueError, match="non-decreasing"):
        deepest_middle_point(
            [0.0, 1.0, 2.0],
            [0.1, 0.5, 0.4],
            [0.9, 0.5, 0.1],
        )


def test_no_observed_equal_margin_crossing_does_not_extrapolate():
    with pytest.raises(ValueError, match="does not identify one interior"):
        deepest_middle_point(
            [0.0, 1.0, 2.0],
            [0.1, 0.2, 0.3],
            [1.0, 0.8, 0.6],
        )

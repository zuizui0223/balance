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
    scale = 17.0
    second = deepest_middle_point(e, [scale * x for x in L], [scale * x for x in rho])
    assert abs(first.environment - second.environment) < 1e-12
    assert abs(first.xi - second.xi) < 1e-12
    assert abs(second.depth - scale * first.depth) < 1e-10


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

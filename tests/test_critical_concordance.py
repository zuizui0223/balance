import math

import pytest

from balance_domain.concordance import compare_critical_paths


def test_same_critical_point_from_direct_and_decomposed_views():
    result = compare_critical_paths(
        environment=[0, 1, 2],
        direct_worldline_gap=[-1, 0, 1],
        decomposed_gap=[-0.5, 0, 0.5],
    )
    assert result.status == "SAME_CRITICAL_POINT"
    assert result.direct_crossings == (1.0,)
    assert result.decomposed_crossings == (1.0,)
    assert math.isclose(result.critical_point_difference, 0.0)


def test_shifted_crossings_are_called_parallel_critical_points():
    result = compare_critical_paths(
        environment=[0, 1, 2],
        direct_worldline_gap=[-1.0, -0.2, 1.0],
        decomposed_gap=[-1.0, 0.5, 1.0],
        critical_point_tolerance=0.05,
    )
    assert result.status == "PARALLEL_CRITICAL_POINTS"
    assert len(result.direct_crossings) == 1
    assert len(result.decomposed_crossings) == 1
    assert abs(result.critical_point_difference) > 0.05


def test_multiple_crossings_fail_closed_for_single_critical_point_claim():
    result = compare_critical_paths(
        environment=[0, 1, 2, 3, 4],
        direct_worldline_gap=[-1, 1, -1, 1, 2],
        decomposed_gap=[-1, 1, 2, 3, 4],
    )
    assert result.status == "MULTIPLE_OR_UNMATCHED_CRITICAL_POINTS"
    assert len(result.direct_crossings) > 1


def test_no_crossing_is_not_forced_into_a_critical_point():
    result = compare_critical_paths(
        environment=[0, 1, 2],
        direct_worldline_gap=[-1, -0.8, -0.2],
        decomposed_gap=[-0.9, -0.7, -0.1],
    )
    assert result.status == "NO_CRITICAL_CROSSING"
    assert result.critical_point_difference is None


def test_extreme_finite_gap_magnitudes_recover_midpoint_crossing():
    result = compare_critical_paths(
        environment=[0.0, 10.0],
        direct_worldline_gap=[-1.0e308, 1.0e308],
        decomposed_gap=[-5.0e307, 5.0e307],
    )
    assert result.status == "SAME_CRITICAL_POINT"
    assert result.direct_crossings == pytest.approx((5.0,))
    assert result.decomposed_crossings == pytest.approx((5.0,))


def test_gap_value_tolerance_does_not_merge_distinct_environmental_zero_nodes():
    result = compare_critical_paths(
        environment=[0.0, 1.0e-12, 2.0e-12],
        direct_worldline_gap=[0.0, 0.0, 1.0],
        decomposed_gap=[0.0, 1.0, 1.0],
        value_tolerance=1.0e-9,
        critical_point_tolerance=1.0e-15,
    )
    assert result.direct_crossings == (0.0, 1.0e-12)
    assert result.decomposed_crossings == (0.0,)
    assert result.status == "MULTIPLE_OR_UNMATCHED_CRITICAL_POINTS"


def test_unrepresentable_critical_point_difference_fails_closed():
    with pytest.raises(ValueError, match="difference overflowed"):
        compare_critical_paths(
            environment=[-1.0e308, 0.0, 1.0e308],
            direct_worldline_gap=[-1.0, 9.0, 9.0],
            decomposed_gap=[-9.0, -9.0, 1.0],
        )

import math

import pytest

from balance_domain.width_depth import constant_slope_depth, width_depth_bounds


def test_constant_slope_solution_matches_exact_geometry():
    width = 3.0
    left = 2.0
    right = 1.0
    depth = constant_slope_depth(width=width, left_slope=left, right_slope=right)
    assert math.isclose(depth, 2.0)

    left_width = depth / left
    right_width = depth / right
    assert math.isclose(left_width + right_width, width)
    assert math.isclose(left_width / right_width, right / left)


def test_width_and_depth_brackets_are_dual():
    result = width_depth_bounds(
        depth=1.5,
        width=3.0,
        left_slope_min=0.8,
        left_slope_max=1.2,
        right_slope_min=0.5,
        right_slope_max=1.0,
    )
    assert result.width_lower <= 3.0 <= result.width_upper
    assert result.depth_lower_from_width <= 1.5 <= result.depth_upper_from_width


def test_large_slopes_do_not_overflow_constant_slope_formula():
    result = constant_slope_depth(
        width=1.0,
        left_slope=1.0e308,
        right_slope=1.0e308,
    )
    assert result == pytest.approx(5.0e307)


def test_large_reciprocal_sum_keeps_finite_depth_bound():
    result = width_depth_bounds(
        depth=1.0e-308,
        width=1.0e308,
        left_slope_min=1.0e-308,
        left_slope_max=1.0,
        right_slope_min=1.0e-308,
        right_slope_max=1.0,
    )
    # Direct float arithmetic forms 1e308 + 1e308 = inf and used to collapse
    # this lower bound to zero.  The exact value is 1/2.
    assert result.depth_lower_from_width == pytest.approx(0.5)
    assert result.depth_upper_from_width == pytest.approx(5.0e307)
    assert result.width_upper == pytest.approx(2.0)


def test_unrepresentable_positive_width_depth_output_fails_closed():
    with pytest.raises(ValueError, match="must remain finite"):
        constant_slope_depth(
            width=1.0e308,
            left_slope=1.0e308,
            right_slope=1.0e308,
        )

    with pytest.raises(ValueError, match="must remain finite"):
        width_depth_bounds(
            depth=1.0e308,
            width=1.0,
            left_slope_min=1.0e-308,
            left_slope_max=1.0e-308,
            right_slope_min=1.0e-308,
            right_slope_max=1.0e-308,
        )


def test_invalid_bounds_fail_closed():
    bad = [
        dict(depth=1, width=2, left_slope_min=2, left_slope_max=1, right_slope_min=1, right_slope_max=2),
        dict(depth=1, width=2, left_slope_min=1, left_slope_max=2, right_slope_min=0, right_slope_max=2),
    ]
    for kwargs in bad:
        with pytest.raises(ValueError):
            width_depth_bounds(**kwargs)

import math

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


def test_invalid_bounds_fail_closed():
    bad = [
        dict(depth=1, width=2, left_slope_min=2, left_slope_max=1, right_slope_min=1, right_slope_max=2),
        dict(depth=1, width=2, left_slope_min=1, left_slope_max=2, right_slope_min=0, right_slope_max=2),
    ]
    for kwargs in bad:
        try:
            width_depth_bounds(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid width-depth bounds should fail")

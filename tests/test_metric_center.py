import math

from balance_domain.metric_center import constant_slope_centers, metric_middle_coordinate


def test_metric_middle_coordinate_is_half_at_equal_metric_depth():
    assert math.isclose(metric_middle_coordinate(3.0, 3.0), 0.5, abs_tol=1e-12)


def test_constant_slope_environmental_center_is_geometric_midpoint():
    result = constant_slope_centers(
        left_boundary=0.0,
        right_boundary=10.0,
        left_margin_slope=1.0,
        right_margin_slope=3.0,
    )
    assert math.isclose(result.environmental_center, 5.0, abs_tol=1e-12)
    assert math.isclose(result.fitness_center, 7.5, abs_tol=1e-12)
    assert math.isclose(result.displacement, 2.5, abs_tol=1e-12)


def test_equal_slopes_make_fitness_and_environmental_centers_coincide():
    result = constant_slope_centers(2.0, 8.0, 4.0, 4.0)
    assert math.isclose(result.environmental_center, 5.0, abs_tol=1e-12)
    assert math.isclose(result.fitness_center, 5.0, abs_tol=1e-12)
    assert math.isclose(result.displacement, 0.0, abs_tol=1e-12)

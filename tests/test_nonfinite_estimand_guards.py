import math

import pytest

from balance_domain import (
    analyze_balance_path,
    analyze_worldline_path,
    boundary_sensitivity,
    compare_critical_paths,
    constant_slope_centers,
    constant_slope_depth,
    deepest_middle_point,
    deepest_point_sensitivity,
    diagonal_metric_boundary_depth,
    environmental_depth,
    metric_middle_coordinate,
    width_depth_bounds,
)
from balance_domain.covering_certificate import (
    certified_balance_ball_radius,
    lipschitz_covering_certificate,
    lipschitz_lower_envelope,
    lipschitz_zero_bracket,
    maximum_covering_radius_for_target_depth,
)


def test_static_and_worldline_paths_reject_nonfinite_values():
    with pytest.raises(ValueError):
        analyze_balance_path([0, 1, math.inf], [0.1, 0.2, 0.3], [0.5] * 3, [1.0] * 3)
    with pytest.raises(ValueError):
        analyze_balance_path([0, 1, 2], [0.1, math.nan, 0.3], [0.5] * 3, [1.0] * 3)
    with pytest.raises(ValueError):
        analyze_worldline_path([0, 1], [1.0, 1.0], [0.9, math.nan], [0.1, 0.2])
    with pytest.raises(ValueError):
        analyze_worldline_path([0, 1], [1.0, 1.0], [0.9, 0.8], [0.1, 0.2], tolerance=math.inf)


def test_deepest_path_rejects_nonfinite_values():
    with pytest.raises(ValueError):
        deepest_middle_point([0, 1, 2], [0.1, math.nan, 0.9], [0.9, 0.5, 0.1])
    with pytest.raises(ValueError):
        deepest_middle_point([0, 1, math.inf], [0.1, 0.5, 0.9], [0.9, 0.5, 0.1])


def test_environmental_and_metric_depth_reject_nonfinite_values():
    with pytest.raises(ValueError):
        environmental_depth(
            conflict_margin=math.nan,
            reserve_margin=1.0,
            conflict_gradient=[1.0],
            reserve_gradient=[1.0],
        )
    with pytest.raises(ValueError):
        environmental_depth(
            conflict_margin=1.0,
            reserve_margin=1.0,
            conflict_gradient=[math.inf],
            reserve_gradient=[1.0],
        )
    with pytest.raises(ValueError):
        diagonal_metric_boundary_depth(1.0, [math.nan], [1.0])
    with pytest.raises(ValueError):
        diagonal_metric_boundary_depth(1.0, [1.0], [math.inf])


def test_center_and_width_depth_reject_nonfinite_values():
    with pytest.raises(ValueError):
        metric_middle_coordinate(math.nan, 1.0)
    with pytest.raises(ValueError):
        constant_slope_centers(0.0, 1.0, math.inf, 1.0)
    with pytest.raises(ValueError):
        width_depth_bounds(
            depth=1.0,
            width=math.nan,
            left_slope_min=1.0,
            left_slope_max=2.0,
            right_slope_min=1.0,
            right_slope_max=2.0,
        )
    with pytest.raises(ValueError):
        constant_slope_depth(width=1.0, left_slope=1.0, right_slope=math.inf)


def test_sensitivity_and_concordance_reject_nonfinite_values():
    with pytest.raises(ValueError):
        boundary_sensitivity(a0=math.nan, L_prime0=1.0, b2=1.0, rho_prime2=-1.0)
    with pytest.raises(ValueError):
        deepest_point_sensitivity(a=1.0, b=1.0, L_prime=math.inf, rho_prime=-1.0)
    with pytest.raises(ValueError):
        compare_critical_paths([0, 1], [-1.0, math.nan], [-1.0, 1.0])
    with pytest.raises(ValueError):
        compare_critical_paths([0, 1], [-1.0, 1.0], [-1.0, 1.0], value_tolerance=math.inf)


def test_covering_certificates_reject_nonfinite_values_and_negative_tolerance():
    with pytest.raises(ValueError):
        lipschitz_covering_certificate(
            sampled_min_margins=[0.2, math.nan],
            lipschitz_constants=[0.1, 0.1],
            covering_radius=0.5,
        )
    with pytest.raises(ValueError):
        maximum_covering_radius_for_target_depth(
            sampled_min_margins=[0.2],
            lipschitz_constants=[0.1],
            target_depth=math.inf,
        )
    with pytest.raises(ValueError):
        lipschitz_lower_envelope(
            sampled_values=[0.2],
            distances_to_query=[math.inf],
            lipschitz_constant=0.1,
        )
    with pytest.raises(ValueError):
        certified_balance_ball_radius(margins=[math.nan], lipschitz_constants=[0.1])
    with pytest.raises(ValueError):
        lipschitz_zero_bracket(
            positive_margin=0.2,
            negative_margin=-0.2,
            path_length=1.0,
            lipschitz_constant=1.0,
            tolerance=-1e-6,
        )

import pytest

from balance_domain.accessibility_scope import accessibility_scope_bounds
from balance_domain.environmental_depth import environmental_depth
from balance_domain.metric_center import constant_slope_centers, metric_middle_coordinate
from balance_domain.metric_depth import diagonal_metric_boundary_depth
from balance_domain.sensitivity import boundary_sensitivity, deepest_point_sensitivity
from balance_domain.width_depth import constant_slope_depth, width_depth_bounds


def test_sensitivity_diagnostics_reject_boolean_evidence():
    with pytest.raises(ValueError, match="boolean"):
        boundary_sensitivity(a0=True, L_prime0=1.0, b2=1.0, rho_prime2=-1.0)
    with pytest.raises(ValueError, match="boolean"):
        deepest_point_sensitivity(a=1.0, b=0.0, L_prime=True, rho_prime=-1.0)


def test_nonzero_exact_sensitivity_cannot_underflow_to_zero():
    with pytest.raises(ValueError, match="underflowed to zero"):
        boundary_sensitivity(
            a0=5e-324,
            L_prime0=1e308,
            b2=0.0,
            rho_prime2=1.0,
        )


def test_environmental_depth_rejects_boolean_evidence():
    with pytest.raises(ValueError, match="boolean"):
        environmental_depth(
            conflict_margin=True,
            reserve_margin=1.0,
            conflict_gradient=[1.0],
            reserve_gradient=[1.0],
        )
    with pytest.raises(ValueError, match="boolean"):
        environmental_depth(
            conflict_margin=1.0,
            reserve_margin=1.0,
            conflict_gradient=[True],
            reserve_gradient=[1.0],
        )


def test_environmental_middle_coordinate_cannot_collapse_to_boundary():
    with pytest.raises(ValueError, match="strictly inside"):
        environmental_depth(
            conflict_margin=5e-324,
            reserve_margin=1e308,
            conflict_gradient=[1.0],
            reserve_gradient=[1.0],
        )


def test_metric_depth_rejects_boolean_evidence():
    with pytest.raises(ValueError, match="boolean"):
        diagonal_metric_boundary_depth(True, [1.0], [1.0])
    with pytest.raises(ValueError, match="boolean"):
        diagonal_metric_boundary_depth(1.0, [True], [1.0])
    with pytest.raises(ValueError, match="boolean"):
        diagonal_metric_boundary_depth(1.0, [1.0], [True])


def test_metric_center_rejects_boolean_evidence_and_boundary_rounding():
    with pytest.raises(ValueError, match="boolean"):
        metric_middle_coordinate(True, 1.0)
    with pytest.raises(ValueError, match="strictly inside"):
        metric_middle_coordinate(1e308, 5e-324)
    with pytest.raises(ValueError, match="boolean"):
        constant_slope_centers(0.0, 1.0, True, 1.0)


def test_constant_slope_center_rescues_representable_extreme_weighted_center():
    result = constant_slope_centers(
        left_boundary=0.0,
        right_boundary=1e308,
        left_margin_slope=1e308,
        right_margin_slope=5e-324,
    )
    assert result.fitness_center == 5e-324
    assert result.environmental_center == pytest.approx(5e307)
    assert result.displacement == pytest.approx(-5e307)


def test_width_depth_diagnostics_reject_boolean_evidence():
    with pytest.raises(ValueError, match="boolean"):
        width_depth_bounds(
            depth=True,
            width=1.0,
            left_slope_min=1.0,
            left_slope_max=2.0,
            right_slope_min=1.0,
            right_slope_max=2.0,
        )
    with pytest.raises(ValueError, match="boolean"):
        constant_slope_depth(width=1.0, left_slope=True, right_slope=1.0)


def test_accessibility_scope_rejects_boolean_evidence():
    with pytest.raises(ValueError, match="boolean"):
        accessibility_scope_bounds(
            conflict_load=True,
            reserve_definite=1.0,
            reserve_possible=0.5,
        )
    with pytest.raises(ValueError, match="boolean"):
        accessibility_scope_bounds(
            conflict_load=1.0,
            reserve_definite=True,
            reserve_possible=0.5,
        )

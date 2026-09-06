import math

from balance_domain.metric_depth import (
    diagonal_metric_boundary_depth,
    metric_middle_world_depth,
)


def test_euclidean_metric_reduces_to_margin_over_gradient_norm():
    result = diagonal_metric_boundary_depth(6.0, (3.0, 4.0), (1.0, 1.0))
    assert math.isclose(result.depth, 6.0 / 5.0, rel_tol=1e-12)
    # Linearized boundary is reached exactly.
    assert math.isclose(6.0 + 3.0 * result.displacement[0] + 4.0 * result.displacement[1], 0.0, abs_tol=1e-12)


def test_consistent_unit_rescaling_preserves_metric_depth():
    # Original coordinate e has gradient 2 and metric Q=1.
    original = diagonal_metric_boundary_depth(4.0, (2.0,), (1.0,))

    # Reparameterize y = 100 e. Then grad_y = grad_e / 100 and
    # Q_y = Q_e / 100^2 so the physical perturbation norm is unchanged.
    rescaled = diagonal_metric_boundary_depth(4.0, (0.02,), (0.0001,))
    assert math.isclose(original.depth, rescaled.depth, rel_tol=1e-12)


def test_middle_world_depth_uses_nearest_metric_boundary():
    sch, bita, depth, nearest = metric_middle_world_depth(
        conflict_margin=2.0,
        conflict_gradient=(1.0, 0.0),
        architecture_margin=3.0,
        architecture_gradient=(0.0, 1.0),
        metric_diag=(1.0, 4.0),
    )
    assert math.isclose(sch.depth, 2.0, rel_tol=1e-12)
    assert math.isclose(bita.depth, 6.0, rel_tol=1e-12)
    assert math.isclose(depth, 2.0, rel_tol=1e-12)
    assert nearest == "SCH_BOUNDARY"

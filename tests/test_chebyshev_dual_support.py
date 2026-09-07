import pytest


def test_one_dimensional_interval_center_has_two_boundary_dual_support():
    # Constraints: e >= t and 2-e >= t.
    # Primal center: e*=1, t*=1.
    # Dual: mu1=mu2=1/2, with a=(1,-1), s=(1,1), b=(0,2).
    mu1 = mu2 = 0.5
    assert mu1 * 1.0 + mu2 * (-1.0) == pytest.approx(0.0)
    assert mu1 * 1.0 + mu2 * 1.0 == pytest.approx(1.0)
    dual_value = mu1 * 0.0 + mu2 * 2.0
    assert dual_value == pytest.approx(1.0)


def test_p2_triangle_needs_three_symmetric_shadow_weights():
    # Three unit-normalized boundaries at 120-degree angles balance at the center.
    # This is the p+1=3 tight support pattern.
    import math

    normals = [
        (1.0, 0.0),
        (-0.5, math.sqrt(3.0) / 2.0),
        (-0.5, -math.sqrt(3.0) / 2.0),
    ]
    mu = [1.0 / 3.0] * 3
    sx = sum(w * a[0] for w, a in zip(mu, normals))
    sy = sum(w * a[1] for w, a in zip(mu, normals))
    assert sx == pytest.approx(0.0)
    assert sy == pytest.approx(0.0)
    assert sum(mu) == pytest.approx(1.0)


def test_zero_dual_weight_means_boundary_does_not_affect_local_depth():
    # d t*/d b_k = mu_k under a fixed LP basis.
    mu = [0.5, 0.5, 0.0]
    intercept_shift = [0.1, -0.2, 99.0]
    first_order_depth_shift = sum(m * db for m, db in zip(mu, intercept_shift))
    assert first_order_depth_shift == pytest.approx(-0.05)

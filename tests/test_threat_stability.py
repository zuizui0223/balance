import math

import pytest

from balance_domain.threat_stability import (
    diagonal_affine_gradient_from_minimum_switch,
    diagonal_affine_threat_distance,
    lipschitz_threat_radius,
    threat_fragility_index,
)


def test_lipschitz_radius_uses_nearest_possible_overtake():
    result = lipschitz_threat_radius(
        gaps=[0.6, 0.3],
        pairwise_lipschitz=[0.2, 0.3],
    )
    assert result.radius == pytest.approx(1.0)
    assert result.limiting_competitor == 1


def test_constant_pairwise_difference_never_switches():
    result = lipschitz_threat_radius(
        gaps=[0.5],
        pairwise_lipschitz=[0.0],
    )
    assert math.isinf(result.radius)


def test_nonzero_lipschitz_overflow_cannot_masquerade_as_structural_infinity():
    with pytest.raises(ValueError, match="limiting threat radius must remain finite"):
        lipschitz_threat_radius(
            gaps=[1.0e308],
            pairwise_lipschitz=[5e-324],
        )


def test_nonlimiting_huge_finite_radius_does_not_block_finite_certificate():
    result = lipschitz_threat_radius(
        gaps=[1.0e308, 1.0],
        pairwise_lipschitz=[5e-324, 1.0],
    )
    assert result.radius == pytest.approx(1.0)
    assert result.limiting_competitor == 1


def test_affine_metric_distance_matches_rescaled_geometry():
    # gap=2, gradient difference=(2,0), Q=diag(4,1):
    # sqrt(a^T Q^-1 a)=sqrt(4/4)=1, so distance=2.
    distance = diagonal_affine_threat_distance(
        gap=2.0,
        gradient_difference=[2.0, 0.0],
        metric_diag=[4.0, 1.0],
    )
    assert distance == pytest.approx(2.0)


def test_affine_metric_distance_survives_unrepresentable_dual_norm():
    distance = diagonal_affine_threat_distance(
        gap=1.0e308,
        gradient_difference=[1.0e308],
        metric_diag=[1.0e-308],
    )
    assert distance == pytest.approx(1.0e-154)


def test_nearest_switch_vector_recovers_affine_gradient_difference():
    # For a=(2,0), gap=2 and Q=diag(4,1), the Q-shortest move to the
    # tie hyperplane is delta=(-1,0). The inverse formula should recover a.
    recovered = diagonal_affine_gradient_from_minimum_switch(
        gap=2.0,
        switch_vector=[-1.0, 0.0],
        metric_diag=[4.0, 1.0],
    )
    assert recovered == pytest.approx((2.0, 0.0))
    distance = diagonal_affine_threat_distance(
        gap=2.0,
        gradient_difference=recovered,
        metric_diag=[4.0, 1.0],
    )
    assert distance == pytest.approx(2.0)


def test_inverse_gradient_recovery_survives_unrepresentable_intermediates():
    # q*d^2 and gap*q*d are far outside float range, while their ratio is not.
    recovered = diagonal_affine_gradient_from_minimum_switch(
        gap=1.0e308,
        switch_vector=[-1.0e100],
        metric_diag=[1.0e308],
    )
    assert recovered == pytest.approx((1.0e208,))


def test_fragility_index_distinguishes_identity_from_state_robustness():
    assert threat_fragility_index(threat_radius=0.4, state_depth=1.0) == pytest.approx(0.4)
    assert threat_fragility_index(threat_radius=2.0, state_depth=1.0) == pytest.approx(2.0)


def test_infinite_threat_radius_remains_meaningful_in_fragility_index():
    result = threat_fragility_index(threat_radius=math.inf, state_depth=1.0)
    assert math.isinf(result)


def test_finite_fragility_overflow_and_underflow_fail_closed():
    with pytest.raises(ValueError, match="threat fragility index"):
        threat_fragility_index(threat_radius=1.0e308, state_depth=5e-324)
    with pytest.raises(ValueError, match="threat fragility index"):
        threat_fragility_index(threat_radius=5e-324, state_depth=1.0e308)


def test_invalid_nonunique_threat_fails_closed():
    with pytest.raises(ValueError):
        lipschitz_threat_radius(gaps=[0.0], pairwise_lipschitz=[1.0])


def test_inverse_gradient_recovery_requires_nonzero_switch():
    with pytest.raises(ValueError):
        diagonal_affine_gradient_from_minimum_switch(
            gap=1.0,
            switch_vector=[0.0, 0.0],
            metric_diag=[1.0, 1.0],
        )


def test_threat_geometry_rejects_nonfinite_observations_but_not_structural_infinity():
    with pytest.raises(ValueError):
        lipschitz_threat_radius(gaps=[math.nan], pairwise_lipschitz=[1.0])
    with pytest.raises(ValueError):
        diagonal_affine_threat_distance(
            gap=1.0,
            gradient_difference=[math.inf],
            metric_diag=[1.0],
        )
    with pytest.raises(ValueError):
        diagonal_affine_gradient_from_minimum_switch(
            gap=1.0,
            switch_vector=[math.nan],
            metric_diag=[1.0],
        )
    with pytest.raises(ValueError):
        threat_fragility_index(threat_radius=math.nan, state_depth=1.0)

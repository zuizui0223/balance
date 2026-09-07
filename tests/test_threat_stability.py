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


def test_affine_metric_distance_matches_rescaled_geometry():
    # gap=2, gradient difference=(2,0), Q=diag(4,1):
    # sqrt(a^T Q^-1 a)=sqrt(4/4)=1, so distance=2.
    distance = diagonal_affine_threat_distance(
        gap=2.0,
        gradient_difference=[2.0, 0.0],
        metric_diag=[4.0, 1.0],
    )
    assert distance == pytest.approx(2.0)


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


def test_fragility_index_distinguishes_identity_from_state_robustness():
    assert threat_fragility_index(threat_radius=0.4, state_depth=1.0) == pytest.approx(0.4)
    assert threat_fragility_index(threat_radius=2.0, state_depth=1.0) == pytest.approx(2.0)


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

import math

import pytest

from balance_domain.threat_stability import (
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


def test_fragility_index_distinguishes_identity_from_state_robustness():
    assert threat_fragility_index(threat_radius=0.4, state_depth=1.0) == pytest.approx(0.4)
    assert threat_fragility_index(threat_radius=2.0, state_depth=1.0) == pytest.approx(2.0)


def test_invalid_nonunique_threat_fails_closed():
    with pytest.raises(ValueError):
        lipschitz_threat_radius(gaps=[0.0], pairwise_lipschitz=[1.0])

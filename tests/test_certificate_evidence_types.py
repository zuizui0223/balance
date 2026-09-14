import math

import pytest

from balance_domain.affine_envelope import (
    affine_upper_envelope_segments,
    alternative_reserve,
    endpoint_reserve_certificate,
)
from balance_domain.covering_certificate import (
    certified_balance_ball_radius,
    lipschitz_covering_certificate,
    lipschitz_zero_bracket,
)
from balance_domain.threat_stability import (
    diagonal_affine_gradient_from_minimum_switch,
    diagonal_affine_threat_distance,
    lipschitz_threat_radius,
    threat_fragility_index,
)


def test_threat_certificates_reject_boolean_evidence():
    with pytest.raises(ValueError, match="boolean"):
        lipschitz_threat_radius([True], [1.0])
    with pytest.raises(ValueError, match="boolean"):
        lipschitz_threat_radius([1.0], [True])
    with pytest.raises(ValueError, match="boolean"):
        diagonal_affine_threat_distance(gap=True, gradient_difference=[1.0], metric_diag=[1.0])
    with pytest.raises(ValueError, match="boolean"):
        diagonal_affine_gradient_from_minimum_switch(
            gap=1.0,
            switch_vector=[True],
            metric_diag=[1.0],
        )
    with pytest.raises(ValueError, match="boolean"):
        threat_fragility_index(threat_radius=True, state_depth=1.0)


def test_structural_infinite_threat_radius_remains_distinct_from_invalid_input():
    result = lipschitz_threat_radius([1.0], [0.0])
    assert math.isinf(result.radius) and result.radius > 0
    assert math.isinf(threat_fragility_index(threat_radius=result.radius, state_depth=1.0))


def test_affine_envelope_certificates_reject_boolean_evidence():
    with pytest.raises(ValueError, match="boolean"):
        affine_upper_envelope_segments([True, 1.0], [0.0, 0.0], start=0.0, end=1.0)
    with pytest.raises(ValueError, match="boolean"):
        alternative_reserve(
            environment=True,
            shared_slope=1.0,
            shared_intercept=1.0,
            alternative_slopes=[0.0],
            alternative_intercepts=[0.0],
        )
    with pytest.raises(ValueError, match="boolean"):
        endpoint_reserve_certificate(
            start=0.0,
            end=1.0,
            shared_slope=1.0,
            shared_intercept=1.0,
            alternative_slopes=[0.0],
            alternative_intercepts=[0.0],
            strict_tolerance=True,
        )


def test_covering_certificates_reject_boolean_evidence():
    with pytest.raises(ValueError, match="boolean"):
        lipschitz_covering_certificate(
            sampled_min_margins=[True],
            lipschitz_constants=[1.0],
            covering_radius=0.1,
        )
    with pytest.raises(ValueError, match="boolean"):
        lipschitz_covering_certificate(
            sampled_min_margins=[1.0],
            lipschitz_constants=[1.0],
            covering_radius=True,
        )
    with pytest.raises(ValueError, match="boolean"):
        lipschitz_zero_bracket(
            positive_margin=1.0,
            negative_margin=-1.0,
            path_length=2.0,
            lipschitz_constant=1.0,
            tolerance=True,
        )


def test_zero_lipschitz_covering_radius_retains_structural_infinity():
    radius = certified_balance_ball_radius(margins=[1.0], lipschitz_constants=[0.0])
    assert math.isinf(radius) and radius > 0

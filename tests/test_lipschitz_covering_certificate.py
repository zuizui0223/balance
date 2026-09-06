import math

import pytest

from balance_domain.covering_certificate import (
    lipschitz_covering_certificate,
    maximum_covering_radius_for_target_depth,
)


def test_whole_domain_balance_is_certified_when_all_lower_bounds_stay_positive():
    result = lipschitz_covering_certificate(
        sampled_min_margins=(0.30, 0.22, 0.18),
        lipschitz_constants=(0.5, 0.4, 0.2),
        covering_radius=0.20,
    )
    assert result.boundary_lower_bounds == pytest.approx((0.20, 0.14, 0.14))
    assert result.certified_global_depth == pytest.approx(0.14)
    assert result.whole_domain_balance_certified


def test_positive_sample_grid_can_remain_continuously_unresolved():
    result = lipschitz_covering_certificate(
        sampled_min_margins=(0.05, 0.08),
        lipschitz_constants=(1.0, 0.5),
        covering_radius=0.10,
    )
    assert result.certified_global_depth == pytest.approx(-0.05)
    assert not result.whole_domain_balance_certified


def test_required_covering_radius_for_target_depth():
    h = maximum_covering_radius_for_target_depth(
        sampled_min_margins=(0.30, 0.20),
        lipschitz_constants=(0.5, 0.25),
        target_depth=0.10,
    )
    assert h == pytest.approx(0.4)


def test_constant_boundaries_allow_infinite_radius_when_target_already_met():
    h = maximum_covering_radius_for_target_depth(
        sampled_min_margins=(0.3, 0.4),
        lipschitz_constants=(0.0, 0.0),
        target_depth=0.2,
    )
    assert math.isinf(h)


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        lipschitz_covering_certificate(
            sampled_min_margins=(0.2,),
            lipschitz_constants=(-1.0,),
            covering_radius=0.1,
        )
    with pytest.raises(ValueError):
        lipschitz_covering_certificate(
            sampled_min_margins=(0.2, 0.3),
            lipschitz_constants=(0.2,),
            covering_radius=0.1,
        )

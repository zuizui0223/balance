import math

import pytest

from balance_domain.covering_certificate import (
    certified_balance_ball_radius,
    certified_outside_ball_radius,
    lipschitz_covering_certificate,
    lipschitz_lower_envelope,
    lipschitz_zero_bracket,
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


def test_large_product_with_finite_lower_bound_is_recovered_exactly():
    result = lipschitz_covering_certificate(
        sampled_min_margins=(1.0e308,),
        lipschitz_constants=(1.0e308,),
        covering_radius=2.0,
    )
    assert result.boundary_lower_bounds == pytest.approx((-1.0e308,))
    assert result.certified_global_depth == pytest.approx(-1.0e308)
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


def test_nonzero_lipschitz_radius_overflow_does_not_become_structural_infinity():
    with pytest.raises(ValueError, match="maximum covering radius must remain finite"):
        maximum_covering_radius_for_target_depth(
            sampled_min_margins=(1.0e308,),
            lipschitz_constants=(5e-324,),
            target_depth=0.0,
        )
    with pytest.raises(ValueError, match="certified BALANCE ball radius must remain finite"):
        certified_balance_ball_radius(
            margins=(1.0e308,),
            lipschitz_constants=(5e-324,),
        )
    with pytest.raises(ValueError, match="certified outside-ball radius must remain finite"):
        certified_outside_ball_radius(
            margins=(-1.0e308,),
            lipschitz_constants=(5e-324,),
        )


def test_nonlimiting_huge_radius_and_lower_envelope_terms_need_not_materialize():
    radius = certified_balance_ball_radius(
        margins=(1.0e308, 1.0),
        lipschitz_constants=(5e-324, 1.0),
    )
    assert radius == pytest.approx(1.0)

    lower = lipschitz_lower_envelope(
        sampled_values=(0.0, 1.0),
        distances_to_query=(1.0e308, 0.0),
        lipschitz_constant=1.0e308,
    )
    assert lower == pytest.approx(1.0)


def test_zero_lipschitz_negative_margin_certifies_structural_outside_infinity():
    radius = certified_outside_ball_radius(
        margins=(-0.2, 0.4),
        lipschitz_constants=(0.0, 1.0),
    )
    assert math.isinf(radius)


def test_zero_bracket_consistency_does_not_hide_behind_float_infinity():
    # Exact endpoint change is 3e308 while K*D is only 2e308.  Naive float
    # arithmetic makes both sides inf and would not detect the inconsistency.
    with pytest.raises(ValueError, match="inconsistent"):
        lipschitz_zero_bracket(
            positive_margin=1.5e308,
            negative_margin=-1.5e308,
            path_length=2.0,
            lipschitz_constant=1.0e308,
            tolerance=0.0,
        )


def test_impossible_target_depth_does_not_return_negative_radius():
    with pytest.raises(ValueError, match="no non-negative covering radius"):
        maximum_covering_radius_for_target_depth(
            sampled_min_margins=(0.10, 0.30),
            lipschitz_constants=(0.0, 0.5),
            target_depth=0.20,
        )
    with pytest.raises(ValueError, match="no non-negative covering radius"):
        maximum_covering_radius_for_target_depth(
            sampled_min_margins=(0.10, 0.30),
            lipschitz_constants=(0.5, 0.5),
            target_depth=0.20,
        )


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

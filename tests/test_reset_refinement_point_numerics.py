from fractions import Fraction as F

import pytest

from balance_domain.bounded_switching_design import (
    identify_bounded_switching,
    plan_reset_refinement,
)


DOWN = [
    (F(-5, 100), F(-5, 100), "differentiated"),
    (F(-8, 100), F(-8, 100), "shared"),
]
META = dict(
    common_phi_scale="synthetic units",
    fixed_context="synthetic fixed context",
    latent_monotone_and_instantaneous_declared=True,
)


def test_nonzero_nominal_query_cannot_disappear_to_zero_float():
    tiny = F(1, 10**400)
    receipt = identify_bounded_switching(
        [(F(0), F(0), "shared"), (tiny, tiny, "differentiated")],
        DOWN,
        **META,
    )
    with pytest.raises(ValueError, match="forward reset query phi underflows"):
        plan_reset_refinement(
            receipt,
            forward_query_error=0,
            reverse_query_error=0,
            matched_reset_available_declared=True,
        )


def test_positive_exact_guarantee_cannot_be_reported_as_zero():
    tiny = F(1, 10**400)
    high = F(1) + 2 * tiny
    receipt = identify_bounded_switching(
        [(F(1), F(1), "shared"), (high, high, "differentiated")],
        DOWN,
        **META,
    )
    with pytest.raises(ValueError, match="forward guaranteed span reduction underflows"):
        plan_reset_refinement(
            receipt,
            forward_query_error=0,
            reverse_query_error=0,
            matched_reset_available_declared=True,
        )


def test_ordinary_exact_nominal_query_and_positive_gain_are_unchanged():
    receipt = identify_bounded_switching(
        [("0.095", "0.105", "shared"), ("0.115", "0.125", "differentiated")],
        [("-0.055", "-0.045", "differentiated"), ("-0.085", "-0.075", "shared")],
        **META,
    )
    plan = plan_reset_refinement(
        receipt,
        forward_query_error="0.005",
        reverse_query_error="0.005",
        matched_reset_available_declared=True,
    )
    assert plan.status == "guaranteed_refinement"
    assert plan.best_directions == ("reverse",)
    reverse = next(option for option in plan.options if option.direction == "reverse")
    assert reverse.query_phi == pytest.approx(-0.065)
    assert reverse.guaranteed_span_reduction == pytest.approx(0.015)
    assert plan.guaranteed_width_span_reduction == pytest.approx(0.015)

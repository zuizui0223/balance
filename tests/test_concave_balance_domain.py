import pytest

from balance_domain.concave_domain import (
    audit_concave_margin,
    certify_concave_balance_segment,
    concave_segment_lower_bounds,
)


def test_positive_endpoint_margins_certify_entire_concave_segment():
    # [L, rho_1, rho_2]
    out = certify_concave_balance_segment(
        [0.4, 0.2, 0.5],
        [0.3, 0.6, 0.1],
    )
    assert out.certified_balance_segment
    assert out.segment_margin_floor == pytest.approx(0.1)
    assert out.limiting_margin_index == 2


def test_nonpositive_endpoint_margin_fails_closed():
    out = certify_concave_balance_segment(
        [0.4, 0.2],
        [0.3, -0.01],
    )
    assert not out.certified_balance_segment


def test_jensen_lower_bound_is_direct_shape_audit():
    lower = concave_segment_lower_bounds([0.2, 0.4], [0.6, 0.2], 0.25)
    assert lower == pytest.approx((0.3, 0.35))

    ok = audit_concave_margin(left=0.2, right=0.6, observed=0.34, t=0.25)
    assert not ok.concavity_violated
    assert ok.lower_bound == pytest.approx(0.3)

    bad = audit_concave_margin(left=0.2, right=0.6, observed=0.25, t=0.25)
    assert bad.concavity_violated
    assert bad.residual == pytest.approx(-0.05)


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        concave_segment_lower_bounds([1.0], [1.0, 2.0], 0.5)
    with pytest.raises(ValueError):
        audit_concave_margin(left=1.0, right=1.0, observed=1.0, t=1.2)

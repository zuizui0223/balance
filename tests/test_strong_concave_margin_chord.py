import pytest

from balance_domain.concave_domain import (
    audit_strong_concave_chord,
    strong_concave_bulge_bounds,
)


def test_midpoint_bulge_uses_one_eighth_rule():
    lower, upper = strong_concave_bulge_bounds(
        curvature_lower=2.0,
        curvature_upper=6.0,
        t=0.5,
        metric_distance_sq=4.0,
    )
    assert lower == pytest.approx(1.0)
    assert upper == pytest.approx(3.0)


def test_quadratic_concave_margin_hits_exact_bulge():
    # f(t)=1-2(t-0.5)^2 -> -f''=4, endpoints=.5, midpoint=1.
    out = audit_strong_concave_chord(
        left=0.5,
        right=0.5,
        observed=1.0,
        t=0.5,
        curvature_lower=4.0,
        curvature_upper=4.0,
    )
    assert out.observed_bulge == pytest.approx(0.5)
    assert out.bulge_lower == pytest.approx(0.5)
    assert out.bulge_upper == pytest.approx(0.5)
    assert not out.violates_lower
    assert not out.violates_upper


def test_too_shallow_interior_rejects_registered_strong_concavity():
    out = audit_strong_concave_chord(
        left=0.4,
        right=0.4,
        observed=0.45,
        t=0.5,
        curvature_lower=1.0,
        curvature_upper=4.0,
    )
    assert out.bulge_lower == pytest.approx(0.125)
    assert out.observed_bulge == pytest.approx(0.05)
    assert out.violates_lower


def test_invalid_bounds_fail_closed():
    with pytest.raises(ValueError):
        strong_concave_bulge_bounds(
            curvature_lower=3.0,
            curvature_upper=2.0,
            t=0.5,
        )

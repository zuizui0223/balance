import math

import pytest

from balance_domain.concave_domain import (
    audit_concave_margin,
    audit_strong_concave_chord,
    certify_concave_balance_segment,
    classify_interval_concave_chord,
    concave_segment_lower_bounds,
    interval_concave_bulge_bounds,
    strong_concave_bulge_bounds,
)


def test_nan_observation_cannot_masquerade_as_no_concavity_violation():
    with pytest.raises(ValueError):
        audit_concave_margin(
            left=0.2,
            right=0.6,
            observed=math.nan,
            t=0.5,
        )
    with pytest.raises(ValueError):
        audit_strong_concave_chord(
            left=0.2,
            right=0.6,
            observed=math.nan,
            t=0.5,
            curvature_lower=0.0,
            curvature_upper=1.0,
        )


def test_concave_endpoint_certificates_reject_nonfinite_margins():
    with pytest.raises(ValueError):
        concave_segment_lower_bounds([0.2, math.nan], [0.3, 0.4], 0.5)
    with pytest.raises(ValueError):
        certify_concave_balance_segment([0.2, math.inf], [0.3, 0.4])


def test_strong_concavity_preserves_unbounded_upper_curvature_but_rejects_bad_numbers():
    lower, upper = strong_concave_bulge_bounds(
        curvature_lower=0.2,
        curvature_upper=math.inf,
        t=0.5,
    )
    assert lower == pytest.approx(0.025)
    assert math.isinf(upper)

    with pytest.raises(ValueError):
        strong_concave_bulge_bounds(
            curvature_lower=math.nan,
            curvature_upper=1.0,
            t=0.5,
        )
    with pytest.raises(ValueError):
        strong_concave_bulge_bounds(
            curvature_lower=0.0,
            curvature_upper=-math.inf,
            t=0.5,
        )
    with pytest.raises(ValueError):
        strong_concave_bulge_bounds(
            curvature_lower=0.0,
            curvature_upper=1.0,
            t=0.5,
            metric_distance_sq=math.nan,
        )


def test_interval_audit_rejects_nonfinite_observation_bounds():
    with pytest.raises(ValueError):
        interval_concave_bulge_bounds(
            left_lower=0.1,
            left_upper=0.2,
            right_lower=0.1,
            right_upper=0.2,
            interior_lower=0.15,
            interior_upper=math.nan,
            t=0.5,
        )
    with pytest.raises(ValueError):
        classify_interval_concave_chord(
            left_lower=0.1,
            left_upper=0.2,
            right_lower=0.1,
            right_upper=0.2,
            interior_lower=0.15,
            interior_upper=0.3,
            t=0.5,
            curvature_lower=math.nan,
        )


def test_nonfinite_tolerances_fail_closed():
    with pytest.raises(ValueError):
        audit_concave_margin(
            left=0.2,
            right=0.6,
            observed=0.4,
            t=0.5,
            tolerance=math.nan,
        )
    with pytest.raises(ValueError):
        audit_strong_concave_chord(
            left=0.2,
            right=0.6,
            observed=0.4,
            t=0.5,
            curvature_lower=0.0,
            curvature_upper=1.0,
            tolerance=math.inf,
        )

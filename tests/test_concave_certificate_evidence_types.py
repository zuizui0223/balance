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


def test_concave_endpoint_certificates_reject_boolean_margins_and_t():
    with pytest.raises(ValueError, match="boolean"):
        concave_segment_lower_bounds([True, 1.0], [1.0, 1.0], 0.5)
    with pytest.raises(ValueError, match="boolean"):
        concave_segment_lower_bounds([1.0], [1.0], True)
    with pytest.raises(ValueError, match="boolean"):
        certify_concave_balance_segment([1.0], [True])


def test_jensen_audit_rejects_boolean_scientific_inputs():
    base = dict(left=0.2, right=0.6, observed=0.4, t=0.5, tolerance=0.0)
    for field in base:
        malformed = dict(base)
        malformed[field] = True
        with pytest.raises(ValueError, match="boolean"):
            audit_concave_margin(**malformed)


def test_strong_concavity_rejects_boolean_inputs_but_preserves_structural_infinity():
    base = dict(
        curvature_lower=0.2,
        curvature_upper=1.0,
        t=0.5,
        metric_distance_sq=1.0,
    )
    for field in base:
        malformed = dict(base)
        malformed[field] = True
        with pytest.raises(ValueError, match="boolean"):
            strong_concave_bulge_bounds(**malformed)

    lower, upper = strong_concave_bulge_bounds(
        curvature_lower=0.2,
        curvature_upper=math.inf,
        t=0.5,
        metric_distance_sq=1.0,
    )
    assert lower == pytest.approx(0.025)
    assert math.isinf(upper) and upper > 0


def test_strong_chord_audit_rejects_boolean_inputs():
    base = dict(
        left=0.2,
        right=0.6,
        observed=0.5,
        t=0.5,
        curvature_lower=0.0,
        curvature_upper=1.0,
        metric_distance_sq=1.0,
        tolerance=0.0,
    )
    for field in base:
        malformed = dict(base)
        malformed[field] = True
        with pytest.raises(ValueError, match="boolean"):
            audit_strong_concave_chord(**malformed)


def test_interval_concavity_rejects_boolean_inputs():
    interval = dict(
        left_lower=0.0,
        left_upper=0.1,
        right_lower=0.0,
        right_upper=0.1,
        interior_lower=0.2,
        interior_upper=0.3,
        t=0.5,
    )
    for field in interval:
        malformed = dict(interval)
        malformed[field] = True
        with pytest.raises(ValueError, match="boolean"):
            interval_concave_bulge_bounds(**malformed)

    classified = dict(
        interval,
        curvature_lower=0.0,
        curvature_upper=math.inf,
        metric_distance_sq=1.0,
    )
    for field in classified:
        malformed = dict(classified)
        malformed[field] = True
        with pytest.raises(ValueError, match="boolean"):
            classify_interval_concave_chord(**malformed)


def test_default_unbounded_upper_curvature_remains_structural_constraint():
    result = classify_interval_concave_chord(
        left_lower=0.0,
        left_upper=0.0,
        right_lower=0.0,
        right_upper=0.0,
        interior_lower=1.0,
        interior_upper=2.0,
        t=0.5,
    )
    assert result.classification == "IDENTIFIED_WITHIN_INTERVALS"
    assert math.isinf(result.required_bulge_upper) and result.required_bulge_upper > 0

import math

import pytest

from balance_domain.concave_domain import (
    classify_interval_concave_chord,
    interval_concave_bulge_bounds,
    robust_positive_concave_endpoints,
)


def test_interval_bulge_bounds_are_sharp_under_marginal_intervals():
    lo, hi = interval_concave_bulge_bounds(
        left_lower=0.2,
        left_upper=0.3,
        right_lower=0.4,
        right_upper=0.5,
        interior_lower=0.5,
        interior_upper=0.6,
        t=0.5,
    )
    assert lo == pytest.approx(0.1)
    assert hi == pytest.approx(0.3)


def test_interval_chord_identified_when_possible_set_inside_model_band():
    out = classify_interval_concave_chord(
        left_lower=0.4,
        left_upper=0.4,
        right_lower=0.4,
        right_upper=0.4,
        interior_lower=0.52,
        interior_upper=0.54,
        t=0.5,
        curvature_lower=0.8,
        curvature_upper=1.2,
    )
    assert out.required_bulge_lower == pytest.approx(0.1)
    assert out.required_bulge_upper == pytest.approx(0.15)
    assert out.classification == "IDENTIFIED_WITHIN_INTERVALS"


def test_interval_chord_robustly_rejects_concavity_when_upper_gap_negative():
    out = classify_interval_concave_chord(
        left_lower=0.5,
        left_upper=0.5,
        right_lower=0.5,
        right_upper=0.5,
        interior_lower=0.35,
        interior_upper=0.45,
        t=0.5,
    )
    assert out.possible_bulge_upper < 0.0
    assert out.classification == "LOWER_BOUND_VIOLATED"
    assert math.isinf(out.required_bulge_upper)


def test_partial_overlap_is_unresolved_not_forced():
    out = classify_interval_concave_chord(
        left_lower=0.4,
        left_upper=0.5,
        right_lower=0.4,
        right_upper=0.5,
        interior_lower=0.45,
        interior_upper=0.7,
        t=0.5,
        curvature_lower=0.4,
        curvature_upper=1.6,
    )
    assert out.classification == "UNRESOLVED"


def test_robust_positive_endpoint_lower_bounds_certify_segment_under_concavity():
    out = robust_positive_concave_endpoints(
        left_lower_margins=[0.2, 0.1, 0.3],
        right_lower_margins=[0.4, 0.5, 0.2],
    )
    assert out.certified_balance_segment
    assert out.segment_margin_floor == pytest.approx(0.1)


def test_endpoint_t_with_unbounded_upper_curvature_is_not_nan():
    out = classify_interval_concave_chord(
        left_lower=0.4,
        left_upper=0.4,
        right_lower=0.4,
        right_upper=0.4,
        interior_lower=0.4,
        interior_upper=0.4,
        t=0.0,
    )
    assert out.required_bulge_upper == pytest.approx(0.0)


def test_invalid_interval_fails_closed():
    with pytest.raises(ValueError):
        interval_concave_bulge_bounds(
            left_lower=1.0,
            left_upper=0.0,
            right_lower=0.0,
            right_upper=1.0,
            interior_lower=0.0,
            interior_upper=1.0,
            t=0.5,
        )

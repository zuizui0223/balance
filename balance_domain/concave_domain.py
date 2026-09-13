from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite, isinf
from typing import Sequence


@dataclass(frozen=True)
class ConcaveSegmentCertificate:
    certified_balance_segment: bool
    segment_margin_floor: float
    limiting_margin_index: int | None


@dataclass(frozen=True)
class JensenAudit:
    lower_bound: float
    residual: float
    concavity_violated: bool


@dataclass(frozen=True)
class StrongConcaveChordAudit:
    chord_value: float
    bulge_lower: float
    bulge_upper: float
    observed_bulge: float
    violates_lower: bool
    violates_upper: bool


@dataclass(frozen=True)
class IntervalChordClassification:
    possible_bulge_lower: float
    possible_bulge_upper: float
    required_bulge_lower: float
    required_bulge_upper: float
    classification: str


def _finite(value: float, name: str) -> float:
    out = float(value)
    if not isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def _finite_vector(values: Sequence[float], name: str) -> tuple[float, ...]:
    out = tuple(float(value) for value in values)
    if not all(isfinite(value) for value in out):
        raise ValueError(f"{name} must contain only finite values")
    return out


def _q(value: float) -> Fraction:
    return Fraction.from_float(float(value))


def _finite_output(value: Fraction, name: str) -> float:
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} is not float-representable; rescale units") from exc
    if not isfinite(out):
        raise ValueError(f"{name} is not float-representable; rescale units")
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision; rescale units")
    return out


def _convex_exact(left: float, right: float, t: float) -> Fraction:
    tq = _q(t)
    return (Fraction(1) - tq) * _q(left) + tq * _q(right)


def _strong_concave_bulge_bounds_exact(
    *,
    curvature_lower: float,
    curvature_upper: float,
    t: float,
    metric_distance_sq: float,
) -> tuple[Fraction, Fraction | None]:
    curvature_lower = _finite(curvature_lower, "curvature_lower")
    curvature_upper = float(curvature_upper)
    t = _finite(t, "t")
    metric_distance_sq = _finite(metric_distance_sq, "metric_distance_sq")
    if not isfinite(curvature_upper) and not (isinf(curvature_upper) and curvature_upper > 0):
        raise ValueError("curvature_upper must be finite or positive infinity")
    if not 0.0 <= t <= 1.0:
        raise ValueError("t must lie in [0, 1]")
    if curvature_lower < 0.0 or curvature_upper < curvature_lower:
        raise ValueError("curvature bounds must satisfy 0 <= lower <= upper")
    if metric_distance_sq < 0.0:
        raise ValueError("metric_distance_sq must be nonnegative")

    tq = _q(t)
    factor = Fraction(1, 2) * tq * (Fraction(1) - tq) * _q(metric_distance_sq)
    lower = _q(curvature_lower) * factor
    if factor == 0:
        upper: Fraction | None = Fraction(0)
    elif isinf(curvature_upper):
        upper = None
    else:
        upper = _q(curvature_upper) * factor
    return lower, upper


def _interval_concave_bulge_bounds_exact(
    *,
    left_lower: float,
    left_upper: float,
    right_lower: float,
    right_upper: float,
    interior_lower: float,
    interior_upper: float,
    t: float,
) -> tuple[Fraction, Fraction]:
    left_lower = _finite(left_lower, "left_lower")
    left_upper = _finite(left_upper, "left_upper")
    right_lower = _finite(right_lower, "right_lower")
    right_upper = _finite(right_upper, "right_upper")
    interior_lower = _finite(interior_lower, "interior_lower")
    interior_upper = _finite(interior_upper, "interior_upper")
    t = _finite(t, "t")
    if not 0.0 <= t <= 1.0:
        raise ValueError("t must lie in [0, 1]")
    if left_lower > left_upper or right_lower > right_upper or interior_lower > interior_upper:
        raise ValueError("each interval must satisfy lower <= upper")

    possible_lower = _q(interior_lower) - _convex_exact(left_upper, right_upper, t)
    possible_upper = _q(interior_upper) - _convex_exact(left_lower, right_lower, t)
    return possible_lower, possible_upper


def concave_segment_lower_bounds(
    left_margins: Sequence[float],
    right_margins: Sequence[float],
    t: float,
) -> tuple[float, ...]:
    if not left_margins or len(left_margins) != len(right_margins):
        raise ValueError("endpoint margin vectors must have the same nonzero length")
    left = _finite_vector(left_margins, "left_margins")
    right = _finite_vector(right_margins, "right_margins")
    t = _finite(t, "t")
    if not 0.0 <= t <= 1.0:
        raise ValueError("t must lie in [0, 1]")
    return tuple(
        _finite_output(_convex_exact(a, b, t), "concave chord lower bound")
        for a, b in zip(left, right)
    )


def certify_concave_balance_segment(
    left_margins: Sequence[float],
    right_margins: Sequence[float],
) -> ConcaveSegmentCertificate:
    if not left_margins or len(left_margins) != len(right_margins):
        raise ValueError("endpoint margin vectors must have the same nonzero length")
    left = _finite_vector(left_margins, "left_margins")
    right = _finite_vector(right_margins, "right_margins")

    endpoint_floors = [min(a, b) for a, b in zip(left, right)]
    limiting = min(range(len(endpoint_floors)), key=endpoint_floors.__getitem__)
    floor = endpoint_floors[limiting]
    return ConcaveSegmentCertificate(
        certified_balance_segment=floor > 0.0,
        segment_margin_floor=floor,
        limiting_margin_index=limiting,
    )


def audit_concave_margin(
    *,
    left: float,
    right: float,
    observed: float,
    t: float,
    tolerance: float = 0.0,
) -> JensenAudit:
    left = _finite(left, "left")
    right = _finite(right, "right")
    observed = _finite(observed, "observed")
    t = _finite(t, "t")
    tolerance = _finite(tolerance, "tolerance")
    if not 0.0 <= t <= 1.0:
        raise ValueError("t must lie in [0, 1]")
    if tolerance < 0.0:
        raise ValueError("tolerance must be nonnegative")

    lower_q = _convex_exact(left, right, t)
    residual_q = _q(observed) - lower_q
    return JensenAudit(
        lower_bound=_finite_output(lower_q, "Jensen lower bound"),
        residual=_finite_output(residual_q, "Jensen residual"),
        concavity_violated=residual_q < -_q(tolerance),
    )


def strong_concave_bulge_bounds(
    *,
    curvature_lower: float,
    curvature_upper: float,
    t: float,
    metric_distance_sq: float = 1.0,
) -> tuple[float, float]:
    lower_q, upper_q = _strong_concave_bulge_bounds_exact(
        curvature_lower=curvature_lower,
        curvature_upper=curvature_upper,
        t=t,
        metric_distance_sq=metric_distance_sq,
    )
    return (
        _finite_output(lower_q, "strong-concavity lower bulge"),
        float("inf") if upper_q is None else _finite_output(upper_q, "strong-concavity upper bulge"),
    )


def audit_strong_concave_chord(
    *,
    left: float,
    right: float,
    observed: float,
    t: float,
    curvature_lower: float,
    curvature_upper: float,
    metric_distance_sq: float = 1.0,
    tolerance: float = 0.0,
) -> StrongConcaveChordAudit:
    left = _finite(left, "left")
    right = _finite(right, "right")
    observed = _finite(observed, "observed")
    t = _finite(t, "t")
    tolerance = _finite(tolerance, "tolerance")
    if not 0.0 <= t <= 1.0:
        raise ValueError("t must lie in [0, 1]")
    if tolerance < 0.0:
        raise ValueError("tolerance must be nonnegative")

    chord_q = _convex_exact(left, right, t)
    lower_q, upper_q = _strong_concave_bulge_bounds_exact(
        curvature_lower=curvature_lower,
        curvature_upper=curvature_upper,
        t=t,
        metric_distance_sq=metric_distance_sq,
    )
    bulge_q = _q(observed) - chord_q
    tol_q = _q(tolerance)
    return StrongConcaveChordAudit(
        chord_value=_finite_output(chord_q, "strong-concavity chord value"),
        bulge_lower=_finite_output(lower_q, "strong-concavity lower bulge"),
        bulge_upper=(
            float("inf") if upper_q is None
            else _finite_output(upper_q, "strong-concavity upper bulge")
        ),
        observed_bulge=_finite_output(bulge_q, "observed concavity bulge"),
        violates_lower=bulge_q < lower_q - tol_q,
        violates_upper=False if upper_q is None else bulge_q > upper_q + tol_q,
    )


def interval_concave_bulge_bounds(
    *,
    left_lower: float,
    left_upper: float,
    right_lower: float,
    right_upper: float,
    interior_lower: float,
    interior_upper: float,
    t: float,
) -> tuple[float, float]:
    possible_lower_q, possible_upper_q = _interval_concave_bulge_bounds_exact(
        left_lower=left_lower,
        left_upper=left_upper,
        right_lower=right_lower,
        right_upper=right_upper,
        interior_lower=interior_lower,
        interior_upper=interior_upper,
        t=t,
    )
    return (
        _finite_output(possible_lower_q, "possible concavity bulge lower bound"),
        _finite_output(possible_upper_q, "possible concavity bulge upper bound"),
    )


def classify_interval_concave_chord(
    *,
    left_lower: float,
    left_upper: float,
    right_lower: float,
    right_upper: float,
    interior_lower: float,
    interior_upper: float,
    t: float,
    curvature_lower: float = 0.0,
    curvature_upper: float = float("inf"),
    metric_distance_sq: float = 1.0,
) -> IntervalChordClassification:
    possible_lower_q, possible_upper_q = _interval_concave_bulge_bounds_exact(
        left_lower=left_lower,
        left_upper=left_upper,
        right_lower=right_lower,
        right_upper=right_upper,
        interior_lower=interior_lower,
        interior_upper=interior_upper,
        t=t,
    )
    required_lower_q, required_upper_q = _strong_concave_bulge_bounds_exact(
        curvature_lower=curvature_lower,
        curvature_upper=curvature_upper,
        t=t,
        metric_distance_sq=metric_distance_sq,
    )

    if possible_upper_q < required_lower_q:
        classification = "LOWER_BOUND_VIOLATED"
    elif required_upper_q is not None and possible_lower_q > required_upper_q:
        classification = "UPPER_BOUND_VIOLATED"
    elif (
        possible_lower_q >= required_lower_q
        and (required_upper_q is None or possible_upper_q <= required_upper_q)
    ):
        classification = "IDENTIFIED_WITHIN_INTERVALS"
    else:
        classification = "UNRESOLVED"

    return IntervalChordClassification(
        possible_bulge_lower=_finite_output(
            possible_lower_q, "possible concavity bulge lower bound"
        ),
        possible_bulge_upper=_finite_output(
            possible_upper_q, "possible concavity bulge upper bound"
        ),
        required_bulge_lower=_finite_output(
            required_lower_q, "required concavity bulge lower bound"
        ),
        required_bulge_upper=(
            float("inf") if required_upper_q is None
            else _finite_output(required_upper_q, "required concavity bulge upper bound")
        ),
        classification=classification,
    )


def robust_positive_concave_endpoints(
    *,
    left_lower_margins: Sequence[float],
    right_lower_margins: Sequence[float],
) -> ConcaveSegmentCertificate:
    if not left_lower_margins or len(left_lower_margins) != len(right_lower_margins):
        raise ValueError("endpoint lower-bound vectors must have the same nonzero length")
    return certify_concave_balance_segment(left_lower_margins, right_lower_margins)

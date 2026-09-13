from __future__ import annotations

from dataclasses import dataclass
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
    return tuple((1.0 - t) * a + t * b for a, b in zip(left, right))


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
    if tolerance < 0.0:
        raise ValueError("tolerance must be nonnegative")
    lower = concave_segment_lower_bounds([left], [right], t)[0]
    residual = observed - lower
    return JensenAudit(
        lower_bound=lower,
        residual=residual,
        concavity_violated=residual < -tolerance,
    )


def strong_concave_bulge_bounds(
    *,
    curvature_lower: float,
    curvature_upper: float,
    t: float,
    metric_distance_sq: float = 1.0,
) -> tuple[float, float]:
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
    factor = 0.5 * t * (1.0 - t) * metric_distance_sq
    upper = float("inf") if isinf(curvature_upper) and factor > 0.0 else curvature_upper * factor
    if factor == 0.0:
        upper = 0.0
    return curvature_lower * factor, upper


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
    if tolerance < 0.0:
        raise ValueError("tolerance must be nonnegative")
    chord = concave_segment_lower_bounds([left], [right], t)[0]
    lower, upper = strong_concave_bulge_bounds(
        curvature_lower=curvature_lower,
        curvature_upper=curvature_upper,
        t=t,
        metric_distance_sq=metric_distance_sq,
    )
    bulge = observed - chord
    return StrongConcaveChordAudit(
        chord_value=chord,
        bulge_lower=lower,
        bulge_upper=upper,
        observed_bulge=bulge,
        violates_lower=bulge < lower - tolerance,
        violates_upper=bulge > upper + tolerance,
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

    possible_lower = interior_lower - (
        (1.0 - t) * left_upper + t * right_upper
    )
    possible_upper = interior_upper - (
        (1.0 - t) * left_lower + t * right_lower
    )
    return possible_lower, possible_upper


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
    possible_lower, possible_upper = interval_concave_bulge_bounds(
        left_lower=left_lower,
        left_upper=left_upper,
        right_lower=right_lower,
        right_upper=right_upper,
        interior_lower=interior_lower,
        interior_upper=interior_upper,
        t=t,
    )
    required_lower, required_upper = strong_concave_bulge_bounds(
        curvature_lower=curvature_lower,
        curvature_upper=curvature_upper,
        t=t,
        metric_distance_sq=metric_distance_sq,
    )

    if possible_upper < required_lower:
        classification = "LOWER_BOUND_VIOLATED"
    elif possible_lower > required_upper:
        classification = "UPPER_BOUND_VIOLATED"
    elif possible_lower >= required_lower and possible_upper <= required_upper:
        classification = "IDENTIFIED_WITHIN_INTERVALS"
    else:
        classification = "UNRESOLVED"

    return IntervalChordClassification(
        possible_bulge_lower=possible_lower,
        possible_bulge_upper=possible_upper,
        required_bulge_lower=required_lower,
        required_bulge_upper=required_upper,
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

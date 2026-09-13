from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class EnvelopeSegment:
    start: float
    end: float
    active_alternative: int


@dataclass(frozen=True)
class EndpointReserveCertificate:
    left_reserve: float
    right_reserve: float
    interval_lower_bound: float
    positive_throughout_interval: bool


def _value(slope: float, intercept: float, x: float) -> float:
    return slope * x + intercept


def _finite_affines(slopes: Sequence[float], intercepts: Sequence[float]) -> tuple[tuple[float, ...], tuple[float, ...]]:
    if len(slopes) != len(intercepts) or not slopes:
        raise ValueError("slopes and intercepts must have the same nonzero length")
    slope_values = tuple(float(value) for value in slopes)
    intercept_values = tuple(float(value) for value in intercepts)
    if not all(isfinite(value) for value in slope_values + intercept_values):
        raise ValueError("slopes and intercepts must be finite")
    return slope_values, intercept_values


def affine_upper_envelope_segments(
    slopes: Sequence[float],
    intercepts: Sequence[float],
    *,
    start: float,
    end: float,
) -> tuple[EnvelopeSegment, ...]:
    """Return active upper-envelope segments for affine alternatives on [start,end].

    Exact pairwise intersections provide all possible switch points. Ties at a
    single breakpoint are assigned by the adjacent open intervals; exact tie
    intervals occur only for duplicate affine functions and do not create
    extra switches.
    """
    slopes, intercepts = _finite_affines(slopes, intercepts)
    start = float(start)
    end = float(end)
    if not isfinite(start) or not isfinite(end):
        raise ValueError("start and end must be finite")
    if not start < end:
        raise ValueError("start must be smaller than end")

    cuts = {start, end}
    n = len(slopes)
    for i in range(n):
        for j in range(i + 1, n):
            denom = slopes[i] - slopes[j]
            if denom == 0.0:
                continue
            x = (intercepts[j] - intercepts[i]) / denom
            if start < x < end:
                cuts.add(x)

    ordered = sorted(cuts)
    raw: list[EnvelopeSegment] = []
    for left, right in zip(ordered[:-1], ordered[1:]):
        mid = 0.5 * (left + right)
        values = [
            _value(a, b, mid)
            for a, b in zip(slopes, intercepts)
        ]
        active = max(range(n), key=values.__getitem__)
        raw.append(EnvelopeSegment(left, right, active))

    if not raw:
        return ()

    merged: list[EnvelopeSegment] = [raw[0]]
    for segment in raw[1:]:
        previous = merged[-1]
        if segment.active_alternative == previous.active_alternative:
            merged[-1] = EnvelopeSegment(
                previous.start,
                segment.end,
                previous.active_alternative,
            )
        else:
            merged.append(segment)
    return tuple(merged)


def alternative_reserve(
    *,
    environment: float,
    shared_slope: float,
    shared_intercept: float,
    alternative_slopes: Sequence[float],
    alternative_intercepts: Sequence[float],
) -> float:
    alternative_slopes, alternative_intercepts = _finite_affines(
        alternative_slopes, alternative_intercepts
    )
    environment = float(environment)
    shared_slope = float(shared_slope)
    shared_intercept = float(shared_intercept)
    if not all(isfinite(value) for value in (environment, shared_slope, shared_intercept)):
        raise ValueError("environment and shared affine coefficients must be finite")
    shared = _value(shared_slope, shared_intercept, environment)
    best_alt = max(
        _value(a, b, environment)
        for a, b in zip(alternative_slopes, alternative_intercepts)
    )
    return shared - best_alt


def endpoint_reserve_certificate(
    *,
    start: float,
    end: float,
    shared_slope: float,
    shared_intercept: float,
    alternative_slopes: Sequence[float],
    alternative_intercepts: Sequence[float],
    strict_tolerance: float = 0.0,
) -> EndpointReserveCertificate:
    """Certify an affine-envelope reserve over a full scalar interval.

    Under the registered affine-envelope model, the reserve is concave, so its
    minimum over a closed interval equals the smaller endpoint reserve.
    """
    start = float(start)
    end = float(end)
    strict_tolerance = float(strict_tolerance)
    if not all(isfinite(value) for value in (start, end, strict_tolerance)):
        raise ValueError("interval endpoints and strict_tolerance must be finite")
    if not start < end:
        raise ValueError("start must be smaller than end")
    if strict_tolerance < 0:
        raise ValueError("strict_tolerance must be nonnegative")

    left = alternative_reserve(
        environment=start,
        shared_slope=shared_slope,
        shared_intercept=shared_intercept,
        alternative_slopes=alternative_slopes,
        alternative_intercepts=alternative_intercepts,
    )
    right = alternative_reserve(
        environment=end,
        shared_slope=shared_slope,
        shared_intercept=shared_intercept,
        alternative_slopes=alternative_slopes,
        alternative_intercepts=alternative_intercepts,
    )
    lower = min(left, right)
    return EndpointReserveCertificate(
        left_reserve=left,
        right_reserve=right,
        interval_lower_bound=lower,
        positive_throughout_interval=lower > strict_tolerance,
    )


def threat_switch_bound(number_of_alternatives: int) -> int:
    if number_of_alternatives < 1:
        raise ValueError("number_of_alternatives must be positive")
    return number_of_alternatives - 1

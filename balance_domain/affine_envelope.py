from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
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


def _finite_affines(
    slopes: Sequence[float],
    intercepts: Sequence[float],
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    if len(slopes) != len(intercepts) or not slopes:
        raise ValueError("slopes and intercepts must have the same nonzero length")
    slope_values = tuple(float(value) for value in slopes)
    intercept_values = tuple(float(value) for value in intercepts)
    if not all(isfinite(value) for value in slope_values + intercept_values):
        raise ValueError("slopes and intercepts must be finite")
    return slope_values, intercept_values


def _exact(value: float) -> Fraction:
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


def _exact_value(slope: Fraction, intercept: Fraction, x: Fraction) -> Fraction:
    return slope * x + intercept


def _alternative_reserve_exact(
    *,
    environment: float,
    shared_slope: float,
    shared_intercept: float,
    alternative_slopes: Sequence[float],
    alternative_intercepts: Sequence[float],
) -> Fraction:
    alternative_slopes, alternative_intercepts = _finite_affines(
        alternative_slopes, alternative_intercepts
    )
    environment = float(environment)
    shared_slope = float(shared_slope)
    shared_intercept = float(shared_intercept)
    if not all(isfinite(value) for value in (environment, shared_slope, shared_intercept)):
        raise ValueError("environment and shared affine coefficients must be finite")

    x = _exact(environment)
    shared = _exact_value(_exact(shared_slope), _exact(shared_intercept), x)
    best_alt = max(
        _exact_value(_exact(a), _exact(b), x)
        for a, b in zip(alternative_slopes, alternative_intercepts)
    )
    return shared - best_alt


def affine_upper_envelope_segments(
    slopes: Sequence[float],
    intercepts: Sequence[float],
    *,
    start: float,
    end: float,
) -> tuple[EnvelopeSegment, ...]:
    """Return active upper-envelope segments for affine alternatives on [start,end].

    Pairwise intersections and active-alternative comparisons are evaluated
    exactly at the supplied-float level.  Ties at a single breakpoint are
    assigned by the adjacent open intervals; duplicate affine functions do not
    create extra switches.
    """
    slopes, intercepts = _finite_affines(slopes, intercepts)
    start = float(start)
    end = float(end)
    if not isfinite(start) or not isfinite(end):
        raise ValueError("start and end must be finite")
    if not start < end:
        raise ValueError("start must be smaller than end")

    slope_q = tuple(_exact(value) for value in slopes)
    intercept_q = tuple(_exact(value) for value in intercepts)
    start_q = _exact(start)
    end_q = _exact(end)

    cuts = {start_q, end_q}
    n = len(slopes)
    for i in range(n):
        for j in range(i + 1, n):
            denom = slope_q[i] - slope_q[j]
            if denom == 0:
                continue
            x = (intercept_q[j] - intercept_q[i]) / denom
            if start_q < x < end_q:
                cuts.add(x)

    ordered = sorted(cuts)
    raw: list[tuple[Fraction, Fraction, int]] = []
    for left, right in zip(ordered[:-1], ordered[1:]):
        mid = (left + right) / 2
        values = [
            _exact_value(a, b, mid)
            for a, b in zip(slope_q, intercept_q)
        ]
        active = max(range(n), key=values.__getitem__)
        raw.append((left, right, active))

    if not raw:
        return ()

    merged: list[tuple[Fraction, Fraction, int]] = [raw[0]]
    for left, right, active in raw[1:]:
        previous_left, previous_right, previous_active = merged[-1]
        if active == previous_active:
            merged[-1] = (previous_left, right, previous_active)
        else:
            merged.append((left, right, active))

    segments: list[EnvelopeSegment] = []
    for left, right, active in merged:
        left_f = _finite_output(left, "envelope segment boundary")
        right_f = _finite_output(right, "envelope segment boundary")
        if not left_f < right_f:
            raise ValueError(
                "distinct affine switch points collapse at float precision; rescale environment units"
            )
        segments.append(EnvelopeSegment(left_f, right_f, active))
    return tuple(segments)


def alternative_reserve(
    *,
    environment: float,
    shared_slope: float,
    shared_intercept: float,
    alternative_slopes: Sequence[float],
    alternative_intercepts: Sequence[float],
) -> float:
    reserve = _alternative_reserve_exact(
        environment=environment,
        shared_slope=shared_slope,
        shared_intercept=shared_intercept,
        alternative_slopes=alternative_slopes,
        alternative_intercepts=alternative_intercepts,
    )
    return _finite_output(reserve, "alternative reserve")


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

    left_q = _alternative_reserve_exact(
        environment=start,
        shared_slope=shared_slope,
        shared_intercept=shared_intercept,
        alternative_slopes=alternative_slopes,
        alternative_intercepts=alternative_intercepts,
    )
    right_q = _alternative_reserve_exact(
        environment=end,
        shared_slope=shared_slope,
        shared_intercept=shared_intercept,
        alternative_slopes=alternative_slopes,
        alternative_intercepts=alternative_intercepts,
    )
    lower_q = min(left_q, right_q)
    return EndpointReserveCertificate(
        left_reserve=_finite_output(left_q, "left reserve"),
        right_reserve=_finite_output(right_q, "right reserve"),
        interval_lower_bound=_finite_output(lower_q, "interval reserve lower bound"),
        positive_throughout_interval=lower_q > _exact(strict_tolerance),
    )


def threat_switch_bound(number_of_alternatives: int) -> int:
    if type(number_of_alternatives) is not int or number_of_alternatives < 1:
        raise ValueError("number_of_alternatives must be a positive integer")
    return number_of_alternatives - 1

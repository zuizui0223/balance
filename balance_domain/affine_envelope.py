from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class EnvelopeSegment:
    start: float
    end: float
    active_alternative: int


def _value(slope: float, intercept: float, x: float) -> float:
    return slope * x + intercept


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

    if len(slopes) != len(intercepts) or not slopes:
        raise ValueError("slopes and intercepts must have the same nonzero length")
    if not start < end:
        raise ValueError("start must be smaller than end")

    cuts = {float(start), float(end)}
    n = len(slopes)
    for i in range(n):
        for j in range(i + 1, n):
            denom = float(slopes[i]) - float(slopes[j])
            if denom == 0.0:
                continue
            x = (float(intercepts[j]) - float(intercepts[i])) / denom
            if start < x < end:
                cuts.add(x)

    ordered = sorted(cuts)
    raw: list[EnvelopeSegment] = []
    for left, right in zip(ordered[:-1], ordered[1:]):
        mid = 0.5 * (left + right)
        values = [
            _value(float(a), float(b), mid)
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
    if len(alternative_slopes) != len(alternative_intercepts) or not alternative_slopes:
        raise ValueError("alternative slopes/intercepts must have the same nonzero length")
    shared = _value(shared_slope, shared_intercept, environment)
    best_alt = max(
        _value(float(a), float(b), environment)
        for a, b in zip(alternative_slopes, alternative_intercepts)
    )
    return shared - best_alt


def threat_switch_bound(number_of_alternatives: int) -> int:
    if number_of_alternatives < 1:
        raise ValueError("number_of_alternatives must be positive")
    return number_of_alternatives - 1

from __future__ import annotations

from dataclasses import dataclass
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


def concave_segment_lower_bounds(
    left_margins: Sequence[float],
    right_margins: Sequence[float],
    t: float,
) -> tuple[float, ...]:
    if not 0.0 <= t <= 1.0:
        raise ValueError("t must lie in [0, 1]")
    if not left_margins or len(left_margins) != len(right_margins):
        raise ValueError("endpoint margin vectors must have the same nonzero length")
    return tuple((1.0 - t) * float(a) + t * float(b) for a, b in zip(left_margins, right_margins))


def certify_concave_balance_segment(
    left_margins: Sequence[float],
    right_margins: Sequence[float],
) -> ConcaveSegmentCertificate:
    if not left_margins or len(left_margins) != len(right_margins):
        raise ValueError("endpoint margin vectors must have the same nonzero length")

    endpoint_floors = [min(float(a), float(b)) for a, b in zip(left_margins, right_margins)]
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
    if tolerance < 0.0:
        raise ValueError("tolerance must be nonnegative")
    lower = concave_segment_lower_bounds([left], [right], t)[0]
    residual = float(observed) - lower
    return JensenAudit(
        lower_bound=lower,
        residual=residual,
        concavity_violated=residual < -tolerance,
    )

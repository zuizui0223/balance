"""Critical-point concordance between direct and decomposed worldline views."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class CriticalConcordanceResult:
    direct_crossings: tuple[float, ...]
    decomposed_crossings: tuple[float, ...]
    critical_point_difference: float | None
    status: str


def _crossing(e0: float, e1: float, y0: float, y1: float) -> float:
    if y1 == y0:
        return (e0 + e1) / 2.0
    return e0 + (-y0) * (e1 - e0) / (y1 - y0)


def _zero_crossings(
    environment: tuple[float, ...],
    values: tuple[float, ...],
    tolerance: float,
) -> tuple[float, ...]:
    out: list[float] = []
    n = len(environment)
    for i in range(n - 1):
        y0, y1 = values[i], values[i + 1]
        if abs(y0) <= tolerance:
            out.append(environment[i])
        elif y0 * y1 < 0:
            out.append(_crossing(environment[i], environment[i + 1], y0, y1))
    if abs(values[-1]) <= tolerance:
        out.append(environment[-1])

    deduped: list[float] = []
    for x in out:
        if not deduped or abs(x - deduped[-1]) > tolerance:
            deduped.append(x)
    return tuple(deduped)


def compare_critical_paths(
    environment: Sequence[float],
    direct_worldline_gap: Sequence[float],
    decomposed_gap: Sequence[float],
    *,
    value_tolerance: float = 1e-9,
    critical_point_tolerance: float = 1e-6,
) -> CriticalConcordanceResult:
    """Compare architecture crossings obtained by two independent views.

    ``direct_worldline_gap`` is ``W_D*-W_S*``.
    ``decomposed_gap`` is ``sL-K``.

    A common critical point is claimed only when each path has exactly one
    zero crossing and their environmental locations agree within the
    prospectively supplied ``critical_point_tolerance``.
    """
    e = tuple(float(x) for x in environment)
    direct = tuple(float(x) for x in direct_worldline_gap)
    decomposed = tuple(float(x) for x in decomposed_gap)
    n = len(e)
    if n < 2 or not (len(direct) == len(decomposed) == n):
        raise ValueError("all paths must have equal length >= 2")
    if any(e[i + 1] <= e[i] for i in range(n - 1)):
        raise ValueError("environment must be strictly increasing")
    if value_tolerance <= 0 or critical_point_tolerance < 0:
        raise ValueError("tolerances must be valid")

    dc = _zero_crossings(e, direct, value_tolerance)
    mc = _zero_crossings(e, decomposed, value_tolerance)

    if len(dc) == len(mc) == 0:
        return CriticalConcordanceResult(dc, mc, None, "NO_CRITICAL_CROSSING")
    if len(dc) != 1 or len(mc) != 1:
        return CriticalConcordanceResult(dc, mc, None, "MULTIPLE_OR_UNMATCHED_CRITICAL_POINTS")

    delta = dc[0] - mc[0]
    if abs(delta) <= critical_point_tolerance:
        status = "SAME_CRITICAL_POINT"
    else:
        status = "PARALLEL_CRITICAL_POINTS"
    return CriticalConcordanceResult(dc, mc, delta, status)

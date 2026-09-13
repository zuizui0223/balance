from __future__ import annotations

from dataclasses import dataclass
import math


_ROUNDOFF_RELATIVE_TOLERANCE = 64.0 * math.ulp(1.0)


@dataclass(frozen=True)
class DeepestMiddleWorldPoint:
    environment: float
    conflict_load: float
    reserve: float
    xi: float
    depth: float
    interpolation_interval: tuple[int, int]


def _validate(environment, conflict, reserve) -> None:
    if not (len(environment) == len(conflict) == len(reserve)):
        raise ValueError("environment, conflict and reserve must have equal length")
    if len(environment) < 2:
        raise ValueError("at least two path points are required")
    if not all(math.isfinite(value) for values in (environment, conflict, reserve) for value in values):
        raise ValueError("environment, conflict and reserve must be finite")
    if any(environment[i + 1] <= environment[i] for i in range(len(environment) - 1)):
        raise ValueError("environment must be strictly increasing")
    if any(value < 0 for value in conflict):
        raise ValueError("conflict load must be non-negative")
    if any(value < 0 for value in reserve):
        raise ValueError("reserve must be non-negative")
    if any(conflict[i + 1] < conflict[i] for i in range(len(conflict) - 1)):
        raise ValueError("conflict load must be non-decreasing for the monotone theorem")
    if any(reserve[i + 1] > reserve[i] for i in range(len(reserve) - 1)):
        raise ValueError("reserve must be non-increasing for the monotone theorem")


def _roundoff_equal(left: float, right: float) -> bool:
    """Return whether two margins differ only at floating-point roundoff scale."""

    if left == right:
        return True
    scale = max(abs(left), abs(right))
    if scale == 0.0:
        return True
    return abs(left - right) <= _ROUNDOFF_RELATIVE_TOLERANCE * scale


def _middle_coordinate(conflict: float, reserve: float) -> float:
    """Return L/(L+rho) without overflowing when both finite margins are huge."""

    scale = max(conflict, reserve)
    if scale <= 0.0:
        raise ValueError("equal-margin point must have positive total margin")
    l_scaled = conflict / scale
    r_scaled = reserve / scale
    return l_scaled / (l_scaled + r_scaled)


def deepest_middle_point(environment, conflict, reserve) -> DeepestMiddleWorldPoint:
    """Locate the equal-margin deepest BALANCE point on a piecewise-linear path.

    The routine is an empirical interpolation helper for the monotone theorem. It
    does not infer a crossing outside the sampled range. Numerical equality is
    judged only at machine-roundoff-relative scale so a change of fitness units
    cannot create or erase an equal-margin sample.
    """
    environment = [float(x) for x in environment]
    conflict = [float(x) for x in conflict]
    reserve = [float(x) for x in reserve]
    _validate(environment, conflict, reserve)

    difference = [l - r for l, r in zip(conflict, reserve)]

    exact = [
        i
        for i, (l, r) in enumerate(zip(conflict, reserve))
        if _roundoff_equal(l, r)
    ]
    if exact:
        if len(exact) > 1:
            raise ValueError("equal-margin point is not unique on the sampled path")
        i = exact[0]
        return DeepestMiddleWorldPoint(
            environment=environment[i],
            conflict_load=conflict[i],
            reserve=reserve[i],
            xi=_middle_coordinate(conflict[i], reserve[i]),
            depth=min(conflict[i], reserve[i]),
            interpolation_interval=(i, i),
        )

    intervals = [
        i
        for i in range(len(difference) - 1)
        if difference[i] < 0 < difference[i + 1]
    ]
    if len(intervals) != 1:
        raise ValueError("sampled path does not identify one interior equal-margin crossing")

    i = intervals[0]
    d0, d1 = difference[i], difference[i + 1]
    difference_scale = max(abs(d0), abs(d1))
    if difference_scale == 0.0:
        raise RuntimeError("internal equal-margin crossing lost signed difference")
    d0_scaled = d0 / difference_scale
    d1_scaled = d1 / difference_scale
    fraction = -d0_scaled / (d1_scaled - d0_scaled)

    def interp(values):
        return (1.0 - fraction) * values[i] + fraction * values[i + 1]

    e_star = interp(environment)
    l_star = interp(conflict)
    r_star = interp(reserve)

    return DeepestMiddleWorldPoint(
        environment=e_star,
        conflict_load=l_star,
        reserve=r_star,
        xi=_middle_coordinate(l_star, r_star),
        depth=min(l_star, r_star),
        interpolation_interval=(i, i + 1),
    )

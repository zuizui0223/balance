from __future__ import annotations

from dataclasses import dataclass


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


def deepest_middle_point(environment, conflict, reserve) -> DeepestMiddleWorldPoint:
    """Locate the equal-margin deepest BALANCE point on a piecewise-linear path.

    The routine is an empirical interpolation helper for the monotone theorem. It
    does not infer a crossing outside the sampled range.
    """
    environment = [float(x) for x in environment]
    conflict = [float(x) for x in conflict]
    reserve = [float(x) for x in reserve]
    _validate(environment, conflict, reserve)

    difference = [l - r for l, r in zip(conflict, reserve)]

    exact = [i for i, value in enumerate(difference) if abs(value) <= 1e-12]
    if exact:
        if len(exact) > 1:
            raise ValueError("equal-margin point is not unique on the sampled path")
        i = exact[0]
        value = conflict[i]
        total = conflict[i] + reserve[i]
        if total <= 0:
            raise ValueError("equal-margin point must have positive total margin")
        return DeepestMiddleWorldPoint(
            environment=environment[i],
            conflict_load=conflict[i],
            reserve=reserve[i],
            xi=conflict[i] / total,
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
    fraction = -d0 / (d1 - d0)

    def interp(values):
        return values[i] + fraction * (values[i + 1] - values[i])

    e_star = interp(environment)
    l_star = interp(conflict)
    r_star = interp(reserve)
    total = l_star + r_star
    if total <= 0:
        raise ValueError("interpolated equal-margin point must have positive total margin")

    return DeepestMiddleWorldPoint(
        environment=e_star,
        conflict_load=l_star,
        reserve=r_star,
        xi=l_star / total,
        depth=min(l_star, r_star),
        interpolation_interval=(i, i + 1),
    )

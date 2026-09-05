"""Map the BALANCE domain directly from matched optimized worldlines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class WorldlinePathResult:
    environment: tuple[float, ...]
    shared_optimum_fitness: tuple[float, ...]
    differentiated_optimum_fitness: tuple[float, ...]
    conflict_load: tuple[float, ...]
    direct_gap: tuple[float, ...]
    states: tuple[str, ...]
    critical_crossings: tuple[float, ...]
    balance_intervals: tuple[tuple[float, float], ...]
    balance_width: float


def _crossing(e0: float, e1: float, y0: float, y1: float) -> float:
    if y1 == y0:
        return (e0 + e1) / 2.0
    return e0 + (-y0) * (e1 - e0) / (y1 - y0)


def analyze_worldline_path(
    environment: Sequence[float],
    shared_optimum_fitness: Sequence[float],
    differentiated_optimum_fitness: Sequence[float],
    conflict_load: Sequence[float],
    *,
    tolerance: float = 1e-9,
) -> WorldlinePathResult:
    """Identify BALANCE directly from two matched optimized worldlines.

    This is the Chapter-2 empirical route that does not require a full BITA
    decomposition into ``s`` and ``K``.  It requires only a common fitness
    scale, an SCH-positive conflict receipt ``L>0``, and the matched optimized
    architecture fitnesses ``W_S*`` and ``W_D*``.
    """
    e = tuple(float(x) for x in environment)
    Ws = tuple(float(x) for x in shared_optimum_fitness)
    Wd = tuple(float(x) for x in differentiated_optimum_fitness)
    L = tuple(float(x) for x in conflict_load)
    tol = float(tolerance)
    n = len(e)

    if n < 2 or not (len(Ws) == len(Wd) == len(L) == n):
        raise ValueError("all paths must have equal length >= 2")
    if any(e[i + 1] <= e[i] for i in range(n - 1)):
        raise ValueError("environment must be strictly increasing")
    if any(x < 0 for x in L):
        raise ValueError("conflict_load must be non-negative")
    if tol <= 0:
        raise ValueError("tolerance must be positive")

    gap = tuple(d - s for s, d in zip(Ws, Wd))
    states = []
    for li, gi in zip(L, gap):
        if li <= tol:
            states.append("SCH_NO_CONFLICT_WORLD" if gi <= tol else "OUTSIDE_REGISTERED_SCH_CONFLICT")
        elif gi < -tol:
            states.append("BALANCE_MIDDLE_WORLD")
        elif abs(gi) <= tol:
            states.append("ARCHITECTURE_CRITICAL_INTERFACE")
        else:
            states.append("BITA_DIFFERENTIATION_WORLD")

    crossings = []
    for i in range(n - 1):
        if L[i] <= tol and L[i + 1] <= tol:
            continue
        g0, g1 = gap[i], gap[i + 1]
        if abs(g0) <= tol and L[i] > tol:
            crossings.append(e[i])
        elif g0 * g1 < 0 and (L[i] > tol or L[i + 1] > tol):
            crossings.append(_crossing(e[i], e[i + 1], g0, g1))
    if abs(gap[-1]) <= tol and L[-1] > tol:
        crossings.append(e[-1])

    intervals = []
    in_balance = False
    start = None
    for i, state in enumerate(states):
        if state == "BALANCE_MIDDLE_WORLD" and not in_balance:
            start = e[i]
            if i > 0 and gap[i - 1] >= 0 and L[i - 1] > tol:
                start = _crossing(e[i - 1], e[i], gap[i - 1], gap[i])
            in_balance = True
        if in_balance and state != "BALANCE_MIDDLE_WORLD":
            end = e[i]
            if i > 0 and gap[i - 1] < 0 and L[i - 1] > tol:
                end = _crossing(e[i - 1], e[i], gap[i - 1], gap[i])
            intervals.append((float(start), float(end)))
            in_balance = False
            start = None
    if in_balance:
        intervals.append((float(start), e[-1]))

    width = sum(b - a for a, b in intervals)
    return WorldlinePathResult(
        environment=e,
        shared_optimum_fitness=Ws,
        differentiated_optimum_fitness=Wd,
        conflict_load=L,
        direct_gap=gap,
        states=tuple(states),
        critical_crossings=tuple(crossings),
        balance_intervals=tuple(intervals),
        balance_width=width,
    )

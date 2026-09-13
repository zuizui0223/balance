"""Map the BALANCE domain directly from matched optimized worldlines."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

from .boundary import analyze_two_margin_path


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
    decomposition into ``s`` and ``K``. It requires only a common fitness
    scale, an SCH-positive conflict receipt ``L>0``, and the matched optimized
    architecture fitnesses ``W_S*`` and ``W_D*``.

    Internally, occupancy is routed through the canonical two-margin primitive
    using ``L`` and the direct reserve ``rho_direct=W_S*-W_D*=-Delta``.
    """
    e = tuple(float(x) for x in environment)
    Ws = tuple(float(x) for x in shared_optimum_fitness)
    Wd = tuple(float(x) for x in differentiated_optimum_fitness)
    L = tuple(float(x) for x in conflict_load)
    tol = float(tolerance)
    n = len(e)

    if n < 2 or not (len(Ws) == len(Wd) == len(L) == n):
        raise ValueError("all paths must have equal length >= 2")
    if not all(math.isfinite(x) for values in (e, Ws, Wd, L) for x in values) or not math.isfinite(tol):
        raise ValueError("all path values and tolerance must be finite")
    if any(e[i + 1] <= e[i] for i in range(n - 1)):
        raise ValueError("environment must be strictly increasing")
    if any(x < 0 for x in L):
        raise ValueError("conflict_load must be non-negative")
    if tol <= 0:
        raise ValueError("tolerance must be positive")

    gap = tuple(d - s for s, d in zip(Ws, Wd))
    reserve = tuple(-value for value in gap)
    boundary = analyze_two_margin_path(e, L, reserve, tolerance=tol)

    states = []
    for point in boundary.points:
        if not point.conflict_active:
            if point.reserve_position == "NEGATIVE":
                states.append("OUTSIDE_REGISTERED_SCH_CONFLICT")
            else:
                states.append("SCH_NO_CONFLICT_WORLD")
        elif point.reserve_position == "POSITIVE":
            states.append("BALANCE_MIDDLE_WORLD")
        elif point.reserve_position == "INTERFACE":
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

    return WorldlinePathResult(
        environment=e,
        shared_optimum_fitness=Ws,
        differentiated_optimum_fitness=Wd,
        conflict_load=L,
        direct_gap=gap,
        states=tuple(states),
        critical_crossings=tuple(crossings),
        balance_intervals=boundary.middle_intervals,
        balance_width=boundary.middle_width,
    )

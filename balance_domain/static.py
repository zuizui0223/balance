"""Static topology and resilience metrics for the BALANCE domain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


class BalancePathTopologyError(ValueError):
    """Raised when registered path constraints imply an impossible topology."""


@dataclass(frozen=True)
class BalancePathResult:
    environment: tuple[float, ...]
    conflict_load: tuple[float, ...]
    decoupling: tuple[float, ...]
    architecture_cost: tuple[float, ...]
    recoverable_loss: tuple[float, ...]
    margin: tuple[float, ...]
    criticality_index: tuple[float | None, ...]
    architecture_pressure_ratio: tuple[float | None, ...]
    reserve: tuple[float, ...]
    states: tuple[str, ...]
    zero_crossings: tuple[float, ...]
    balance_intervals: tuple[tuple[float, float], ...]
    balance_width: float
    integrated_reserve: float
    monotone_no_reentry_conditions_hold: bool
    topology: str


def _crossing(e0: float, e1: float, y0: float, y1: float) -> float:
    if y1 == y0:
        return (e0 + e1) / 2.0
    return e0 + (-y0) * (e1 - e0) / (y1 - y0)


def _level_crossing(e0: float, e1: float, y0: float, y1: float, level: float) -> float:
    return _crossing(e0, e1, y0 - level, y1 - level)


def _linear_value(e0: float, e1: float, y0: float, y1: float, x: float) -> float:
    if x <= e0:
        return y0
    if x >= e1:
        return y1
    t = (x - e0) / (e1 - e0)
    return y0 + t * (y1 - y0)


def analyze_balance_path(
    environment: Sequence[float],
    conflict_load: Sequence[float],
    decoupling: Sequence[float],
    architecture_cost: Sequence[float],
) -> BalancePathResult:
    """Analyse BALANCE occupancy along an ordered environmental path.

    States are defined as:
    - NO_CONFLICT: L == 0
    - BALANCE: L > 0 and Phi=sL-K < 0
    - CRITICAL: L > 0 and Phi == 0 (within numerical tolerance)
    - DIFFERENTIATION: L > 0 and Phi > 0

    ``criticality_index`` follows the manuscript interior coordinate
    ``xi = L / (L + rho)``, where ``rho = K-sL``, and is reported only inside
    BALANCE. ``architecture_pressure_ratio`` preserves the distinct quantity
    ``sL/K`` when ``K>0``.
    """
    e = tuple(float(x) for x in environment)
    L = tuple(float(x) for x in conflict_load)
    s = tuple(float(x) for x in decoupling)
    K = tuple(float(x) for x in architecture_cost)
    n = len(e)
    if n < 2 or not (len(L) == len(s) == len(K) == n):
        raise ValueError("all paths must have equal length >= 2")
    if any(e[i + 1] <= e[i] for i in range(n - 1)):
        raise ValueError("environment must be strictly increasing")
    if any(x < 0 for x in L) or any(x < 0 for x in K):
        raise ValueError("conflict load and architecture cost must be non-negative")
    if any(x < 0 or x > 1 for x in s):
        raise ValueError("decoupling must lie in [0,1]")

    R = tuple(si * li for si, li in zip(s, L))
    phi = tuple(ri - ki for ri, ki in zip(R, K))
    tol = 1e-12
    pressure_ratio = tuple(None if ki == 0 else ri / ki for ri, ki in zip(R, K))
    reserve = tuple(ki - ri for ri, ki in zip(R, K))

    states = []
    for li, pi in zip(L, phi):
        if li <= tol:
            states.append("NO_CONFLICT")
        elif abs(pi) <= tol:
            states.append("CRITICAL")
        elif pi < 0:
            states.append("BALANCE")
        else:
            states.append("DIFFERENTIATION")

    criticality = tuple(
        li / (li + rho) if state == "BALANCE" else None
        for li, rho, state in zip(L, reserve, states)
    )

    crossings = []
    for i in range(n - 1):
        p0, p1 = phi[i], phi[i + 1]
        if abs(p0) <= tol:
            crossings.append(e[i])
        elif p0 * p1 < 0:
            crossings.append(_crossing(e[i], e[i + 1], p0, p1))
    if abs(phi[-1]) <= tol:
        crossings.append(e[-1])

    # BALANCE has two independent boundaries: L>tol and Phi<-tol.  A state
    # transition may be caused by either or both.  Interpolate only quantities
    # that actually bracket their registered boundary, then take the later
    # entry / earlier exit when both constraints change in the same segment.
    intervals = []
    in_balance = False
    start = None
    for i, state in enumerate(states):
        if state == "BALANCE" and not in_balance:
            start = e[i]
            if i > 0:
                candidates = []
                if L[i - 1] <= tol < L[i]:
                    candidates.append(_level_crossing(e[i - 1], e[i], L[i - 1], L[i], tol))
                if phi[i - 1] >= -tol and phi[i] < -tol:
                    candidates.append(_level_crossing(e[i - 1], e[i], phi[i - 1], phi[i], -tol))
                if candidates:
                    start = max(candidates)
            in_balance = True
        if in_balance and state != "BALANCE":
            end = e[i]
            if i > 0:
                candidates = []
                if L[i - 1] > tol >= L[i]:
                    candidates.append(_level_crossing(e[i - 1], e[i], L[i - 1], L[i], tol))
                if phi[i - 1] < -tol and phi[i] >= -tol:
                    candidates.append(_level_crossing(e[i - 1], e[i], phi[i - 1], phi[i], -tol))
                if candidates:
                    end = min(candidates)
            intervals.append((float(start), float(end)))
            in_balance = False
            start = None
    if in_balance:
        intervals.append((float(start), e[-1]))

    width = sum(b - a for a, b in intervals)
    path_width = e[-1] - e[0]
    if width < -tol or width > path_width + tol:
        raise BalancePathTopologyError("BALANCE width lies outside the registered environmental path")

    # Integrate rho on exactly the same clipped BALANCE intervals used for the
    # width estimand.  Linear interpolation makes the clipped trapezoids exact
    # for the sampled reserve path and avoids integrating outside the domain.
    area = 0.0
    for a, b in intervals:
        for i in range(n - 1):
            left = max(a, e[i])
            right = min(b, e[i + 1])
            if right <= left:
                continue
            r0 = _linear_value(e[i], e[i + 1], reserve[i], reserve[i + 1], left)
            r1 = _linear_value(e[i], e[i + 1], reserve[i], reserve[i + 1], right)
            area += 0.5 * (max(r0, 0.0) + max(r1, 0.0)) * (right - left)

    L_nondec = all(L[i + 1] >= L[i] - tol for i in range(n - 1))
    s_nondec = all(s[i + 1] >= s[i] - tol for i in range(n - 1))
    K_noninc = all(K[i + 1] <= K[i] + tol for i in range(n - 1))
    monotone = L_nondec and s_nondec and K_noninc

    nb = len(intervals)
    if nb == 0:
        topology = "NO_BALANCE"
    elif nb == 1:
        topology = "SINGLE_BALANCE_DOMAIN"
    else:
        topology = "REENTRANT_OR_MULTIPLE_BALANCE_DOMAINS"

    if monotone and nb > 1:
        raise BalancePathTopologyError(
            "re-entry is incompatible with registered monotone no-reentry conditions"
        )

    return BalancePathResult(
        environment=e,
        conflict_load=L,
        decoupling=s,
        architecture_cost=K,
        recoverable_loss=R,
        margin=phi,
        criticality_index=criticality,
        architecture_pressure_ratio=pressure_ratio,
        reserve=reserve,
        states=tuple(states),
        zero_crossings=tuple(crossings),
        balance_intervals=tuple(intervals),
        balance_width=width,
        integrated_reserve=area,
        monotone_no_reentry_conditions_hold=monotone,
        topology=topology,
    )

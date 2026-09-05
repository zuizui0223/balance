"""Static topology and resilience metrics for the BALANCE domain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class BalancePathResult:
    environment: tuple[float, ...]
    conflict_load: tuple[float, ...]
    decoupling: tuple[float, ...]
    architecture_cost: tuple[float, ...]
    recoverable_loss: tuple[float, ...]
    margin: tuple[float, ...]
    criticality_index: tuple[float | None, ...]
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
    q = tuple(None if ki == 0 else ri / ki for ri, ki in zip(R, K))
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

    crossings = []
    for i in range(n - 1):
        p0, p1 = phi[i], phi[i + 1]
        if abs(p0) <= tol:
            crossings.append(e[i])
        elif p0 * p1 < 0:
            crossings.append(_crossing(e[i], e[i + 1], p0, p1))
    if abs(phi[-1]) <= tol:
        crossings.append(e[-1])

    intervals = []
    in_balance = False
    start = None
    for i, state in enumerate(states):
        if state == "BALANCE" and not in_balance:
            start = e[i]
            if i > 0 and phi[i - 1] >= 0:
                start = _crossing(e[i - 1], e[i], phi[i - 1], phi[i])
            in_balance = True
        if in_balance and state != "BALANCE":
            end = e[i]
            if i > 0 and phi[i - 1] < 0:
                end = _crossing(e[i - 1], e[i], phi[i - 1], phi[i])
            intervals.append((float(start), float(end)))
            in_balance = False
            start = None
    if in_balance:
        intervals.append((float(start), e[-1]))

    width = sum(b - a for a, b in intervals)
    area = 0.0
    for i in range(n - 1):
        r0 = max(reserve[i], 0.0) if L[i] > 0 else 0.0
        r1 = max(reserve[i + 1], 0.0) if L[i + 1] > 0 else 0.0
        area += 0.5 * (r0 + r1) * (e[i + 1] - e[i])

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
        raise AssertionError("re-entry is incompatible with registered monotone no-reentry conditions")

    return BalancePathResult(
        environment=e,
        conflict_load=L,
        decoupling=s,
        architecture_cost=K,
        recoverable_loss=R,
        margin=phi,
        criticality_index=q,
        reserve=reserve,
        states=tuple(states),
        zero_crossings=tuple(crossings),
        balance_intervals=tuple(intervals),
        balance_width=width,
        integrated_reserve=area,
        monotone_no_reentry_conditions_hold=monotone,
        topology=topology,
    )

"""Static topology and resilience metrics for the BALANCE domain."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
import math
from typing import Sequence

from .boundary import _finite_numeric, analyze_two_margin_path, two_margin_middle_position


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


def _fraction_to_float(value: F, name: str) -> float:
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale units"
        ) from exc
    if not math.isfinite(out):
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale units"
        )
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision; rescale units")
    return out


def _crossing(e0: float, e1: float, y0: float, y1: float) -> float:
    e0_q = F.from_float(e0)
    e1_q = F.from_float(e1)
    y0_q = F.from_float(y0)
    y1_q = F.from_float(y1)
    if y1_q == y0_q:
        crossing_q = (e0_q + e1_q) / 2
    else:
        crossing_q = e0_q + (-y0_q) * (e1_q - e0_q) / (y1_q - y0_q)
    return _fraction_to_float(crossing_q, "critical crossing coordinate")


def _linear_value_fraction(
    e0: float,
    e1: float,
    y0: float,
    y1: float,
    x: float,
) -> F:
    if x <= e0:
        return F.from_float(y0)
    if x >= e1:
        return F.from_float(y1)
    e0_q = F.from_float(e0)
    e1_q = F.from_float(e1)
    y0_q = F.from_float(y0)
    y1_q = F.from_float(y1)
    x_q = F.from_float(x)
    t_q = (x_q - e0_q) / (e1_q - e0_q)
    return y0_q + t_q * (y1_q - y0_q)


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

    Internally, path occupancy is routed through the canonical two-margin
    primitive using ``L`` and ``rho=K-sL=-Phi``.  ``criticality_index`` follows
    the manuscript interior coordinate ``xi = L / (L + rho)`` and is reported
    only inside BALANCE. ``architecture_pressure_ratio`` preserves the distinct
    quantity ``sL/K`` when ``K>0``.
    """
    e = tuple(_finite_numeric(x, f"environment[{i}]") for i, x in enumerate(environment))
    L = tuple(_finite_numeric(x, f"conflict_load[{i}]") for i, x in enumerate(conflict_load))
    s = tuple(_finite_numeric(x, f"decoupling[{i}]") for i, x in enumerate(decoupling))
    K = tuple(_finite_numeric(x, f"architecture_cost[{i}]") for i, x in enumerate(architecture_cost))
    n = len(e)
    if n < 2 or not (len(L) == len(s) == len(K) == n):
        raise ValueError("all paths must have equal length >= 2")
    if any(e[i + 1] <= e[i] for i in range(n - 1)):
        raise ValueError("environment must be strictly increasing")
    if any(x < 0 for x in L) or any(x < 0 for x in K):
        raise ValueError("conflict load and architecture cost must be non-negative")
    if any(x < 0 or x > 1 for x in s):
        raise ValueError("decoupling must lie in [0,1]")

    l_q = tuple(F.from_float(value) for value in L)
    s_q = tuple(F.from_float(value) for value in s)
    k_q = tuple(F.from_float(value) for value in K)
    r_q = tuple(si * li for si, li in zip(s_q, l_q))
    phi_q = tuple(ri - ki for ri, ki in zip(r_q, k_q))
    reserve_q = tuple(ki - ri for ri, ki in zip(r_q, k_q))

    R = tuple(_fraction_to_float(value, "recoverable loss") for value in r_q)
    phi = tuple(_fraction_to_float(value, "architecture margin") for value in phi_q)
    reserve = tuple(_fraction_to_float(value, "architecture reserve") for value in reserve_q)
    tol = 1e-12
    pressure_ratio = tuple(
        None if ki == 0 else _fraction_to_float(ri / ki, "architecture pressure ratio")
        for ri, ki in zip(r_q, k_q)
    )

    boundary = analyze_two_margin_path(e, L, reserve, tolerance=tol)
    states = []
    for point in boundary.points:
        if not point.conflict_active:
            states.append("NO_CONFLICT")
        elif point.reserve_position == "POSITIVE":
            states.append("BALANCE")
        elif point.reserve_position == "INTERFACE":
            states.append("CRITICAL")
        else:
            states.append("DIFFERENTIATION")

    criticality = tuple(
        two_margin_middle_position(li, rho) if state == "BALANCE" else None
        for li, rho, state in zip(L, reserve, states)
    )

    crossings = []
    for i in range(n - 1):
        p0, p1 = phi[i], phi[i + 1]
        if abs(p0) <= tol:
            crossings.append(e[i])
        elif (p0 < 0 < p1) or (p1 < 0 < p0):
            crossings.append(_crossing(e[i], e[i + 1], p0, p1))
    if abs(phi[-1]) <= tol:
        crossings.append(e[-1])

    intervals = boundary.middle_intervals
    width = boundary.middle_width

    # Integrate rho on exactly the same clipped BALANCE intervals used for the
    # width estimand. Linear interpolation makes the clipped trapezoids exact
    # for the sampled reserve path and avoids integrating outside the domain.
    area_q = F(0, 1)
    zero = F(0, 1)
    for a, b in intervals:
        for i in range(n - 1):
            left = max(a, e[i])
            right = min(b, e[i + 1])
            if right <= left:
                continue
            r0_q = _linear_value_fraction(e[i], e[i + 1], reserve[i], reserve[i + 1], left)
            r1_q = _linear_value_fraction(e[i], e[i + 1], reserve[i], reserve[i + 1], right)
            clipped0_q = max(r0_q, zero)
            clipped1_q = max(r1_q, zero)
            width_q = F.from_float(right) - F.from_float(left)
            area_q += (clipped0_q + clipped1_q) * width_q / 2
    area = _fraction_to_float(area_q, "integrated reserve")

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
        balance_intervals=intervals,
        balance_width=width,
        integrated_reserve=area,
        monotone_no_reentry_conditions_hold=monotone,
        topology=topology,
    )

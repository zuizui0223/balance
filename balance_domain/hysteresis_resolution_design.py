"""Design monotone BALANCE sweeps for a target hysteresis-width resolution.

If the forward and reverse maximum forcing increments are ``delta_up`` and
``delta_down``, the finite-step overestimation of hysteresis width is bounded by
``delta_up + delta_down``.  This module allocates a declared total error budget
between two sweep spans to minimize the required integer number of intervals.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite, sqrt


@dataclass(frozen=True)
class HysteresisResolutionDesign:
    forward_span: float
    reverse_span: float
    width_error_budget: float
    forward_intervals: int
    reverse_intervals: int
    total_intervals: int
    forward_step: float
    reverse_step: float
    guaranteed_width_inflation: float
    continuous_optimal_forward_step: float
    continuous_optimal_reverse_step: float
    continuous_interval_lower_bound: float


def optimal_hysteresis_resolution_design(
    *,
    forward_span: float,
    reverse_span: float,
    width_error_budget: float,
) -> HysteresisResolutionDesign:
    """Return the minimum-total-interval two-sweep design.

    For integer interval counts ``n_up,n_down`` the guarantee is

        forward_span/n_up + reverse_span/n_down <= width_error_budget.

    The continuous relaxation allocates step sizes in proportion to square
    roots of sweep spans.  The exact integer optimum is found exhaustively below
    a constructive equal-budget feasible design.
    """
    su = float(forward_span)
    sd = float(reverse_span)
    eta = float(width_error_budget)
    if not all(isfinite(x) for x in (su, sd, eta)):
        raise ValueError("spans and error budget must be finite")
    if su <= 0.0 or sd <= 0.0 or eta <= 0.0:
        raise ValueError("spans and error budget must be positive")

    root_sum = sqrt(su) + sqrt(sd)
    delta_up_cont = eta * sqrt(su) / root_sum
    delta_down_cont = eta * sqrt(sd) / root_sum
    lower_bound = root_sum * root_sum / eta

    # Equal error allocation supplies a finite feasible integer upper bound.
    n_up_eq = max(1, ceil(2.0 * su / eta))
    n_down_eq = max(1, ceil(2.0 * sd / eta))
    best = (n_up_eq + n_down_eq, n_up_eq, n_down_eq)

    # Any better solution has n_up < current best total.  For each n_up, the
    # minimum feasible n_down is determined analytically from the remaining
    # error budget.
    for n_up in range(1, best[0]):
        delta_up = su / n_up
        remaining = eta - delta_up
        if remaining <= 0.0:
            continue
        n_down = max(1, ceil(sd / remaining - 1e-15))
        while su / n_up + sd / n_down > eta + 1e-15:
            n_down += 1
        candidate = (n_up + n_down, n_up, n_down)
        if candidate < best:
            best = candidate

    _, n_up, n_down = best
    delta_up = su / n_up
    delta_down = sd / n_down
    guaranteed = delta_up + delta_down
    if guaranteed > eta + 1e-12:
        raise RuntimeError("integer design failed declared hysteresis-width precision")

    return HysteresisResolutionDesign(
        forward_span=su,
        reverse_span=sd,
        width_error_budget=eta,
        forward_intervals=n_up,
        reverse_intervals=n_down,
        total_intervals=n_up + n_down,
        forward_step=delta_up,
        reverse_step=delta_down,
        guaranteed_width_inflation=guaranteed,
        continuous_optimal_forward_step=delta_up_cont,
        continuous_optimal_reverse_step=delta_down_cont,
        continuous_interval_lower_bound=lower_bound,
    )

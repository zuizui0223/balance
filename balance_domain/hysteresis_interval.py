"""Inverse identification of BALANCE hysteresis from finite forcing resolution.

The forward and reverse architecture-switch thresholds are not observed exactly
when the forcing variable Phi is sampled on a finite monotone grid. This module
turns the declared maximum forcing increments into conservative identification
intervals for the true thresholds and hysteresis width.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class HysteresisInterval:
    observed_forward_switch: float
    observed_reverse_switch: float
    max_up_step: float
    max_down_step: float
    forward_lower: float
    forward_upper: float
    reverse_lower: float
    reverse_upper: float
    observed_width: float
    true_width_lower: float
    true_width_upper: float
    horizon: float | None
    switching_cost_sum_lower: float | None
    switching_cost_sum_upper: float | None


def identify_hysteresis_interval(
    observed_forward_switch: float,
    observed_reverse_switch: float,
    *,
    max_up_step: float,
    max_down_step: float,
    horizon: float | None = None,
) -> HysteresisInterval:
    """Bound true thresholds from monotone finite-step switch observations.

    For an increasing path, the observed first switching point ``F_hat`` obeys

        F_hat - delta_up <= F < F_hat,

    where ``F=C_SD/T >= 0`` is the exact shared->differentiated threshold.

    For a decreasing path, the observed first switching point ``R_hat`` obeys

        R_hat < R <= R_hat + delta_down,

    where ``R=-C_DS/T <= 0`` is the exact differentiated->shared threshold.

    Because a switch is actually observed under a strict threshold rule, both
    crossing-step bounds must be strictly positive: a zero jump would imply an
    empty set such as ``F_hat <= F < F_hat``. Likewise, an observed forward
    switch must occur at positive Phi and an observed reverse switch at negative
    Phi. The returned closed intervals are conservative envelopes of the strict
    sets after intersecting them with ``F>=0`` and ``R<=0``.
    """
    fhat = float(observed_forward_switch)
    rhat = float(observed_reverse_switch)
    du = float(max_up_step)
    dd = float(max_down_step)
    if not all(isfinite(x) for x in (fhat, rhat, du, dd)):
        raise ValueError("switch points and step bounds must be finite")
    if du <= 0.0 or dd <= 0.0:
        raise ValueError("observed strict switches require strictly positive step bounds")
    if fhat <= 0.0:
        raise ValueError("observed forward switch must be positive under non-negative switching cost")
    if rhat >= 0.0:
        raise ValueError("observed reverse switch must be negative under non-negative switching cost")
    if fhat < rhat:
        raise ValueError("observed forward switch must not lie below reverse switch")

    # Intersect the finite-resolution brackets with the model constraints
    # F>=0 and R<=0. The intervals are closed conservative envelopes; the true
    # threshold sets retain their strict side at F_hat / R_hat.
    forward_lower = max(0.0, fhat - du)
    forward_upper = fhat
    reverse_lower = rhat
    reverse_upper = min(0.0, rhat + dd)
    observed_width = fhat - rhat

    # Minimum feasible width uses the smallest forward threshold and largest
    # reverse threshold after sign intersection. Maximum is approached by the
    # two observed outer switch points and is returned as a closed envelope.
    width_lower = forward_lower - reverse_upper
    width_upper = observed_width

    cost_lower = cost_upper = None
    T = None
    if horizon is not None:
        T = float(horizon)
        if not isfinite(T) or T <= 0.0:
            raise ValueError("horizon must be finite and positive")
        # Exact BALANCE width = (C_SD + C_DS)/T.
        cost_lower = T * width_lower
        cost_upper = T * width_upper

    return HysteresisInterval(
        observed_forward_switch=fhat,
        observed_reverse_switch=rhat,
        max_up_step=du,
        max_down_step=dd,
        forward_lower=forward_lower,
        forward_upper=forward_upper,
        reverse_lower=reverse_lower,
        reverse_upper=reverse_upper,
        observed_width=observed_width,
        true_width_lower=width_lower,
        true_width_upper=width_upper,
        horizon=T,
        switching_cost_sum_lower=cost_lower,
        switching_cost_sum_upper=cost_upper,
    )

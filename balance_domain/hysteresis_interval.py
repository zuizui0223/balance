"""Inverse identification of BALANCE hysteresis from finite forcing resolution.

The forward and reverse architecture-switch thresholds are not observed exactly
when the forcing variable Phi is sampled on a finite monotone grid.  This module
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

    where ``F`` is the exact shared->differentiated threshold.

    For a decreasing path, the observed first switching point ``R_hat`` obeys

        R_hat < R <= R_hat + delta_down,

    where ``R`` is the exact differentiated->shared threshold.

    The returned closed intervals are conservative envelopes that include the
    strict endpoints.  Since BALANCE switching costs are non-negative, the true
    hysteresis width is additionally truncated below at zero.
    """
    fhat = float(observed_forward_switch)
    rhat = float(observed_reverse_switch)
    du = float(max_up_step)
    dd = float(max_down_step)
    if not all(isfinite(x) for x in (fhat, rhat, du, dd)):
        raise ValueError("switch points and step bounds must be finite")
    if du < 0.0 or dd < 0.0:
        raise ValueError("step bounds must be non-negative")
    if fhat < rhat:
        raise ValueError("observed forward switch must not lie below reverse switch")

    forward_lower = fhat - du
    forward_upper = fhat
    reverse_lower = rhat
    reverse_upper = rhat + dd
    observed_width = fhat - rhat
    width_lower = max(0.0, observed_width - du - dd)
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

"""Inverse identification of BALANCE hysteresis from finite forcing resolution.

The forward and reverse architecture-switch thresholds are not observed exactly
when the forcing variable Phi is sampled on a finite monotone grid. This module
turns the declared maximum forcing increments into conservative identification
intervals for the true thresholds and hysteresis width.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from math import inf, isfinite, nextafter


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


def _point_to_float(value: F, name: str) -> float:
    """Convert one exact point estimand without inventing 0/inf."""
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale forcing units"
        ) from exc
    if not isfinite(out):
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale forcing units"
        )
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision; rescale forcing units")
    return out


def _lower_bound_to_float(value: F, name: str, *, clamp_zero: bool = False) -> float:
    """Convert an exact lower bound, moving outward only when rounding is inward."""
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale forcing units"
        ) from exc
    if not isfinite(out):
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale forcing units"
        )
    if F.from_float(out) > value:
        out = nextafter(out, -inf)
        if not isfinite(out):
            raise ValueError(
                f"{name} has no finite conservative float lower bound; rescale forcing units"
            )
    if clamp_zero and out < 0.0:
        out = 0.0
    return out


def _upper_bound_to_float(value: F, name: str, *, clamp_zero: bool = False) -> float:
    """Convert an exact upper bound, moving outward only when rounding is inward."""
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale forcing units"
        ) from exc
    if not isfinite(out):
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale forcing units"
        )
    if F.from_float(out) < value:
        out = nextafter(out, inf)
        if not isfinite(out):
            raise ValueError(
                f"{name} has no finite conservative float upper bound; rescale forcing units"
            )
    if clamp_zero and out > 0.0:
        out = 0.0
    return out


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

    All differences and optional horizon rescalings are evaluated exactly at
    the supplied-float level. Point estimands fail closed if they leave the
    finite float surface; lower/upper identification bounds are rounded only in
    the conservative outward direction when required.
    """
    try:
        fhat = float(observed_forward_switch)
        rhat = float(observed_reverse_switch)
        du = float(max_up_step)
        dd = float(max_down_step)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("switch points and step bounds must be finite numeric values") from exc
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

    fhat_q = F.from_float(fhat)
    rhat_q = F.from_float(rhat)
    du_q = F.from_float(du)
    dd_q = F.from_float(dd)
    zero = F(0, 1)

    # Exact mathematical envelopes after intersecting with F>=0 and R<=0.
    forward_lower_q = max(zero, fhat_q - du_q)
    reverse_upper_q = min(zero, rhat_q + dd_q)
    observed_width_q = fhat_q - rhat_q
    width_lower_q = max(zero, forward_lower_q - reverse_upper_q)
    width_upper_q = observed_width_q

    forward_lower = _lower_bound_to_float(
        forward_lower_q, "forward threshold lower bound", clamp_zero=True
    )
    forward_upper = fhat
    reverse_lower = rhat
    reverse_upper = _upper_bound_to_float(
        reverse_upper_q, "reverse threshold upper bound", clamp_zero=True
    )
    observed_width = _point_to_float(observed_width_q, "observed hysteresis width")
    width_lower = _lower_bound_to_float(
        width_lower_q, "true hysteresis width lower bound", clamp_zero=True
    )
    width_upper = _upper_bound_to_float(
        width_upper_q, "true hysteresis width upper bound"
    )

    cost_lower = cost_upper = None
    T = None
    if horizon is not None:
        try:
            T = float(horizon)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("horizon must be finite and positive") from exc
        if not isfinite(T) or T <= 0.0:
            raise ValueError("horizon must be finite and positive")
        t_q = F.from_float(T)
        cost_lower_q = t_q * width_lower_q
        cost_upper_q = t_q * width_upper_q
        cost_lower = _lower_bound_to_float(
            cost_lower_q, "switching cost sum lower bound", clamp_zero=True
        )
        cost_upper = _upper_bound_to_float(
            cost_upper_q, "switching cost sum upper bound"
        )

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

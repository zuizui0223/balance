"""Inverse switching-cost contract from ordered, bracketed forcing records.

This optional route assumes the deterministic, instantaneous switching rule on
one calibrated Phi scale and a fixed payoff horizon. It does not infer costs
from hysteresis area, state frequencies, sampling duration, or an unobserved
switch. None represents an unbounded endpoint, not zero.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from math import isfinite
from typing import Sequence

Record = tuple[float, str]


@dataclass(frozen=True)
class Interval:
    lower: float | None
    upper: float | None
    lower_closed: bool = True
    upper_closed: bool = True


@dataclass(frozen=True)
class SwitchingIdentification:
    forward_threshold: Interval
    reverse_threshold: Interval
    width: Interval
    forward_switch_observed: bool
    reverse_switch_observed: bool
    cost_shared_to_diff: Interval | None
    cost_diff_to_shared: Interval | None
    total_switching_cost: Interval | None
    horizon_bounds: tuple[float, float] | None
    cost_scale_identified: bool
    scope: str


def _interval(lo, hi, lc=True, uc=True) -> Interval:
    if lo is not None and hi is not None:
        if lo > hi or (lo == hi and not (lc and uc)):
            raise ValueError("records incompatible with nonnegative costs and strict switching")
    return Interval(lo, hi, lc if lo is not None else False, uc if hi is not None else False)


def _threshold(records: Sequence[Record], forward: bool) -> tuple[Interval, bool]:
    rows=tuple((float(phi), state) for phi,state in records)
    old, new=("shared","differentiated") if forward else ("differentiated","shared")
    if not rows or rows[0][1] != old:
        raise ValueError(f"path must begin with a recorded {old} state before switching")
    if any(not isfinite(phi) or state not in {old,new} for phi,state in rows):
        raise ValueError("forcing records must be finite and have valid architecture states")
    if any((b<a if forward else b>a) for (a,_),(b,_) in zip(rows,rows[1:])):
        raise ValueError("forcing path must be monotone in its declared direction")
    switch=next((i for i,(_,s) in enumerate(rows) if s==new), None)
    if switch is not None and any(s!=new for _,s in rows[switch:]):
        raise ValueError("recrossing on a monotone path violates the deterministic contract")
    stay=rows[-1][0] if switch is None else rows[switch-1][0]
    moved=None if switch is None else rows[switch][0]
    if forward:
        return _interval(max(0.0,stay), moved, True, False), switch is not None
    return _interval(moved, min(0.0,stay), False, True), switch is not None


def _scale_nonnegative(interval: Interval, tlo: float, thi: float) -> Interval:
    return _interval(
        None if interval.lower is None else tlo*interval.lower,
        None if interval.upper is None else thi*interval.upper,
        interval.lower_closed, interval.upper_closed,
    )


def identify_switching_records(
    upward: Sequence[Record], downward: Sequence[Record], *,
    common_phi_scale: str,
    fixed_context: str,
    instantaneous_rule_declared: bool,
    horizon_bounds: tuple[float,float] | None = None,
) -> SwitchingIdentification:
    """Intersect stay/switch inequalities and optionally recover cost intervals.

    F=C_SD/T >= 0; R=-C_DS/T <= 0. Increasing path: last stay <= F < first switch.
    Decreasing path: first switch < R <= last stay. No-switch paths are censored.
    ``horizon_bounds`` must be independently supplied; sampling time is not T.
    Bounds are exact conditional on error-free Phi and state labels and the
    declared rule, not confidence intervals for noisy field observations.
    """
    if (not isinstance(common_phi_scale,str) or not common_phi_scale.strip()
            or not isinstance(fixed_context,str) or not fixed_context.strip()
            or instantaneous_rule_declared is not True):
        raise ValueError("declare common Phi scale, fixed context and instantaneous switching")
    f, fs = _threshold(upward,True)
    r, rs = _threshold(downward,False)
    width=_interval(
        f.lower-r.upper,
        None if f.upper is None or r.lower is None else f.upper-r.lower,
        f.lower_closed and r.upper_closed,
        f.upper_closed and r.lower_closed,
    )
    cf=cr=ct=None
    horizon=None
    if horizon_bounds is not None:
        lo,hi=map(float,horizon_bounds)
        if not all(isfinite(v) for v in (lo,hi)) or not 0<lo<=hi:
            raise ValueError("independent horizon bounds must satisfy 0 < lower <= upper")
        horizon=(lo,hi)
        cf=_scale_nonnegative(f,lo,hi)
        reverse_cost_ratio=_interval(-r.upper,None if r.lower is None else -r.lower,
                                     r.upper_closed,r.lower_closed)
        cr=_scale_nonnegative(reverse_cost_ratio,lo,hi)
        ct=_scale_nonnegative(width,lo,hi)
    return SwitchingIdentification(
        f,r,width,fs,rs,cf,cr,ct,horizon,
        horizon is not None and horizon[0]==horizon[1],
        "conditional_error_free_brackets; unknown_horizon_identifies_cost_over_horizon_only"
        if horizon is None else "conditional_error_free_brackets_with_independent_horizon",
    )


def synthetic_example() -> dict:
    r=identify_switching_records(
        [(0.05,"shared"),(0.10,"shared"),(0.12,"differentiated")],
        [(0.01,"differentiated"),(-0.05,"differentiated"),(-0.08,"shared")],
        common_phi_scale="synthetic payoff/time units", fixed_context="synthetic environment",
        instantaneous_rule_declared=True, horizon_bounds=(10,10),
    )
    return {"data_kind":"synthetic_bracket_witness", "receipt":asdict(r)}


if __name__ == "__main__":
    print(json.dumps(synthetic_example(),indent=2,allow_nan=False))

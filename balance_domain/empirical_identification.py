"""Inverse switching-cost contract from ordered, bracketed forcing records.

This optional route assumes the deterministic, instantaneous switching rule on
one calibrated Phi scale and a fixed payoff horizon. It does not infer costs
from hysteresis area, state frequencies, sampling duration, or an unobserved
switch. ``None`` represents an unbounded endpoint, not zero; numeric interval
endpoints are always finite.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from math import isfinite
from typing import Sequence

Record = tuple[float, str]
_MISSING_IDENTIFIERS = {"none", "null", "nan", "required_before_use"}


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
    common_phi_scale: str
    fixed_context: str
    scope: str


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a non-empty frozen string identifier")
    text = value.strip()
    if not text or text.casefold() in _MISSING_IDENTIFIERS:
        raise ValueError(f"{name} must be frozen before use")
    return text


def _finite_number(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric, not boolean")
    try:
        out = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite numeric value") from exc
    if not isfinite(out):
        raise ValueError(f"{name} must be a finite numeric value")
    return out


def _interval(lo, hi, lc=True, uc=True) -> Interval:
    for value in (lo, hi):
        if value is not None and not isfinite(value):
            raise ValueError("interval endpoints must be finite or None for unbounded")
    if lo is not None and hi is not None:
        if lo > hi or (lo == hi and not (lc and uc)):
            raise ValueError("records incompatible with nonnegative costs and strict switching")
    return Interval(lo, hi, lc if lo is not None else False, uc if hi is not None else False)


def _threshold(records: Sequence[Record], forward: bool) -> tuple[Interval, bool]:
    rows = []
    try:
        for index, record in enumerate(records):
            phi_raw, state = record
            phi = _finite_number(phi_raw, f"forcing record {index} Phi")
            rows.append((phi, state))
    except (TypeError, ValueError) as exc:
        if isinstance(exc, ValueError) and "forcing record" in str(exc):
            raise
        raise ValueError("forcing records must be (Phi, state) pairs") from exc
    rows = tuple(rows)
    old, new = ("shared", "differentiated") if forward else ("differentiated", "shared")
    if not rows or rows[0][1] != old:
        raise ValueError(f"path must begin with a recorded {old} state before switching")
    if any(state not in {old, new} for _, state in rows):
        raise ValueError("forcing records must have valid architecture states")
    if any((b < a if forward else b > a) for (a, _), (b, _) in zip(rows, rows[1:])):
        raise ValueError("forcing path must be monotone in its declared direction")
    switch = next((i for i, (_, state) in enumerate(rows) if state == new), None)
    if switch is not None and any(state != new for _, state in rows[switch:]):
        raise ValueError("recrossing on a monotone path violates the deterministic contract")
    stay = rows[-1][0] if switch is None else rows[switch - 1][0]
    moved = None if switch is None else rows[switch][0]
    if forward:
        return _interval(max(0.0, stay), moved, True, False), switch is not None
    return _interval(moved, min(0.0, stay), False, True), switch is not None


def _scale_nonnegative(interval: Interval, tlo: float, thi: float) -> Interval:
    return _interval(
        None if interval.lower is None else tlo * interval.lower,
        None if interval.upper is None else thi * interval.upper,
        interval.lower_closed,
        interval.upper_closed,
    )


def identify_switching_records(
    upward: Sequence[Record],
    downward: Sequence[Record],
    *,
    common_phi_scale: str,
    fixed_context: str,
    instantaneous_rule_declared: bool,
    horizon_bounds: tuple[float, float] | None = None,
) -> SwitchingIdentification:
    """Intersect stay/switch inequalities and optionally recover cost intervals.

    ``F=C_SD/T >= 0`` and ``R=-C_DS/T <= 0``. Increasing path: last stay
    ``<= F <`` first switch. Decreasing path: first switch ``< R <=`` last stay.
    No-switch paths are censored. ``horizon_bounds`` must be independently
    supplied; sampling time is not ``T``.

    Bounds are exact conditional on error-free Phi and state labels and the
    declared rule, not confidence intervals for noisy field observations.
    ``None`` is the only representation of an unbounded endpoint. If finite
    threshold/horizon inputs overflow the numeric representation while deriving
    a width or cost interval, the receipt fails closed rather than emitting
    ``inf`` as if it were a finite identified endpoint.

    The calibrated Phi-scale label and fixed-context identifier are frozen into
    the returned receipt. Placeholder identifiers are rejected so a numerical
    interval cannot become detached from the conditions under which it was
    identified.
    """
    scale = _required_text(common_phi_scale, "common_phi_scale")
    context = _required_text(fixed_context, "fixed_context")
    if instantaneous_rule_declared is not True:
        raise ValueError("declare common Phi scale, fixed context and instantaneous switching")

    f, fs = _threshold(upward, True)
    r, rs = _threshold(downward, False)
    width = _interval(
        f.lower - r.upper,
        None if f.upper is None or r.lower is None else f.upper - r.lower,
        f.lower_closed and r.upper_closed,
        f.upper_closed and r.lower_closed,
    )

    cf = cr = ct = None
    horizon = None
    if horizon_bounds is not None:
        try:
            lo_raw, hi_raw = horizon_bounds
        except (TypeError, ValueError) as exc:
            raise ValueError("horizon_bounds must contain exactly two finite numeric values") from exc
        lo = _finite_number(lo_raw, "horizon lower bound")
        hi = _finite_number(hi_raw, "horizon upper bound")
        if not 0 < lo <= hi:
            raise ValueError("independent horizon bounds must satisfy 0 < lower <= upper")
        horizon = (lo, hi)
        cf = _scale_nonnegative(f, lo, hi)
        reverse_cost_ratio = _interval(
            -r.upper,
            None if r.lower is None else -r.lower,
            r.upper_closed,
            r.lower_closed,
        )
        cr = _scale_nonnegative(reverse_cost_ratio, lo, hi)
        ct = _scale_nonnegative(width, lo, hi)

    return SwitchingIdentification(
        forward_threshold=f,
        reverse_threshold=r,
        width=width,
        forward_switch_observed=fs,
        reverse_switch_observed=rs,
        cost_shared_to_diff=cf,
        cost_diff_to_shared=cr,
        total_switching_cost=ct,
        horizon_bounds=horizon,
        cost_scale_identified=horizon is not None and horizon[0] == horizon[1],
        common_phi_scale=scale,
        fixed_context=context,
        scope=(
            "conditional_error_free_brackets; unknown_horizon_identifies_cost_over_horizon_only"
            if horizon is None
            else "conditional_error_free_brackets_with_independent_horizon"
        ),
    )


def synthetic_example() -> dict:
    result = identify_switching_records(
        [(0.05, "shared"), (0.10, "shared"), (0.12, "differentiated")],
        [(0.01, "differentiated"), (-0.05, "differentiated"), (-0.08, "shared")],
        common_phi_scale="synthetic payoff/time units",
        fixed_context="synthetic environment",
        instantaneous_rule_declared=True,
        horizon_bounds=(10, 10),
    )
    return {"data_kind": "synthetic_bracket_witness", "receipt": asdict(result)}


if __name__ == "__main__":
    print(json.dumps(synthetic_example(), indent=2, allow_nan=False))

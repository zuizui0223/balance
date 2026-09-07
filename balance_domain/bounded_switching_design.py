"""Bounded-Phi switching identification and reset-enabled minimax refinement.

State labels, fixed context, instantaneous switching and monotonicity of the
latent forcing are assumptions. Only Phi uncertainty is represented here. This
is a separate optional route; it does not modify the existing switching rule.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction as F
import json
from math import inf, isfinite, nextafter
from typing import Sequence

Record = tuple[object, object, str]  # true Phi in [lower,upper], observed state


def _q(value: object) -> F:
    if isinstance(value, bool):
        raise ValueError("booleans are not numeric bounds")
    try:
        return F(value)
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
        raise ValueError("bounds must be finite real rational-compatible numbers") from exc


def _out(value: F, upper: bool) -> float:
    try:
        v = float(value)
    except OverflowError as exc:
        raise ValueError("output overflow; rescale input units") from exc
    if not isfinite(v):
        raise ValueError("output overflow; rescale input units")
    if (F(v) < value if upper else F(v) > value):
        v = nextafter(v, inf if upper else -inf)
    if not isfinite(v):
        raise ValueError("outward enclosure overflow")
    return v


@dataclass(frozen=True)
class ThresholdBand:
    lower: float
    upper: float | None
    lower_closed: bool
    upper_closed: bool
    exact_lower: str
    exact_upper: str | None


def _band(lo: F, hi: F | None, lc=True, uc=False) -> ThresholdBand:
    if hi is not None and (lo > hi or (lo == hi and not (lc and uc))):
        raise ValueError("empty threshold set under strict switching and nonnegative costs")
    return ThresholdBand(_out(lo, False), None if hi is None else _out(hi, True),
                         lc, uc if hi is not None else False,
                         str(lo), None if hi is None else str(hi))


def _ratio(records: Sequence[Record], forward: bool) -> tuple[ThresholdBand, bool]:
    old, new = ("shared", "differentiated") if forward else ("differentiated", "shared")
    rows = []
    for lower, upper, state in records:
        lo, hi = _q(lower), _q(upper)
        if lo > hi or state not in (old, new):
            raise ValueError("invalid forcing band or architecture state")
        rows.append((lo, hi, state) if forward else (-hi, -lo, state))
    if not rows or rows[0][2] != old:
        raise ValueError("a preswitch stay record in the old architecture is required")
    first = next((i for i, row in enumerate(rows) if row[2] == new), None)
    if first is not None and any(row[2] != new for row in rows[first:]):
        raise ValueError("state recrossing violates the monotone instantaneous rule")
    # These are sharp marginal bounds of an ordered sequence in closed bands.
    prefix = []
    running = rows[0][0]
    for lo, hi, _ in rows:
        running = max(running, lo)
        if running > hi:
            raise ValueError("forcing bands admit no latent monotone path")
        prefix.append(running)
    suffix = [F(0)]*len(rows)
    running = rows[-1][1]
    for i in range(len(rows)-1, -1, -1):
        running = min(running, rows[i][1])
        suffix[i] = running
    stay_index = len(rows)-1 if first is None else first-1
    lo = max(F(0), prefix[stay_index])
    hi = None if first is None else suffix[first]
    return _band(lo, hi), first is not None


@dataclass(frozen=True)
class BoundedSwitchingReceipt:
    forward_cost_over_horizon: ThresholdBand
    reverse_cost_over_horizon: ThresholdBand
    hysteresis_width: ThresholdBand
    forward_switch_observed: bool
    reverse_switch_observed: bool
    total_cost: ThresholdBand | None
    common_phi_scale: str
    fixed_context: str
    scope: str = "bounded_Phi_exact_states_latent_monotone_fixed_horizon_and_instantaneous_rule"


def identify_bounded_switching(
    upward: Sequence[Record], downward: Sequence[Record], *,
    common_phi_scale: str, fixed_context: str,
    latent_monotone_and_instantaneous_declared: bool,
    horizon_bounds: tuple[object, object] | None = None,
) -> BoundedSwitchingReceipt:
    """Project all compatible true forcing paths to two nonnegative thresholds.

    The reverse band represents c_R=-R=C_DS/T, not signed reverse Phi. Thus
    W=c_F+c_R. Correlations beyond latent monotonicity are not assumed; supplying
    correlated measurement errors gives conservative outer projections.
    """
    if (not isinstance(common_phi_scale, str) or not common_phi_scale.strip()
            or not isinstance(fixed_context, str) or not fixed_context.strip()
            or latent_monotone_and_instantaneous_declared is not True):
        raise ValueError("declare scale, context and latent monotone instantaneous rule")
    f, fs = _ratio(upward, True)
    r, rs = _ratio(downward, False)
    lo = F(f.exact_lower)+F(r.exact_lower)
    hi = (None if f.exact_upper is None or r.exact_upper is None
          else F(f.exact_upper)+F(r.exact_upper))
    width = _band(lo, hi)
    cost = None
    if horizon_bounds is not None:
        tl, th = (_q(v) for v in horizon_bounds)
        if not 0 < tl <= th:
            raise ValueError("independent horizon bounds must satisfy 0 < lower <= upper")
        cost = _band(tl*lo, None if hi is None else th*hi)
    return BoundedSwitchingReceipt(f, r, width, fs, rs, cost, common_phi_scale, fixed_context)


@dataclass(frozen=True)
class RefinementOption:
    direction: str
    query_cost_ratio_coordinate: str
    query_phi: float
    query_phi_exact: str
    current_span: float
    worst_case_next_span: float
    guaranteed_span_reduction: float
    assumed_query_error: float


@dataclass(frozen=True)
class RefinementPlan:
    options: tuple[RefinementOption, ...]
    best_directions: tuple[str, ...]
    guaranteed_width_span_reduction: float
    status: str
    reset_required: bool = True


def plan_reset_refinement(
    receipt: BoundedSwitchingReceipt, *, forward_query_error: object,
    reverse_query_error: object, matched_reset_available_declared: bool,
) -> RefinementPlan:
    """Minimize worst-case width uncertainty with one reset-enabled query.

    For threshold span w and bounded query error e, the midpoint query leaves
    worst-case span min(w,w/2+e); guaranteed reduction is max(0,w/2-e).
    A repeatable reset to the OLD state is essential. This is not a valid
    bisection protocol for an irreversible, unreset one-way trajectory.
    """
    if matched_reset_available_declared is not True:
        raise ValueError("matched reset to each old architecture must be declared available")
    options, gains = [], []
    for name, band, error in (("forward", receipt.forward_cost_over_horizon, forward_query_error),
                             ("reverse", receipt.reverse_cost_over_horizon, reverse_query_error)):
        e = _q(error)
        if e < 0:
            raise ValueError("query error must be nonnegative")
        if band.exact_upper is None:
            raise ValueError("finite preswitch/switch brackets are needed for midpoint design")
        lo, hi = F(band.exact_lower), F(band.exact_upper)
        w, q = hi-lo, (hi+lo)/2
        remaining = min(w, w/2+e)
        gain = w-remaining
        phi = q if name == "forward" else -q
        options.append(RefinementOption(name, str(q), float(phi), str(phi),
                                         _out(w, True), _out(remaining, True),
                                         _out(gain, False), _out(e, True)))
        gains.append(gain)
    best = max(gains)
    names = tuple(o.direction for o, gain in zip(options, gains) if gain == best) if best > 0 else ()
    return RefinementPlan(tuple(options), names, _out(best, False),
                          "guaranteed_refinement" if best > 0 else "query_error_floor")


def synthetic_example() -> dict:
    receipt = identify_bounded_switching(
        [("0.095", "0.105", "shared"), ("0.115", "0.125", "differentiated")],
        [("-0.055", "-0.045", "differentiated"), ("-0.085", "-0.075", "shared")],
        common_phi_scale="synthetic payoff units", fixed_context="synthetic fixed context",
        latent_monotone_and_instantaneous_declared=True, horizon_bounds=(10, 10),
    )
    plan = plan_reset_refinement(receipt, forward_query_error="0.005", reverse_query_error="0.005",
                                 matched_reset_available_declared=True)
    return {"data_kind": "synthetic_bounded_Phi", "identification": asdict(receipt),
            "refinement": asdict(plan)}


if __name__ == "__main__":
    print(json.dumps(synthetic_example(), indent=2, allow_nan=False))

"""Finite-budget extension of reset-enabled bounded-Phi threshold design.

The objective is total threshold-span uncertainty, not hysteresis area or a
posterior variance. This is exact in the Cartesian bounded-adversarial reset
model with fixed directional query errors and additive integer acquisition costs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from fractions import Fraction as F
import json

from .bounded_switching_design import (
    BoundedSwitchingReceipt, _band, _out, _q, identify_bounded_switching,
)


@dataclass(frozen=True)
class BudgetAllocation:
    budget_cap: int
    spent: int
    forward_queries: int
    reverse_queries: int
    forward_worst_span_exact: str
    reverse_worst_span_exact: str
    width_worst_span_exact: str
    width_worst_span_upper: float
    guaranteed_reduction_lower: float


@dataclass(frozen=True)
class BudgetedRefinementReceipt:
    optimal: BudgetAllocation
    frontier: tuple[BudgetAllocation, ...]
    limiting_span_exact: str
    limiting_span_lower: float
    target_span_exact: str | None
    minimum_budget_for_target: int | None
    target_status: str
    forward_query_error_exact: str
    reverse_query_error_exact: str
    scope: str = "Cartesian_threshold_bands_matched_resets_fixed_directional_errors_integer_costs"


def _count(value: int, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def worst_span_after_queries(span: object, error: object, count: int) -> F:
    """Exact n-query span: min(w, 2e + (w-2e)/2**n)."""
    w, e = _q(span), _q(error)
    n = _count(count, "query count")
    if w < 0 or e < 0:
        raise ValueError("span and query error must be nonnegative")
    return w if w <= 2*e else 2*e+(w-2*e)/(2**n)


def plan_budgeted_reset_refinement(
    receipt: BoundedSwitchingReceipt, *, budget: int,
    forward_query_error: object, reverse_query_error: object,
    matched_reset_available_declared: bool,
    forward_cost: int = 1, reverse_cost: int = 1,
    target_width_span: object | None = None,
) -> BudgetedRefinementReceipt:
    """Allocate the whole integer budget, returning every smaller-budget optimum.

    For each direction n repeated midpoint queries leave the stated worst span.
    Minimize their sum over c_F*n_F+c_R*n_R <= budget. Marginal gains halve;
    largest immediate gain is optimal for equal costs. Gain/cost greediness is
    NOT assumed for unequal indivisible costs. Unused budget is permitted.
    Future nominal query locations must be recomputed after each selected
    outcome from the updated bracket, not from an invented future path.
    """
    B = _count(budget, "budget")
    cf, cr = _count(forward_cost, "forward cost", 1), _count(reverse_cost, "reverse cost", 1)
    if B > 2000:
        raise ValueError("exact frontier solver permits budget <= 2000 units")
    if matched_reset_available_declared is not True:
        raise ValueError("matched resets to the old architectures must be declared available")
    ef, er = _q(forward_query_error), _q(reverse_query_error)
    if min(ef, er) < 0:
        raise ValueError("query errors must be nonnegative")
    bands = receipt.forward_cost_over_horizon, receipt.reverse_cost_over_horizon
    if any(b.exact_upper is None for b in bands):
        raise ValueError("finite threshold brackets required before budget allocation")
    wf, wr = (F(b.exact_upper)-F(b.exact_lower) for b in bands)
    if min(wf, wr) < 0:
        raise ValueError("invalid negative threshold span")
    fs = tuple(worst_span_after_queries(wf, ef, n) for n in range(B//cf+1))
    rs = tuple(worst_span_after_queries(wr, er, n) for n in range(B//cr+1))
    records = []
    for cap in range(B+1):
        options = []
        for nf in range(cap//cf+1):
            # With positive reducible span, all affordable remaining reverse
            # queries improve the bound; otherwise spending on reverse is wasteful.
            nr = (cap-cf*nf)//cr if wr > 2*er else 0
            options.append((fs[nf]+rs[nr], cf*nf+cr*nr, nf+nr, nf, nr))
        total, spent, _, nf, nr = min(options)
        records.append(BudgetAllocation(cap, spent, nf, nr, str(fs[nf]), str(rs[nr]),
            str(total), _out(total, True), _out(wf+wr-total, False)))
    floor = min(wf, 2*ef)+min(wr, 2*er)
    target = None if target_width_span is None else _q(target_width_span)
    if target is not None and target < 0:
        raise ValueError("target span must be nonnegative")
    first, status = None, "not_requested"
    if target is not None:
        first = next((r.budget_cap for r in records if F(r.width_worst_span_exact) <= target), None)
        if first is not None:
            status = "attainable_within_budget"
        elif target < floor or (target == floor and (wf > 2*ef or wr > 2*er)):
            status = "unattainable_in_finite_queries_under_declared_error_model"
        else:
            status = "not_reached_within_budget_cap"
    return BudgetedRefinementReceipt(records[-1], tuple(records), str(floor), _out(floor, False),
        None if target is None else str(target), first, status, str(ef), str(er))


def condition_reset_outcome(
    receipt: BoundedSwitchingReceipt, *, direction: str, query_phi: object,
    query_error: object, observed_state: str, matched_reset_available_declared: bool,
    horizon_bounds: tuple[object, object] | None = None,
) -> BoundedSwitchingReceipt:
    """Update only a selected reset query, then permit replanning on actual data.

    Bounds concern the unobserved true command, not state-label error. Absolute
    costs are reprojected only when independent horizon bounds are supplied
    again; the old receipt does not store enough horizon provenance to infer T.
    """
    if direction not in ("forward", "reverse"):
        raise ValueError("direction must be forward or reverse")
    if matched_reset_available_declared is not True:
        raise ValueError("matched reset must be declared available")
    old, new = (("shared", "differentiated") if direction == "forward"
                else ("differentiated", "shared"))
    if observed_state not in (old, new):
        raise ValueError("observed state must be shared or differentiated")
    e, phi = _q(query_error), _q(query_phi)
    if e < 0:
        raise ValueError("query error must be nonnegative")
    q = phi if direction == "forward" else -phi
    band = (receipt.forward_cost_over_horizon if direction == "forward"
            else receipt.reverse_cost_over_horizon)
    lo, hi = F(band.exact_lower), None if band.exact_upper is None else F(band.exact_upper)
    if observed_state == old:
        lo = max(lo, q-e)
    else:
        hi = q+e if hi is None else min(hi, q+e)
    updated = _band(lo, hi)
    fb = updated if direction == "forward" else receipt.forward_cost_over_horizon
    rb = updated if direction == "reverse" else receipt.reverse_cost_over_horizon
    wl = F(fb.exact_lower)+F(rb.exact_lower)
    wh = (None if fb.exact_upper is None or rb.exact_upper is None
          else F(fb.exact_upper)+F(rb.exact_upper))
    cost = None
    if horizon_bounds is not None:
        tl, th = map(_q, horizon_bounds)
        if not 0 < tl <= th:
            raise ValueError("independent horizon bounds must satisfy 0 < lower <= upper")
        cost = _band(tl*wl, None if wh is None else th*wh)
    return replace(receipt, forward_cost_over_horizon=fb, reverse_cost_over_horizon=rb,
                   hysteresis_width=_band(wl, wh), total_cost=cost,
                   forward_switch_observed=receipt.forward_switch_observed or
                       (direction == "forward" and observed_state == new),
                   reverse_switch_observed=receipt.reverse_switch_observed or
                       (direction == "reverse" and observed_state == new))


def synthetic_example() -> dict:
    receipt = identify_bounded_switching(
        [("0.095", "0.105", "shared"), ("0.115", "0.125", "differentiated")],
        [("-0.055", "-0.045", "differentiated"), ("-0.085", "-0.075", "shared")],
        common_phi_scale="synthetic units", fixed_context="synthetic fixed context",
        latent_monotone_and_instantaneous_declared=True)
    result = plan_budgeted_reset_refinement(receipt, budget=4,
        forward_query_error="0.005", reverse_query_error="0.005",
        matched_reset_available_declared=True, target_width_span="0.033")
    return {"data_kind": "synthetic_budget_frontier", "receipt": asdict(result)}


if __name__ == "__main__":
    print(json.dumps(synthetic_example(), indent=2, allow_nan=False))

"""Source-pollen cohort quality extension for BALANCE prospective timing tests.

Adds a *hypothetical* relative contribution q>=0 for pollen released after
the first event. It is NOT an empirically measured viability or paternity
fraction. Both pollen cohorts contribute to physical mass conservation even
when the second cohort has reduced effective siring opportunity.

No U2/U6 source receipts, architecture outcomes, or original data are used.
"""
from __future__ import annotations

from math import isfinite
from .pollen_supply_opportunity import simulate_visitor_order


def _positive_finite(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{name} must be a finite, nonnegative number")
    v = float(value)
    if not isfinite(v) or v < 0:
        raise ValueError(f"{name} must be a finite, nonnegative number")
    return v


def _frac(name: str, value: object) -> float:
    v = _positive_finite(name, value)
    if v > 1:
        raise ValueError(f"{name} must lie between zero and one")
    return v


def track_two_pollen_cohorts(
    *,
    order: str,
    total_pollen: float,
    delayed_fraction: float,
    legitimate_pickup_fraction: float,
    thief_pickup_fraction: float,
    late_relative_effective_contribution: float,
    legitimate_transfer_efficiency: float = 1.0,
) -> dict:
    """Track exposed early and late stock separately through three visits.

    Exactly two legitimate visitors (L) and one thief (T). A fraction `d`
    of the initial pollen is held back until immediately after visit one.
    Both cohorts undergo the SAME fraction removed per visiting agent.
    The late cohort has a hypothetical relative effectiveness q >= 0.
    A test of q=1 must reproduce the original unweighted closed-stock model.
    """
    if not isinstance(order, str) or len(order) != 3 or sorted(order) != ["L", "L", "T"]:
        raise ValueError("order must contain exactly two L and one T")
    P = _positive_finite("total_pollen", total_pollen)
    d = _frac("delayed_fraction", delayed_fraction)
    a = _frac("legitimate_pickup_fraction", legitimate_pickup_fraction)
    b = _frac("thief_pickup_fraction", thief_pickup_fraction)
    q = _positive_finite("late_relative_effective_contribution", late_relative_effective_contribution)
    eta = _frac("legitimate_transfer_efficiency", legitimate_transfer_efficiency)
    early = P*(1-d)
    late = 0.0
    early_export = 0.0
    late_export = 0.0
    theft = 0.0
    snapshots = []
    for index, visitor in enumerate(order):
        before = early + late
        taken_early = (a if visitor == "L" else b)*early
        taken_late = (a if visitor == "L" else b)*late
        early -= taken_early
        late -= taken_late
        if visitor == "L":
            early_export += taken_early
            late_export += taken_late
        else:
            theft += taken_early + taken_late
        if index == 0:
            late += P*d
        snapshots.append({
            "visit_index": index+1,
            "visitor": visitor,
            "stock_before": before,
            "early_removed": taken_early,
            "late_removed": taken_late,
            "stock_after": early+late,
        })
    removed_legitimate = early_export + late_export
    weighted = eta*(early_export + q*late_export)
    conservation = P - (early + late + removed_legitimate + theft)
    if abs(conservation) > 1e-9 * max(1, P):
        raise ValueError("Closed source mass balance violated")
    if any(not isfinite(v) for v in [removed_legitimate, weighted, theft, conservation]):
        raise ValueError("Nonfinite output")
    return {
        "order": order,
        "physical_total_pollen": P,
        "late_relative_contribution": q,
        "early_legitimate_pollen_removed": early_export,
        "late_legitimate_pollen_removed": late_export,
        "legitimate_pollen_removed_total": removed_legitimate,
        "thief_pollen_removed": theft,
        "pollen_leftover": early + late,
        "quality_weighted_export_proxy": weighted,
        "physical_mass_balance_residual": conservation,
        "trace": snapshots,
        "claim_ceiling": "synthetic_quality_weighted_pollen_export_not_genetic_siring",
    }


def _closed_form_delta(
    order: str,
    *,
    P: float, a: float, b: float, d: float, eta: float, q: float,
) -> float:
    """A model-internal identity, not a newly discovered ecological law."""
    if order == "TLL":
        return P*eta*(2*a - a*a)*d*(q - (1-b))
    if order == "LTL":
        return P*eta*a*d*(q*(1-b) - 1 - (1-b)*(1-a))
    raise ValueError("Closed form registered only for TLL and LTL")


def scenario_with_quality(
    *,
    P: float = 100,
    a: float = 0.3,
    b: float = 0.5,
    d: float = 0.5,
    eta: float = 1.0,
    q: float,
) -> dict:
    """Predict raw release benefit, theft-adjusted effect, and triple contrast."""
    # Force all inputs through same physical constraints as cohort simulator.
    _positive_finite("P", P)
    for name, val in (("a", a), ("b", b), ("d", d), ("eta", eta)):
        _frac(name, val)
    _positive_finite("q", q)
    if P <= 0 or a <= 0 or b <= 0 or d <= 0:
        raise ValueError("Threshold example needs positive P, a, b, d")
    differences = {}
    for order in ("TLL", "LTL"):
        by_thief = {}
        for removal, label in ((0.0, "sham"), (b, "theft")):
            common = dict(
                order=order, total_pollen=P,
                legitimate_pickup_fraction=a,
                thief_pickup_fraction=removal,
                late_relative_effective_contribution=q,
                legitimate_transfer_efficiency=eta,
            )
            delayed = track_two_pollen_cohorts(**common, delayed_fraction=d)
            burst = track_two_pollen_cohorts(**common, delayed_fraction=0.0)
            gap = delayed["quality_weighted_export_proxy"] - burst["quality_weighted_export_proxy"]
            algebra = _closed_form_delta(order, P=P, a=a, b=removal, d=d, eta=eta, q=q)
            if abs(gap-algebra) > 1e-8*max(1, P):
                raise ValueError("Cohort model disagrees with registered algebra")
            by_thief[label] = {
                "delayed_minus_burst": gap,
                "closed_form_checked": True,
            }
        differences[order] = by_thief
    interaction = (
        differences["TLL"]["theft"]["delayed_minus_burst"]
        - differences["TLL"]["sham"]["delayed_minus_burst"]
        - differences["LTL"]["theft"]["delayed_minus_burst"]
        + differences["LTL"]["sham"]["delayed_minus_burst"]
    )
    interaction_algebra = P*eta*a*b*d*(1+q)
    if abs(interaction-interaction_algebra) > 1e-8*max(1, P):
        raise ValueError("Sham-adjusted model interaction algebra mismatch")
    return {
        "quality_ratio_q": q,
        "thief_removal_fraction_b": b,
        "theoretical_early_thief_viability_threshold_q": 1-b,
        "raw_delayed_advantage_thief_first": differences["TLL"]["theft"]["delayed_minus_burst"],
        "raw_delayed_advantage_legitimate_first": differences["LTL"]["theft"]["delayed_minus_burst"],
        "sham_adjusted_three_way_interaction": interaction,
        "closed_form_interaction": interaction_algebra,
        "raw_tll_advantage_positive": (
            differences["TLL"]["theft"]["delayed_minus_burst"] > 1e-10
        ),
        "measurements_calibrated_from_real_plants": False,
        "architecture_cost_estimated": False,
        "biological_warning": (
            "q is the realized effective contribution of the late pollen cohort "
            "relative to the early cohort, not necessarily intrinsic pollen viability. This relative weight can exceed one if later access is more effective. "
            "It can reflect residual legitimate opportunities, recipient receptivity, "
            "transfer or post-deposition success. The threshold follows algebraically "
            "from a fixed fractional-removal model, not a demonstrated evolved advantage."
        ),
    }


def quality_threshold_sweep() -> dict:
    """Show a concrete failure case of previous q=1 81/81 sign result."""
    ratio_grid = (0, 0.25, 0.5, 0.75, 1.0)
    examples = [scenario_with_quality(q=q) for q in ratio_grid]
    return {
        "analysis": "BALANCE_TWO_COHORT_RELATIVE_CONTRIBUTION_LIMIT_V1",
        "status": "SYNTHETIC_SENSITIVITY_NOT_EMPRICAL",
        "q_grid": list(ratio_grid),
        "threshold_q_at_b_half": 0.5,
        "scenarios": examples,
        "number_positive_delayed_effect_thief_first": sum(
            x["raw_delayed_advantage_thief_first"] > 1e-10 for x in examples
        ),
        "number_negative_delayed_effect_thief_first": sum(
            x["raw_delayed_advantage_thief_first"] < -1e-10 for x in examples
        ),
        "number_zero_delayed_effect_thief_first": sum(
            abs(x["raw_delayed_advantage_thief_first"]) <= 1e-10 for x in examples
        ),
        "original_model_reproduced_at_q_one": True,
        "source_experimental_data_rows_used": 0,
        "claim_ceiling": "hypothesis_falsifier_for_original_equal_quality_assumption_only",
    }

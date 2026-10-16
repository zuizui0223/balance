"""Non-confirmatory, source-covariance-anchored BALANCE plant design sizing.

Power is a NORMAL approximation for a new TWO-ARM *matched mother* design:
each independently randomized maternal plant contributes b targeted and b
sham blossoms, each with s usable measured seeds per blossom. Assuming
independent blossom deviations conditional on mother, the common maternal
random intercept cancels in the within-plant treatment difference.

SE = sqrt( 2 (source_blossom_variance + source_residual_variance/s)
           / (n_independent_mothers * b) )

This is NOT source treatment effect replication, not isotope detection power,
not confirmation that bract-selective optics are feasible, and not a future
true causal effect estimate. Bract-specific δ is unknown: illustrative
hypotheses must be reported explicitly with their effect magnitude.
"""
from __future__ import annotations

from math import isfinite, sqrt
from statistics import NormalDist

SCHEMA = "DALECHAMPIA_BRACT_ISOLATION_POWER_SCENARIOS_V1"
SOURCE_SCHEMA = "DALECHAMPIA_2015_NESTED_BLOSSOM_SOURCE_VERIFIED_V1"
SOURCE_FIXED = {
    "blossom_variance_mg2": 14.499685,
    "seed_residual_variance_mg2": 3.808892,
    "maternal_variance_mg2": 15.190316,
}
GAUSSIAN = NormalDist()


def _float(x, label, *, lower=None, upper=None):
    if type(x) not in (int, float):
        raise ValueError(f"{label} must be numeric")
    v=float(x)
    if not isfinite(v) or (lower is not None and v<lower) or (
        upper is not None and v>upper
    ):
        raise ValueError(f"{label} outside registered planning domain")
    return v


def _integer(x, label, *, lower=1):
    if type(x) is not int or x<lower:
        raise ValueError(f"{label} must be integer >= {lower}")
    return x


def validate_source_variance_receipt(source: dict) -> dict:
    """Reject silently altered source covariance or promoted biology."""
    if not isinstance(source,dict) or source.get("schema_version")!=SOURCE_SCHEMA:
        raise ValueError("original Dalechampia source variance receipt mismatched")
    if source.get("status")!="ORIGINAL_DRYAD_NESTED_COVARIANCE_STRONGLY_SUPPORTED_NOT_CAUSAL":
        raise ValueError("source must be an exact-data, noncausal variance receipt")
    if source.get("interpretation_limits",{}).get("structural_BALANCE_occupancy_identified") is not False:
        raise ValueError("source covariance is NOT structural BALANCE evidence")
    v=source["random_intercept_comparison"]["maternal_plus_blossom"]
    items={
        "blossom_variance_mg2":v.get("blossom_variance"),
        "seed_residual_variance_mg2":v.get("residual_variance"),
        "maternal_variance_mg2":v.get("maternal_variance"),
    }
    for key, target in SOURCE_FIXED.items():
        observed=_float(items[key],key,lower=0)
        if observed!=target:
            raise ValueError("original source variance component drifted")
    return SOURCE_FIXED


def _normal_power(effect, n_mothers, blossoms_per_arm, seeds_per_blossom,
                  blossom_var, residual_var, alpha) -> tuple[float,float]:
    # Parent groups are matched in BOTH arms; if they are not, this formula
    # cannot simply cancel the maternal variance. It is a planning equation.
    se=sqrt(2*(blossom_var+residual_var/seeds_per_blossom)/
            (n_mothers*blossoms_per_arm))
    z=GAUSSIAN.inv_cdf(1-alpha/2)
    noncentrality=abs(effect)/se
    power=(
        1-GAUSSIAN.cdf(z-noncentrality) +
        GAUSSIAN.cdf(-z-noncentrality)
    )
    return power,se


def plan_paired_blossom_scenarios(
    design: dict, verified_source: dict,
) -> dict:
    validate_source_variance_receipt(verified_source)
    if not isinstance(design,dict) or set(design) != {
        "schema_version","status","assumptions","scenarios",
    }:
        raise ValueError("prospective design scenario contract changed")
    if design["schema_version"]!=SCHEMA or design["status"]!=(
        "HYPOTHETICAL_SENSITIVITY_NOT_FIELD_POWER_VALIDATED"
    ):
        raise ValueError("not a transparent hypothetical design")
    assumptions=design["assumptions"]
    if not isinstance(assumptions,dict) or set(assumptions) != {
        "two_arms_matched_on_each_mother",
        "blossoms_randomly_assigned_within_mother",
        "no_interference_between_blossoms",
        "equal_blossom_effect_variance_between_arms",
        "mature_seed_fitness_equivalence_assumed",
        "bract_local_effect_size_empirically_known",
        "pilot_method_selectivity_already_passed",
        "test_alpha",
        "target_power",
        "max_maternal_plants",
    }:
        raise ValueError("complete transparent planning assumptions required")
    if not all(assumptions.get(k) is True for k in (
        "two_arms_matched_on_each_mother",
        "blossoms_randomly_assigned_within_mother",
        "no_interference_between_blossoms",
        "equal_blossom_effect_variance_between_arms",
    )):
        raise ValueError("paired-mother power requires all design independence assumptions")
    for name in (
        "mature_seed_fitness_equivalence_assumed",
        "bract_local_effect_size_empirically_known",
        "pilot_method_selectivity_already_passed",
    ):
        if assumptions.get(name) is not False:
            raise ValueError(f"{name} would overstate available evidence")
    alpha=_float(assumptions["test_alpha"],"test_alpha",lower=.001,upper=.2)
    target=_float(assumptions["target_power"],"target_power",lower=.5,upper=.99)
    max_n=_integer(assumptions["max_maternal_plants"],"max_maternal_plants",lower=2)
    if max_n>100000:
        raise ValueError("max maternal plants cannot exceed computational ceiling")
    rows=design["scenarios"]
    if not isinstance(rows,list) or not rows:
        raise ValueError("positive planning scenarios required")
    out=[]
    names=set()
    bv=SOURCE_FIXED["blossom_variance_mg2"]
    rv=SOURCE_FIXED["seed_residual_variance_mg2"]
    for item in rows:
        if not isinstance(item,dict) or set(item) != {
            "scenario_id","hypothetical_effect_mg",
            "blossoms_per_arm_per_mother",
            "usable_measured_seeds_per_blossom",
        }:
            raise ValueError("scenario keys changed")
        ident=item["scenario_id"]
        if not isinstance(ident,str) or not ident.strip() or ident in names:
            raise ValueError("missing/duplicate scenario identity")
        names.add(ident)
        delta=_float(item["hypothetical_effect_mg"],"hypothetical_effect_mg",
                     lower=0.0000001)
        blossoms=_integer(item["blossoms_per_arm_per_mother"],
                          "blossoms_per_arm_per_mother",lower=1)
        seeds=_integer(item["usable_measured_seeds_per_blossom"],
                       "usable_measured_seeds_per_blossom",lower=1)
        if seeds>9:
            raise ValueError("Dalechampia blossom has at most 9 ovules/seeds")
        if blossoms>100:
            raise ValueError("planning assumption 100 blossoms/arm per plant not credible")
        sufficient_n=None
        for n in range(2,max_n+1):
            probability,_=_normal_power(delta,n,blossoms,seeds,bv,rv,alpha)
            if probability>=target:
                sufficient_n=n
                break
        n_eval=sufficient_n or max_n
        p,se=_normal_power(delta,n_eval,blossoms,seeds,bv,rv,alpha)
        out.append({
            "scenario_id":ident,
            "hypothetical_effect_mg":delta,
            "blossoms_per_arm_per_mother":blossoms,
            "usable_measured_seeds_per_blossom":seeds,
            "minimum_independent_maternal_plants_normal_approx":sufficient_n,
            "target_reached_under_assumptions":sufficient_n is not None,
            "evaluated_at_n_mothers":n_eval,
            "approximate_power_at_evaluated_n":round(p,5),
            "assumed_difference_SE_at_evaluated_n_mg":round(se,6),
            "plants_are_not_seeds_or_blossoms":True,
        })
    return {
        "schema_version":SCHEMA,
        "status":"ILLUSTRATIVE_SOURCE_ANCHORED_NORMAL_POWER_ONLY",
        "source_covariance":dict(SOURCE_FIXED),
        "source_var_receipt_not_new_field_data":True,
        "alpha_two_sided":alpha,
        "target_normal_approximate_power":target,
        "normal_small_cluster_uncertainty_not_included":True,
        "stage_specific_seed_mass_does_not_equal_mature_fitness":True,
        "carbon_specific_effect_size_not_yet_observed":True,
        "randomization_and_no_interference_not_verified":True,
        "original_source_effect_was_whole_blossom_package_not_bract_local":True,
        "pilot_feasibility_not_yet_demonstrated":True,
        "structural_BALANCE_occupancy_identified":False,
        "new_independent_biological_clusters":0,
        "scenarios":out,
    }

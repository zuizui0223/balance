"""Design-based inference for a prospective three-arm Dalechampia tracer experiment.

Primary statistical estimand: randomized difference in developing-seed 13C
atom-percent excess (APE) between BRACT_13CO2_PULSE and FRUIT_LEAK_MIMIC,
paired by greenhouse/stage block, on DISTINCT maternal plants.

A positive randomized contrast means these two labelling REGIMES differ. It
does NOT establish that source bract photosynthate reached the seed: chamber
source isolation, fruit uptake dose-response, experimental randomization
chronology, interference and carbon mass-balance need independent validation.

The prior source-discrimination module performs per-block numerical screens.
This module NEVER discards blocks based on observed seed enrichment or those
outcome-dependent screens. It includes all complete preassigned blocks and
provides a finite-sample paired sign-flip RANDOMIZATION test under the
specified sharp-null/exchangeable-label design, NOT a causal source certificate.

With n matched independently assigned B/F pairs, 2**n sign permutations
exist. For nonzero aligned differences, a two-sided exact test cannot produce
p < .05 for n <= 5. Six blocks = 18 INDEPENDENT maternal plants is the
mathematical p-value resolution floor, not 80% biological power.
"""
from __future__ import annotations

from itertools import product
import hashlib
import math
import random
from typing import Any

from .dalechampia_tracer_source import (
    ARMS,
    screen_bract_13c_source,
    validate_tracer_plan,
)

SCHEMA="DALECHAMPIA_13C_BLOCK_RANDOMIZATION_INFERENCE_V1"
DEFAULT_EXACT_ENUMERATION_MAX_BLOCKS=16
MAX_RANDOMIZATION_MONTE_CARLO_SAMPLES=200000
MIN_RANDOMIZATION_MONTE_CARLO_SAMPLES=10000
PRIMARY="BRACT_13CO2_PULSE_MINUS_FRUIT_LEAK_MIMIC_SEED_APE"


def _numeric(value: Any, name: str, *, low=None, high=None) -> float:
    if type(value) not in (float,int):
        raise ValueError(f"{name} must be a numerical plan value")
    val=float(value)
    if not math.isfinite(val) or (low is not None and val<low) or (
        high is not None and val>high
    ):
        raise ValueError(f"{name} outside allowed inference range")
    return val


def _int(value:Any,name:str,*,low=1,high=None)->int:
    if type(value) is not int or value<low or (high is not None and value>high):
        raise ValueError(f"{name} must be a bounded integer")
    return value


def exact_two_sided_resolution(n_blocks:int)->float:
    """Smallest possible two-sided exact sign-flip p (nonzero effect), n>=1."""
    n=_int(n_blocks,"n_blocks",low=1)
    return min(1.0,math.ldexp(2.0,-n))


def minimum_blocks_to_reject_two_sided(alpha:float)->int:
    """Smallest n whose two-sided sign-test permutation support reaches alpha."""
    cutoff=_numeric(alpha,"two_sided_alpha",low=0.000001,high=.2)
    return max(1,math.ceil(math.log2(2.0/cutoff)))


def block_resolution_table(alpha:float,*,n_start=3,n_stop=16)->dict:
    first=_int(n_start,"n_start",low=1)
    last=_int(n_stop,"n_stop",low=first,high=30)
    a=_numeric(alpha,"two_sided_alpha",low=0.000001,high=.2)
    floor=minimum_blocks_to_reject_two_sided(a)
    return {
        "schema_version":"DALECHAMPIA_13C_BLOCK_PERMUTATION_RESOLUTION_V1",
        "status":"EXACT_RANDOMIZATION_COMBINATORICS_NOT_BIOLOGICAL_POWER",
        "alpha_two_sided":a,
        "independent_maternal_plants_per_complete_three_arm_block":3,
        "minimum_blocks_with_possible_two_sided_p_below_or_equal_alpha":floor,
        "minimum_independent_maternal_plants_at_resolution_floor":3*floor,
        "not_actual_power_or_biological_effect":True,
        "rows":[{
            "n_independent_blocks":n,
            "n_independent_maternal_plants":3*n,
            "exact_sign_assignments":2**n,
            "minimum_attainable_two_sided_p":exact_two_sided_resolution(n),
            "two_sided_significance_mathematically_possible":(
                exact_two_sided_resolution(n)<=a
            ),
        } for n in range(first,last+1)],
    }


def validate_inference_plan(plan:dict)->dict:
    required={
        "schema_version","status","context_id","calibration_plan_sha256",
        "primary_contrast","test_sidedness","two_sided_alpha",
        "max_exact_blocks","monte_carlo_draws","monte_carlo_seed",
        "blocks_with_zero_effect_or_failed_QC_dropped","scope_exclusions",
    }
    if not isinstance(plan,dict) or set(plan)!=required:
        raise ValueError("entire prospective inferential plan required")
    if plan["schema_version"]!=SCHEMA:
        raise ValueError("13C block inferential schema mismatch")
    if plan["status"]!="SELF_DECLARED_BEFORE_OUTCOMES_NOT_TIME_VERIFIED":
        raise ValueError("randomization inference rules NOT externally frozen")
    if not isinstance(plan["context_id"],str) or not plan["context_id"].strip():
        raise ValueError("registered population and sampling context missing")
    sha=plan["calibration_plan_sha256"]
    if not isinstance(sha,str) or len(sha)!=64 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("original calibration JSON SHA256 fingerprint required")
    if plan["primary_contrast"]!=PRIMARY or plan["test_sidedness"]!="TWO_SIDED":
        raise ValueError("precommitted B vs F primary two-sided contrast required")
    _numeric(plan["two_sided_alpha"],"two_sided_alpha",low=0.000001,high=.2)
    _int(plan["max_exact_blocks"],"max_exact_blocks",low=6,high=20)
    _int(plan["monte_carlo_draws"],"monte_carlo_draws",
         low=MIN_RANDOMIZATION_MONTE_CARLO_SAMPLES,
         high=MAX_RANDOMIZATION_MONTE_CARLO_SAMPLES)
    _int(plan["monte_carlo_seed"],"monte_carlo_seed",low=0)
    if plan["blocks_with_zero_effect_or_failed_QC_dropped"] is not False:
        raise ValueError("post-outcome exclusions invalidate paired randomization")
    excl=plan["scope_exclusions"]
    if not isinstance(excl,dict) or set(excl)!={
        "randomization_chronology_verified","plant_interference_ignored",
        "calibrated_uptake_monotonicity_verified",
        "causal_bract_to_seed_carbon_source_identified",
        "bract_specific_mature_seed_fitness_identified",
        "structural_BALANCE_occupancy_identified",
    } or any(v is not False for v in excl.values()):
        raise ValueError("inference must not claim verified causal/source fitness")
    return plan


def _seed_ape(row:dict)->float:
    return (float(row["seed_postchase_atom_percent_13c"]) -
            float(row["seed_background_atom_percent_13c"]))


def _collect_all_block_differences(rows:list[dict])->list[dict]:
    blocks={}
    for r in rows:
        bid=r["block_id"]
        arm=r["arm"]
        if bid not in blocks:
            blocks[bid]={}
        if arm in blocks[bid]:
            raise ValueError("source block arm duplicated")
        blocks[bid][arm]=r
    out=[]
    for name,group in sorted(blocks.items()):
        if set(group)!=set(ARMS):
            raise ValueError("randomized block incomplete")
        sham,target,mimic=(group[k] for k in ARMS)
        b=_seed_ape(target)
        f=_seed_ape(mimic)
        s=_seed_ape(sham)
        out.append({
            "block_id":name,
            "bract_target_minus_mimic_seed_APE":b-f,
            "bract_target_minus_sham_seed_APE":b-s,
            "fruit_mimic_minus_sham_seed_APE":f-s,
        })
    return out


def _signflip_exact(differences:list[float],*,alpha:float)->dict:
    """All 2**n assignments, no asymptotic independence/pseudo-seed SE."""
    n=len(differences)
    obs=math.fsum(differences)
    scale=max(1.,math.fsum(abs(x) for x in differences))
    tolerance=1e-12*scale
    total=2**n
    extreme_two=0
    extreme_positive=0
    for flips in product((-1.,1.),repeat=n):
        perm=math.fsum(s*d for s,d in zip(flips,differences))
        if abs(perm)+tolerance>=abs(obs):
            extreme_two+=1
        if perm+tolerance>=obs:
            extreme_positive+=1
    return {
        "mode":"EXACT_ENUMERATION_OF_ALL_MATCHED_SIGN_ASSIGNMENTS",
        "permutations_evaluated":total,
        "two_sided_p":extreme_two/total,
        "one_sided_positive_p_descriptive":extreme_positive/total,
        "p_value_monte_carlo_standard_error":None,
        "plus_one_randomization_correction_used":False,
        "p_value_less_than_alpha":extreme_two/total<alpha,
    }


def _signflip_monte_carlo(differences:list[float],*,alpha:float,
                          seed:int,draws:int)->dict:
    """MC p-value with conservative +1 pseudo-count, deterministic seed."""
    rng=random.Random(seed)
    obs=math.fsum(differences)
    tolerance=1e-12*max(1.,math.fsum(abs(x) for x in differences))
    extreme_two=0
    extreme_positive=0
    for _ in range(draws):
        perm=math.fsum((x if rng.getrandbits(1) else -x)
                        for x in differences)
        if abs(perm)+tolerance>=abs(obs):
            extreme_two+=1
        if perm+tolerance>=obs:
            extreme_positive+=1
    p_two=(extreme_two+1)/(draws+1)
    p_one=(extreme_positive+1)/(draws+1)
    return {
        "mode":"DETERMINISTIC_MONTE_CARLO_SIGN_FLIP_NOT_EXACT",
        "permutations_evaluated":draws,
        "two_sided_p":p_two,
        "one_sided_positive_p_descriptive":p_one,
        "p_value_monte_carlo_standard_error":math.sqrt(
            p_two*(1-p_two)/(draws+1)
        ),
        "plus_one_randomization_correction_used":True,
        "p_value_less_than_alpha":p_two<alpha,
    }


def analyze_block_randomization(
    source_plan:dict,inference_plan:dict,raw_plant_records:list[dict],
    *,actual_calibration_sha256:str|None=None,
)->dict:
    """Test all randomized plants, never select isotope-positive blocks.

    The sharp no-regime-effect null and treatment-label exchangeability
    conditional on the sham assignment, valid plant-level random allocation
    and no between-plant interference are explicit UNVERIFIED premises.
    """
    validate_tracer_plan(source_plan)
    validate_inference_plan(inference_plan)
    if actual_calibration_sha256 is None or (
        inference_plan["calibration_plan_sha256"]!=actual_calibration_sha256
    ):
        raise ValueError("inference rules not bound to the actual isotope calibration SHA256")
    # This screen independently validates every plant/arm, outcome value,
    # stage, unit and genuine identity field; its outcome-based PASS/HOLD is
    # NOT used for filtering blocks or creating artificial significance.
    source_screen=screen_bract_13c_source(source_plan,raw_plant_records)
    receipts=_collect_all_block_differences(raw_plant_records)
    n=len(receipts)
    if n!=source_screen["n_randomized_blocks"] or 3*n!=source_screen["n_distinct_maternal_plants"]:
        raise ValueError("source blocks and statistical inference units disagree")
    values=[x["bract_target_minus_mimic_seed_APE"] for x in receipts]
    if not all(math.isfinite(x) for x in values):
        raise ValueError("nonfinite source endpoint differences")
    alpha=float(inference_plan["two_sided_alpha"])
    minimum=minimum_blocks_to_reject_two_sided(alpha)
    if n<=inference_plan["max_exact_blocks"]:
        permutation=_signflip_exact(values,alpha=alpha)
    else:
        permutation=_signflip_monte_carlo(
            values,alpha=alpha,seed=inference_plan["monte_carlo_seed"],
            draws=inference_plan["monte_carlo_draws"],
        )
    means={
        "target_minus_mimic_seed_atom_percent_excess":math.fsum(
            v["bract_target_minus_mimic_seed_APE"] for v in receipts
        )/n,
        "target_minus_sham_seed_atom_percent_excess":math.fsum(
            v["bract_target_minus_sham_seed_APE"] for v in receipts
        )/n,
        "mimic_minus_sham_seed_atom_percent_excess":math.fsum(
            v["fruit_mimic_minus_sham_seed_APE"] for v in receipts
        )/n,
    }
    # A statistically detected treatment-regime contrast is not direct
    # source attribution. Source screening is an adjacent diagnostic,
    # and the code cannot independently verify chamber comparability.
    return {
        "schema_version":SCHEMA,
        "status":"BLOCKED_RANDOMIZED_TRACER_REGIME_CONTRAST_NOT_CARBON_SOURCE_CAUSALITY",
        "context_id":source_plan["context_id"],
        "n_independent_randomized_three_arm_blocks":n,
        "n_independent_maternal_plants":3*n,
        "n_total_source_isotope_rows":len(raw_plant_records),
        "all_preassigned_blocks_included_without_APE_based_exclusion":True,
        "two_sided_alpha":alpha,
        "minimum_blocks_for_exact_two_sided_significance_possibility":minimum,
        "minimum_mothers_for_exact_two_sided_significance_possibility":3*minimum,
        "exact_minimum_attainable_two_sided_p":exact_two_sided_resolution(n),
        "design_has_sufficient_p_value_resolution":(
            n>=minimum
        ),
        "descriptive_block_means_atom_percent_excess":{
            k:round(v,9) for k,v in means.items()
        },
        "seed_source_contrasts_atom_percent_excess_by_block":[{
            k:(round(v,9) if k!="block_id" else v)
            for k,v in x.items()
        } for x in receipts],
        "sharp_no_regime_effect_randomization_inference":permutation,
        "source_screen_original_status":source_screen["status"],
        "source_screen_numeric_method_failures_by_block":{
            x["block_id"]:x["source_discrimination_method_failures"]
            for x in source_screen["per_block_source_screen"]
        },
        "screen_status_not_used_to_select_inference_blocks":True,
        "p_value_is_about_randomized_regime_difference_only":True,
        "randomization_chronology_externally_verified":False,
        "sharp_null_exchangeability_and_no_interference_verified":False,
        "fruit_dose_response_and_absorption_equivalence_verified":False,
        "source_specific_C13_to_seed_transport_caused_by_bract":False,
        "estimated_fraction_seed_carbon_from_bract":None,
        "mature_seed_fitness_effect_identified":False,
        "structural_BALANCE_occupancy_identified":False,
        "additional_independent_biological_clusters":0,
        "interpretation":(
            "Design-based randomization test conditional on preassigned block "
            "and pairwise source-arm exchangeability under a sharp null; "
            "no source-specific assimilation claim from treatment label or "
            "p-value without external gas/fruit physiological validation"
        ),
    }

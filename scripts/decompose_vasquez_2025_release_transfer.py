"""Paired original-trial release × transfer decomposition of 2025 Solanum data.

This is a POST-OPEN exploratory arithmetic audit, not mechanistic causal
mediation. Released fraction B/A and conditional PTE H/B share B in opposite
positions; anticorrelation of these ratios is not proof that increasing
pollen release inhibits deposition or a new biological trade-off.

Original source data are authenticated by SHA-256 via from_authenticated_rows;
60 nested recipient lines are grouped into 15 DONOR/BEE trials first.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from math import isfinite, sqrt
from pathlib import Path
import random
from statistics import mean

from scripts.reanalyse_vasquez_2025_trial_denominators import from_authenticated_rows

SEED = 20261122
BOOTSTRAPS = 20000
SPECIES = ("S.rostratum", "S.dulcamara")


def _percentile(values, probability: float) -> float:
    data = sorted(values)
    if not data or not (0 <= probability <= 1):
        raise ValueError("Cannot calculate percentile for empty or invalid distribution")
    at = (len(data)-1)*probability
    lower = int(at)
    upper = min(lower+1,len(data)-1)
    fraction=at-lower
    return data[lower]*(1-fraction)+data[upper]*fraction


def _pearson(a: list[float], b: list[float]) -> float | None:
    if len(a) != len(b) or len(a)<2:
        raise ValueError("Paired nontrivial observations are required")
    a0=mean(a)
    b0=mean(b)
    xx=sum((v-a0)**2 for v in a)
    yy=sum((v-b0)**2 for v in b)
    if xx<1e-30 or yy<1e-30:
        return None
    return sum((x-a0)*(y-b0) for x,y in zip(a,b))/sqrt(xx*yy)


def _average_ranks(a: list[float]) -> list[float]:
    pairs=sorted((v,i) for i,v in enumerate(a))
    result=[0.0]*len(a)
    j=0
    while j<len(pairs):
        k=j+1
        while k<len(pairs) and pairs[k][0]==pairs[j][0]:
            k+=1
        rank=((j+1)+k)/2.0
        for t in range(j,k):
            result[pairs[t][1]]=rank
        j=k
    return result


def _spearman(a: list[float], b: list[float]) -> float | None:
    return _pearson(_average_ranks(a),_average_ranks(b))


def _components(rows:list[dict])->dict[str,float]:
    if len(rows)<2:
        raise ValueError("Each species must have at least two actual donor trials")
    release=[r["release_fraction"] for r in rows]
    conditional=[r["transfer_conditional_fraction"] for r in rows]
    throughput=[r["source_to_stigma_fraction"] for r in rows]
    if any(not all(isfinite(x) and x>=0 for x in
                   (r,t,y)) or abs(r*t-y)>1e-10
           for r,t,y in zip(release,conditional,throughput)):
        raise ValueError("Donor-trial component arithmetic is inconsistent")
    rm=mean(release)
    tm=mean(conditional)
    ym=mean(throughput)
    covariance=ym-rm*tm
    return {
        "mean_release_fraction":rm,
        "mean_conditional_transfer_fraction":tm,
        "mean_source_to_stigma_fraction":ym,
        "mean_of_independently_multiplied_source_averages":rm*tm,
        "paired_release_transfer_population_covariance":covariance,
    }


def _symmetric_decomposition(grouped: dict[str,list[dict]])->dict[str,float]:
    a=_components(grouped["S.rostratum"])
    b=_components(grouped["S.dulcamara"])
    release=(b["mean_release_fraction"]-a["mean_release_fraction"])*(
        b["mean_conditional_transfer_fraction"]+a["mean_conditional_transfer_fraction"]
    )/2
    conditional=(b["mean_conditional_transfer_fraction"]-a["mean_conditional_transfer_fraction"])*(
        b["mean_release_fraction"]+a["mean_release_fraction"]
    )/2
    covariance=(b["paired_release_transfer_population_covariance"]-
                a["paired_release_transfer_population_covariance"])
    observed=(b["mean_source_to_stigma_fraction"]-
              a["mean_source_to_stigma_fraction"])
    error=release+conditional+covariance-observed
    if abs(error)>1e-12:
        raise ValueError("Symmetric original source decomposition fails identity")
    return {
        "release_component_percentage_points":100*release,
        "conditional_transfer_component_percentage_points":100*conditional,
        "paired_covariance_component_percentage_points":100*covariance,
        "actual_dulcamara_minus_rostratum_source_throughput_pp":100*observed,
        "decomposition_error_pp":100*error,
    }


def analyze_paired_trials(
    source:dict, *, bootstrap_count:int=BOOTSTRAPS, seed:int=SEED,
)->dict:
    """Source dict is output of hash-checking from_authenticated_rows()."""
    if (isinstance(bootstrap_count,bool)
        or not isinstance(bootstrap_count,int) or bootstrap_count <100):
        raise ValueError("Bootstrap count must be a positive integer >=100")
    if isinstance(seed,bool) or not isinstance(seed,int):
        raise ValueError("Seed must be a plain integer")
    original=source.get("trials")
    if not isinstance(original,list) or len(original)!=15:
        raise ValueError("Expected 15 independent original donor trials")
    grouped=defaultdict(list)
    source_ids=set()
    for entry in original:
        name=entry["source_species"]
        if name not in SPECIES:
            raise ValueError("Unexpected original source species label")
        source_id=(entry["source_hive"],entry["source_bee_id"])
        if source_id in source_ids:
            raise ValueError("Duplicate original donor-bee identifier")
        source_ids.add(source_id)
        released=entry["fraction_released_pct_of_measured_source"]/100
        pte=entry["pollen_transfer_efficiency_pct_of_removed"]/100
        full=entry["source_to_four_stigmas_pct_of_production"]/100
        h=entry["measured_recipient_stigma_grains"]
        b=entry["measured_released_grains"]
        if not all(isfinite(x) and x>0 for x in (released,pte,full,h,b)):
            raise ValueError("Original source donor trial must have finite positive measures")
        if h>b or abs(released*pte-full)>1e-11:
            raise ValueError("Donor-to-recipient source accounting identity failed")
        grouped[name].append({
            "release_fraction":released,
            "transfer_conditional_fraction":pte,
            "source_to_stigma_fraction":full,
            "released_grains":b,
            "stigmatic_grains":h,
        })
    if {k:len(v) for k,v in grouped.items()}!={"S.rostratum":6,"S.dulcamara":9}:
        raise ValueError("Original 2025 donor units must remain 6 and 9")
    original_decomposition=_symmetric_decomposition(grouped)
    species_results={}
    for sp in SPECIES:
        records=grouped[sp]
        comp=_components(records)
        original_cov=comp["paired_release_transfer_population_covariance"]
        exclusions=[
            _components(records[:i]+records[i+1:])[
                "paired_release_transfer_population_covariance"
            ] for i in range(len(records))
        ]
        pearson=_pearson(
            [r["release_fraction"] for r in records],
            [r["transfer_conditional_fraction"] for r in records]
        )
        spearman=_spearman(
            [r["release_fraction"] for r in records],
            [r["transfer_conditional_fraction"] for r in records]
        )
        count_association=_spearman(
            [r["released_grains"] for r in records],
            [r["stigmatic_grains"] for r in records]
        )
        species_results[sp]={
            "n_donor_bee_trials":len(records),
            "group_mean_release_pct":100*comp["mean_release_fraction"],
            "group_mean_conditional_PTE_pct":100*comp["mean_conditional_transfer_fraction"],
            "group_mean_full_source_transfer_pct":100*comp["mean_source_to_stigma_fraction"],
            "product_of_separate_group_means_pct":100*comp[
                "mean_of_independently_multiplied_source_averages"],
            "paired_covariance_pct_points":100*original_cov,
            "full_transfer_as_fraction_of_independent_mean_product":(
                comp["mean_source_to_stigma_fraction"]/
                comp["mean_of_independently_multiplied_source_averages"]
            ),
            "release_pct_vs_conditional_PTE_pearson":pearson,
            "release_pct_vs_conditional_PTE_spearman":spearman,
            "absolute_released_grains_vs_absolute_stigmatic_grains_spearman":count_association,
            "n_single_donor_deletions":len(exclusions),
            "covariance_sign_preserving_single_donor_deletions":sum(
                1 for v in exclusions if v*original_cov>0
            ),
            "single_donor_covariance_range_pct_points":[
                100*min(exclusions),100*max(exclusions)
            ],
            "no_correlation_p_values":True,
        }
    rng=random.Random(seed)
    boot={k:[] for k in (
        "release_component_percentage_points",
        "conditional_transfer_component_percentage_points",
        "paired_covariance_component_percentage_points",
        "actual_dulcamara_minus_rostratum_source_throughput_pp",
        "cov_rostratum_pp","cov_dulcamara_pp",
    )}
    for _ in range(bootstrap_count):
        pick={
            sp:rng.choices(grouped[sp],k=len(grouped[sp]))
            for sp in SPECIES
        }
        components=_symmetric_decomposition(pick)
        for key in (
            "release_component_percentage_points",
            "conditional_transfer_component_percentage_points",
            "paired_covariance_component_percentage_points",
            "actual_dulcamara_minus_rostratum_source_throughput_pp"
        ):
            boot[key].append(components[key])
        boot["cov_rostratum_pp"].append(
            100*_components(pick["S.rostratum"])[
                "paired_release_transfer_population_covariance"
            ]
        )
        boot["cov_dulcamara_pp"].append(
            100*_components(pick["S.dulcamara"])[
                "paired_release_transfer_population_covariance"
            ]
        )
    ci={
        name:{
            "trial_bootstrap_95pct_interval":[
                _percentile(values,.025),_percentile(values,.975)
            ],
            "bootstrap_resamples":bootstrap_count,
            "n_negative_resamples":sum(x<0 for x in values),
            "n_positive_resamples":sum(x>0 for x in values),
            "not_hive_or_plant_cluster_robust":True,
        }
        for name,values in boot.items()
    }
    return {
        "analysis":"BALANCE_VASQUEZ_2025_ACTUAL_PAIRED_RELEASE_PTE_COVARIANCE_V1",
        "status":"POSTOPEN_AUTHENTIC_ORIGINAL_15_TRIAL_ARITHMETIC_DECOMPOSITION_NOT_CAUSAL",
        "n_original_donor_trials":15,
        "n_recipient_rows_nested":60,
        "original_article_doi":"10.26786/1920-7603(2025)836",
        "source_sha256":source["source"]["raw_csv_sha256"],
        "species":species_results,
        "symmetric_between_species_arithmetic_decomposition":original_decomposition,
        "paired_trial_bootstrap_descriptive":ci,
        "fixed_bootstrap_seed":seed,
        "strict_interpretation":{
            "ratio_shared_denominator_B_induces_spurious_correlation_risk":True,
            "negative_covariance_is_NOT_evidence_of_causal_pollen_release_transfer_tradeoff":True,
            "absolute_grain_count_correlation_is_exploratory_not_causal":True,
            "no_source_plant_ID_or_valid_two_hive_population_cluster_inference":True,
            "no_randomized_morphology_species_comparison":True,
            "no_independent_evolutionary_replication":True,
            "no_true_pollen_fate_ground_body_or_basket_microdata":True,
            "no_genetic_paternity_or_seed_fitness":True,
            "no_frozen_BALANCE_U2_U6_V4_update":True,
            "no_new_independent_original_research_programme":True,
        },
        "raw_donor_row_values_exported":False,
    }


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--original-csv",type=Path,required=True)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    genuine=from_authenticated_rows(args.original_csv.read_bytes())
    result=analyze_paired_trials(genuine)
    text=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text+"\n",encoding="utf-8")
    for sp,x in result["species"].items():
        print(
            "VASQUEZ_PAIR_COV|species={}|n={}|released_pct={:.8f}|PTE_pct={:.8f}|"
            "actual_pct={:.8f}|means_product_pct={:.8f}|cov_pp={:+.8f}|"
            "pearson={:+.6f}|spearman={:+.6f}|H_vs_B_spearman={:+.6f}|"
            "delete_sign={}/{}".format(
                sp,x["n_donor_bee_trials"],x["group_mean_release_pct"],
                x["group_mean_conditional_PTE_pct"],
                x["group_mean_full_source_transfer_pct"],
                x["product_of_separate_group_means_pct"],
                x["paired_covariance_pct_points"],
                x["release_pct_vs_conditional_PTE_pearson"],
                x["release_pct_vs_conditional_PTE_spearman"],
                x["absolute_released_grains_vs_absolute_stigmatic_grains_spearman"],
                x["covariance_sign_preserving_single_donor_deletions"],
                x["n_single_donor_deletions"],
            )
        )
    z=result["symmetric_between_species_arithmetic_decomposition"]
    print("VASQUEZ_PAIR_COMPONENTS|release={:+.8f}|PTE={:+.8f}|"
          "covariance={:+.8f}|observed={:+.8f}|residual={:.3e}".format(
        z["release_component_percentage_points"],
        z["conditional_transfer_component_percentage_points"],
        z["paired_covariance_component_percentage_points"],
        z["actual_dulcamara_minus_rostratum_source_throughput_pp"],
        z["decomposition_error_pp"],
    ))


if __name__=="__main__":
    main()

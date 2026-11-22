"""Hive-stratified and single-donor influence diagnostic on authentic 2025 trials.

This runs strictly AFTER the original 15-trial estimand was chosen. No
species-by-hive causal interaction or population colony-inference is claimed
from only 2 original hives (one with a single S. rostratum trial).
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from statistics import mean

from scripts.reanalyse_vasquez_2025_trial_denominators import from_authenticated_rows

FATES=(
    "source_to_four_stigmas_pct_of_production",
    "pollen_transfer_efficiency_pct_of_removed",
    "fraction_released_pct_of_measured_source",
)


def source_stratified_sensitivity(raw:bytes)->dict:
    data=from_authenticated_rows(raw)
    rows=data["trials"]
    by_hive=defaultdict(lambda:defaultdict(list))
    for r in rows:
        by_hive[r["source_hive"]][r["source_species"]].append(r)
    if set(by_hive)!={"B1","B2"}:
        raise ValueError("Unexpected source hive membership")
    s1,s2="S.rostratum","S.dulcamara"
    expected={"B1":{s1:5,s2:5},"B2":{s1:1,s2:4}}
    for hive,group in by_hive.items():
        if {k:len(v) for k,v in group.items()} != expected[hive]:
            raise ValueError("Original 2-hive species allocations changed")
    comparisons=[]
    for hive,source in sorted(by_hive.items()):
        d={"hive":hive,
           "n_rostratum":len(source[s1]),
           "n_dulcamara":len(source[s2]),
           "at_least_two_trials_each_species":min(len(source[s1]),len(source[s2]))>=2,
           "within_hive_dulcamara_minus_rostratum":{
               field:mean(x[field] for x in source[s2])-mean(x[field] for x in source[s1])
               for field in FATES
           },
           "caution":"Single observational hive; donor plants untracked; no species-specific causal architecture estimate"}
        comparisons.append(d)
    excluded=[]
    for i,row in enumerate(rows):
        remaining=rows[:i]+rows[i+1:]
        species={s:[x for x in remaining if x["source_species"]==s] for s in (s1,s2)}
        excluded.append({
            "removed_species":row["source_species"],
            "end_to_end_diff_pct_points":mean(
                x[FATES[0]] for x in species[s2]
            )-mean(x[FATES[0]] for x in species[s1])
        })
    effects=[x["end_to_end_diff_pct_points"] for x in excluded]
    if len(effects)!=15:
        raise ValueError("Source all-donor leave-one-out analysis incomplete")
    return {
        "analysis":"BALANCE_VASQUEZ_2025_TRIAL_HIVE_SENSITIVITY",
        "status":"ACTUAL_SOURCE_POSTOPEN_DESCRIPTIVE_HIVE_CHECK_NOT_CONFIRMATORY",
        "source_sha256":data["source"]["raw_csv_sha256"],
        "n_source_trials":15,
        "n_hives":2,
        "within_hive_comparisons":comparisons,
        "single_donor_deletion":{
            "n_source_trials_removed_one_at_a_time":len(effects),
            "n_differences_positive":sum(x>0 for x in effects),
            "min_end_to_end_dulcamara_minus_rostratum_pp":min(effects),
            "max_end_to_end_dulcamara_minus_rostratum_pp":max(effects),
        },
        "limits":{
            "postopen_hive_and_influence_checks":True,
            "B2_rostratum_n1_no_species_replication_within_B2":True,
            "two_hives_insufficient_for_population_cluster_inference":True,
            "species_not_randomized":True,
            "donor_plant_ID_missing":True,
            "no_inference_on_ground_basket_body_channels":True,
            "no_original_genetic_paternity":True
        }
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-csv",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    out=source_stratified_sensitivity(args.original_csv.read_bytes())
    result=json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)
    print(result)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(result+"\n",encoding="utf-8")


if __name__=="__main__":
    main()

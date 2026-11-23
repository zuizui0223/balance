"""Authenticated orchid 2021 paper-aligned 379-row + first-six opportunity audit.

Source CSV has 383 recipient rows, 16 Emasc + 16 Intact code groups.
The original Methods say 16 E/15 I, but the later 379-recipient model says
15 E/16 I. Intact source code 4 alone has four visits; omitting its rows
matches 379 and the general Methods' 16/15, but does NOT prove the
authors' actual inclusion policy, nor does it resolve Emasc 2/3 possibly
being one donor, Emasc 7 having only two visits, or R varying in 4 codes.

The first-six common-opportunity decomposition describes whether stain
deposition is zero and how many massulae reach a positive stigma, not
whether pollen touched the stigma or genetically fathered seeds.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
from math import isfinite
from pathlib import Path
from random import Random
from statistics import mean

from scripts.audit_harder_2021_export_sensitivity import (
    _read_source_groups, _contrast, ORIGINAL_SHA256, ORIGINAL_BYTES
)

SEED=20261124
N_BOOT=20000
EXPECTED_FIELDS=("Trial_type","Trial","M_init","R","Visit","Deposition")
EARLY_VISITS=(1,2,3,4,5,6)


def _verified_recipient_groups(raw:bytes)->dict[tuple[str,str],list[dict]]:
    if len(raw)!=ORIGINAL_BYTES or hashlib.sha256(raw).hexdigest()!=ORIGINAL_SHA256:
        raise ValueError("Only authenticated original 8041-byte 2021 orchid source accepted")
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if tuple(reader.fieldnames or ())!=EXPECTED_FIELDS:
        raise ValueError("Original published source header/order changed")
    records=list(reader)
    if len(records)!=383 or any(None in row or None in row.values() for row in records):
        raise ValueError("Original orchid recipient records incomplete")
    grouped=defaultdict(list)
    for line,row in enumerate(records,start=2):
        label=row["Trial_type"]
        trial=row["Trial"]
        if label not in ("Emasc","Intact") or not trial:
            raise ValueError(f"Invalid source trial identity at line {line}")
        try:
            visit=int(row["Visit"])
            m_init=int(row["M_init"])
            depo=int(row["Deposition"])
        except (TypeError,ValueError) as exc:
            raise ValueError(f"Invalid source numeric field at line {line}") from exc
        if visit<1 or m_init<1 or depo<0:
            raise ValueError("Invalid observed orchid visit or massula values")
        key=(label,trial)
        grouped[key].append({
            "visit":visit,"M_init":m_init,"deposition":depo,
        })
    if Counter(k[0] for k in grouped)!=Counter({"Emasc":16,"Intact":16}):
        raise ValueError("Expected 16/16 original source code groups")
    for key,g in grouped.items():
        if len({x["M_init"] for x in g})!=1 or len({x["visit"] for x in g})!=len(g):
            raise ValueError(f"Original source data not a unique visit sequence: {key}")
        if sum(x["deposition"] for x in g)>g[0]["M_init"]:
            raise ValueError("Stained donor deposited more than its initial stock")
    return dict(grouped)


def _groups_from_recipient(groups:dict, keys:list[tuple[str,str]])->list[dict]:
    result=[]
    for group_key in keys:
        arr=groups[group_key]
        start=arr[0]["M_init"]
        result.append({
            "treatment":group_key[0],
            "source_trial_code":group_key[1],
            "source_recipient_rows":len(arr),
            "M_init":start,
            "donor_massula_deposited":sum(r["deposition"] for r in arr),
            "source_deposition_fraction":sum(r["deposition"] for r in arr)/start,
        })
    return result


def _quantile(seq,q):
    sorted_values=sorted(seq)
    if not sorted_values:
        raise ValueError("Empty bootstrap distribution")
    at=(len(sorted_values)-1)*q
    lower=int(at)
    w=at-lower
    return sorted_values[lower]*(1-w)+sorted_values[
        min(lower+1,len(sorted_values)-1)]*w


def _six_window_summary(groups:dict,bootstraps:int=N_BOOT)->dict:
    eligible=[]
    lost=[]
    for key,arr in sorted(groups.items()):
        index={r["visit"]:r for r in arr}
        if not all(visit in index for visit in EARLY_VISITS):
            lost.append({"treatment":key[0],"code":key[1],"n_source_rows":len(arr)})
            continue
        source=arr[0]["M_init"]
        obs=[index[v]["deposition"] for v in EARLY_VISITS]
        positives=[c for c in obs if c>0]
        positive_fraction=len(positives)/6
        normalized_positive=mean(positives)/source if positives else None
        frac=sum(obs)/source
        if normalized_positive is None and frac!=0:
            raise ValueError("Inconsistent positive-stigma coding")
        if normalized_positive is not None and abs(
            frac-6*positive_fraction*normalized_positive)>1e-12:
            raise ValueError("Six-recipient positive-intensity accounting identity failed")
        eligible.append({
            "treatment":key[0],"code":key[1],
            "initial_massulae":source,
            "six_recipient_deposition_pct":100*frac,
            "fraction_six_stigmas_with_stained_donor_massulae":positive_fraction,
            "positive_stigma_mean_deposition_per_initial_massulae":normalized_positive,
            "positive_n":len(positives),
            "first_six_counts":obs,
        })
    treatment=defaultdict(list)
    for r in eligible:
        treatment[r["treatment"]].append(r)
    if {k:len(v) for k,v in treatment.items()}!={"Emasc":14,"Intact":15}:
        raise ValueError("Original first-six comparable donor code group counts mismatch")
    if len(eligible)!=29 or sum(len(v) for v in treatment.values())!=29:
        raise ValueError("Unexpected early-window coding")
    attr=(
        "six_recipient_deposition_pct",
        "fraction_six_stigmas_with_stained_donor_massulae",
        "positive_stigma_mean_deposition_per_initial_massulae"
    )
    def group_stat(trial_group,field):
        x=[row[field] for row in trial_group if row[field] is not None]
        return mean(x) if x else None
    summary={}
    for tr,group in sorted(treatment.items()):
        summary[tr]={
            "n_original_source_coded_groups":len(group),
            "n_recipient_rows_at_shared_1_to_6_positions":len(group)*6,
            "n_with_any_stained_donor_deposition":sum(r["positive_n"]>0 for r in group),
            "n_with_no_stained_donor_deposition":sum(r["positive_n"]==0 for r in group),
            "means_by_equal_coded_group":{
                f:group_stat(group,f) for f in attr
            },
            "per_recipient_position":{
                str(v):{
                    "n_coded_groups":len(group),
                    "n_positive_stigmas":sum(r["first_six_counts"][v-1]>0 for r in group),
                    "fraction_no_stained_donor_massulae":sum(
                        r["first_six_counts"][v-1]==0 for r in group
                    )/len(group),
                    "mean_massulae_per_original_source_stigma_visit":mean(
                        r["first_six_counts"][v-1] for r in group
                    )
                } for v in EARLY_VISITS
            }
        }
    def between(group):
        return {
            field:group_stat(group["Intact"],field)-group_stat(group["Emasc"],field)
            if group_stat(group["Intact"],field) is not None and
               group_stat(group["Emasc"],field) is not None else None
            for field in attr
        }
    observed=between(treatment)
    rng=Random(SEED)
    draws={k:[] for k in attr}
    undefined={k:0 for k in attr}
    for _ in range(bootstraps):
        draw={
            arm:rng.choices(treatment[arm],k=len(treatment[arm]))
            for arm in ("Emasc","Intact")
        }
        r=between(draw)
        for f in attr:
            if r[f] is None:undefined[f]+=1
            else:draws[f].append(r[f])
    bootstrap={
        field:{
            "intact_minus_emasculated_95pct_interval":[
                _quantile(draws[field],.025),_quantile(draws[field],.975)
            ] if draws[field] else None,
            "resamples_with_defined_statistic":len(draws[field]),
            "undefined_resamples":undefined[field],
            "n_bootstrap_coded_groups":bootstraps,
            "not_a_valid_confirmatory_donor_population_or_genetic_paternity_test":True,
        } for field in attr
    }
    return {
        "eligible_coded_group_counts":{"Emasc":14,"Intact":15},
        "n_total_recipient_position_observations":174,
        "excluded_coded_group_metadata":lost,
        "arm_descriptions":summary,
        "observed_intact_minus_emasculated":observed,
        "postopen_trial_code_bootstrap":bootstrap,
        "source_recipient_opportunity_held_constant_at_six":True,
        "one_truncated_recipient_sequence_is_not_a_new_independent_donor":True,
        "stigma_contact_vs_zero_transfer_not_identified":True,
        "positive_conditional_amount_does_not_identify_pollen_viability":True,
    }


def run(original:bytes,bootstrap_count:int=N_BOOT)->dict:
    if isinstance(bootstrap_count,bool) or not isinstance(bootstrap_count,int) or bootstrap_count<100:
        raise ValueError("Bootstrap count requires integer >= 100")
    groups=_verified_recipient_groups(original)
    coded=_read_source_groups(original)
    no_intact4=[r for r in coded if not (
        r["treatment"]=="Intact" and r["source_trial_code"]=="4"
    )]
    if len(no_intact4)!=31:
        raise ValueError("Expected paper-aligned single extra intact code group")
    removed=groups[("Intact","4")]
    if len(removed)!=4 or sorted(x["visit"] for x in removed)!=[1,2,3,4]:
        raise ValueError("Paper-aligned 379-row candidate trial 4 does not have four recipient visits")
    assert 383-len(removed)==379
    paper_candidate=_contrast(no_intact4)
    if (paper_candidate["n_emasculated_coded_groups"],
        paper_candidate["n_intact_coded_groups"])!=(16,15):
        raise ValueError("Original Methods 16/15 manuscript candidate not reproduced")
    all32=_contrast(coded)
    early=_six_window_summary(groups,bootstrap_count)
    return {
        "analysis":"BALANCE_ORCHID_HARDER_2021_PAPER_ALIGNED_379_ROW_FIRST_SIX_HURDLE_V1",
        "status":"ACTUAL_AUTHENTIC_SOURCE_ORIGINAL_31_PAPER_CANDIDATE_AND_29_COMMON_SIX_CODES_POSTOPEN",
        "original_article_doi":"10.1086/712378",
        "source_data_doi":"10.5061/dryad.41ns1rnc0",
        "source_sha256":ORIGINAL_SHA256,
        "original_383_recipient_rows":383,
        "n_original_source_trial_codes":32,
        "published_methods_group_counts":{"Emasc":16,"Intact":15},
        "published_model_fitting_group_counts":{"Emasc":15,"Intact":16},
        "published_model_fitting_n_recipient_rows":379,
        "original_source_all32_descriptive_contrast":all32,
        "paper_aligned_candidate":{
            "excluded_treatment":"Intact",
            "excluded_original_source_code":"4",
            "excluded_n_recipient_rows":4,
            "retained_n_recipient_rows":379,
            "retained_coded_group_counts":{"Emasc":16,"Intact":15},
            "matches_published_general_methods_arm_counts":True,
            "matches_published_second_stage_recipient_count":True,
            "does_not_match_published_second_stage_reversed_arm_counts":True,
            "does_not_prove_original_paper_exclusion_rule":True,
            "source_code_group_contrast":paper_candidate,
        },
        "original_source_six_recipient_hurdle":early,
        "inference_limits":{
            "source_code_groups_may_not_be_independent_unique_donors":True,
            "candidate_inclusion_not_confirmed_by_author_code":True,
            "original_paper_internal_group_allocation_contradictory":True,
            "emasculated7_two_recipient_records_unresolved":True,
            "emasculated2_3_possibly_one_sequence_unconfirmed":True,
            "original_R_varies_within_four_source_codes":True,
            "first_six_extensive_zero_is_not_contact_probability":True,
            "first_six_positive_massula_load_is_not_fatherhood":True,
            "time_recipient_order_and_competing_massulae_not_orthogonally_randomized":True,
            "postopen_original_study_sensitivity_not_an_independent_experiment":True,
            "no_frozen_BALANCE_V4_architecture_outcomes_changed":True,
        },
        "original_trial_rows_committed":0,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--original-csv",type=Path,required=True)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    result=run(args.original_csv.read_bytes())
    txt=json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)
    print(txt)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(txt+"\n",encoding="utf-8")
    full=result["paper_aligned_candidate"]["source_code_group_contrast"]
    early=result["original_source_six_recipient_hurdle"]
    print("ORCHID_379_PAPER_CANDIDATE|E={}|I={}|ratio={:.8f}|diff={:+.8f}".format(
        full["n_emasculated_coded_groups"],
        full["n_intact_coded_groups"],
        full["intact_over_emasculated_mean_ratio"],
        full["intact_minus_emasculated_difference"]))
    for arm,row in early["arm_descriptions"].items():
        m=row["means_by_equal_coded_group"]
        print("ORCHID_SIX_HURDLE|arm={}|n={}|zero_all={}|six_export_pct={:.8f}|nonzero_fraction={:.8f}|positive_normalized={}".format(
            arm,row["n_original_source_coded_groups"],
            row["n_with_no_stained_donor_deposition"],
            m["six_recipient_deposition_pct"],
            m["fraction_six_stigmas_with_stained_donor_massulae"],
            m["positive_stigma_mean_deposition_per_initial_massulae"]))
    for key,value in early["observed_intact_minus_emasculated"].items():
        ci=early["postopen_trial_code_bootstrap"][key]["intact_minus_emasculated_95pct_interval"]
        print("ORCHID_SIX_HURDLE_DIFF|outcome={}|diff={:+.8f}|ci=[{:+.8f},{:+.8f}]".format(
            key,value,ci[0],ci[1]))


if __name__=="__main__":
    main()

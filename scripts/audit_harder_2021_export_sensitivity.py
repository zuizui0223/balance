"""Post-open original orchid source-code-group sensitivity without trial exclusion.

Harder et al. (2021) paper: 16 emasculated + 15 intact trials.
Original Zenodo mirror CSV: 16 'Emasc' + 16 'Intact' distinct coded trial
identifiers, 383 recipient rows. EMASC trial IDs 2 and 3 share M_init=201,
R=0, and show consecutive Visit 1..10 and 11..17; a split donor sequence is
plausible but not independently certified by unique bee/plant IDs. At least
four source coded trial groups vary R across visits even though the data
README labels R 'final donor pollinaria'. Do NOT silently pick a favored
31-trial assignment or infer true massula transport loss from R.

Audit three fully labeled groups:
A) every 32 original *coded* groups (NOT known independent donor trials);
B) merge only the flagged contiguous source Emasc 2+3 (31 coded groups,
   Emasc=15, Intact=16; does NOT reproduce paper's group counts);
C) all 16 possible one-intact-coded-group omissions from all-32
   (31 groups with Emasc=16, Intact=15, but *without* resolving E2/E3).

The biological quantity is stained-donor massula deposition across recorded
stigmas divided by initial donor massulae estimated from a neighboring donor
flower. Truncating to recipient visits 1..6 is an exploratory coverage guard,
not a preexisting published confirmatory analysis. Count each coded group once.
All intervals are bootstrap *coded-group* descriptions, not genetic male
fertility, colony-robust inference or verified 31-donor original refits.
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
import random
from statistics import mean,median

from scripts.audit_harder_2021_zenodo_mirror import FILE,MD5,verified_original_source

ORIGINAL_SHA256="303428b859bcba4756ac78c4ffd4b42121a6efce5b0cd2cc2030834705f62cbc"
ORIGINAL_BYTES=8041
EXPECTED_FIELDS=("Trial_type","Trial","M_init","R","Visit","Deposition")
BOOT_SEED=20261124
N_BOOT=20000


def _read_source_groups(raw:bytes)->list[dict]:
    if len(raw)!=ORIGINAL_BYTES or hashlib.sha256(raw).hexdigest()!=ORIGINAL_SHA256:
        raise ValueError("Analysis requires the exact archived public source CSV")
    if hashlib.md5(raw).hexdigest()!=MD5:
        raise ValueError("Original-source Dryad/Zenodo mirror MD5 conflict")
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if tuple(reader.fieldnames or ())!=EXPECTED_FIELDS:
        raise ValueError("Orchid source column names/order changed")
    entries=list(reader)
    if len(entries)!=383 or any(None in row or None in row.values() for row in entries):
        raise ValueError("Expected intact 383 original orchid recipient rows")
    groups=defaultdict(list)
    for line,row in enumerate(entries,2):
        if not row["Trial_type"] or row["Trial_type"] not in ("Emasc","Intact"):
            raise ValueError(f"Source group label invalid at line {line}")
        key=(row["Trial_type"],row["Trial"].strip())
        if not key[1]:raise ValueError("Missing source trial ID")
        numbers={}
        for name in ("Visit","M_init","R","Deposition"):
            try:n=float(row[name])
            except (ValueError,TypeError) as e:
                raise ValueError(f"Original field {name} missing/non-numeric") from e
            if not isfinite(n) or n<0 or n!=int(n):
                raise ValueError(f"Original field {name} requires nonnegative integer")
            numbers[name]=int(n)
        if numbers["M_init"]<=0 or numbers["Visit"]<=0:
            raise ValueError("Original initial massulae/visit index invalid")
        groups[key].append(numbers)
    if Counter(k[0] for k in groups)!=Counter({"Emasc":16,"Intact":16}):
        raise ValueError("Original 32 group identities changed")
    trials=[]
    for (arm,trial),rows in sorted(groups.items()):
        initial={r["M_init"] for r in rows}
        if len(initial)!=1:
            raise ValueError("Source initial donor massula count varies within code group")
        visit=[r["Visit"] for r in rows]
        if len(visit)!=len(set(visit)):
            raise ValueError("Duplicated visit index within original donor code")
        pollen=sum(r["Deposition"] for r in rows)
        initial_count=next(iter(initial))
        if pollen>initial_count:
            raise ValueError("More donor massulae deposited than initially available")
        trials.append({
            "treatment":arm,"source_trial_code":trial,
            "source_recipient_rows":len(rows),
            "visit_min":min(visit),"visit_max":max(visit),
            "visits_contiguous":sorted(visit)==list(range(min(visit),max(visit)+1)),
            "n_R_values_in_group":len({r["R"] for r in rows}),
            "M_init":initial_count,
            "donor_massula_deposited":pollen,
            "source_deposition_fraction":pollen/initial_count,
            "early_six_visit_deposition_fraction":(
                sum(r["Deposition"] for r in rows if r["Visit"]<=6)/initial_count
                if min(visit)==1 and len(visit)>=6 and
                set(range(1,7)).issubset(set(visit))
                else None
            ),
        })
    return trials


def _merge_possible_split(trials:list[dict])->list[dict]:
    keyed={(x["treatment"],x["source_trial_code"]):x for x in trials}
    a=keyed[("Emasc","2")]
    b=keyed[("Emasc","3")]
    if not(a["visit_min"]==1 and a["visit_max"]==10
           and b["visit_min"]==11 and b["visit_max"]==17
           and a["M_init"]==b["M_init"]==201
           and a["n_R_values_in_group"]==b["n_R_values_in_group"]==1):
        raise ValueError("Published donor-sequence continuity flag is not verifiable")
    combined={
        **a,"source_trial_code":"2+3_POSSIBLE_CONTIGUOUS_MERGE",
        "source_recipient_rows":a["source_recipient_rows"]+b["source_recipient_rows"],
        "visit_min":1,"visit_max":17,
        "visits_contiguous":a["visits_contiguous"] and b["visits_contiguous"],
        "donor_massula_deposited":(
            a["donor_massula_deposited"]+b["donor_massula_deposited"]
        )
    }
    if combined["donor_massula_deposited"]>combined["M_init"]:
        raise ValueError("Hypothesized split-trial merger violates donor pollen mass balance")
    combined["source_deposition_fraction"]=(
        combined["donor_massula_deposited"]/combined["M_init"]
    )
    return [x for x in trials if x is not a and x is not b]+[combined]


def _average(trials:list[dict], field:str)->float:
    values=[r[field] for r in trials if r[field] is not None]
    if not values:raise ValueError("No comparable source outcomes")
    return mean(values)


def _contrast(groups:list[dict],field:str="source_deposition_fraction")->dict:
    by={arm:[x for x in groups if x["treatment"]==arm]
        for arm in ("Emasc","Intact")}
    if any(not items for items in by.values()):raise ValueError("Missing one treatment arm")
    em=_average(by["Emasc"],field)
    intact=_average(by["Intact"],field)
    return {
        "n_emasculated_coded_groups":len(by["Emasc"]),
        "n_intact_coded_groups":len(by["Intact"]),
        "emasculated_mean":em,"intact_mean":intact,
        "intact_minus_emasculated_difference":intact-em,
        "intact_over_emasculated_mean_ratio":intact/em if em>0 else None,
        "interpretation":"stained donor massulae deposited relative to initial estimated donor massulae; NOT genetically sired offspring"
    }


def _quantile(values:list[float],q:float)->float:
    a=sorted(values)
    pos=(len(a)-1)*q
    low=int(pos)
    f=pos-low
    return (1-f)*a[low]+f*a[min(low+1,len(a)-1)]


def diagnostic_source_effect(raw:bytes,bootstrap_reps:int=N_BOOT)->dict:
    if not isinstance(bootstrap_reps,int) or bootstrap_reps<100:
        raise ValueError("bootstrap_reps must be integer >=100")
    coded=_read_source_groups(raw)
    merge=_merge_possible_split(coded)
    if len(coded)!=32 or len(merge)!=31:
        raise ValueError("Original ambiguous orchid source groups not preserved")
    coded_contrast=_contrast(coded)
    merged_contrast=_contrast(merge)
    intact=[x for x in coded if x["treatment"]=="Intact"]
    omission=[]
    for excluded in intact:
        counterfactual=[x for x in coded if x is not excluded]
        info=_contrast(counterfactual)
        omission.append({
            "excluded_intact_trial_code":excluded["source_trial_code"],
            "intact_minus_emasculated_export_diff":info[
                "intact_minus_emasculated_difference"],
            "intact_over_emasculated_source_export_ratio":info[
                "intact_over_emasculated_mean_ratio"],
        })
    assert len(omission)==16
    em=[x for x in coded if x["treatment"]=="Emasc"]
    rng=random.Random(BOOT_SEED)
    boot=[]
    for _ in range(bootstrap_reps):
        a=rng.choices(em,k=len(em))
        b=rng.choices(intact,k=len(intact))
        boot.append(_average(b,"source_deposition_fraction")-
                    _average(a,"source_deposition_fraction"))
    first6=[x for x in coded if x["early_six_visit_deposition_fraction"] is not None]
    if len(first6)>32 or not first6:
        raise ValueError("No original six-recipient sensitivity support")
    first6_contrast=_contrast(first6,"early_six_visit_deposition_fraction")
    return {
        "analysis":"BALANCE_ORCHID_HARDER_2021_DONOR_MASSULA_EXPORT_SOURCE_ID_SENSITIVITY",
        "status":"AUTHENTIC_ORIGINAL_SOURCE_32_CODE_GROUP_EXPLORATORY_DISCREPANCY_ANALYSIS",
        "source_sha256":ORIGINAL_SHA256,
        "source_dryad_doi":"10.5061/dryad.41ns1rnc0",
        "paper_doi":"10.1086/712378",
        "original_source_recipient_rows":383,
        "n_original_coded_trial_groups":32,
        "paper_reported_total_trials":31,
        "source_group_counts":{"Emasc":16,"Intact":16},
        "published_trial_counts":{"Emasc":16,"Intact":15},
        "source_coded_groups_mean_export_fraction":coded_contrast,
        "possible_contiguous_split_Emasc_2_3_merge":{
            "hypothesis":"sequential visits 1..10 and 11..17, both M_init=201, not a certified bee identity",
            "results_if_merged":merged_contrast,
        },
        "all_sixteen_possible_one_intact_group_omission_envelope":{
            "n_scenarios":len(omission),
            "no_selected_favorable_trial_exclusion":True,
            "n_effect_sign_in_original_paper_direction":sum(
                x["intact_minus_emasculated_export_diff"]<0 for x in omission
            ),
            "min_export_difference":min(x["intact_minus_emasculated_export_diff"] for x in omission),
            "max_export_difference":max(x["intact_minus_emasculated_export_diff"] for x in omission),
            "min_ratio":min(x["intact_over_emasculated_source_export_ratio"] for x in omission),
            "max_ratio":max(x["intact_over_emasculated_source_export_ratio"] for x in omission),
        },
        "six_recipient_common_observed_window":{
            "definition":"only original coded trials starting at Visit=1 and observing every position 1..6",
            "contrast":first6_contrast,
            "excluded_ambiguous_or_short_code_groups":len(coded)-len(first6),
        },
        "original_coded_group_bootstrap":{
            "reps":bootstrap_reps,
            "seed":BOOT_SEED,
            "descriptive_95pct_intact_minus_emasculated_diff":[
                _quantile(boot,.025),_quantile(boot,.975)
            ],
            "not_a_sampling_CI_for_paper_31_trial_population":True,
            "known_within_source_coded_trial_ambiguous_identity":True
        },
        "original_group_anomalies":{
            "inconsistent_original_R_within_coded_group_count":sum(
                z["n_R_values_in_group"]>1 for z in coded
            ),
            "coded_groups_starting_at_visit_not_one":sum(z["visit_min"]!=1 for z in coded),
            "coded_groups_shorter_than_six_visits":sum(
                z["source_recipient_rows"]<6 for z in coded
            ),
            "R_may_not_be_unique_terminal_donor_pollinaria":True,
            "cannot_compute_2021_doubled_transport_loss_from_this_table":True,
        },
        "claim_limits":{
            "no_unique_original_31_trial_mapping":True,
            "32_code_groups_not_verified_32_independent_bees":True,
            "all_possible_original_intact_omissions_not_one_chosen":True,
            "possible_Emasc_split_is_NOT_confirmed_as_same_donor":True,
            "no_true_species_comparison_new":True,
            "not_seed_paternity_or_male_genetic_success":True,
            "source_mirror_not_a_second_original_study":True,
            "no_randomized_flower_modularity":True,
            "no_frozen_V4_human_architecture_coding_change":True,
        },
        "raw_source_rows_exported":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-csv",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    report=diagnostic_source_effect(args.original_csv.read_bytes())
    print(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True))
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()

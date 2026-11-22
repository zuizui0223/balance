"""Actual 15-donor-trial Solanum pollen delivery estimands from Zenodo CSV.

One source donor/bee trial is the replication unit (4 recipient rows).
Compare two distinct source denominators on the SAME 15 trials:
  pte_i = 100 * (H1+H2+H3+H4)_i / released_i
  full_i = 100 * (H1+H2+H3+H4)_i / total_i.
No soil/basket/terminal-body columns occur in the released CSV.
Nonparametric within-species trial bootstrap is DESCRIPTIVE and assumes
exchangeability of donor trials within species despite two original hives
and missing source-plant IDs. No new causal randomization p-value is fitted.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import json
from math import isfinite
from pathlib import Path
import random
import statistics

from scripts.audit_vasquez_2025_trial_structure import (
    RAW_BYTES,RAW_CSV,RAW_SHA256,EXPECTED_COLUMNS,
    authenticated_source
)

N_BOOT = 20000
BOOT_SEED = 20261122


def from_authenticated_rows(raw: bytes)->dict:
    if len(raw)!=RAW_BYTES or hashlib.sha256(raw).hexdigest()!=RAW_SHA256:
        raise ValueError("Original Zenodo data.csv SHA256 mismatch; refuse other bytes")
    import io
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if tuple(reader.fieldnames or ())!=EXPECTED_COLUMNS:
        raise ValueError("Unexpected published recipient source columns")
    data=list(reader)
    if len(data)!=60:
        raise ValueError("Source data are expected to have exactly 60 recipient rows")
    buckets=defaultdict(list)
    for i,row in enumerate(data,2):
        if None in row or None in row.values():
            raise ValueError(f"Ragged original Zenodo row {i}")
        if any(not str(row[k]).strip() for k in EXPECTED_COLUMNS):
            raise ValueError(f"Blank original recipient value at line {i}")
        key=(row["flower_sp"],row["trial_number"],row["bee_hive"],row["bee_ID"])
        if not key[0] in ("S.rostratum","S.dulcamara"):
            raise ValueError("Unexpected source species identity")
        try:
            position=int(row["recipient"])
        except ValueError as exc:
            raise ValueError("Recipient order must be original 1..4 integers") from exc
        if position not in (1,2,3,4):
            raise ValueError("Unexpected source recipient order")
        values={}
        for col in ("duration_visit","pollen_stigma","donor_released",
                    "donor_remaining","donor_total"):
            try: x=float(row[col])
            except ValueError as exc:
                raise ValueError(f"Invalid original numeric field {col}") from exc
            if not isfinite(x) or x<0 or (col=="duration_visit" and x==0):
                raise ValueError(f"Invalid original numeric range {col}")
            values[col]=x
        buckets[key].append({"recipient":position,**values})
    if len(buckets)!=15:
        raise ValueError("Source recipient rows do not identify exactly 15 trials")
    species_counts=Counter()
    trial_metrics=[]
    hive_species=Counter()
    bee_ids=set()
    for key,group in sorted(buckets.items()):
        species,trial_num,hive,bee=key
        if len(group)!=4 or sorted(z["recipient"] for z in group)!=[1,2,3,4]:
            raise ValueError("Source trial missing a measured recipient position")
        if (hive,bee) in bee_ids:
            raise ValueError("Bee ID reused in another supposedly independent donor trial")
        bee_ids.add((hive,bee))
        species_counts[species]+=1
        hive_species[(species,hive)]+=1
        donor={}
        for column in ("donor_released","donor_remaining","donor_total"):
            source_values=[float(z[column]) for z in group]
            if max(source_values)-min(source_values)>max(0.01,1e-8*max(source_values)):
                raise ValueError("Original within-trial donor stock duplicated inconsistently")
            donor[column]=source_values[0]
        released=donor["donor_released"]
        remaining=donor["donor_remaining"]
        total=donor["donor_total"]
        if total<=0 or released<=0 or remaining<0:
            raise ValueError("Original donor pollen pool not positive")
        # All source counts are estimated to finite precision, with small
        # numeric rounding discrepancy allowed; never silently replace A.
        mass_error=(released+remaining)-total
        if abs(mass_error)>max(0.1,1e-6*total):
            raise ValueError("Donor total/released/remaining fail source mass balance")
        stigmas=[z["pollen_stigma"] for z in sorted(group,key=lambda x:x["recipient"])]
        H=sum(stigmas)
        if H<=0 or H>released:
            raise ValueError("Recipient total exceeds source-pollen removal")
        rec={
            "source_species":species,
            "source_trial_id":trial_num,
            "source_hive":hive,
            "source_bee_id":bee,
            "number_recipient_stigmas":4,
            "measured_released_grains":released,
            "measured_total_donor_grains":total,
            "measured_remaining_grains":remaining,
            "measured_recipient_stigma_grains":H,
            "fraction_released_pct_of_measured_source":100*released/total,
            "pollen_transfer_efficiency_pct_of_removed":100*H/released,
            "source_to_four_stigmas_pct_of_production":100*H/total,
            "first_recipient_pct_of_four_stigmas":100*stigmas[0]/H,
            "recipient_pollen_counts":stigmas,
            "source_count_balance_error_grains":mass_error,
        }
        assert abs(rec["source_to_four_stigmas_pct_of_production"]-
                   rec["fraction_released_pct_of_measured_source"]*
                   rec["pollen_transfer_efficiency_pct_of_removed"]/100)<1e-12
        trial_metrics.append(rec)
    if species_counts!=Counter({"S.rostratum":6,"S.dulcamara":9}):
        raise ValueError("Original donor-trial species n 6/9 not recovered")
    if len(bee_ids)!=15:
        raise ValueError("Unexpected bee unit reuse")
    return {
        "source": {
            "raw_csv_sha256":RAW_SHA256,
            "n_donor_trials":15,
            "n_original_recipient_measurements":60,
            "n_distinct_bee_identifiers":len(bee_ids),
            "n_original_hives":len({h for _,h in hive_species}),
            "species_by_hive_trials":[
                {"species":s,"hive":h,"trials":n}
                for (s,h),n in sorted(hive_species.items())
            ],
            "author_ground_basket_body_columns_present":False,
            "original_author_reproductive_paternity_measured":False,
        },
        "trials":trial_metrics,
    }


def _percentile(values, q):
    arr=sorted(values)
    pos=(len(arr)-1)*q
    low=int(pos)
    delta=pos-low
    return arr[low]*(1-delta)+arr[min(low+1,len(arr)-1)]*delta


def trial_descriptive_summary(parsed: dict, *, bootstrap_samples=N_BOOT):
    if not isinstance(bootstrap_samples,int) or bootstrap_samples<100:
        raise ValueError("Bootstrap count should be fixed positive integer >=100")
    rows=parsed["trials"]
    species=defaultdict(list)
    for x in rows:
        species[x["source_species"]].append(x)
    sps=("S.rostratum","S.dulcamara")
    if tuple(sorted(species))!=tuple(sorted(sps)):
        raise ValueError("Incorrect original species grouping")
    fields=(
        "fraction_released_pct_of_measured_source",
        "pollen_transfer_efficiency_pct_of_removed",
        "source_to_four_stigmas_pct_of_production",
        "first_recipient_pct_of_four_stigmas",
    )
    table={}
    for name in sps:
        group=species[name]
        table[name]={
            "n_donor_bee_trials":len(group),
            "n_donor_bees":len({(x["source_hive"],x["source_bee_id"]) for x in group}),
            "mean_per_trial":{f:statistics.mean(x[f] for x in group) for f in fields},
            "median_per_trial":{f:statistics.median(x[f] for x in group) for f in fields},
            "range_per_trial":{f:[min(x[f] for x in group),max(x[f] for x in group)] for f in fields},
            "hive_counts":dict(Counter(x["source_hive"] for x in group)),
        }
    rng=random.Random(BOOT_SEED)
    boot_values={}
    # Only one prespecified primary denominator-sensitive contrast (H/A).
    # The pte H/B and removal B/A are reported for interpretation, not
    # selected to prefer a smaller trial-bootstrap p-value.
    for key in fields[:3]:
        a=[x[key] for x in species["S.rostratum"]]
        b=[x[key] for x in species["S.dulcamara"]]
        dist=[]
        for _ in range(bootstrap_samples):
            aa=statistics.mean(rng.choices(a,k=len(a)))
            bb=statistics.mean(rng.choices(b,k=len(b)))
            dist.append(bb-aa)
        boot_values[key]={
            "dulcamara_minus_rostratum_pct_points":statistics.mean(b)-statistics.mean(a),
            "descriptive_95pct_trial_bootstrap_interval":[
                _percentile(dist,.025),_percentile(dist,.975)
            ],
            "bootstrap_replicates":bootstrap_samples,
            "not_random_assignment_or_colony_robust_confidence":True,
        }
    return {
        "analysis":"BALANCE_VASQUEZ_2025_ACTUAL_TRIAL_LEVEL_END_TO_END_POLLEN_TRANSFER_V1",
        "status":"ORIGINAL_ZENODO_60_RECIPIENT_ROWS_AGGREGATED_TO_15_AUTHENTIC_TRIALS",
        "article_doi":"10.26786/1920-7603(2025)836",
        "zenodo_record_id":17102653,
        "source_hash":RAW_SHA256,
        "independent_original_research_programmes":1,
        "total_donor_trials":15,
        "nested_stigma_rows":60,
        "species":table,
        "predefined_trial_level_species_mean_differences":boot_values,
        "published_author_species_mean_PTE_pct_of_removed":{
            "S.rostratum":0.86,"S.dulcamara":1.00
        },
        "published_author_species_mean_removed_pct_of_production":{
            "S.rostratum":13.55,"S.dulcamara":37.77
        },
        "original_species_results_not_forced_to_match_author_rounded_figures":True,
        "statistical_limits":{
            "bootstrap_level":"One donor-bee trial (4 recipient measurements nested)",
            "bootstrap_exchangeability":"Within species, trial exchangeability assumed descriptively; only two hives and plants not identified",
            "no_inferential_species_causality":True,
            "no_colony_robust_population_generalization":True,
            "no_species_equivalence_claim":True,
            "no_ground_corbicula_terminal_body_source_rows":True,
            "no_genetic_paternity":True,
            "not_novel_evolutionary_transition":True,
            "no_BALANCE_phi_or_K":True,
        },
        "raw_trial_rows_in_repo":0,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-csv",type=Path)
    p.add_argument("--download",action="store_true")
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    if args.original_csv:
        raw=args.original_csv.read_bytes()
    elif args.download:
        raw,_=authenticated_source()
    else:
        raise SystemExit("HOLD: genuine original Zenodo source CSV not supplied or download not requested")
    source=from_authenticated_rows(raw)
    summary=trial_descriptive_summary(source)
    output=json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)
    print(output)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output+"\n",encoding="utf-8")


if __name__=="__main__":
    main()

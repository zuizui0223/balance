#!/usr/bin/env python3
"""Replay 48-species public-documentation rank association within family.

Consumes authenticated, versioned original GBIF occurrence and GloBI text
sources. Emits a purely exploratory, exactly enumerated conditional
EXCHANGEABILITY REFERENCE, not a preregistered biological p-value, true
interaction frequency, sampling-effort causal effect or BALANCE worldline.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from balance_domain.gbif_globi_within_family import (
    MANIFEST, analyze_effort_family_rank_from_source,
)


def write_readout(root:Path,manifest:Path,out:Path)->dict:
    if out.exists():
        raise ValueError("refuse to overwrite prior original-documentation audit")
    result=analyze_effort_family_rank_from_source(root,manifest)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as stream:
        json.dump(result,stream,indent=2,sort_keys=True,allow_nan=False)
        stream.write("\n")
    return result


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo-root",type=Path,default=ROOT)
    parser.add_argument("--manifest",type=Path,default=ROOT/MANIFEST)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=write_readout(args.repo_root,args.manifest,args.out)
    p=result["primary_indexed_occurrence_counts"]
    q=result["georeferenced_occurrence_counts_sensitivity"]
    print(json.dumps({
        "status":result["status"],
        "mixed_families":p["n_informative_mixed_families"],
        "all_documented_higher_in_mixed_pairs":
            p["n_pairs_documented_has_higher_GBIF_count"],
        "n_conditional_family_label_assignments":
            p["conditional_reference_assignments"],
        "upper_reference_fraction":
            p["conditional_one_sided_upper_reference_fraction"],
        "two_sided_reference_fraction":
            p["conditional_two_sided_reference_fraction"],
        "georeferenced_rank_agrees":q["observed_documented_rank_sum"]==
            p["observed_documented_rank_sum"],
        "confirmed_field_effort_effect":False,
        "focal_interaction_conflict_prevalence_identified":False,
        "strict_BALANCE_occupancy_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""Reproduce archived public GloBI INTERACTION OPPORTUNITY pilot.

This reads the four committed original GloBI API *text* snapshots, validates
Git blob source hashes, and refuses any biological conflict inference.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from balance_domain.globi_opportunity import summarize_globi_files


def build_pilot_receipt(root:Path,contract:Path,out:Path)->dict:
    if out.exists():
        raise ValueError("cannot overwrite GloBI source interaction pilot receipt")
    result=summarize_globi_files(root,contract)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True,allow_nan=False)
        f.write("\n")
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,default=ROOT)
    p.add_argument("--contract",type=Path,
                   default=ROOT/"data/BALANCE_GLOBI_OPPORTUNITY_SOURCE_SNAPSHOT_V1.json")
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    r=build_pilot_receipt(args.repo_root,args.contract,args.out)
    print(json.dumps({
        "status":r["status"],
        "queries":r["n_source_selected_plant_queries"],
        "original_relation_records":r["total_original_snapshot_relation_rows"],
        "strict_target_species_records":r["total_strict_exact_target_taxon_rows"],
        "wrong_target_taxon_records":r["total_mismatched_target_taxon_rows"],
        "source_qualified_Solanum_rostratum_Dunal_observations":None,
        "new_SCH_conflict":False,"structural_BALANCE":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

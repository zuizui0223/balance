#!/usr/bin/env python3
"""Report real official GBIF occurrence effort and saved GloBI coverage.

All 48 originally GBIF-selected botanical species are included. Absence
of indexed occurrence or GloBI relationships is missing record coverage,
not biological absence. This is NOT a causal ecological trade-off model.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from balance_domain.gbif_occurrence_effort import source_effort_audit_from_files

FIELDS=(
    "gbif_species_key","species","family","order",
    "gbif_occurrence_search_count",
    "gbif_occurrence_search_has_coordinates_count",
    "globi_exact_target_name_relation_rows","globi_name_recorded",
)


def write_source_readout(root:Path,manifest:Path,out_json:Path,out_csv:Path)->dict:
    if out_json==out_csv or out_json.exists() or out_csv.exists():
        raise ValueError("source audit receipt destination exists or is ambiguous")
    result=source_effort_audit_from_files(root,manifest)
    out_json.parent.mkdir(parents=True,exist_ok=True)
    out_csv.parent.mkdir(parents=True,exist_ok=True)
    with out_json.open("x",encoding="utf-8") as fp:
        json.dump(result,fp,indent=2,sort_keys=True,allow_nan=False)
        fp.write("\n")
    with out_csv.open("x",encoding="utf-8",newline="") as fp:
        writer=csv.DictWriter(fp,fieldnames=FIELDS)
        writer.writeheader()
        for row in result["species"]:
            writer.writerow({k:row[k] for k in FIELDS})
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo-root",type=Path,default=ROOT)
    parser.add_argument("--manifest",type=Path,
        default=ROOT/"data/BALANCE_GBIF_OCCURRENCE_EFFORT_48_SOURCE_MANIFEST_V1.json")
    parser.add_argument("--out-json",type=Path,required=True)
    parser.add_argument("--out-csv",type=Path,required=True)
    a=parser.parse_args()
    v=write_source_readout(a.repo_root,a.manifest,a.out_json,a.out_csv)
    print(json.dumps({
        "status":v["status"],
        "n_species":v["n_species_first_selected"],
        "species_with_GBIF_occurrences":v["source_source_aggregate"][
            "n_with_any_GBIF_occurrence"
        ],
        "GloBI_documented_median_GBIF_occurrences":v[
            "source_source_aggregate"
        ]["median_GBIF_occurrences_GloBI_documented"],
        "GloBI_undocumented_median_GBIF_occurrences":v[
            "source_source_aggregate"
        ]["median_GBIF_occurrences_GloBI_undocumented"],
        "new_conflict_fitness_inference":False,
        "structural_BALANCE_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

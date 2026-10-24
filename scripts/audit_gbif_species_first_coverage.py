#!/usr/bin/env python3
"""Generate reproducible GBIF/GloBI source-first data coverage JSON and CSV.

This is ecological-network OBSERVATION COVERAGE, not measured functional
trade-offs or BALANCE model output. Each source candidate remains in the table.
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

from balance_domain.gbif_species_first_coverage import audit_source_files

FIELDS=(
    "gbif_species_key","gbif_accepted_species_name","family",
    "GBIF_search_numOccurrences_field","original_GloBI_rows",
    "GloBI_exact_target_name_rows","GloBI_direct_identical_GBIF_key_rows",
    "GloBI_name_only_other_identifier_rows",
    "GloBI_other_taxon_target_rows",
    "literal_flower_visit_or_pollinate_rows",
)


def write_readout(root:Path,out_json:Path,out_csv:Path)->dict:
    if out_json==out_csv or out_json.exists() or out_csv.exists():
        raise ValueError("source-first report destination exists or is ambiguous")
    result=audit_source_files(root)
    out_json.parent.mkdir(parents=True,exist_ok=True)
    out_csv.parent.mkdir(parents=True,exist_ok=True)
    with out_json.open("x",encoding="utf-8") as f:
        json.dump(result,f,sort_keys=True,indent=2,allow_nan=False)
        f.write("\n")
    with out_csv.open("x",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(FIELDS))
        writer.writeheader()
        for row in result["species_coverage"]:
            writer.writerow({k:row.get(k) for k in FIELDS})
    return result


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,default=ROOT)
    p.add_argument("--out-json",type=Path,required=True)
    p.add_argument("--out-csv",type=Path,required=True)
    args=p.parse_args()
    data=write_readout(args.repo_root,args.out_json,args.out_csv)
    print(json.dumps({
        "status":data["status"],
        "n_species":data["n_gbif_accepted_taxa_selected"],
        "species_with_GloBI_records":data[
            "n_species_with_exact_target_name_relation"],
        "relation_rows":data["n_exact_target_name_rows"],
        "direct_gbif_key_rows":data[
            "n_exact_target_and_direct_GBIF_key_rows"],
        "taxa_with_flower_visit_labels":data[
            "n_taxa_with_flower_visit_or_pollinate_label"],
        "structural_BALANCE_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

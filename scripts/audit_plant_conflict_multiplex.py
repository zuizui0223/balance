#!/usr/bin/env python3
"""Read-only source-indexed plant functional-conflict multiplex summary."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from balance_domain.plant_conflict_multiplex import REQUIRED_FILES, analyze_multiplex_sources


def source_multiplex_receipt(root:Path,out:Path)->dict:
    if out.exists():
        raise ValueError("refuse to overwrite a prior source pair multiplex receipt")
    files={relative:root/relative for relative in REQUIRED_FILES}
    result=analyze_multiplex_sources(files)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as fh:
        json.dump(result,fh,indent=2,sort_keys=True,allow_nan=False)
        fh.write("\n")
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,default=ROOT)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    report=source_multiplex_receipt(args.repo_root,args.out)
    print(json.dumps({
        "status":report["status"],
        "records":report["total_source_screened_records"],
        "distinct_dependency_groups":report["n_distinct_source_dependency_groups"],
        "cross_source_species_overlap":report["n_cross_source_species_overlaps"],
        "dual_conflict_positive_different_organization":report[
            "n_source_dual_positive_distinct_architecture_cases"
        ],
        "independently_adjudicated":False,
        "structural_BALANCE_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

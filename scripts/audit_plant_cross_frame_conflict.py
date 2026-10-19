#!/usr/bin/env python3
"""Reproduce two frozen plant-review frames without a fake prevalence estimate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from balance_domain.plant_cross_frame_conflict import (
    REQUIRED_SOURCE_PATHS, analyze_cross_frame_sources,
)


def build_receipt(root:Path,out:Path)->dict:
    if out.exists():
        raise ValueError("refusing overwrite of an existing source-frame receipt")
    paths={relative:root/relative for relative in REQUIRED_SOURCE_PATHS}
    result=analyze_cross_frame_sources(paths)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as fh:
        json.dump(result,fh,sort_keys=True,indent=2,allow_nan=False)
        fh.write("\n")
    return result


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,default=ROOT)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    readout=build_receipt(args.repo_root,args.out)
    print(json.dumps({
        "status":readout["status"],
        "u1_positive":readout["screened_review_frames"]["U1"]["n_demonstrated_same_coordinate_conflicts"],
        "u2_positive":readout["screened_review_frames"]["U2"]["n_demonstrated_same_coordinate_conflicts"],
        "shared_species":readout["n_shared_species_between_frames"],
        "cross_frame_prevalence_estimated":False,
        "structural_BALANCE_occupancy_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

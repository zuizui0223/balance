#!/usr/bin/env python3
"""Read-only, outcome-free matched-bract optical selectivity pilot receipt.

This validates a *self-declared* pre-biological-outcome physical methods
configuration. It cannot verify the external chronology, treatment allocation
or future 13C transport and seed-fitness effects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from balance_domain.dalechampia_bract_isolation import (
    evaluate_bract_local_optical_pilot,
    parse_method_csv,
)


def evaluate_files(thresholds:Path, observations:Path, out:Path) -> dict:
    if out.exists():
        raise ValueError("cannot overwrite previous prospective method-only receipt")
    config_bytes=thresholds.read_bytes()
    data_bytes=observations.read_bytes()
    data=evaluate_bract_local_optical_pilot(
        json.loads(config_bytes),
        parse_method_csv(data_bytes),
    )
    data["calibration_spec_sha256"]=hashlib.sha256(config_bytes).hexdigest()
    data["method_only_observation_sha256"]=hashlib.sha256(data_bytes).hexdigest()
    data["original_field_source_lineage_independently_verified"]=False
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as fp:
        json.dump(data,fp,indent=2,sort_keys=True,allow_nan=False)
        fp.write("\n")
    return data


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--thresholds",type=Path,required=True)
    parser.add_argument("--measurements",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=evaluate_files(args.thresholds,args.measurements,args.out)
    print(json.dumps({
        "status":result["status"],
        "n_independent_plants":result["n_unique_maternal_plants"],
        "n_failed_maternal_blocks":result["n_failed_maternal_blocks"],
        "seed_fitness_estimated":False,
        "bract_carbon_flux_identified":False,
        "structural_BALANCE_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

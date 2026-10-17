#!/usr/bin/env python3
"""Evaluate source-discrimination measurements for a prospective bract 13C assay.

Only runs with externally produced numeric tracer data AND self-declared
pre-outcome calibrations. This does not verify that pre-registration actually
preceded experiments; the receipt expressly refuses carbon causal/fitness
or structural BALANCE identification even if all supplied blocks pass.
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

from balance_domain.dalechampia_tracer_source import (
    parse_tracer_csv,screen_bract_13c_source,
)


def build_receipt(spec_path:Path, measurements_path:Path, output_path:Path) -> dict:
    if output_path.exists():
        raise ValueError("refusing to overwrite source-discrimination pilot receipt")
    calibration_bytes=spec_path.read_bytes()
    observed_bytes=measurements_path.read_bytes()
    results=screen_bract_13c_source(
        json.loads(calibration_bytes),parse_tracer_csv(observed_bytes)
    )
    results["calibration_json_sha256"]=hashlib.sha256(calibration_bytes).hexdigest()
    results["isotope_measurement_csv_sha256"]=hashlib.sha256(observed_bytes).hexdigest()
    results["external_calibration_proof_or_preregistered_timestamp_verified"]=False
    output_path.parent.mkdir(parents=True,exist_ok=True)
    with output_path.open("x",encoding="utf-8") as target:
        json.dump(results,target,sort_keys=True,indent=2,allow_nan=False)
        target.write("\n")
    return results


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--calibration",type=Path,required=True)
    parser.add_argument("--isotope-measurements",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=build_receipt(args.calibration,args.isotope_measurements,args.out)
    print(json.dumps({
        "status":result["status"],
        "independent_maternal_plants":result["n_distinct_maternal_plants"],
        "independent_three_arm_blocks":result["n_randomized_blocks"],
        "carbon_source_causally_identified":False,
        "seed_fitness_effect_identified":False,
        "strict_BALANCE_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

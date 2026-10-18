#!/usr/bin/env python3
"""Run a provenance-pinned, independent-mother blocked 13C randomization test.

An arm-difference p-value cannot establish bract source carbon causality;
calibrated source localization, biological uptake comparisons and fitness
identification all remain future empirical requirements.
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

from balance_domain.dalechampia_tracer_source import parse_tracer_csv
from balance_domain.dalechampia_tracer_randomization import analyze_block_randomization


def build_inferential_receipt(
    source_calibration:Path, inference_contract:Path,
    isotope_rows:Path, out:Path,
)->dict:
    if out.exists():
        raise ValueError("refusing to overwrite source randomization inference receipt")
    source_bytes=source_calibration.read_bytes()
    inference_bytes=inference_contract.read_bytes()
    plant_bytes=isotope_rows.read_bytes()
    result=analyze_block_randomization(
        json.loads(source_bytes),
        json.loads(inference_bytes),
        parse_tracer_csv(plant_bytes),
        actual_calibration_sha256=hashlib.sha256(source_bytes).hexdigest(),
    )
    result["source_calibration_sha256"]=hashlib.sha256(source_bytes).hexdigest()
    result["pre_outcome_inference_rules_sha256"]=hashlib.sha256(inference_bytes).hexdigest()
    result["observed_isotope_measurement_sha256"]=hashlib.sha256(plant_bytes).hexdigest()
    result["external_pre_outcome_protocol_time_authenticated"]=False
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as w:
        json.dump(result,w,indent=2,sort_keys=True,allow_nan=False)
        w.write("\n")
    return result


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-calibration",type=Path,required=True)
    parser.add_argument("--inference-contract",type=Path,required=True)
    parser.add_argument("--isotope-measurements",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    out=build_inferential_receipt(
        args.source_calibration,args.inference_contract,
        args.isotope_measurements,args.out,
    )
    print(json.dumps({
        "status":out["status"],
        "n_independent_blocks":out["n_independent_randomized_three_arm_blocks"],
        "smallest_possible_two_sided_p":out["exact_minimum_attainable_two_sided_p"],
        "computed_two_sided_p":
            out["sharp_no_regime_effect_randomization_inference"]["two_sided_p"],
        "bract_carbon_source_causally_identified":False,
        "mature_seed_fitness_identified":False,
        "strict_BALANCE_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

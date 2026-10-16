#!/usr/bin/env python3
"""Source-variance-based scenario planning, NEVER evidence of field power."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from balance_domain.dalechampia_paired_design_power import plan_paired_blossom_scenarios


def build_plan(source_path:Path,scenarios_path:Path,out:Path) -> dict:
    if out.exists():
        raise ValueError("refusing overwrite of existing design sensitivity report")
    original_bytes=source_path.read_bytes()
    design_bytes=scenarios_path.read_bytes()
    plan=plan_paired_blossom_scenarios(
        json.loads(design_bytes),json.loads(original_bytes)
    )
    plan["published_source_variance_receipt_sha256"]=hashlib.sha256(original_bytes).hexdigest()
    plan["scenario_config_sha256"]=hashlib.sha256(design_bytes).hexdigest()
    plan["projected_future_effect_inferred_from_published_treatments"]=False
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as fp:
        json.dump(plan,fp,sort_keys=True,indent=2,allow_nan=False)
        fp.write("\n")
    return plan


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-variance",type=Path,
                        default=ROOT/"data/DALECHAMPIA_2015_NESTED_BLOSSOM_SOURCE_VERIFIED_V1.json")
    parser.add_argument("--scenarios",type=Path,
                        default=ROOT/"data/DALECHAMPIA_BRACT_ISOLATION_POWER_SCENARIOS_V1.json")
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=build_plan(args.source_variance,args.scenarios,args.out)
    print(json.dumps({
        "status":result["status"],
        "hypothetical_scenario_count":len(result["scenarios"]),
        "observed_bract_specific_effect_size_estimated":False,
        "seed_fitness_measured":False,
        "structural_BALANCE_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

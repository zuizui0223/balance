#!/usr/bin/env python3
"""Compare exact regenerated source receipt to frozen original-Dryad analysis.

A match means source bytes and *registered deterministic descriptive algorithm*
replayed; it does NOT reproduce the 2015 mixed-effects paper, seed carbon
causality, or structural BALANCE architecture values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def validate_source_freeze(frozen: dict, reproduced: dict, raw_bytes: bytes) -> dict:
    if frozen.get("schema_version") != "DALECHAMPIA_2015_EXACT_DRYAD_SENSITIVITY_FREEZE_V1":
        raise ValueError("frozen exact-Dryad source schema mismatch")
    if frozen.get("status") != "ORIGINAL_PUBLIC_DRYAD_SOURCE_RECOMPUTED_NOT_SOURCE_MIXED_MODEL":
        raise ValueError("source freeze not approved for this inference")
    digest=hashlib.sha256(raw_bytes).hexdigest()
    if digest != frozen.get("exact_generated_receipt_sha256"):
        raise ValueError("computed source readout SHA256 drifted from frozen receipt")
    if reproduced.get("contract_sha256") != frozen["original_source_contract_sha256"]:
        raise ValueError("source contract digest mismatch")
    if reproduced.get("original_files_sha256") != frozen["original_source_file_sha256"]:
        raise ValueError("original Dryad files digest mismatch")
    seed = frozen["observed_seed_support"]
    for expected, actual in (
        (seed["recorded_seed_rows"], reproduced.get("n_seed_records")),
        (seed["recorded_seed_masses"], reproduced.get("n_seed_masses_recorded")),
        (seed["maternal_plants_with_any_seeds"], reproduced.get("n_maternal_plants_with_any_seed_record")),
        (seed["blossom_identities"], reproduced.get("n_blossoms")),
    ):
        if expected != actual:
            raise ValueError("source support changed")
    if seed["abortion_morphology_independently_verified"] is not False:
        raise ValueError("original morphology not independently observed")
    physiological=frozen["bract_gas_within_plant"]
    gas=reproduced.get("gas_exchange_within_plant",{})
    for expected, actual in (
        (physiological["n_plants"], gas.get("source_physiology_plants")),
        (physiological["green_n"], gas.get("source_green_bract_measurements")),
        (physiological["white_n"], gas.get("source_white_bract_measurements")),
        (physiological["mean_green"], gas.get("area_based_green_mean")),
        (physiological["mean_white"], gas.get("area_based_white_mean")),
        (physiological["mean_green_minus_white"], gas.get("within_plant_green_minus_white_mean")),
        (physiological["plant_bootstrap_95"], gas.get("bootstrap_plant_cluster_95_interval")),
    ):
        if expected != actual:
            raise ValueError("source gas pairing or result changed")

    for lane, contrasts in frozen["paired_maternal_seed_mass"]["contrasts"].items():
        actual_lane=reproduced.get("analyses",{}).get(lane)
        if not isinstance(actual_lane,dict):
            raise ValueError("maternal source analysis lane missing")
        records={x["comparison"]:x for x in actual_lane["arm_contrasts"]}
        for arm, ref in contrasts.items():
            obj=records.get(arm)
            if not obj or (ref["n"] != obj.get("n_maternal_pairs")
                or ref["mean"] != obj.get("mean_of_within_mother_blossom_mean_differences_mg")
                or ref["ci95"] != obj.get("bootstrap_percentile_95_interval_mg")):
                raise ValueError("maternal source contrast drifted")
    limits=frozen["scientific_ceiling"]
    if (limits.get("direct_structural_balance_identified") is not False
            or reproduced.get("structural_BALANCE_identified") is not False
            or reproduced.get("original_2015_published_model_reproduced") is not False
            or reproduced.get("numeric_abortions_independently_confirmed_by_morphology") is not False):
        raise ValueError("source readout overpromoted into causal BALANCE evidence")
    return {
        "status":"ORIGINAL_DRYAD_DESCRIPTIVE_RECEIPT_INDEPENDENTLY_REPLAYED",
        "source_receipt_sha256":digest,
        "source_raw_doi":"10.5061/dryad.nb675",
        "source_mixed_model_reproduced":False,
        "structural_BALANCE_identified":False,
    }


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--frozen",type=Path,required=True)
    parser.add_argument("--computed",type=Path,required=True)
    args=parser.parse_args()
    raw=args.computed.read_bytes()
    calculated=json.loads(raw)
    frozen=json.loads(args.frozen.read_text(encoding="utf-8"))
    print(json.dumps(validate_source_freeze(frozen,calculated,raw),sort_keys=True))


if __name__=="__main__":
    main()

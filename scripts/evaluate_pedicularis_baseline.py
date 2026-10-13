#!/usr/bin/env python3
"""Emit a hashed method-only SCH/XY water-baseline screening receipt.

This is a field-method feasibility aid, not an empirical BALANCE result.
Input rejects pollen/seed/fitness columns and uses one verified independent
water compartment per plant; there is no outcome-based threshold selection.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.pedicularis_baseline import (
    FIELDS, evaluate_pedicularis_baseline_method,
)


def build_receipt(pilot_csv: Path, frozen_config_json: Path, out: Path) -> dict:
    if out.exists():
        raise ValueError("baseline receipt output already exists")
    pilot_bytes = pilot_csv.read_bytes()
    config_bytes = frozen_config_json.read_bytes()
    config = json.loads(config_bytes)
    with pilot_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("baseline pilot CSV header differs from method-only schema")
        rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError("baseline pilot CSV contains extra values beyond method-only schema")
    result = evaluate_pedicularis_baseline_method(rows, config)
    receipt = {
        "schema_version": "PEDICULARIS_SCH_XY_BASELINE_METHOD_RECEIPT_V1",
        "status": result.status,
        "reasons": list(result.reasons),
        "context_id": result.context_id,
        "fitness_scale_id": result.fitness_scale_id,
        "plant_counts": result.plant_counts,
        "water_depth_extrema_mm": result.water_depth_extrema_mm,
        "sch_y0_profile_endpoint_gap_mm": result.sch_y0_profile_endpoint_gap_mm,
        "claim_level": result.claim_level,
        "source_field_lineage_verified": result.source_field_lineage_verified,
        "reproduction_outcomes_read": result.reproduction_outcomes_read,
        "structural_architecture_cost_identified": (
            result.structural_architecture_cost_identified
        ),
        "source_csv_sha256": hashlib.sha256(pilot_bytes).hexdigest(),
        "frozen_config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "environment_state_labels": [
            "SCH_FIXED", "XY_Y0_DRY", "XY_Y1_WET"
        ],
        "provenance_boundary": (
            "hashes identify supplied method-only files; cannot independently "
            "link these to the archived SCH/BITA source surface or prove pre-outcome timing"
        ),
        "functional_state_BALANCE_identified": False,
        "structural_architecture_BALANCE_identified": False,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=out.parent,
        prefix=".pedicularis-baseline-", suffix=".tmp", delete=False,
    ) as handle:
        tmp = Path(handle.name)
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write("\n")
    try:
        os.replace(tmp, out)
    finally:
        if tmp.exists():
            tmp.unlink()
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--thresholds", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = build_receipt(args.pilot, args.thresholds, args.out)
    print(json.dumps({
        "status": receipt["status"],
        "reasons": receipt["reasons"],
        "claim_level": receipt["claim_level"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

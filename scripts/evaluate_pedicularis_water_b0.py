#!/usr/bin/env python3
"""Pedicularis three-arm water-method pilot gate.

The input CSV contains *only method measurements*, no fitness or insect
response outcomes. No experiment has run merely because this tool exists.
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

from balance_domain.pedicularis_water_b0 import FIELDS, evaluate_water_b0


def build_receipt(pilot: Path, config_file: Path, output: Path) -> dict:
    if output.exists():
        raise ValueError("B0 method receipt output already exists")
    source_bytes = pilot.read_bytes()
    config_bytes = config_file.read_bytes()
    config = json.loads(config_bytes)
    with pilot.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("B0 method-only CSV header differs from frozen schema")
        records = list(reader)
    if any(None in row for row in records):
        raise ValueError("B0 CSV has fields beyond allowed method-only header")
    receipt = evaluate_water_b0(records, config)
    receipt["source_csv_sha256"] = hashlib.sha256(source_bytes).hexdigest()
    receipt["threshold_config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=output.parent,
        prefix=".pedicularis-b0-", suffix=".tmp", delete=False,
    ) as file:
        temp = Path(file.name)
        json.dump(receipt, file, indent=2, sort_keys=True)
        file.write("\n")
    try:
        os.replace(temp, output)
    finally:
        if temp.exists():
            temp.unlink()
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--thresholds", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = build_receipt(args.pilot, args.thresholds, args.out)
    print(json.dumps({
        "status": result["status"],
        "gate_reasons": result["gate_reasons"],
        "n_focal_flowers": result["n_focal_flowers"],
        "n_distinct_plants_total": result["n_distinct_plants_total"],
        "claim_ceiling": result["claim_ceiling"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

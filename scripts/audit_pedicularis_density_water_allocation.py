#!/usr/bin/env python3
"""Prospective outcome-blinded Pedicularis density x water design support."""
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
from balance_domain.pedicularis_density_water_allocation import (
    FIELDS, assess_density_water_allocation,
)


def build_receipt(rows_path: Path, protocol_path: Path, b0_path: Path, out_path: Path):
    if out_path.exists():
        raise ValueError("allocation receipt already exists")
    raw_bytes = rows_path.read_bytes()
    config_bytes = protocol_path.read_bytes()
    b0_bytes = b0_path.read_bytes()
    config = json.loads(config_bytes)
    b0_receipt = json.loads(b0_bytes)
    b0_sha = hashlib.sha256(b0_bytes).hexdigest()
    with rows_path.open(encoding="utf-8", newline="") as h:
        reader = csv.DictReader(h)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("density allocation CSV header differs from canonical schema")
        records = list(reader)
    if any(None in row for row in records):
        raise ValueError("allocation CSV contains unregistered columns")
    receipt = assess_density_water_allocation(
        records, config, b0_method_receipt=b0_receipt,
        b0_method_sha256=b0_sha,
    )
    receipt["allocation_csv_sha256"] = hashlib.sha256(raw_bytes).hexdigest()
    receipt["protocol_json_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    receipt["linked_b0_receipt_sha256"] = b0_sha
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=out_path.parent,
        prefix=".pedicularis-density-water-", suffix=".tmp", delete=False,
    ) as h:
        temp = Path(h.name)
        json.dump(receipt, h, indent=2, sort_keys=True)
        h.write("\n")
    try:
        os.replace(temp, out_path)
    finally:
        if temp.exists():
            temp.unlink()
    return receipt


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--allocation", type=Path, required=True)
    p.add_argument("--protocol", type=Path, required=True)
    p.add_argument("--b0-method-receipt", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = build_receipt(args.allocation, args.protocol, args.b0_method_receipt, args.out)
    print(json.dumps({
        "status": result["status"],
        "n_independent_plants": result["n_independent_plants"],
        "n_independent_patches": result["n_independent_patches"],
        "patches_by_stratum": result["patches_by_stratum"],
        "gate_reasons": result["gate_reasons"],
        "claim_ceiling": result["claim_ceiling"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

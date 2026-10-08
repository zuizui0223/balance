#!/usr/bin/env python3
"""Measure Pedicularis exsertion versus waterline geometry without outcomes."""
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

from balance_domain.pedicularis_exposure_geometry import (
    FIELDS, audit_exposure_geometry,
)


def build_receipt(data_path: Path, protocol_path: Path, output_path: Path) -> dict:
    if output_path.exists():
        raise ValueError("exposure geometry receipt already exists")
    source_bytes = data_path.read_bytes()
    protocol_bytes = protocol_path.read_bytes()
    with data_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("exposure geometry CSV columns differ from canonical method-only schema")
        rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError("exposure geometry CSV has extra data fields")
    config = json.loads(protocol_bytes)
    result = audit_exposure_geometry(rows, config)
    result["source_csv_sha256"] = hashlib.sha256(source_bytes).hexdigest()
    result["protocol_sha256"] = hashlib.sha256(protocol_bytes).hexdigest()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=output_path.parent,
        prefix=".pedicularis-exposure-", suffix=".tmp", delete=False,
    ) as handle:
        temp = Path(handle.name)
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    try:
        os.replace(temp, output_path)
    finally:
        if temp.exists():
            temp.unlink()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = build_receipt(args.observations, args.protocol, args.out)
    print(json.dumps({
        "status": report["status"],
        "n_distinct_plants": report["n_distinct_plants"],
        "n_contrasting_whorls": report["n_contrasting_whorls"],
        "gate_reasons": report["gate_reasons"],
        "evidence_ceiling": report["evidence_ceiling"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

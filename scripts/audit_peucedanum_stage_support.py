#!/usr/bin/env python3
"""Audit stage-specific Peucedanum support from source-verified normalized CSV."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from balance_domain.peucedanum_ingest import NORMALIZED_FIELDS
from balance_domain.peucedanum_stage_support import audit_stage_support

EXPECTED_SHA = "ed6bf4c5301309283ca2e3d2033fdab1e253d46ed94bbba5fde1f3ee43281dbc"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--normalized", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if args.out.exists():
        raise ValueError("output already exists")
    if hashlib.sha256(args.normalized.read_bytes()).hexdigest() != EXPECTED_SHA:
        raise ValueError("normalized input differs from frozen source-verified CSV")
    with args.normalized.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != NORMALIZED_FIELDS:
            raise ValueError("normalized CSV schema mismatch")
        result = audit_stage_support(reader)
    if result["source_rows"] != 685 or result["observed_plot_year_cells"] != 19:
        raise ValueError("source support drift")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "source_rows": result["source_rows"],
                      "totals": result["totals"]}, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Source-hash-bound exploratory stage-slope readout."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from balance_domain.peucedanum_ingest import NORMALIZED_FIELDS
from balance_domain.peucedanum_stage_slopes import stage_slopes

EXPECTED = "ed6bf4c5301309283ca2e3d2033fdab1e253d46ed94bbba5fde1f3ee43281dbc"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--normalized",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():
        raise ValueError("output exists")
    if hashlib.sha256(args.normalized.read_bytes()).hexdigest()!=EXPECTED:
        raise ValueError("source hash mismatch")
    with args.normalized.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != NORMALIZED_FIELDS:
            raise ValueError("normalized schema mismatch")
        rows=list(reader)
    if len(rows)!=685:
        raise ValueError("source row count drift")
    result=stage_slopes(rows)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"cells":result["cells"]},sort_keys=True))


if __name__=="__main__":
    main()

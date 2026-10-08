#!/usr/bin/env python3
"""Combine source-bound exploration receipts without promoting causal claims."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

from balance_domain.peucedanum_stage_verdict import adjudicate_stage_exploration


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run(support: Path, raw: Path, adjusted: Path, output: Path):
    if output.exists():
        raise ValueError("stage-verdict output already exists")
    result = adjudicate_stage_exploration(_load(support), _load(raw), _load(adjusted))
    result["input_sha256"] = {
        "support": hashlib.sha256(support.read_bytes()).hexdigest(),
        "unadjusted": hashlib.sha256(raw.read_bytes()).hexdigest(),
        "adjusted": hashlib.sha256(adjusted.read_bytes()).hexdigest(),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=output.parent,
        prefix=".peucedanum-stage-verdict-", suffix=".tmp", delete=False
    ) as file:
        temp = Path(file.name)
        json.dump(result, file, indent=2, sort_keys=True)
        file.write("\n")
    try:
        os.replace(temp, output)
    finally:
        if temp.exists():
            temp.unlink()
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--support", type=Path, required=True)
    p.add_argument("--unadjusted", type=Path, required=True)
    p.add_argument("--adjusted", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = run(args.support, args.unadjusted, args.adjusted, args.out)
    print(json.dumps({
        "status": result["status"],
        "descriptive_sign_flip_count": result["descriptive_sign_flip_count"],
        "adjusted_variants": result["adjusted_variants"],
        "claim_ceiling": result["claim_ceiling"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

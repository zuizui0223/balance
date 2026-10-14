#!/usr/bin/env python3
"""Audit published architecture candidates without fabricating direct worldlines."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.structural_source_gate import adjudicate_structural_registry


def run_source_audit(source: Path, output: Path) -> dict:
    if output.exists():
        raise ValueError("source audit output already exists")
    content = source.read_bytes()
    registry = json.loads(content)
    result = adjudicate_structural_registry(registry)
    result["source_registry_sha256"] = hashlib.sha256(content).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=output.parent,
        prefix=".structural-source-", suffix=".tmp", delete=False,
    ) as handle:
        temp = Path(handle.name)
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    try:
        os.replace(temp, output)
    finally:
        if temp.exists():
            temp.unlink()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=Path,
        default=ROOT / "data/BALANCE_STRUCTURAL_WORLDLINE_SOURCE_AUDIT_V1.json"
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run_source_audit(args.source, args.out)
    print(json.dumps({
        "status": result["status"],
        "candidate_count": result["candidate_count"],
        "source_eligible_count": result["source_eligible_count"],
        "direct_structural_worldline_receipt_count": (
            result["direct_structural_worldline_receipt_count"]
        ),
    }, sort_keys=True))


if __name__ == "__main__":
    main()

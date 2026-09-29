#!/usr/bin/env python3
"""Validate and merge returned BALANCE plant coder worksheets."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_coder_return import (  # noqa: E402
    merge_coder_returns,
    write_merged_coder_returns,
)


DEFAULT_OUT = ROOT / "release" / "generated" / "plant_coder_returns"


def _lane_paths(lane: str) -> dict[str, Path]:
    data = ROOT / "data"
    if lane == "U1":
        return {
            "u1_sample_path": data / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv",
        }
    if lane == "U2":
        return {
            "u2_sample_path": data / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv",
        }
    if lane == "U6":
        return {
            "u6_freeze_path": data / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json",
        }
    raise ValueError(f"unknown lane {lane!r}")


def merge_lane(
    *,
    lane: str,
    coder_a: Path,
    coder_b: Path,
    out_dir: Path = DEFAULT_OUT,
) -> dict:
    kwargs = _lane_paths(lane)
    rows = merge_coder_returns(
        lane=lane,
        coder_a_path=coder_a,
        coder_b_path=coder_b,
        **kwargs,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    merged_path = out_dir / f"BALANCE_PLANT_{lane}_DOUBLE_CODE_RETURN_MERGED_V1.csv"
    receipt_path = out_dir / f"BALANCE_PLANT_{lane}_DOUBLE_CODE_RETURN_RECEIPT_V1.json"
    write_merged_coder_returns(merged_path, rows, lane=lane)
    group_field = "dependency_group" if lane == "U6" else "cluster_id"

    receipt = {
        "schema_version": "BALANCE_PLANT_CODER_RETURN_RECEIPT_V1",
        "lane": lane,
        "n_rows": len(rows),
        "n_dependency_groups": len({row[group_field] for row in rows}),
        "coder_ids": sorted({row["coder_id"] for row in rows}),
        "merged_ledger": str(merged_path),
        "next_step": "agreement diagnostics before any source adjudication",
        "claim_ceiling": "validated_coder_return_merge_only_no_biological_result",
    }
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "merged": str(merged_path),
        "receipt": str(receipt_path),
        "n_rows": len(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", choices=("U1", "U2", "U6"), required=True)
    parser.add_argument("--coder-a", type=Path, required=True)
    parser.add_argument("--coder-b", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    print(json.dumps(
        merge_lane(
            lane=args.lane,
            coder_a=args.coder_a,
            coder_b=args.coder_b,
            out_dir=args.out_dir,
        ),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()

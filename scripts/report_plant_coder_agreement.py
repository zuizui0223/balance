#!/usr/bin/env python3
"""Build canonical BALANCE plant independent-coder agreement artifacts."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_agreement_report import build_lane_agreement_report  # noqa: E402


DEFAULT_OUT = ROOT / "release" / "generated" / "plant_coder_agreement"


def _lane_kwargs(lane: str) -> dict[str, Path]:
    data = ROOT / "data"
    if lane == "U1":
        return {"u1_sample_path": data / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"}
    if lane == "U2":
        return {"u2_sample_path": data / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"}
    if lane == "U6":
        return {"u6_freeze_path": data / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"}
    raise ValueError(f"unknown lane {lane!r}")


def build_outputs(
    *,
    lane: str,
    coding_path: Path,
    out_dir: Path = DEFAULT_OUT,
) -> dict:
    report = build_lane_agreement_report(
        lane=lane,
        coding_path=coding_path,
        **_lane_kwargs(lane),
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"BALANCE_PLANT_{lane}_AGREEMENT_REPORT_V1.json"
    disagreement_path = out_dir / f"BALANCE_PLANT_{lane}_DISAGREEMENTS_V1.csv"

    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with disagreement_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "lane",
                "field",
                "dependency_group",
                "coder_a_value",
                "coder_b_value",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for field, items in report["exact_disagreements"].items():
            for item in items:
                writer.writerow({
                    "lane": lane,
                    "field": field,
                    **item,
                })

    return {
        "agreement_report": str(report_path),
        "disagreements": str(disagreement_path),
        "reliability_pass": report["reliability_pass"],
        "adjudication_allowed": report["adjudication_allowed"],
        "next_step": report["next_step"],
        "failed_fields": report["failed_fields"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", choices=("U1", "U2", "U6"), required=True)
    parser.add_argument("--coding", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    print(json.dumps(
        build_outputs(
            lane=args.lane,
            coding_path=args.coding,
            out_dir=args.out_dir,
        ),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Freeze the U2 V2 predictor-receipt surface after expansion coding returns."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_predictor_expansion import (  # noqa: E402
    build_v2_from_files,
    write_v2_predictor_receipts,
)


V1 = ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
TEMPLATE = ROOT / "data" / "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv"
DEFAULT_OUT = ROOT / "release" / "generated" / "plant_u2_predictor_expansion_v2"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_v2(*, coding_return: Path, out_dir: Path = DEFAULT_OUT) -> dict:
    rows = build_v2_from_files(
        v1_receipts_path=V1,
        frozen_template_path=TEMPLATE,
        returned_expansion_path=coding_return,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt_frame = (
        out_dir / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2.csv"
    )
    write_v2_predictor_receipts(receipt_frame, rows)

    resolved = [row for row in rows if row["reported_value"] != "UNRESOLVED"]
    groups_complete = []
    for group in sorted({row["cluster_id"] for row in rows}):
        subset = [row for row in rows if row["cluster_id"] == group]
        if len(subset) == 3 and all(
            row["reported_value"] != "UNRESOLVED"
            and row["outcome_independence"] == "TRUE"
            for row in subset
        ):
            groups_complete.append(group)

    receipt = {
        "schema_version": "BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2",
        "status": "FROZEN_SCREENED_AWAITING_INDEPENDENT_ADJUDICATION",
        "v1_receipts_sha256": _sha256(V1),
        "expansion_template_sha256": _sha256(TEMPLATE),
        "coding_return_sha256": _sha256(coding_return),
        "v2_receipt_frame": receipt_frame.name,
        "v2_receipt_frame_sha256": _sha256(receipt_frame),
        "n_receipts": len(rows),
        "n_resolved_receipts": len(resolved),
        "n_groups_with_three_resolved_independent_predictors": len(groups_complete),
        "groups_with_three_resolved_independent_predictors": groups_complete,
        "adjudication_status": "SCREENED_ONLY",
        "next_step": (
            "send frozen V2 receipt frame to a separate independent predictor adjudicator"
        ),
        "claim_ceiling": "predictor_receipt_freeze_only_no_architecture_or_effect_result",
    }
    receipt_path = out_dir / "BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "receipt_frame": str(receipt_frame),
        "freeze_receipt": str(receipt_path),
        **receipt,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coding-return", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    print(json.dumps(
        freeze_v2(coding_return=args.coding_return, out_dir=args.out_dir),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()

"""Read-only U6 source-stage evidence and V4 screen-level sensitivity report."""
from __future__ import annotations

import json
from pathlib import Path

from balance_domain.u6_source_coordinate_audit import build_u6_source_coordinate_audit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

if __name__ == "__main__":
    result = build_u6_source_coordinate_audit(
        DATA / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json",
        [
            DATA / f"BALANCE_PLANT_U6_CANDIDATE_ADJUDICATION_BATCH_{suffix}_V1.csv"
            for suffix in "ABC"
        ],
        DATA / "BALANCE_U6_POSTOPEN_STAGE_REVIEW_FLAGS_20261119.csv",
        DATA / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
        DATA / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        DATA / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

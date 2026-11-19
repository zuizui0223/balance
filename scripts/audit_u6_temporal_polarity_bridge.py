"""Read-only source-backed U6 sequential visitor-order polarity reconciliation."""
from __future__ import annotations

import json
from pathlib import Path

from balance_domain.u6_temporal_polarity_bridge import build_u6_temporal_polarity_bridge

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data"

if __name__ == "__main__":
    result = build_u6_temporal_polarity_bridge(
        D / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json",
        [
            D / f"BALANCE_PLANT_U6_CANDIDATE_ADJUDICATION_BATCH_{x}_V1.csv"
            for x in "ABC"
        ],
        D / "BALANCE_U6_TEMPORAL_POLARITY_CROSSWALK_20261119.csv",
        D / "BALANCE_U6_POSTOPEN_STAGE_REVIEW_FLAGS_20261119.csv",
        D / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
        D / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        D / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))

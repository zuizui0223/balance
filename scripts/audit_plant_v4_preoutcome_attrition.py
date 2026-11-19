"""Read-only exact V4 predictor-design attrition report; never reads architecture outcomes."""
from __future__ import annotations

import json
from pathlib import Path

from balance_domain.plant_v4_preoutcome_attrition import (
    build_v4_preoutcome_attrition_audit,
)

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    result = build_v4_preoutcome_attrition_audit(
        ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
        ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

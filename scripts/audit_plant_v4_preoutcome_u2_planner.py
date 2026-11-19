"""Compare six hypothetical future U2 predictor cells without opening V4 outcomes."""
from __future__ import annotations

import json
from pathlib import Path

from balance_domain.plant_v4_preoutcome_u2_planner import (
    build_v4_preoutcome_u2_scenario_planner,
)

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    result = build_v4_preoutcome_u2_scenario_planner(
        ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
        ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))

"""Read-only binary information ceiling and primary-source dependence diagnostic."""
from __future__ import annotations

import json
from pathlib import Path

from balance_domain.plant_v4_preoutcome_information import (
    build_v4_preoutcome_information_benchmark,
)

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    result = build_v4_preoutcome_information_benchmark(
        ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
        ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

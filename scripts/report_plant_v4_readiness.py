#!/usr/bin/env python3
"""Print the canonical BALANCE plant V4 readiness and publication-gate snapshot."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_reactivation import evaluate_v4_reactivation_gate  # noqa: E402
from balance_domain.plant_readiness import build_plant_v4_readiness  # noqa: E402


def build_report() -> dict:
    readiness = build_plant_v4_readiness(
        u1_first20_conflict_path=ROOT / "data" / "BALANCE_PLANT_U1_BLIND_CONFLICT_SCREEN_V1.csv",
        u1_production27_conflict_path=ROOT / "data" / "BALANCE_PLANT_U1_PRODUCTION_BLIND_CONFLICT_SCREEN_V1.csv",
        u1_sample_path=ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv",
        u1_worksheet_path=ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv",
        u1_adjudication_path=ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
        u2_conflict_path=ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
        u2_sample_path=ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv",
        u2_worksheet_path=ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
        u2_adjudication_path=ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
        u2_predictor_receipts_path=ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        u6_freeze_path=ROOT / "data" / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json",
        u6_worksheet_path=ROOT / "data" / "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv",
        u6_adjudication_path=ROOT / "data" / "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv",
        u6_predictor_receipts_path=ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        u6_dependence_path=ROOT / "data" / "BALANCE_PLANT_U6_CROSS_UNIVERSE_DEPENDENCE_V1.csv",
    )
    reactivation = evaluate_v4_reactivation_gate(
        ROOT / "data" / "BALANCE_PLANT_V4_REACTIVATION_GATE_V1.json"
    )
    return {
        "analysis": "balance_plant_v4_readiness_snapshot",
        "programme_readiness": readiness,
        "standalone_reactivation_gate": reactivation,
    }


def main() -> None:
    print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

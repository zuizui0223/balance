#!/usr/bin/env python3
"""Report readiness or build final BALANCE plant V4 pre-fit analysis inputs."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_analysis_pipeline import build_v4_analysis_inputs  # noqa: E402
from balance_domain.plant_assembly_builder import build_v4_licensed_assembly  # noqa: E402
from balance_domain.plant_confirmatory import load_plant_predictor_receipts  # noqa: E402
from balance_domain.plant_macro_agreement import load_double_coding  # noqa: E402
from balance_domain.plant_model_assembly import FIELDS as ASSEMBLY_FIELDS  # noqa: E402
from balance_domain.plant_readiness import build_plant_v4_readiness  # noqa: E402
from balance_domain.plant_u2 import (  # noqa: E402
    load_u2_adjudication,
    load_u2_double_code_sample,
    load_u2_source_packet,
)
from balance_domain.plant_u6 import (  # noqa: E402
    load_u6_cross_universe_dependence,
    load_u6_frozen_source_packet,
    load_u6_pass2_adjudication,
    load_u6_pass2_double_coding,
)

DEFAULT_OUT = ROOT / "release" / "generated" / "plant_v4_analysis_inputs"


def _paths() -> dict[str, Path]:
    data = ROOT / "data"
    return {
        "u1_first20_conflict": data / "BALANCE_PLANT_U1_BLIND_CONFLICT_SCREEN_V1.csv",
        "u1_production27_conflict": data / "BALANCE_PLANT_U1_PRODUCTION_BLIND_CONFLICT_SCREEN_V1.csv",
        "u1_sample": data / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv",
        "u1_worksheet": data / "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv",
        "u1_adjudication": data / "BALANCE_PLANT_U1_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
        "u2_conflict": data / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
        "u2_sample": data / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv",
        "u2_worksheet": data / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
        "u2_adjudication": data / "BALANCE_PLANT_U2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
        "u2_receipts": data / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        "u2_sources": data / "BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv",
        "u6_freeze": data / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json",
        "u6_worksheet": data / "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv",
        "u6_adjudication": data / "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv",
        "u6_receipts": data / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        "u6_dependence": data / "BALANCE_PLANT_U6_CROSS_UNIVERSE_DEPENDENCE_V1.csv",
        "u6_source_recovery": data / "BALANCE_PLANT_U6_PASS2_SOURCE_RECOVERY_FRAME_V1.csv",
        "u6_sources": data / "BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv",
    }


def current_readiness() -> dict:
    p = _paths()
    return build_plant_v4_readiness(
        u1_first20_conflict_path=p["u1_first20_conflict"],
        u1_production27_conflict_path=p["u1_production27_conflict"],
        u1_sample_path=p["u1_sample"],
        u1_worksheet_path=p["u1_worksheet"],
        u1_adjudication_path=p["u1_adjudication"],
        u2_conflict_path=p["u2_conflict"],
        u2_sample_path=p["u2_sample"],
        u2_worksheet_path=p["u2_worksheet"],
        u2_adjudication_path=p["u2_adjudication"],
        u2_predictor_receipts_path=p["u2_receipts"],
        u6_freeze_path=p["u6_freeze"],
        u6_worksheet_path=p["u6_worksheet"],
        u6_adjudication_path=p["u6_adjudication"],
        u6_predictor_receipts_path=p["u6_receipts"],
        u6_dependence_path=p["u6_dependence"],
    )


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ASSEMBLY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_outputs(out_dir: Path = DEFAULT_OUT) -> dict:
    readiness = current_readiness()
    if not readiness["primary_model_assembly_ready"]:
        raise RuntimeError(
            "V4 primary assembly is not ready: "
            + ", ".join(readiness["open_gate_names"])
        )

    p = _paths()
    u2_coding = load_double_coding(p["u2_worksheet"])
    u2_sample = load_u2_double_code_sample(p["u2_sample"])
    u2_adjudication = load_u2_adjudication(
        p["u2_adjudication"],
        u2_sample,
        u2_coding,
    )
    u2_receipts = load_plant_predictor_receipts(p["u2_receipts"])
    u2_sources = load_u2_source_packet(p["u2_sources"])

    u6_coding = load_u6_pass2_double_coding(
        p["u6_worksheet"],
        p["u6_freeze"],
    )
    u6_adjudication = load_u6_pass2_adjudication(
        p["u6_adjudication"],
        p["u6_freeze"],
        u6_coding,
    )
    u6_receipts = load_plant_predictor_receipts(p["u6_receipts"])
    u6_dependence = load_u6_cross_universe_dependence(
        p["u6_dependence"],
        p["u6_freeze"],
    )
    u6_sources = load_u6_frozen_source_packet(
        p["u6_sources"],
        p["u6_freeze"],
        p["u6_source_recovery"],
    )

    assembly = build_v4_licensed_assembly(
        u2_adjudication_rows=u2_adjudication,
        u2_predictor_receipts=u2_receipts,
        u2_source_packet_rows=u2_sources,
        u6_adjudication_rows=u6_adjudication,
        u6_predictor_receipts=u6_receipts,
        u6_dependence_rows=u6_dependence,
        u6_frozen_source_packet_rows=u6_sources,
    )
    pipeline = build_v4_analysis_inputs(assembly)

    out_dir.mkdir(parents=True, exist_ok=True)
    assembly_path = out_dir / "BALANCE_PLANT_V4_LICENSED_ASSEMBLY.csv"
    readout_path = out_dir / "BALANCE_PLANT_V4_ASSEMBLY_READOUT.json"
    main_path = out_dir / "BALANCE_PLANT_V4_STAN_INPUT.json"
    prior_path = out_dir / "BALANCE_PLANT_V4_PRIOR_SENSITIVITY_INPUT.json"
    generality_path = out_dir / "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_INPUT.json"

    _write_csv(assembly_path, assembly)
    readout_path.write_text(
        json.dumps(pipeline["assembly_readout"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    main_path.write_text(
        json.dumps(pipeline["main_stan_input"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    prior_path.write_text(
        json.dumps(
            pipeline["prior_sensitivity_stan_input"],
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    if pipeline["temporal_generality_stan_input"] is not None:
        generality_path.write_text(
            json.dumps(
                pipeline["temporal_generality_stan_input"],
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )
    elif generality_path.exists():
        generality_path.unlink()

    return {
        "assembly": str(assembly_path),
        "assembly_readout": str(readout_path),
        "main_stan_input": str(main_path),
        "prior_sensitivity_stan_input": str(prior_path),
        "temporal_generality_status": pipeline["temporal_generality_status"],
        "temporal_generality_blockers": pipeline["temporal_generality_blockers"],
        "temporal_generality_input": (
            str(generality_path)
            if pipeline["temporal_generality_stan_input"] is not None
            else None
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build licensed assembly and V4 pre-fit inputs; fail closed if gates remain open.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT,
    )
    args = parser.parse_args()

    if args.build:
        print(json.dumps(build_outputs(args.out_dir), indent=2, sort_keys=True))
    else:
        print(json.dumps(current_readiness(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

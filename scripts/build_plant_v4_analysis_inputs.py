#!/usr/bin/env python3
"""Report readiness or build final BALANCE plant V4 pre-fit analysis inputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_analysis_pipeline import build_v4_analysis_inputs  # noqa: E402
from balance_domain.plant_assembly_builder import build_v4_licensed_assembly  # noqa: E402
from balance_domain.plant_confirmatory import load_plant_predictor_receipts  # noqa: E402
from balance_domain.plant_predictor_adjudication import (  # noqa: E402
    load_predictor_adjudication_return,
)
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
HUMAN_WORKSPACE_RECEIPT = "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_RECEIPT_V1.json"
ANALYSIS_INPUT_RECEIPT = "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json"
ANALYSIS_INPUT_PROVENANCE_CONTRACT = (
    ROOT / "data" / "BALANCE_PLANT_V4_ANALYSIS_INPUT_PROVENANCE_V1.json"
)
PRIMARY_HUMAN_BASENAMES = (
    "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
    "BALANCE_PLANT_U2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
    "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv",
    "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv",
    "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_analysis_input_provenance_contract() -> dict:
    data = json.loads(
        ANALYSIS_INPUT_PROVENANCE_CONTRACT.read_text(encoding="utf-8")
    )
    if data.get("schema_version") != "BALANCE_PLANT_V4_ANALYSIS_INPUT_PROVENANCE_V1":
        raise ValueError("V4 analysis-input provenance contract schema mismatch")
    if data.get("status") != (
        "FROZEN_PRE_OUTCOME_BEFORE_INDEPENDENT_ARCHITECTURE_CODING"
    ):
        raise ValueError("V4 analysis-input provenance contract is not frozen pre-outcome")
    source = data.get("source_workspace") or {}
    if source.get("receipt") != HUMAN_WORKSPACE_RECEIPT:
        raise ValueError("V4 analysis-input provenance source receipt drifted")
    if tuple(source.get("required_primary_files") or ()) != PRIMARY_HUMAN_BASENAMES:
        raise ValueError("V4 analysis-input provenance primary file set drifted")
    if source.get("file_sha256_must_match_receipt") is not True:
        raise ValueError("V4 analysis-input provenance must require source SHA256")
    workspace = data.get("output_workspace") or {}
    if workspace.get("existing_output_directory_overwrite_allowed") is not False:
        raise ValueError("V4 analysis-input workspace overwrite policy drifted")
    if workspace.get("write_mode") != "temporary_sibling_workspace_then_atomic_rename":
        raise ValueError("V4 analysis-input workspace write mode drifted")
    return data


def _validated_human_workspace_receipt(input_dir: Path | None) -> tuple[Path, dict]:
    if input_dir is None:
        raise ValueError(
            "V4 build requires a composed human-input workspace with a provenance receipt"
        )
    receipt_path = input_dir / HUMAN_WORKSPACE_RECEIPT
    if not receipt_path.is_file():
        raise ValueError(f"V4 human workspace receipt is missing: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("schema_version") != "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_V1":
        raise ValueError("V4 human workspace receipt schema mismatch")
    if receipt.get("analysis") != "balance_plant_v4_human_input_workspace":
        raise ValueError("V4 human workspace receipt analysis mismatch")
    if receipt.get("primary_model_assembly_ready") is not True:
        raise ValueError("V4 human workspace receipt is not primary-assembly ready")
    if any((receipt.get("primary_human_open_gates") or {}).values()):
        raise ValueError("V4 human workspace receipt still has primary human gates open")
    if receipt.get("next_step") != "BUILD_V4_ANALYSIS_INPUTS":
        raise ValueError("V4 human workspace receipt next step drifted")

    files = receipt.get("files") or {}
    for basename in PRIMARY_HUMAN_BASENAMES:
        item = files.get(basename)
        if not isinstance(item, dict):
            raise ValueError(f"V4 human workspace receipt lacks {basename}")
        expected = item.get("composed_sha256")
        if not isinstance(expected, str) or not expected:
            raise ValueError(f"V4 human workspace receipt lacks SHA256 for {basename}")
        path = input_dir / basename
        if not path.is_file():
            raise ValueError(f"V4 human workspace file is missing: {path}")
        observed = _sha256(path)
        if observed != expected:
            raise ValueError(
                f"V4 human workspace SHA256 mismatch for {basename}: "
                f"{observed} != {expected}"
            )
    return receipt_path, receipt


def _override(default: Path, input_dir: Path | None) -> Path:
    """Use an explicit handoff-workspace file when present; never mutate repo inputs."""
    if input_dir is None:
        return default
    candidate = input_dir / default.name
    return candidate if candidate.exists() else default


def _paths(input_dir: Path | None = None) -> dict[str, Path]:
    data = ROOT / "data"
    defaults = {
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
        "u2_receipts_frozen": data / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        "u2_sources": data / "BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv",
        "u6_freeze": data / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json",
        "u6_worksheet": data / "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv",
        "u6_adjudication": data / "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv",
        "u6_receipts": data / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        "u6_receipts_frozen": data / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        "u6_dependence": data / "BALANCE_PLANT_U6_CROSS_UNIVERSE_DEPENDENCE_V1.csv",
        "u6_source_recovery": data / "BALANCE_PLANT_U6_PASS2_SOURCE_RECOVERY_FRAME_V1.csv",
        "u6_sources": data / "BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv",
    }
    mutable_keys = {
        "u1_worksheet",
        "u1_adjudication",
        "u2_worksheet",
        "u2_adjudication",
        "u2_receipts",
        "u6_worksheet",
        "u6_adjudication",
        "u6_receipts",
    }
    return {
        key: _override(path, input_dir) if key in mutable_keys else path
        for key, path in defaults.items()
    }


def _validate_predictor_receipt_overrides(paths: dict[str, Path]) -> None:
    """Validate reviewed receipt overrides against immutable frozen source-screen frames."""
    for lane in ("u2", "u6"):
        reviewed = paths[f"{lane}_receipts"]
        frozen = paths[f"{lane}_receipts_frozen"]
        if reviewed != frozen:
            load_predictor_adjudication_return(reviewed, frozen)


def current_readiness(input_dir: Path | None = None) -> dict:
    p = _paths(input_dir)
    _validate_predictor_receipt_overrides(p)
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


def build_outputs(
    out_dir: Path = DEFAULT_OUT,
    input_dir: Path | None = None,
) -> dict:
    _load_analysis_input_provenance_contract()
    readiness = current_readiness(input_dir)
    if not readiness["primary_model_assembly_ready"]:
        raise RuntimeError(
            "V4 primary assembly is not ready: "
            + ", ".join(readiness["open_gate_names"])
        )

    human_receipt_path, human_receipt = _validated_human_workspace_receipt(input_dir)
    p = _paths(input_dir)
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

    if out_dir.exists():
        raise ValueError(
            "V4 analysis-input output directory already exists; choose a new "
            "immutable workspace"
        )
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(
        prefix=f".{out_dir.name}.tmp-",
        dir=out_dir.parent,
    ))
    try:
        assembly_path = tmp_dir / "BALANCE_PLANT_V4_LICENSED_ASSEMBLY.csv"
        readout_path = tmp_dir / "BALANCE_PLANT_V4_ASSEMBLY_READOUT.json"
        main_path = tmp_dir / "BALANCE_PLANT_V4_STAN_INPUT.json"
        prior_path = tmp_dir / "BALANCE_PLANT_V4_PRIOR_SENSITIVITY_INPUT.json"
        generality_path = tmp_dir / "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_INPUT.json"
        generality_prior_path = (
            tmp_dir / "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_PRIOR_SENSITIVITY_INPUT.json"
        )

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

        output_paths = {
            "licensed_assembly": assembly_path,
            "assembly_readout": readout_path,
            "PRIMARY": main_path,
            "PRIMARY_PRIOR_SENSITIVITY": prior_path,
        }
        if pipeline["temporal_generality_stan_input"] is not None:
            generality_path.write_text(
                json.dumps(
                    pipeline["temporal_generality_stan_input"],
                    indent=2,
                    sort_keys=True,
                ) + "\n",
                encoding="utf-8",
            )
            generality_prior_path.write_text(
                json.dumps(
                    pipeline["temporal_generality_prior_sensitivity_stan_input"],
                    indent=2,
                    sort_keys=True,
                ) + "\n",
                encoding="utf-8",
            )
            output_paths["TEMPORAL_GENERALITY"] = generality_path
            output_paths["TEMPORAL_GENERALITY_PRIOR_SENSITIVITY"] = generality_prior_path

        copied_human_receipt = tmp_dir / HUMAN_WORKSPACE_RECEIPT
        shutil.copyfile(human_receipt_path, copied_human_receipt)
        analysis_receipt = {
            "schema_version": "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1",
            "analysis": "balance_plant_v4_analysis_inputs",
            "analysis_input_provenance_contract": (
                "data/BALANCE_PLANT_V4_ANALYSIS_INPUT_PROVENANCE_V1.json"
            ),
            "analysis_input_provenance_contract_sha256": _sha256(
                ANALYSIS_INPUT_PROVENANCE_CONTRACT
            ),
            "source_human_workspace_receipt": HUMAN_WORKSPACE_RECEIPT,
            "source_human_workspace_receipt_sha256": _sha256(copied_human_receipt),
            "source_human_workspace_file_sha256": {
                basename: human_receipt["files"][basename]["composed_sha256"]
                for basename in PRIMARY_HUMAN_BASENAMES
            },
            "temporal_generality_status": pipeline["temporal_generality_status"],
            "active_fit_jobs": [
                key for key in (
                    "PRIMARY",
                    "PRIMARY_PRIOR_SENSITIVITY",
                    "TEMPORAL_GENERALITY",
                    "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY",
                )
                if key in output_paths
            ],
            "outputs": {
                key: path.name
                for key, path in output_paths.items()
            },
            "output_sha256": {
                key: _sha256(path)
                for key, path in output_paths.items()
            },
            "claim_ceiling": "analysis_input_provenance_only_no_fitted_effect",
        }
        analysis_receipt_path = tmp_dir / ANALYSIS_INPUT_RECEIPT
        analysis_receipt_path.write_text(
            json.dumps(analysis_receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tmp_dir.rename(out_dir)
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    return {
        "analysis_input_receipt": str(out_dir / ANALYSIS_INPUT_RECEIPT),
        "source_human_workspace_receipt": str(out_dir / HUMAN_WORKSPACE_RECEIPT),
        "assembly": str(out_dir / assembly_path.name),
        "assembly_readout": str(out_dir / readout_path.name),
        "main_stan_input": str(out_dir / main_path.name),
        "prior_sensitivity_stan_input": str(out_dir / prior_path.name),
        "temporal_generality_status": pipeline["temporal_generality_status"],
        "temporal_generality_blockers": pipeline["temporal_generality_blockers"],
        "temporal_generality_input": (
            str(out_dir / generality_path.name)
            if pipeline["temporal_generality_stan_input"] is not None
            else None
        ),
        "temporal_generality_prior_sensitivity_input": (
            str(out_dir / generality_prior_path.name)
            if pipeline["temporal_generality_prior_sensitivity_stan_input"]
            is not None
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
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help=(
            "Optional external handoff workspace. Files with canonical mutable input "
            "basenames override repo defaults; frozen source/manifest files remain in repo."
        ),
    )
    args = parser.parse_args()

    if args.build:
        print(json.dumps(
            build_outputs(args.out_dir, input_dir=args.input_dir),
            indent=2,
            sort_keys=True,
        ))
    else:
        print(json.dumps(
            current_readiness(input_dir=args.input_dir),
            indent=2,
            sort_keys=True,
        ))


if __name__ == "__main__":
    main()

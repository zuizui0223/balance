"""Fail-closed intake for returned BALANCE plant human-review files.

This module validates the complete independent-review return bundle before writing any
persistent outputs. It does not adjudicate disagreements or fit a model.
"""
from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from pathlib import Path

from .plant_agreement_report import build_lane_agreement_report
from .plant_coder_return import merge_coder_returns, write_merged_coder_returns
from .plant_predictor_adjudication import build_predictor_adjudication_readout


CODER_RETURN_BASENAMES = {
    ("U1", "CODER_A"): "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv",
    ("U1", "CODER_B"): "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv",
    ("U2", "CODER_A"): "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv",
    ("U2", "CODER_B"): "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv",
    ("U6", "CODER_A"): "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv",
    ("U6", "CODER_B"): "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv",
}
PREDICTOR_RETURN_BASENAMES = {
    "U2": "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    "U6": "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
}

MERGED_BASENAMES = {
    "U1": "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv",
    "U2": "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
    "U6": "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def required_return_paths(return_dir: Path) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for (lane, coder), basename in CODER_RETURN_BASENAMES.items():
        paths[f"{lane}_{coder}"] = return_dir / basename
    for lane, basename in PREDICTOR_RETURN_BASENAMES.items():
        paths[f"{lane}_PREDICTOR"] = return_dir / basename
    return paths


def _require_complete_return_bundle(return_dir: Path) -> dict[str, Path]:
    paths = required_return_paths(return_dir)
    missing = sorted(key for key, path in paths.items() if not path.is_file())
    if missing:
        raise ValueError(
            "human return bundle is incomplete; missing canonical return files: "
            + ", ".join(missing)
        )
    return paths


def _lane_kwargs(root: Path, lane: str) -> dict[str, Path]:
    data = root / "data"
    if lane == "U1":
        return {"u1_sample_path": data / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"}
    if lane == "U2":
        return {"u2_sample_path": data / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"}
    if lane == "U6":
        return {"u6_freeze_path": data / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"}
    raise ValueError(f"unknown lane {lane!r}")


def _write_disagreements(path: Path, lane: str, report: dict) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
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
                writer.writerow({"lane": lane, "field": field, **item})


def validate_human_return_bundle(
    *,
    root: Path,
    return_dir: Path,
) -> dict:
    """Validate all human returns without creating persistent output files."""
    paths = _require_complete_return_bundle(return_dir)
    merged: dict[str, list[dict[str, str]]] = {}
    agreement: dict[str, dict] = {}

    for lane in ("U1", "U2", "U6"):
        merged[lane] = merge_coder_returns(
            lane=lane,
            coder_a_path=paths[f"{lane}_CODER_A"],
            coder_b_path=paths[f"{lane}_CODER_B"],
            **_lane_kwargs(root, lane),
        )

    # Agreement loaders operate on canonical merged-ledger paths. Use a temporary
    # directory so validation remains side-effect free until every return surface passes.
    with tempfile.TemporaryDirectory(prefix="balance-plant-return-intake-") as tmp:
        tmpdir = Path(tmp)
        for lane in ("U1", "U2", "U6"):
            coding_path = tmpdir / MERGED_BASENAMES[lane]
            write_merged_coder_returns(coding_path, merged[lane], lane=lane)
            agreement[lane] = build_lane_agreement_report(
                lane=lane,
                coding_path=coding_path,
                **_lane_kwargs(root, lane),
            )

    frozen_u2 = root / "data" / PREDICTOR_RETURN_BASENAMES["U2"]
    frozen_u6 = root / "data" / PREDICTOR_RETURN_BASENAMES["U6"]
    predictor = {
        "U2": build_predictor_adjudication_readout(
            paths["U2_PREDICTOR"],
            frozen_u2,
        ),
        "U6": build_predictor_adjudication_readout(
            paths["U6_PREDICTOR"],
            frozen_u6,
        ),
    }

    primary_reliability_pass = all(
        agreement[lane]["reliability_pass"] for lane in ("U2", "U6")
    )
    external_validation_reliability_pass = agreement["U1"]["reliability_pass"]
    predictor_primary_complete = (
        predictor["U2"]["n_clusters_with_three_adjudicated_receipts"] == 8
        and predictor["U6"]["n_clusters_with_three_adjudicated_receipts"] == 21
    )

    if not primary_reliability_pass:
        architecture_next = "CODEBOOK_REPAIR_AND_INDEPENDENT_RECODE_SAME_FROZEN_GROUPS"
    else:
        architecture_next = "SOURCE_ADJUDICATION"

    predictor_next = (
        "PREDICTOR_ADJUDICATION_COMPLETE"
        if predictor_primary_complete
        else "RESOLVE_REJECTED_OR_INCOMPLETE_PRIMARY_PREDICTOR_RECEIPTS"
    )

    return {
        "analysis": "balance_plant_human_return_intake",
        "input_files": {
            key: {
                "basename": path.name,
                "sha256": _sha256(path),
            }
            for key, path in sorted(paths.items())
        },
        "merged_rows": merged,
        "agreement": agreement,
        "predictor_adjudication": predictor,
        "primary_reliability_pass": primary_reliability_pass,
        "external_validation_reliability_pass": (
            external_validation_reliability_pass
        ),
        "predictor_primary_complete": predictor_primary_complete,
        "primary_architecture_next_step": architecture_next,
        "predictor_next_step": predictor_next,
        "ready_for_architecture_adjudication": primary_reliability_pass,
        "ready_for_v4_assembly": False,
        "v4_assembly_blocker": (
            "architecture adjudication is a separate post-reliability human gate"
        ),
        "claim_ceiling": "validated_human_return_intake_only_no_biological_result",
    }


def write_human_return_intake(
    *,
    root: Path,
    return_dir: Path,
    out_dir: Path,
) -> dict:
    """Validate the complete bundle, then write one deterministic intake workspace."""
    result = validate_human_return_bundle(root=root, return_dir=return_dir)

    out_dir.mkdir(parents=True, exist_ok=True)
    merged_paths: dict[str, str] = {}
    agreement_paths: dict[str, str] = {}
    disagreement_paths: dict[str, str] = {}

    for lane in ("U1", "U2", "U6"):
        merged_path = out_dir / MERGED_BASENAMES[lane]
        write_merged_coder_returns(
            merged_path,
            result["merged_rows"][lane],
            lane=lane,
        )
        merged_paths[lane] = str(merged_path)

        report_path = out_dir / f"BALANCE_PLANT_{lane}_AGREEMENT_REPORT_V1.json"
        report_path.write_text(
            json.dumps(result["agreement"][lane], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        agreement_paths[lane] = str(report_path)

        disagreement_path = out_dir / f"BALANCE_PLANT_{lane}_DISAGREEMENTS_V1.csv"
        _write_disagreements(
            disagreement_path,
            lane,
            result["agreement"][lane],
        )
        disagreement_paths[lane] = str(disagreement_path)

    predictor_paths: dict[str, str] = {}
    for lane in ("U2", "U6"):
        path = out_dir / f"BALANCE_PLANT_{lane}_PREDICTOR_ADJUDICATION_READOUT_V1.json"
        path.write_text(
            json.dumps(
                result["predictor_adjudication"][lane],
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )
        predictor_paths[lane] = str(path)

    receipt = {
        key: value
        for key, value in result.items()
        if key != "merged_rows"
    }
    receipt["outputs"] = {
        "merged_ledgers": merged_paths,
        "agreement_reports": agreement_paths,
        "disagreement_ledgers": disagreement_paths,
        "predictor_readouts": predictor_paths,
    }
    receipt_path = out_dir / "BALANCE_PLANT_HUMAN_RETURN_INTAKE_RECEIPT_V1.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return {
        "receipt": str(receipt_path),
        "primary_reliability_pass": result["primary_reliability_pass"],
        "external_validation_reliability_pass": result[
            "external_validation_reliability_pass"
        ],
        "predictor_primary_complete": result["predictor_primary_complete"],
        "primary_architecture_next_step": result[
            "primary_architecture_next_step"
        ],
        "predictor_next_step": result["predictor_next_step"],
        "ready_for_v4_assembly": False,
    }

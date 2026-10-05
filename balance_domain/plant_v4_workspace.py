"""Compose independently validated human-review workspaces for BALANCE plant V4.

The primary architecture adjudication and predictor-receipt review may return on different
timelines and therefore live in separate immutable evidence workspaces. This module
combines only already-validated canonical files, re-runs the V4 readiness gate, and writes
one immutable downstream input workspace. U1 external validation is optional and never
blocks the primary workspace.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from .plant_predictor_adjudication import load_predictor_adjudication_return
from .plant_readiness import build_plant_v4_readiness


PRIMARY_RECEIPT = "BALANCE_PLANT_PRIMARY_ARCHITECTURE_ADJUDICATION_RECEIPT_V1.json"
EXTERNAL_RECEIPT = "BALANCE_PLANT_EXTERNAL_ARCHITECTURE_ADJUDICATION_RECEIPT_V1.json"
INTAKE_RECEIPT = "BALANCE_PLANT_HUMAN_RETURN_INTAKE_RECEIPT_V1.json"

U2_CODING = "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv"
U2_ADJUDICATION = "BALANCE_PLANT_U2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv"
U2_PREDICTOR = "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U2_PREDICTOR_V2 = "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2.csv"
U2_PREDICTOR_V2_FROZEN = (
    "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2_FROZEN.csv"
)
U2_PREDICTOR_V2_FREEZE_RECEIPT = (
    "BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2.json"
)
U2_PREDICTOR_EXPANSION_TEMPLATE = (
    "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv"
)
U6_CODING = "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv"
U6_ADJUDICATION = "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv"
U6_PREDICTOR = "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U1_CODING = "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv"
U1_ADJUDICATION = "BALANCE_PLANT_U1_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"receipt must be a JSON object: {path}")
    return data


def _workspace_file(workspace: Path, basename: str) -> Path:
    path = workspace / basename
    if not path.is_file():
        raise ValueError(f"validated workspace file is missing: {path}")
    return path


def _receipt_bound_workspace_file(
    workspace: Path,
    receipt: dict,
    *,
    family: str,
    lane: str,
    basename: str,
) -> Path:
    path = _workspace_file(workspace, basename)
    hashes = (receipt.get("output_sha256") or {}).get(family) or {}
    expected = hashes.get(lane)
    if not isinstance(expected, str) or not expected:
        raise ValueError(
            f"validated workspace receipt lacks output SHA256 for {family}/{lane}"
        )
    observed = _sha256(path)
    if observed != expected:
        raise ValueError(
            f"validated workspace output SHA256 mismatch for {family}/{lane}: "
            f"{observed} != {expected}"
        )
    return path


def _primary_sources(primary_dir: Path) -> tuple[dict, dict[str, Path]]:
    receipt_path = primary_dir / PRIMARY_RECEIPT
    receipt = _load_json(receipt_path)
    if receipt.get("analysis") != "balance_plant_architecture_adjudication_return":
        raise ValueError("primary adjudication receipt analysis mismatch")
    if receipt.get("scope") != "PRIMARY" or receipt.get("complete") is not True:
        raise ValueError("primary adjudication workspace is not complete")
    if receipt.get("primary_model_gate_closed") is not True:
        raise ValueError("primary architecture adjudication gate is not closed")
    outputs = receipt.get("outputs") or {}
    coding = outputs.get("coding_ledgers") or {}
    adjudication = outputs.get("adjudication_ledgers") or {}
    if set(coding) != {"U2", "U6"} or set(adjudication) != {"U2", "U6"}:
        raise ValueError("primary adjudication receipt must contain U2/U6 outputs")
    paths = {
        U2_CODING: _receipt_bound_workspace_file(
            primary_dir, receipt, family="coding_ledgers", lane="U2", basename=coding["U2"]
        ),
        U2_ADJUDICATION: _receipt_bound_workspace_file(
            primary_dir, receipt, family="adjudication_ledgers", lane="U2", basename=adjudication["U2"]
        ),
        U6_CODING: _receipt_bound_workspace_file(
            primary_dir, receipt, family="coding_ledgers", lane="U6", basename=coding["U6"]
        ),
        U6_ADJUDICATION: _receipt_bound_workspace_file(
            primary_dir, receipt, family="adjudication_ledgers", lane="U6", basename=adjudication["U6"]
        ),
    }
    return receipt, paths


def _validate_u2_v2_freeze_receipt(
    *,
    root: Path,
    frozen_frame: Path,
    freeze_receipt_path: Path,
) -> dict:
    freeze = _load_json(freeze_receipt_path)
    if freeze.get("schema_version") != "BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2":
        raise ValueError("U2 V2 freeze receipt schema mismatch")
    if freeze.get("status") != "FROZEN_SCREENED_AWAITING_INDEPENDENT_ADJUDICATION":
        raise ValueError("U2 V2 freeze receipt status mismatch")
    if freeze.get("v2_receipt_frame_sha256") != _sha256(frozen_frame):
        raise ValueError("U2 V2 frozen baseline SHA256 disagrees with freeze receipt")

    data = root / "data"
    if freeze.get("v1_receipts_sha256") != _sha256(data / U2_PREDICTOR):
        raise ValueError("U2 V2 freeze receipt is not bound to current V1 receipts")
    if freeze.get("expansion_template_sha256") != _sha256(
        data / U2_PREDICTOR_EXPANSION_TEMPLATE
    ):
        raise ValueError("U2 V2 freeze receipt is not bound to current expansion template")
    return freeze


def _predictor_sources(
    root: Path,
    predictor_dir: Path,
) -> tuple[dict, dict[str, Path], dict]:
    receipt_path = predictor_dir / INTAKE_RECEIPT
    receipt = _load_json(receipt_path)
    if receipt.get("analysis") != "balance_plant_human_return_intake":
        raise ValueError("predictor intake receipt analysis mismatch")
    if receipt.get("predictor_returns_received") is not True:
        raise ValueError("predictor intake workspace has no reviewed predictor stage")
    if receipt.get("predictor_return_status") != "COMPLETE":
        raise ValueError("predictor review is not COMPLETE")
    if receipt.get("predictor_primary_complete") is not True:
        raise ValueError("predictor review does not close all primary receipt gates")

    version = receipt.get("u2_predictor_receipt_version")
    if version not in {"V1", "V2"}:
        raise ValueError("predictor intake receipt must declare U2 predictor version V1 or V2")

    outputs = receipt.get("outputs") or {}
    frames = outputs.get("predictor_reviewed_frames") or {}
    if set(frames) != {"U2", "U6"}:
        raise ValueError("predictor intake receipt must contain reviewed U2/U6 frames")

    expected_u2 = U2_PREDICTOR if version == "V1" else U2_PREDICTOR_V2
    if frames.get("U2") != expected_u2:
        raise ValueError(
            f"predictor intake U2 reviewed basename does not match declared {version}"
        )
    if frames.get("U6") != U6_PREDICTOR:
        raise ValueError("predictor intake U6 reviewed basename drifted")

    reviewed_u2 = _receipt_bound_workspace_file(
        predictor_dir,
        receipt,
        family="predictor_reviewed_frames",
        lane="U2",
        basename=frames["U2"],
    )
    reviewed_u6 = _receipt_bound_workspace_file(
        predictor_dir,
        receipt,
        family="predictor_reviewed_frames",
        lane="U6",
        basename=frames["U6"],
    )

    paths: dict[str, Path] = {
        expected_u2: reviewed_u2,
        U6_PREDICTOR: reviewed_u6,
    }
    metadata = {
        "u2_predictor_receipt_version": version,
        "u2_predictor_reviewed_basename": expected_u2,
        "u2_predictor_frozen_baseline_basename": U2_PREDICTOR,
        "u2_predictor_freeze_receipt_basename": None,
    }

    data = root / "data"
    if version == "V1":
        frozen_u2 = data / U2_PREDICTOR
        frozen_frames = outputs.get("predictor_frozen_frames") or {}
        freeze_receipts = outputs.get("predictor_freeze_receipts") or {}
        if frozen_frames or freeze_receipts:
            raise ValueError("U2 V1 intake must not carry V2 frozen-baseline outputs")
    else:
        frozen_frames = outputs.get("predictor_frozen_frames") or {}
        freeze_receipts = outputs.get("predictor_freeze_receipts") or {}
        if frozen_frames != {"U2": U2_PREDICTOR_V2_FROZEN}:
            raise ValueError("U2 V2 intake must contain exactly one frozen U2 V2 baseline")
        if freeze_receipts != {"U2": U2_PREDICTOR_V2_FREEZE_RECEIPT}:
            raise ValueError("U2 V2 intake must contain exactly one U2 V2 freeze receipt")

        frozen_u2 = _receipt_bound_workspace_file(
            predictor_dir,
            receipt,
            family="predictor_frozen_frames",
            lane="U2",
            basename=U2_PREDICTOR_V2_FROZEN,
        )
        freeze_receipt_path = _receipt_bound_workspace_file(
            predictor_dir,
            receipt,
            family="predictor_freeze_receipts",
            lane="U2",
            basename=U2_PREDICTOR_V2_FREEZE_RECEIPT,
        )
        _validate_u2_v2_freeze_receipt(
            root=root,
            frozen_frame=frozen_u2,
            freeze_receipt_path=freeze_receipt_path,
        )
        paths[U2_PREDICTOR_V2_FROZEN] = frozen_u2
        paths[U2_PREDICTOR_V2_FREEZE_RECEIPT] = freeze_receipt_path
        metadata["u2_predictor_frozen_baseline_basename"] = (
            U2_PREDICTOR_V2_FROZEN
        )
        metadata["u2_predictor_freeze_receipt_basename"] = (
            U2_PREDICTOR_V2_FREEZE_RECEIPT
        )

    load_predictor_adjudication_return(reviewed_u2, frozen_u2)
    load_predictor_adjudication_return(reviewed_u6, data / U6_PREDICTOR)
    return receipt, paths, metadata


def _external_sources(external_dir: Path) -> tuple[dict, dict[str, Path]]:
    receipt_path = external_dir / EXTERNAL_RECEIPT
    receipt = _load_json(receipt_path)
    if receipt.get("analysis") != "balance_plant_architecture_adjudication_return":
        raise ValueError("external adjudication receipt analysis mismatch")
    if receipt.get("scope") != "EXTERNAL" or receipt.get("complete") is not True:
        raise ValueError("external adjudication workspace is not complete")
    if receipt.get("external_validation_gate_closed") is not True:
        raise ValueError("external architecture adjudication gate is not closed")
    outputs = receipt.get("outputs") or {}
    coding = outputs.get("coding_ledgers") or {}
    adjudication = outputs.get("adjudication_ledgers") or {}
    if set(coding) != {"U1"} or set(adjudication) != {"U1"}:
        raise ValueError("external adjudication receipt must contain U1 outputs")
    return receipt, {
        U1_CODING: _receipt_bound_workspace_file(
            external_dir, receipt, family="coding_ledgers", lane="U1", basename=coding["U1"]
        ),
        U1_ADJUDICATION: _receipt_bound_workspace_file(
            external_dir, receipt, family="adjudication_ledgers", lane="U1", basename=adjudication["U1"]
        ),
    }


def _readiness(
    root: Path,
    workspace: Path,
    *,
    u2_predictor_basename: str,
) -> dict:
    data = root / "data"
    return build_plant_v4_readiness(
        u1_first20_conflict_path=data / "BALANCE_PLANT_U1_BLIND_CONFLICT_SCREEN_V1.csv",
        u1_production27_conflict_path=data / "BALANCE_PLANT_U1_PRODUCTION_BLIND_CONFLICT_SCREEN_V1.csv",
        u1_sample_path=data / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv",
        u1_worksheet_path=(
            workspace / U1_CODING
            if (workspace / U1_CODING).exists()
            else data / U1_CODING
        ),
        u1_adjudication_path=(
            workspace / U1_ADJUDICATION
            if (workspace / U1_ADJUDICATION).exists()
            else data / U1_ADJUDICATION
        ),
        u2_conflict_path=data / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
        u2_sample_path=data / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv",
        u2_worksheet_path=workspace / U2_CODING,
        u2_adjudication_path=workspace / U2_ADJUDICATION,
        u2_predictor_receipts_path=workspace / u2_predictor_basename,
        u6_freeze_path=data / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json",
        u6_worksheet_path=workspace / U6_CODING,
        u6_adjudication_path=workspace / U6_ADJUDICATION,
        u6_predictor_receipts_path=workspace / U6_PREDICTOR,
        u6_dependence_path=data / "BALANCE_PLANT_U6_CROSS_UNIVERSE_DEPENDENCE_V1.csv",
    )


def compose_v4_human_input_workspace(
    *,
    root: Path,
    primary_adjudication_dir: Path,
    predictor_intake_dir: Path,
    out_dir: Path,
    external_adjudication_dir: Path | None = None,
) -> dict:
    """Compose validated human outputs and re-run the frozen V4 readiness gate."""
    primary_receipt, primary = _primary_sources(primary_adjudication_dir)
    predictor_receipt, predictor, predictor_meta = _predictor_sources(
        root,
        predictor_intake_dir,
    )

    sources = {**primary, **predictor}
    external_receipt = None
    if external_adjudication_dir is not None:
        external_receipt, external = _external_sources(external_adjudication_dir)
        sources.update(external)

    if out_dir.exists():
        raise ValueError(
            "V4 human input output directory already exists; choose a new immutable workspace"
        )
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(
        prefix=f".{out_dir.name}.tmp-",
        dir=out_dir.parent,
    ))
    try:
        file_receipts = {}
        for basename, source in sorted(sources.items()):
            target = tmp_dir / basename
            shutil.copyfile(source, target)
            file_receipts[basename] = {
                "source": str(source),
                "source_sha256": _sha256(source),
                "composed_sha256": _sha256(target),
            }

        readiness = _readiness(
            root,
            tmp_dir,
            u2_predictor_basename=predictor_meta[
                "u2_predictor_reviewed_basename"
            ],
        )
        if readiness["open_gate_names"]:
            raise ValueError(
                "composed workspace still has primary human gates open: "
                + ", ".join(readiness["open_gate_names"])
            )
        if readiness["primary_model_assembly_ready"] is not True:
            raise ValueError(
                "composed workspace does not pass the frozen primary assembly gate"
            )

        receipt = {
            "schema_version": "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_V1",
            "analysis": "balance_plant_v4_human_input_workspace",
            "primary_adjudication_receipt_sha256": _sha256(
                primary_adjudication_dir / PRIMARY_RECEIPT
            ),
            "predictor_intake_receipt_sha256": _sha256(
                predictor_intake_dir / INTAKE_RECEIPT
            ),
            "external_adjudication_receipt_sha256": (
                _sha256(external_adjudication_dir / EXTERNAL_RECEIPT)
                if external_adjudication_dir is not None
                else None
            ),
            "external_validation_included": external_receipt is not None,
            "u2_predictor_receipt_version": predictor_meta[
                "u2_predictor_receipt_version"
            ],
            "u2_predictor_reviewed_basename": predictor_meta[
                "u2_predictor_reviewed_basename"
            ],
            "u2_predictor_frozen_baseline_basename": predictor_meta[
                "u2_predictor_frozen_baseline_basename"
            ],
            "u2_predictor_freeze_receipt_basename": predictor_meta[
                "u2_predictor_freeze_receipt_basename"
            ],
            "files": file_receipts,
            "primary_human_open_gates": readiness["primary_human_open_gates"],
            "primary_model_assembly_ready": readiness["primary_model_assembly_ready"],
            "v4_estimability_ready_to_evaluate": readiness[
                "v4_estimability_ready_to_evaluate"
            ],
            "next_step": "BUILD_V4_ANALYSIS_INPUTS",
            "build_command": (
                "python scripts/build_plant_v4_analysis_inputs.py "
                f"--input-dir {out_dir} --build"
            ),
            "claim_ceiling": "validated_human_input_composition_only_no_model_effect",
        }
        receipt_name = "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_RECEIPT_V1.json"
        (tmp_dir / receipt_name).write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tmp_dir.rename(out_dir)
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    return {
        "receipt": str(out_dir / receipt_name),
        "primary_model_assembly_ready": True,
        "external_validation_included": external_receipt is not None,
        "next_step": "BUILD_V4_ANALYSIS_INPUTS",
    }

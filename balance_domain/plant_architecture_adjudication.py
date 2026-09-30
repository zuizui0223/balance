"""Fail-closed architecture-adjudication handoff for BALANCE plant V4.

This module begins only after independent-coder reliability has passed. It builds blinded
source-review packets for architecture adjudication and validates completed adjudication
returns against the frozen coder consensus/disagreement structure. Predictor-review
outputs are deliberately excluded.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from .plant_macro_agreement import load_double_coding
from .plant_u1 import load_u1_sample
from .plant_u1_double_code import load_u1_adjudication
from .plant_u2 import load_u2_adjudication, load_u2_double_code_sample
from .plant_u6 import (
    load_u6_pass1_freeze_manifest,
    load_u6_pass2_adjudication,
    load_u6_pass2_double_coding,
)


SCOPES = ("PRIMARY", "EXTERNAL")
INTAKE_RECEIPT = "BALANCE_PLANT_HUMAN_RETURN_INTAKE_RECEIPT_V1.json"

LANES_BY_SCOPE = {
    "PRIMARY": ("U2", "U6"),
    "EXTERNAL": ("U1",),
}
MERGED_BASENAMES = {
    "U1": "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv",
    "U2": "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
    "U6": "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv",
}
ADJUDICATION_BASENAMES = {
    "U1": "BALANCE_PLANT_U1_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
    "U2": "BALANCE_PLANT_U2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
    "U6": "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv",
}
SOURCE_PACKET_REL = {
    "U1": "data/BALANCE_PLANT_U1_DOUBLE_CODE_SOURCE_PACKET_V1.csv",
    "U2": "data/BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv",
    "U6": "data/BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv",
}
SAMPLE_REL = {
    "U1": "data/BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv",
    "U2": "data/BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv",
}
FREEZE_REL = "data/BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"
CODEBOOK_REL = "data/BALANCE_PLANT_MACRO_CODEBOOK_V1.csv"
PROTOCOL_REL = "docs/BALANCE_PLANT_ARCHITECTURE_ADJUDICATION_PROTOCOL_V1.md"

FORBIDDEN_PACKET_FRAGMENTS = (
    "PREDICTOR_RECEIPT",
    "PREDICTOR_ADJUDICATION",
    "MODEL_FIT",
    "POSTFIT",
    "REACTIVATION",
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _zip_write_bytes(archive: zipfile.ZipFile, arcname: str, data: bytes) -> None:
    info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def _scope(scope: str) -> str:
    value = scope.strip().upper()
    if value not in SCOPES:
        raise ValueError(f"architecture adjudication scope must be one of {SCOPES}")
    return value


def _load_intake_receipt(intake_dir: Path) -> dict:
    path = intake_dir / INTAKE_RECEIPT
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("analysis") != "balance_plant_human_return_intake":
        raise ValueError("human-return intake receipt analysis mismatch")
    if data.get("ready_for_v4_assembly") is not False:
        raise ValueError("architecture adjudication requires a pre-assembly intake receipt")
    return data


def _require_scope_reliability(receipt: dict, scope: str) -> None:
    if scope == "PRIMARY":
        if receipt.get("primary_architecture_returns_received") is not True:
            raise ValueError("PRIMARY adjudication requires primary architecture returns")
        if receipt.get("primary_reliability_pass") is not True:
            raise ValueError("PRIMARY adjudication requires U2/U6 reliability PASS")
    else:
        if receipt.get("external_validation_returns_received") is not True:
            raise ValueError("EXTERNAL adjudication requires U1 return stage")
        if receipt.get("external_validation_reliability_pass") is not True:
            raise ValueError("EXTERNAL adjudication requires U1 reliability PASS")


def _receipt_output_path(
    intake_dir: Path,
    receipt: dict,
    *,
    family: str,
    lane: str,
) -> Path:
    outputs = receipt.get("outputs") or {}
    mapping = outputs.get(family) or {}
    basename = mapping.get(lane)
    if not isinstance(basename, str) or not basename:
        raise ValueError(f"intake receipt lacks {family} output for {lane}")
    path = intake_dir / basename
    if not path.is_file():
        raise ValueError(f"intake output is missing for {lane}: {path}")
    return path


def _load_coding(root: Path, intake_dir: Path, receipt: dict, lane: str):
    path = _receipt_output_path(
        intake_dir,
        receipt,
        family="merged_ledgers",
        lane=lane,
    )
    if lane == "U6":
        return load_u6_pass2_double_coding(path, root / FREEZE_REL)
    return load_double_coding(path)


def _agreement_path(intake_dir: Path, receipt: dict, lane: str) -> Path:
    return _receipt_output_path(
        intake_dir,
        receipt,
        family="agreement_reports",
        lane=lane,
    )


def _disagreement_path(intake_dir: Path, receipt: dict, lane: str) -> Path:
    return _receipt_output_path(
        intake_dir,
        receipt,
        family="disagreement_ledgers",
        lane=lane,
    )


def _packet_payloads(
    *,
    root: Path,
    intake_dir: Path,
    scope: str,
) -> tuple[list[tuple[str, bytes]], dict]:
    scope = _scope(scope)
    receipt = _load_intake_receipt(intake_dir)
    _require_scope_reliability(receipt, scope)

    payloads: list[tuple[str, bytes]] = [
        (CODEBOOK_REL, (root / CODEBOOK_REL).read_bytes()),
        (PROTOCOL_REL, (root / PROTOCOL_REL).read_bytes()),
    ]
    lanes = LANES_BY_SCOPE[scope]
    for lane in lanes:
        source_rel = SOURCE_PACKET_REL[lane]
        payloads.append((f"{lane}/{Path(source_rel).name}", (root / source_rel).read_bytes()))

        merged = _receipt_output_path(
            intake_dir,
            receipt,
            family="merged_ledgers",
            lane=lane,
        )
        payloads.append((f"{lane}/{merged.name}", merged.read_bytes()))

        agreement = _agreement_path(intake_dir, receipt, lane)
        agreement_data = json.loads(agreement.read_text(encoding="utf-8"))
        if agreement_data.get("reliability_pass") is not True:
            raise ValueError(f"{lane} agreement report is not reliability PASS")
        payloads.append((f"{lane}/{agreement.name}", agreement.read_bytes()))

        disagreements = _disagreement_path(intake_dir, receipt, lane)
        payloads.append((f"{lane}/{disagreements.name}", disagreements.read_bytes()))

        template = root / "data" / ADJUDICATION_BASENAMES[lane]
        payloads.append((f"{lane}/{template.name}", template.read_bytes()))

    for arcname, _data in payloads:
        upper = arcname.upper()
        if any(fragment in upper for fragment in FORBIDDEN_PACKET_FRAGMENTS):
            raise ValueError(f"forbidden artifact leaked into adjudication packet: {arcname}")

    provenance = {
        "intake_receipt_sha256": _sha256(intake_dir / INTAKE_RECEIPT),
        "lanes": list(lanes),
        "scope": scope,
    }
    return sorted(payloads, key=lambda item: item[0]), provenance


def build_architecture_adjudication_packet(
    *,
    root: Path,
    intake_dir: Path,
    scope: str,
    out_dir: Path,
) -> dict:
    """Build one deterministic post-reliability adjudication packet."""
    scope = _scope(scope)
    payloads, provenance = _packet_payloads(
        root=root,
        intake_dir=intake_dir,
        scope=scope,
    )
    inventory = [
        {"path": name, "bytes": len(data), "sha256": _sha256_bytes(data)}
        for name, data in payloads
    ]
    receipt = {
        "schema_version": "BALANCE_PLANT_ARCHITECTURE_ADJUDICATION_PACKET_V1",
        "scope": scope,
        "lanes": list(LANES_BY_SCOPE[scope]),
        "role": "POST_RELIABILITY_SOURCE_ADJUDICATION",
        "source_intake_receipt_sha256": provenance["intake_receipt_sha256"],
        "predictor_review_outputs_included": False,
        "packet_inventory": inventory,
        "return_files": {
            lane: ADJUDICATION_BASENAMES[lane]
            for lane in LANES_BY_SCOPE[scope]
        },
        "claim_ceiling": "architecture_adjudication_handoff_only_no_biological_result",
    }
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")

    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"BALANCE_PLANT_{scope}_ARCHITECTURE_ADJUDICATION_PACKET_V1.zip"
    receipt_path = out_dir / f"BALANCE_PLANT_{scope}_ARCHITECTURE_ADJUDICATION_PACKET_V1.json"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for arcname, data in payloads:
            _zip_write_bytes(archive, arcname, data)
        _zip_write_bytes(archive, "PACKET_RECEIPT.json", receipt_bytes)
    receipt_path.write_bytes(receipt_bytes)
    return {
        "packet": str(zip_path),
        "receipt": str(receipt_path),
        "packet_sha256": _sha256(zip_path),
        "receipt_sha256": _sha256(receipt_path),
        "scope": scope,
        "lanes": list(LANES_BY_SCOPE[scope]),
    }


def _validate_completed_adjudication(
    *,
    root: Path,
    intake_dir: Path,
    intake_receipt: dict,
    lane: str,
    path: Path,
) -> list[dict[str, str]]:
    coding = _load_coding(root, intake_dir, intake_receipt, lane)
    if lane == "U1":
        sample = load_u1_sample(root / SAMPLE_REL["U1"])
        rows = load_u1_adjudication(path, sample, coding)
    elif lane == "U2":
        sample = load_u2_double_code_sample(root / SAMPLE_REL["U2"])
        rows = load_u2_adjudication(path, sample, coding)
    elif lane == "U6":
        rows = load_u6_pass2_adjudication(
            path,
            root / FREEZE_REL,
            coding,
        )
    else:
        raise ValueError(f"unknown adjudication lane {lane!r}")

    pending = [
        row for row in rows
        if row["adjudication_status"] != "ADJUDICATED"
    ]
    if pending:
        key = "dependency_group" if lane == "U6" else "cluster_id"
        raise ValueError(
            f"{lane} adjudication return is incomplete; pending groups: "
            + ", ".join(sorted(row[key] for row in pending))
        )
    return rows


def validate_architecture_adjudication_returns(
    *,
    root: Path,
    intake_dir: Path,
    return_dir: Path,
    scope: str,
) -> dict:
    """Validate a completed architecture-adjudication return without persistent writes."""
    scope = _scope(scope)
    intake_receipt = _load_intake_receipt(intake_dir)
    _require_scope_reliability(intake_receipt, scope)

    rows_by_lane: dict[str, list[dict[str, str]]] = {}
    inputs = {}
    for lane in LANES_BY_SCOPE[scope]:
        path = return_dir / ADJUDICATION_BASENAMES[lane]
        if not path.is_file():
            raise ValueError(f"{scope} adjudication return is missing {path.name}")
        rows_by_lane[lane] = _validate_completed_adjudication(
            root=root,
            intake_dir=intake_dir,
            intake_receipt=intake_receipt,
            lane=lane,
            path=path,
        )
        inputs[lane] = {
            "basename": path.name,
            "sha256": _sha256(path),
            "n_rows": len(rows_by_lane[lane]),
        }

    return {
        "analysis": "balance_plant_architecture_adjudication_return",
        "scope": scope,
        "lanes": list(LANES_BY_SCOPE[scope]),
        "source_intake_receipt_sha256": _sha256(intake_dir / INTAKE_RECEIPT),
        "inputs": inputs,
        "rows": rows_by_lane,
        "complete": True,
        "primary_model_gate_closed": scope == "PRIMARY",
        "external_validation_gate_closed": scope == "EXTERNAL",
        "claim_ceiling": "validated_architecture_adjudication_only_no_model_effect",
    }


def write_architecture_adjudication_workspace(
    *,
    root: Path,
    intake_dir: Path,
    return_dir: Path,
    scope: str,
    out_dir: Path,
) -> dict:
    """Validate adjudication returns and atomically write one immutable workspace."""
    result = validate_architecture_adjudication_returns(
        root=root,
        intake_dir=intake_dir,
        return_dir=return_dir,
        scope=scope,
    )
    if out_dir.exists():
        raise ValueError(
            "architecture adjudication output directory already exists; "
            "choose a new immutable workspace"
        )
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(
        prefix=f".{out_dir.name}.tmp-",
        dir=out_dir.parent,
    ))
    try:
        outputs = {"coding_ledgers": {}, "adjudication_ledgers": {}}
        intake_receipt = _load_intake_receipt(intake_dir)
        for lane in result["lanes"]:
            coding = _receipt_output_path(
                intake_dir,
                intake_receipt,
                family="merged_ledgers",
                lane=lane,
            )
            coding_out = tmp_dir / MERGED_BASENAMES[lane]
            shutil.copyfile(coding, coding_out)
            outputs["coding_ledgers"][lane] = coding_out.name

            returned = return_dir / ADJUDICATION_BASENAMES[lane]
            adjudication_out = tmp_dir / returned.name
            shutil.copyfile(returned, adjudication_out)
            outputs["adjudication_ledgers"][lane] = adjudication_out.name

        receipt = {
            key: value
            for key, value in result.items()
            if key != "rows"
        }
        receipt["outputs"] = outputs
        receipt_name = (
            f"BALANCE_PLANT_{result['scope']}_ARCHITECTURE_ADJUDICATION_RECEIPT_V1.json"
        )
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
        "scope": result["scope"],
        "lanes": result["lanes"],
        "complete": True,
    }

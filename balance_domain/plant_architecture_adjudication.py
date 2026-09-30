"""Build post-agreement architecture-adjudication packets for BALANCE plants.

Consensus groups are finalized mechanically only after the lane reliability gate passes.
Groups with any independent-coder disagreement remain fully unresolved for source review.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from .plant_agreement_report import build_lane_agreement_report
from .plant_human_return_intake import MERGED_BASENAMES
from .plant_macro_agreement import AGREEMENT_FIELDS, load_double_coding
from .plant_u1 import load_u1_sample
from .plant_u1_double_code import U1_ADJUDICATION_FIELDS, load_u1_adjudication
from .plant_u2 import (
    U2_ADJUDICATION_FIELDS,
    load_u2_adjudication,
    load_u2_double_code_sample,
)
from .plant_u6 import (
    U6_ADJUDICATION_FIELDS,
    U6_AGREEMENT_FIELDS,
    load_u6_pass1_freeze_manifest,
    load_u6_pass2_adjudication,
    load_u6_pass2_double_coding,
)


PROTOCOL = "docs/BALANCE_PLANT_ARCHITECTURE_ADJUDICATION_PROTOCOL_V1.md"
CODEBOOK = "data/BALANCE_PLANT_MACRO_CODEBOOK_V1.csv"

SOURCE_PACKETS = {
    "U1": "data/BALANCE_PLANT_U1_DOUBLE_CODE_SOURCE_PACKET_V1.csv",
    "U2": "data/BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv",
    "U6": "data/BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv",
}
ADJUDICATION_BASENAMES = {
    "U1": "BALANCE_PLANT_U1_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
    "U2": "BALANCE_PLANT_U2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
    "U6": "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zip_write_bytes(archive: zipfile.ZipFile, arcname: str, data: bytes) -> None:
    info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def _lane_kwargs(root: Path, lane: str) -> dict[str, Path]:
    data = root / "data"
    if lane == "U1":
        return {"u1_sample_path": data / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"}
    if lane == "U2":
        return {"u2_sample_path": data / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"}
    if lane == "U6":
        return {"u6_freeze_path": data / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"}
    raise ValueError(f"unknown lane {lane!r}")


def _group_order(root: Path, lane: str) -> list[str]:
    if lane == "U1":
        return [
            row["dependency_group"]
            for row in load_u1_sample(
                root / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"
            )
        ]
    if lane == "U2":
        return [
            row["dependency_group"]
            for row in load_u2_double_code_sample(
                root / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"
            )
        ]
    if lane == "U6":
        return list(
            load_u6_pass1_freeze_manifest(
                root / "data" / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"
            )["included_dependency_groups"]
        )
    raise ValueError(f"unknown lane {lane!r}")


def _load_coding(root: Path, intake_dir: Path, lane: str) -> list[dict[str, str]]:
    path = intake_dir / MERGED_BASENAMES[lane]
    if not path.is_file():
        raise ValueError(f"intake workspace lacks merged {lane} coding ledger")
    if lane in {"U1", "U2"}:
        return load_double_coding(path)
    return load_u6_pass2_double_coding(
        path,
        root / "data" / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json",
    )


def _agreement_fields(lane: str) -> tuple[str, ...]:
    return AGREEMENT_FIELDS if lane in {"U1", "U2"} else U6_AGREEMENT_FIELDS


def _group_field(lane: str) -> str:
    return "cluster_id" if lane in {"U1", "U2"} else "dependency_group"


def _adjudication_fields(lane: str) -> tuple[str, ...]:
    if lane == "U1":
        return U1_ADJUDICATION_FIELDS
    if lane == "U2":
        return U2_ADJUDICATION_FIELDS
    if lane == "U6":
        return U6_ADJUDICATION_FIELDS
    raise ValueError(f"unknown lane {lane!r}")


def _recomputed_agreement(root: Path, intake_dir: Path, lane: str) -> dict:
    coding_path = intake_dir / MERGED_BASENAMES[lane]
    live = build_lane_agreement_report(
        lane=lane,
        coding_path=coding_path,
        **_lane_kwargs(root, lane),
    )
    stored_path = intake_dir / f"BALANCE_PLANT_{lane}_AGREEMENT_REPORT_V1.json"
    if not stored_path.is_file():
        raise ValueError(f"intake workspace lacks stored {lane} agreement report")
    stored = json.loads(stored_path.read_text(encoding="utf-8"))
    if stored != live:
        raise ValueError(
            f"{lane} agreement report no longer matches the merged coding ledger"
        )
    return live


def _coding_pairs(coding: list[dict[str, str]], lane: str) -> dict[str, dict[str, dict[str, str]]]:
    group_field = _group_field(lane)
    grouped: dict[str, dict[str, dict[str, str]]] = {}
    for row in coding:
        group = row[group_field]
        grouped.setdefault(group, {})[row["coder_id"]] = row
    for group, pair in grouped.items():
        if set(pair) != {"CODER_A", "CODER_B"}:
            raise ValueError(f"{lane} group {group!r} lacks both frozen coder IDs")
    return grouped


def _validate_generated_adjudication(
    *,
    root: Path,
    lane: str,
    path: Path,
    coding: list[dict[str, str]],
) -> None:
    if lane == "U1":
        load_u1_adjudication(
            path,
            load_u1_sample(root / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"),
            coding,
        )
    elif lane == "U2":
        load_u2_adjudication(
            path,
            load_u2_double_code_sample(
                root / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"
            ),
            coding,
        )
    elif lane == "U6":
        load_u6_pass2_adjudication(
            path,
            root / "data" / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json",
            coding,
        )
    else:
        raise ValueError(f"unknown lane {lane!r}")


def build_lane_adjudication_rows(
    *,
    root: Path,
    intake_dir: Path,
    lane: str,
) -> dict:
    """Return a validated post-agreement adjudication surface for one lane."""
    agreement = _recomputed_agreement(root, intake_dir, lane)
    coding = _load_coding(root, intake_dir, lane)
    fields = _agreement_fields(lane)
    group_field = _group_field(lane)
    pairs = _coding_pairs(coding, lane)
    order = _group_order(root, lane)

    if not agreement["reliability_pass"]:
        return {
            "lane": lane,
            "reliability_pass": False,
            "rows": [],
            "review_context": [],
            "n_consensus_autoadjudicated": 0,
            "n_source_review_pending": 0,
            "source_review_groups": [],
            "next_step": "CODEBOOK_REPAIR_AND_INDEPENDENT_RECODE_SAME_FROZEN_GROUPS",
        }

    rows: list[dict[str, str]] = []
    review_context: list[dict[str, str]] = []
    source_review_groups: list[str] = []
    n_consensus = 0

    for group in order:
        pair = pairs[group]
        a = pair["CODER_A"]
        b = pair["CODER_B"]
        disagreements = [field for field in fields if a[field] != b[field]]

        for field in fields:
            review_context.append({
                "dependency_group": group,
                "field": field,
                "coder_a_value": a[field],
                "coder_b_value": b[field],
                "agreement_status": "DISAGREE" if field in disagreements else "AGREE",
            })

        row = {
            group_field: group,
            **{field: "UNRESOLVED" for field in fields},
            "adjudication_status": "PENDING",
            "adjudication_basis": "AWAITING_SOURCE_REVIEW_OF_DISAGREEMENTS",
            "notes": (
                "disagreement_fields=" + ";".join(disagreements)
                if disagreements else ""
            ),
        }

        if not disagreements:
            for field in fields:
                row[field] = a[field]
            row["adjudication_status"] = "ADJUDICATED"
            row["adjudication_basis"] = "CODER_CONSENSUS"
            row["notes"] = "AUTO_CODER_CONSENSUS_AFTER_RELIABILITY_PASS"
            n_consensus += 1
        else:
            source_review_groups.append(group)

        rows.append(row)

    adjudication_fields = _adjudication_fields(lane)
    with tempfile.TemporaryDirectory(prefix=f"balance-{lane.lower()}-adjudication-") as tmp:
        path = Path(tmp) / ADJUDICATION_BASENAMES[lane]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=adjudication_fields,
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
        _validate_generated_adjudication(
            root=root,
            lane=lane,
            path=path,
            coding=coding,
        )

    return {
        "lane": lane,
        "reliability_pass": True,
        "rows": rows,
        "review_context": review_context,
        "n_consensus_autoadjudicated": n_consensus,
        "n_source_review_pending": len(source_review_groups),
        "source_review_groups": source_review_groups,
        "next_step": (
            "SOURCE_REVIEW_OF_DISAGREEMENTS"
            if source_review_groups
            else "ARCHITECTURE_ADJUDICATION_COMPLETE_BY_CODER_CONSENSUS"
        ),
    }


def _csv_bytes(fields: list[str] | tuple[str, ...], rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _packet_payloads(
    *,
    root: Path,
    intake_dir: Path,
    lane_result: dict,
) -> list[tuple[str, bytes]]:
    lane = lane_result["lane"]
    if not lane_result["reliability_pass"]:
        raise ValueError(f"cannot build {lane} adjudication packet before reliability passes")

    payloads = [
        (CODEBOOK, (root / CODEBOOK).read_bytes()),
        (PROTOCOL, (root / PROTOCOL).read_bytes()),
        (
            f"{lane}/{Path(SOURCE_PACKETS[lane]).name}",
            (root / SOURCE_PACKETS[lane]).read_bytes(),
        ),
        (
            f"{lane}/BALANCE_PLANT_{lane}_AGREEMENT_REPORT_V1.json",
            (
                intake_dir / f"BALANCE_PLANT_{lane}_AGREEMENT_REPORT_V1.json"
            ).read_bytes(),
        ),
        (
            f"{lane}/BALANCE_PLANT_{lane}_ARCHITECTURE_REVIEW_CONTEXT_V1.csv",
            _csv_bytes(
                (
                    "dependency_group",
                    "field",
                    "coder_a_value",
                    "coder_b_value",
                    "agreement_status",
                ),
                lane_result["review_context"],
            ),
        ),
        (
            f"{lane}/{ADJUDICATION_BASENAMES[lane]}",
            _csv_bytes(
                _adjudication_fields(lane),
                lane_result["rows"],
            ),
        ),
    ]
    return sorted(payloads, key=lambda item: item[0])


def build_architecture_adjudication_packets(
    *,
    root: Path,
    intake_dir: Path,
    out_dir: Path,
) -> dict:
    """Build deterministic lane packets only after each lane reliability gate passes."""
    intake_receipt_path = (
        intake_dir / "BALANCE_PLANT_HUMAN_RETURN_INTAKE_RECEIPT_V1.json"
    )
    if not intake_receipt_path.is_file():
        raise ValueError("architecture adjudication requires a canonical intake receipt")
    intake_receipt = json.loads(intake_receipt_path.read_text(encoding="utf-8"))
    if intake_receipt.get("schema_version") != (
        "BALANCE_PLANT_HUMAN_RETURN_INTAKE_RECEIPT_V1"
    ):
        raise ValueError("human-return intake receipt schema mismatch")

    lane_results = {
        lane: build_lane_adjudication_rows(
            root=root,
            intake_dir=intake_dir,
            lane=lane,
        )
        for lane in ("U1", "U2", "U6")
    }

    if out_dir.exists():
        raise ValueError(
            "architecture adjudication output directory already exists; "
            "choose a new immutable packet workspace"
        )
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(
        prefix=f".{out_dir.name}.tmp-",
        dir=out_dir.parent,
    ))

    packets: dict[str, dict] = {}
    try:
        for lane, result in lane_results.items():
            if not result["reliability_pass"]:
                packets[lane] = {
                    "generated": False,
                    "reason": result["next_step"],
                }
                continue

            payloads = _packet_payloads(
                root=root,
                intake_dir=intake_dir,
                lane_result=result,
            )
            inventory = [
                {
                    "path": name,
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
                for name, data in payloads
            ]
            receipt = {
                "schema_version": (
                    "BALANCE_PLANT_ARCHITECTURE_ADJUDICATION_PACKET_V1"
                ),
                "lane": lane,
                "source_intake_receipt_sha256": _sha256(intake_receipt_path),
                "n_consensus_autoadjudicated": result[
                    "n_consensus_autoadjudicated"
                ],
                "n_source_review_pending": result["n_source_review_pending"],
                "source_review_groups": result["source_review_groups"],
                "packet_inventory": inventory,
                "claim_ceiling": (
                    "post_reliability_architecture_adjudication_handoff_only_"
                    "no_biological_result"
                ),
            }
            receipt_bytes = (
                json.dumps(receipt, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8")

            zip_name = (
                f"BALANCE_PLANT_{lane}_ARCHITECTURE_ADJUDICATION_PACKET_V1.zip"
            )
            receipt_name = (
                f"BALANCE_PLANT_{lane}_ARCHITECTURE_ADJUDICATION_PACKET_V1.json"
            )
            zip_path = tmp_dir / zip_name
            with zipfile.ZipFile(zip_path, "w") as archive:
                for arcname, data in payloads:
                    _zip_write_bytes(archive, arcname, data)
                _zip_write_bytes(archive, "PACKET_RECEIPT.json", receipt_bytes)
            (tmp_dir / receipt_name).write_bytes(receipt_bytes)
            packets[lane] = {
                "generated": True,
                "packet": zip_name,
                "receipt": receipt_name,
                "packet_sha256": _sha256(zip_path),
                "n_consensus_autoadjudicated": result[
                    "n_consensus_autoadjudicated"
                ],
                "n_source_review_pending": result["n_source_review_pending"],
                "next_step": result["next_step"],
            }

        primary_packets_ready = all(
            packets[lane].get("generated", False)
            for lane in ("U2", "U6")
        )
        build_receipt = {
            "schema_version": (
                "BALANCE_PLANT_ARCHITECTURE_ADJUDICATION_BUILD_RECEIPT_V1"
            ),
            "source_intake_receipt_sha256": _sha256(intake_receipt_path),
            "lanes": packets,
            "primary_packets_ready": primary_packets_ready,
            "u1_external_validation_packet_ready": packets["U1"].get(
                "generated", False
            ),
            "claim_ceiling": (
                "architecture_adjudication_packet_build_only_no_biological_result"
            ),
        }
        build_name = (
            "BALANCE_PLANT_ARCHITECTURE_ADJUDICATION_BUILD_RECEIPT_V1.json"
        )
        (tmp_dir / build_name).write_text(
            json.dumps(build_receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tmp_dir.rename(out_dir)
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    return {
        "receipt": str(
            out_dir / "BALANCE_PLANT_ARCHITECTURE_ADJUDICATION_BUILD_RECEIPT_V1.json"
        ),
        "primary_packets_ready": all(
            packets[lane].get("generated", False)
            for lane in ("U2", "U6")
        ),
        "lanes": packets,
    }

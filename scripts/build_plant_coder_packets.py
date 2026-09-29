#!/usr/bin/env python3
"""Build blinded BALANCE plant independent-coder packets.

Each packet contains the same frozen evidence surfaces and a coder-specific worksheet.
It intentionally excludes source-screen decisions, adjudication templates, agreement
outputs, and the other coder's worksheet rows.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "data" / "BALANCE_PLANT_CODER_HANDOFF_MANIFEST_V1.json"
DEFAULT_OUT = ROOT / "release" / "generated" / "plant_coder_packets"

CODERS = ("CODER_A", "CODER_B")
LANES = ("U1", "U2", "U6")

SHARED_FILES = (
    "data/BALANCE_PLANT_MACRO_CODEBOOK_V1.csv",
    "docs/BALANCE_PLANT_DOUBLE_CODING_PROTOCOL_V1.md",
)

FORBIDDEN_NAME_FRAGMENTS = (
    "SCREENING",
    "CONFLICT_SCREEN",
    "ADJUDICATION",
    "AGREEMENT",
    "PREDICTOR_RECEIPT",
    "REACTIVATION",
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _zip_write_bytes(archive: zipfile.ZipFile, arcname: str, data: bytes) -> None:
    info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def _read_handoff() -> dict:
    data = json.loads(HANDOFF.read_text(encoding="utf-8"))
    if data.get("status") != "READY_FOR_HUMAN_INDEPENDENT_CODING":
        raise ValueError("plant coder handoff is not ready")
    if data["shared"]["frozen_coder_ids"] != list(CODERS):
        raise ValueError("plant coder IDs drifted")
    return data


def _filter_worksheet(path: Path, coder_id: str) -> bytes:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or ())
        rows = [row for row in reader if row.get("coder_id") == coder_id]

    if not fields or "coder_id" not in fields:
        raise ValueError(f"worksheet lacks coder_id: {path}")
    if not rows:
        raise ValueError(f"no rows for {coder_id} in {path}")
    if any(row.get("coder_id") != coder_id for row in rows):
        raise ValueError(f"worksheet filtering leaked the other coder: {path}")

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _packet_payloads(coder_id: str) -> list[tuple[str, bytes]]:
    if coder_id not in CODERS:
        raise ValueError(f"unknown coder_id {coder_id!r}")
    handoff = _read_handoff()

    payloads: list[tuple[str, bytes]] = []
    for rel in SHARED_FILES:
        payloads.append((rel, (ROOT / rel).read_bytes()))

    for lane in LANES:
        lane_info = handoff["lanes"][lane]
        source_rel = lane_info["source_packet"]
        source_name = Path(source_rel).name
        payloads.append((f"{lane}/{source_name}", (ROOT / source_rel).read_bytes()))

        worksheet_rel = lane_info["worksheet"]
        worksheet_name = Path(worksheet_rel).name.replace(
            "_WORKSHEET_", f"_WORKSHEET_{coder_id}_"
        )
        payloads.append(
            (
                f"{lane}/{worksheet_name}",
                _filter_worksheet(ROOT / worksheet_rel, coder_id),
            )
        )

    for arcname, _data in payloads:
        upper = arcname.upper()
        if any(fragment in upper for fragment in FORBIDDEN_NAME_FRAGMENTS):
            # WORKSHEET is intentionally allowed and does not match any forbidden fragment.
            raise ValueError(f"forbidden artifact leaked into coder packet: {arcname}")

    return sorted(payloads, key=lambda item: item[0])


def build_coder_packet(coder_id: str, out_dir: Path = DEFAULT_OUT) -> tuple[Path, Path]:
    payloads = _packet_payloads(coder_id)
    inventory = [
        {"path": arcname, "bytes": len(data), "sha256": _sha256(data)}
        for arcname, data in payloads
    ]
    receipt = {
        "schema_version": "BALANCE_PLANT_CODER_PACKET_RECEIPT_V1",
        "coder_id": coder_id,
        "lanes": list(LANES),
        "shared_evidence_contract": (
            "coder A and coder B receive byte-identical source packets/codebook/protocol; "
            "only worksheet coder_id rows differ"
        ),
        "forbidden_inputs": list(_read_handoff()["shared"]["forbidden_inputs"]),
        "packet_inventory": inventory,
        "claim_ceiling": "independent_coder_handoff_only_no_biological_result",
    }
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")

    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"BALANCE_PLANT_{coder_id}_PACKET_V1.zip"
    receipt_path = out_dir / f"BALANCE_PLANT_{coder_id}_PACKET_V1.json"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for arcname, data in payloads:
            _zip_write_bytes(archive, arcname, data)
        _zip_write_bytes(archive, "PACKET_RECEIPT.json", receipt_bytes)
    receipt_path.write_bytes(receipt_bytes)
    return zip_path, receipt_path


def build_all(out_dir: Path = DEFAULT_OUT) -> dict[str, tuple[Path, Path]]:
    return {coder: build_coder_packet(coder, out_dir) for coder in CODERS}


if __name__ == "__main__":
    outputs = build_all()
    for coder, paths in outputs.items():
        print(coder, *(str(path) for path in paths))

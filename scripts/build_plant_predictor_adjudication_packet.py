#!/usr/bin/env python3
"""Build the blinded BALANCE plant predictor-receipt adjudication packet."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "release" / "generated" / "plant_predictor_adjudication"

FILES = (
    "data/BALANCE_PLANT_MACRO_CODEBOOK_V1.csv",
    "docs/BALANCE_PLANT_PREDICTOR_RECEIPT_ADJUDICATION_PROTOCOL_V1.md",
    "data/BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv",
    "data/BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    "data/BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv",
    "data/BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
)

FORBIDDEN_NAME_FRAGMENTS = (
    "WORKSHEET",
    "ARCHITECTURE_HANDOFF",
    "DOUBLE_CODE_ADJUDICATION",
    "AGREEMENT",
    "REACTIVATION",
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _zip_write_bytes(archive: zipfile.ZipFile, arcname: str, data: bytes) -> None:
    info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def packet_payloads() -> list[tuple[str, bytes]]:
    payloads = [(rel, (ROOT / rel).read_bytes()) for rel in FILES]
    for arcname, _data in payloads:
        upper = arcname.upper()
        if any(fragment in upper for fragment in FORBIDDEN_NAME_FRAGMENTS):
            raise ValueError(
                f"architecture/adjudication artifact leaked into predictor packet: {arcname}"
            )
    return sorted(payloads, key=lambda item: item[0])


def build_packet(out_dir: Path = DEFAULT_OUT) -> tuple[Path, Path]:
    payloads = packet_payloads()
    inventory = [
        {"path": arcname, "bytes": len(data), "sha256": _sha256(data)}
        for arcname, data in payloads
    ]
    receipt = {
        "schema_version": "BALANCE_PLANT_PREDICTOR_ADJUDICATION_PACKET_V1",
        "role": "INDEPENDENT_PREDICTOR_RECEIPT_REVIEW",
        "primary_universes": [
            "U2_BARRETT_2002",
            "U6_POLLEN_THEFT_HARGREAVES_2009",
        ],
        "architecture_outputs_included": False,
        "review_questions": [
            "source_supports_reported_predictor_value",
            "evidence_is_independent_of_focal_architecture_outcome",
            "evidence_type_is_correct",
            "receipt_note_explains_source_side_basis",
        ],
        "allowed_final_status": ["ADJUDICATED", "REJECTED"],
        "packet_inventory": inventory,
        "claim_ceiling": "predictor_provenance_and_independence_review_only",
    }
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")

    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / "BALANCE_PLANT_PREDICTOR_ADJUDICATION_PACKET_V1.zip"
    receipt_path = out_dir / "BALANCE_PLANT_PREDICTOR_ADJUDICATION_PACKET_V1.json"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for arcname, data in payloads:
            _zip_write_bytes(archive, arcname, data)
        _zip_write_bytes(archive, "PACKET_RECEIPT.json", receipt_bytes)
    receipt_path.write_bytes(receipt_bytes)
    return zip_path, receipt_path


if __name__ == "__main__":
    print(*(str(path) for path in build_packet()))

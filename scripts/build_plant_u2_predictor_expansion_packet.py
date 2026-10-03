#!/usr/bin/env python3
"""Build the blinded U2 predictor-expansion coding packet."""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_predictor_expansion import (
    load_expansion_coding,
    validate_expansion_template,
)


DEFAULT_OUT = ROOT / "release" / "generated" / "plant_u2_predictor_expansion"

FILES = (
    "data/BALANCE_PLANT_MACRO_CODEBOOK_V1.csv",
    "docs/BALANCE_PLANT_U2_PREDICTOR_EXPANSION_PROTOCOL_V2.md",
    "data/BALANCE_PLANT_U2_PREDICTOR_EXPANSION_SOURCE_PACKET_V2.csv",
    "data/BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv",
)

FORBIDDEN_NAME_FRAGMENTS = (
    "ARCHITECTURE",
    "CONFLICT_SCREEN",
    "AGREEMENT",
    "ADJUDICATION",
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
    template = validate_expansion_template(
        load_expansion_coding(
            ROOT / "data" / "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv"
        )
    )
    if len(template) != 36 or len({row["cluster_id"] for row in template}) != 12:
        raise ValueError("U2 predictor expansion template drifted from 12 groups / 36 slots")

    payloads = [(rel, (ROOT / rel).read_bytes()) for rel in FILES]
    for arcname, _data in payloads:
        upper = arcname.upper()
        if any(fragment in upper for fragment in FORBIDDEN_NAME_FRAGMENTS):
            raise ValueError(
                f"architecture/outcome artifact leaked into expansion packet: {arcname}"
            )
    return sorted(payloads, key=lambda item: item[0])


def build_packet(out_dir: Path = DEFAULT_OUT) -> tuple[Path, Path]:
    payloads = packet_payloads()
    inventory = [
        {"path": arcname, "bytes": len(data), "sha256": _sha256(data)}
        for arcname, data in payloads
    ]
    receipt = {
        "schema_version": "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_PACKET_V2",
        "role": "INDEPENDENT_U2_PREDICTOR_EXPANSION_CODING",
        "population_rule": "all_12_frozen_unresolved_U2_reliability_groups",
        "n_groups": 12,
        "n_predictor_slots": 36,
        "selective_gap_filling_forbidden": True,
        "architecture_outputs_included": False,
        "conflict_screen_outputs_included": False,
        "allowed_final_coding_status": ["CODED", "EVIDENCE_CEILING"],
        "packet_inventory": inventory,
        "next_step": (
            "validate complete 36-slot return, freeze V2 receipt frame, then send V2 "
            "receipts to a separate independent predictor adjudicator"
        ),
        "claim_ceiling": "prospective_predictor_geometry_coding_only_no_biological_result",
    }
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")

    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_PACKET_V2.zip"
    receipt_path = out_dir / "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_PACKET_V2.json"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for arcname, data in payloads:
            _zip_write_bytes(archive, arcname, data)
        _zip_write_bytes(archive, "PACKET_RECEIPT.json", receipt_bytes)
    receipt_path.write_bytes(receipt_bytes)
    return zip_path, receipt_path


if __name__ == "__main__":
    print(*(str(path) for path in build_packet()))

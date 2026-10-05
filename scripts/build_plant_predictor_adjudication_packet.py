#!/usr/bin/env python3
"""Build the blinded BALANCE plant predictor-receipt adjudication packet."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "release" / "generated" / "plant_predictor_adjudication"

CODEBOOK = ROOT / "data" / "BALANCE_PLANT_MACRO_CODEBOOK_V1.csv"
PROTOCOL_V1 = ROOT / "docs" / "BALANCE_PLANT_PREDICTOR_RECEIPT_ADJUDICATION_PROTOCOL_V1.md"
PROTOCOL_V2 = ROOT / "docs" / "BALANCE_PLANT_PREDICTOR_RECEIPT_ADJUDICATION_PROTOCOL_V2.md"
U2_SOURCE = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv"
U2_V1 = ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U2_EXPANSION_TEMPLATE = ROOT / "data" / "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv"
U2_V2_BASENAME = "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2.csv"
U2_V2_FREEZE_RECEIPT = "BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2.json"
U6_SOURCE = ROOT / "data" / "BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv"
U6_V1 = ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"

FORBIDDEN_NAME_FRAGMENTS = (
    "WORKSHEET",
    "ARCHITECTURE_HANDOFF",
    "DOUBLE_CODE_ADJUDICATION",
    "AGREEMENT",
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


def _validate_u2_v2_freeze_dir(freeze_dir: Path) -> tuple[Path, Path, dict]:
    frame = freeze_dir / U2_V2_BASENAME
    receipt_path = freeze_dir / U2_V2_FREEZE_RECEIPT
    if not frame.is_file() or not receipt_path.is_file():
        raise ValueError(
            "U2 V2 predictor packet requires frozen V2 frame and freeze receipt"
        )

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("schema_version") != "BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2":
        raise ValueError("U2 V2 freeze receipt schema mismatch")
    if receipt.get("status") != "FROZEN_SCREENED_AWAITING_INDEPENDENT_ADJUDICATION":
        raise ValueError("U2 V2 freeze receipt status mismatch")
    if receipt.get("v2_receipt_frame") != U2_V2_BASENAME:
        raise ValueError("U2 V2 freeze receipt frame basename mismatch")
    if receipt.get("v2_receipt_frame_sha256") != _sha256(frame):
        raise ValueError("U2 V2 frozen frame SHA256 mismatch")
    if receipt.get("v1_receipts_sha256") != _sha256(U2_V1):
        raise ValueError("U2 V2 freeze receipt is not bound to current V1 receipts")
    if receipt.get("expansion_template_sha256") != _sha256(U2_EXPANSION_TEMPLATE):
        raise ValueError("U2 V2 freeze receipt is not bound to expansion template")
    return frame, receipt_path, receipt


def packet_payloads(
    *,
    u2_v2_freeze_dir: Path | None = None,
) -> tuple[str, list[tuple[str, bytes]], dict | None]:
    protocol = PROTOCOL_V1 if u2_v2_freeze_dir is None else PROTOCOL_V2
    protocol_arcname = (
        "docs/BALANCE_PLANT_PREDICTOR_RECEIPT_ADJUDICATION_PROTOCOL_V1.md"
        if u2_v2_freeze_dir is None
        else "docs/BALANCE_PLANT_PREDICTOR_RECEIPT_ADJUDICATION_PROTOCOL_V2.md"
    )
    payloads = [
        ("data/BALANCE_PLANT_MACRO_CODEBOOK_V1.csv", CODEBOOK.read_bytes()),
        (protocol_arcname, protocol.read_bytes()),
        ("data/BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv", U2_SOURCE.read_bytes()),
        (
            "data/BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv",
            U6_SOURCE.read_bytes(),
        ),
        (
            "data/BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
            U6_V1.read_bytes(),
        ),
    ]

    freeze_receipt = None
    if u2_v2_freeze_dir is None:
        u2_version = "V1"
        payloads.append(
            (
                "data/BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
                U2_V1.read_bytes(),
            )
        )
    else:
        u2_version = "V2"
        frame, freeze_path, freeze_receipt = _validate_u2_v2_freeze_dir(
            u2_v2_freeze_dir
        )
        payloads.extend([
            (
                f"data/{U2_V2_BASENAME}",
                frame.read_bytes(),
            ),
            (
                f"provenance/{U2_V2_FREEZE_RECEIPT}",
                freeze_path.read_bytes(),
            ),
        ])

    for arcname, _data in payloads:
        upper = arcname.upper()
        if any(fragment in upper for fragment in FORBIDDEN_NAME_FRAGMENTS):
            raise ValueError(
                f"architecture/adjudication artifact leaked into predictor packet: {arcname}"
            )
    return u2_version, sorted(payloads, key=lambda item: item[0]), freeze_receipt


def build_packet(
    out_dir: Path = DEFAULT_OUT,
    *,
    u2_v2_freeze_dir: Path | None = None,
) -> tuple[Path, Path]:
    u2_version, payloads, freeze_receipt = packet_payloads(
        u2_v2_freeze_dir=u2_v2_freeze_dir
    )
    inventory = [
        {"path": arcname, "bytes": len(data), "sha256": _sha256_bytes(data)}
        for arcname, data in payloads
    ]
    # Preserve the already-executed V1 handoff byte-for-byte. Its SHA256 is a
    # frozen provenance receipt, so version metadata is added only to the new V2 packet.
    if u2_version == "V1":
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
    else:
        receipt = {
            "schema_version": "BALANCE_PLANT_PREDICTOR_ADJUDICATION_PACKET_V1",
            "role": "INDEPENDENT_PREDICTOR_RECEIPT_REVIEW",
            "primary_universes": [
                "U2_BARRETT_2002",
                "U6_POLLEN_THEFT_HARGREAVES_2009",
            ],
            "u2_predictor_receipt_version": "V2",
            "u2_frozen_receipt_basename": U2_V2_BASENAME,
            "u2_v2_freeze_receipt_included": True,
            "u2_v2_freeze_receipt_sha256": _sha256_bytes(
                next(
                    data
                    for name, data in payloads
                    if name == f"provenance/{U2_V2_FREEZE_RECEIPT}"
                )
            ),
            "u2_v2_n_groups_with_three_resolved_independent_predictors": (
                freeze_receipt[
                    "n_groups_with_three_resolved_independent_predictors"
                ]
            ),
            "architecture_outputs_included": False,
            "review_questions": [
                "source_supports_reported_predictor_value",
                "evidence_is_independent_of_focal_architecture_outcome",
                "evidence_type_is_correct",
                "receipt_note_explains_source_side_basis",
            ],
            "allowed_final_status": ["ADJUDICATED", "REJECTED"],
            "return_rule": (
                "return U2 receipt CSV under the same versioned basename supplied in "
                "this packet; return U6 under its frozen V1 basename"
            ),
            "packet_inventory": inventory,
            "claim_ceiling": "predictor_provenance_and_independence_review_only",
        }
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")

    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "_V1" if u2_version == "V1" else "_U2V2_V1"
    zip_path = out_dir / f"BALANCE_PLANT_PREDICTOR_ADJUDICATION_PACKET{suffix}.zip"
    receipt_path = out_dir / f"BALANCE_PLANT_PREDICTOR_ADJUDICATION_PACKET{suffix}.json"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for arcname, data in payloads:
            _zip_write_bytes(archive, arcname, data)
        _zip_write_bytes(archive, "PACKET_RECEIPT.json", receipt_bytes)
    receipt_path.write_bytes(receipt_bytes)
    return zip_path, receipt_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--u2-v2-freeze-dir",
        type=Path,
        default=None,
        help=(
            "Optional immutable U2 V2 freeze workspace. When supplied, build a "
            "versioned predictor-adjudication packet containing frozen U2 V2 "
            "receipts instead of tracked U2 V1."
        ),
    )
    args = parser.parse_args()
    print(*(
        str(path)
        for path in build_packet(
            args.out_dir,
            u2_v2_freeze_dir=args.u2_v2_freeze_dir,
        )
    ))


if __name__ == "__main__":
    main()

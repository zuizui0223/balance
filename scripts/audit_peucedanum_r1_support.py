#!/usr/bin/env python3
"""Verify source-row support and missingness before reproducing Peucedanum R1."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.peucedanum_r1_support import audit_normalized_csv  # noqa: E402


def validate_against_expectations(audit: dict, expected: dict) -> None:
    if expected.get("schema_version") != (
        "BALANCE_PEUCEDANUM_2025_R1_ROW_SUPPORT_EXPECTATIONS_V1"
    ):
        raise ValueError("source-row support expectations schema mismatch")
    keys = (
        "source_rows",
        "observed_plot_year_cells",
        "year_counts",
        "plot_counts",
        "missing_counts",
        "differential_candidate_rows",
        "gradient_candidate_rows",
        "candidate_rows_by_plot",
        "reused_year_plot_plant_id_keys",
    )
    for key in keys:
        if audit[key] != expected[key]:
            raise ValueError(f"source-row audit drift at {key}")

    nonzero = [
        {
            "year": cell["year"],
            "population_id": cell["population_id"],
            "missing_intact_fruit_count": cell["missing_intact_fruit_count"],
        }
        for cell in audit["by_year_plot"]
        if cell["missing_intact_fruit_count"]
    ]
    if nonzero != expected["special_missing_cells"]:
        raise ValueError("source-row audit drift at special_missing_cells")
    if any(
        cell["year"] == "2020" and cell["population_id"] == "HL"
        for cell in audit["by_year_plot"]
    ):
        raise ValueError("2020 HL cannot be silently filled with zero rows")


def build_receipt(
    rows_path: Path,
    normalization_receipt_path: Path,
    expectations_path: Path,
) -> dict:
    normalized_bytes = rows_path.read_bytes()
    nr = json.loads(normalization_receipt_path.read_text(encoding="utf-8"))
    expected = json.loads(expectations_path.read_text(encoding="utf-8"))
    normalized_sha256 = hashlib.sha256(normalized_bytes).hexdigest()
    receipt_sha256 = hashlib.sha256(normalization_receipt_path.read_bytes()).hexdigest()
    if normalized_sha256 != expected.get("normalized_csv_sha256"):
        raise ValueError("Peucedanum normalized CSV SHA256 differs from verified bytes")
    if receipt_sha256 != expected.get("normalization_receipt_sha256"):
        raise ValueError("Peucedanum normalization receipt SHA256 differs from verified bytes")
    if nr.get("status") != "SOURCE_VERIFIED_MAPPING_APPLIED":
        raise ValueError("R1 audit requires source-verified normalized rows")
    if nr.get("normalized_rows") != expected["source_rows"]:
        raise ValueError("normalization receipt/source-row expectation mismatch")
    source_files = nr.get("source_files", {})
    if set(source_files) != {"Kudo$Shibata_JEcol_Data.zip"}:
        raise ValueError("R1 audit source files differ from frozen 2025 archive")
    if source_files["Kudo$Shibata_JEcol_Data.zip"]["source_sha256"] != (
        expected["source_archive_sha256"]
    ):
        raise ValueError("R1 audit archive SHA256 differs from frozen source")

    audit = audit_normalized_csv(rows_path)
    validate_against_expectations(audit, expected)
    return {
        **audit,
        "status": "EXACT_2025_ROW_SUPPORT_AUDITED_PRE_MODEL",
        "normalized_file_sha256": normalized_sha256,
        "normalization_receipt_sha256": receipt_sha256,
        "source_archive_sha256": expected["source_archive_sha256"],
        "claim_ceiling": (
            "source_row_support_only_not_fitted_selection_or_BALANCE_result"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalized", type=Path, required=True)
    parser.add_argument("--normalization-receipt", type=Path, required=True)
    parser.add_argument(
        "--expectations",
        type=Path,
        default=ROOT / "empirical/peucedanum/PEUCEDANUM_2025_R1_ROW_SUPPORT_EXPECTATIONS_V1.json",
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError("R1 support audit output already exists")
    receipt = build_receipt(
        args.normalized, args.normalization_receipt, args.expectations
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=args.out.parent,
        prefix=".peucedanum-r1-support-", suffix=".tmp", delete=False,
    ) as handle:
        temp = Path(handle.name)
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write("\n")
    try:
        os.replace(temp, args.out)
    finally:
        if temp.exists():
            temp.unlink()
    print(json.dumps({
        "status": receipt["status"],
        "source_rows": receipt["source_rows"],
        "differential_candidate_rows": receipt["differential_candidate_rows"],
        "gradient_candidate_rows": receipt["gradient_candidate_rows"],
        "reused_biological_id_keys": len(receipt["reused_year_plot_plant_id_keys"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()

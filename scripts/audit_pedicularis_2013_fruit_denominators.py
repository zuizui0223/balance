#!/usr/bin/env python3
"""Reproducible original-XLSX integer denominator audit; no fruit count imputation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from balance_domain.pedicularis_2013_fruit_denominators import (
    audit_fruit_denominators,
)
from scripts.adjudicate_pedicularis_2013_raw_workbook import (
    SOURCE_BYTES, SOURCE_SHA256, SOURCE_MD5, FRUIT_SHEET,
    EXPECTED_FRUIT_HEADER, EXPECTED_COUNTS_FRUIT, _source_rows,
)


def audit_source(workbook_file: Path) -> dict:
    source = workbook_file.read_bytes()
    if (len(source) != SOURCE_BYTES
            or hashlib.sha256(source).hexdigest() != SOURCE_SHA256
            or hashlib.md5(source).hexdigest() != SOURCE_MD5):
        raise ValueError("original Dryad workbook exact source digest changed")
    # Source workbook only. artifact_tool matches existing project XLSX code.
    from artifact_tool import Blob, SpreadsheetFile
    wb = SpreadsheetFile.import_xlsx(Blob.load(str(workbook_file)))
    original = wb.worksheets.get_item(FRUIT_SHEET).get_range("A1:F77").values
    rows, counts = _source_rows(original[0], original[1:],
                                EXPECTED_FRUIT_HEADER, EXPECTED_COUNTS_FRUIT)
    result = audit_fruit_denominators(rows)
    freeze_path = (
        Path(__file__).resolve().parents[1]
        / "data/PEDICULARIS_2013_FRUIT_INTEGER_DENOMINATOR_FREEZE_V1.json"
    )
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if (freeze.get("original_workbook_sha256") != SOURCE_SHA256
            or freeze.get("biological_rows") != len(rows)
            or freeze.get("tolerance_percentage_points")
            != result["rate_tolerance_percent_points"]):
        raise ValueError("integer denominator frozen source contract differs")
    if (freeze.get("fruit_set_integer_incompatible_source_excel_rows")
            != result["fruit_set_rate_not_supported_by_integer_count_rows"]
            or freeze.get("predation_given_compatible_fruit_incompatible_source_excel_rows")
            != result["predation_not_supported_conditional_on_fruit_count_rows"]
            or freeze.get("joint_integer_chain_compatible")
            != result["joint_chain_support_rows"]
            or freeze.get("loose_stress_test_joint_integer_compatible")
            != result["loose_rounding_stress_test_joint_support_rows"]):
        raise ValueError("source denominator inconsistency positions drifted")
    for year in ("2005", "2011"):
        actual = result["counts_by_year"][year]
        expected = freeze["by_year"][year]
        if (actual.get("JOINT_INTEGER_CHAIN_COMPATIBLE_NOT_INDEPENDENTLY_VERIFIED", 0)
            != expected["joint_integer_chain_compatible"]
            or actual.get("FRUIT_SET_DENOMINATOR_NOT_INTEGER_COMPATIBLE", 0)
            != expected["fruit_set_integer_incompatible"]
            or actual.get("PREDATION_NOT_COMPATIBLE_WITH_FRUIT_SET_COUNT", 0)
            != expected["predation_given_compatible_fruit_incompatible"]):
            raise ValueError("source denominator status by year drifted")
    result["frozen_source_row_diagnostic_validated"] = True
    result["source_group_counts"] = counts
    result["original_source_bytes_sha256_verified"] = True
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError("refusing to overwrite denominator source audit")
    result = audit_source(args.workbook)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "n_source_rows": result["original_fruit_sheet_biological_rows"],
        "count_by_year": result["counts_by_year"],
        "joint_integer_chain_supported": result["joint_chain_support_rows"],
        "covariate_identified": result["published_fruit_ANCOVA_covariate_reconstructed"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

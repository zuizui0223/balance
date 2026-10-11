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

#!/usr/bin/env python3
"""Fail-closed R1 numerical audit; never promotes a coarse pattern to BALANCE occupancy."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import tempfile
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ARCHIVE_SHA256 = "07d9f718d58b795553d50c2cb2b33e9a7dd3df9e34b5c1757ed55d5674c777ca"
SOURCE_R_SHA256 = "6efb3a5b619166e0eb3ce491a67112c0009164456508093f513f4bc5c3a19d64"
EXPECTED_FIELDS = (
    "Plot", "S", "S_se", "S_fitted_n", "beta", "beta_se", "beta_fitted_n",
    "female_gain_b", "female_gain_b_se", "female_gain_fitted_n",
    "published_S", "published_beta", "published_b",
    "S_round3_match", "beta_round3_match", "b_round2_match",
)
METRICS = (
    ("S", "S_se", "S_fitted_n", "S_round3_match",
     "final_fruit_set_rate", "linear_selection_differential_S", 3),
    ("beta", "beta_se", "beta_fitted_n", "beta_round3_match",
     "final_fruit_set_rate", "linear_selection_gradient_beta", 3),
    ("female_gain_b", "female_gain_b_se", "female_gain_fitted_n", "b_round2_match",
     None, "female_gain_exponent_b", 2),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value: str, context: str) -> Decimal:
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"R1 {context} is not numeric") from exc
    if not result.is_finite():
        raise ValueError(f"R1 {context} must be finite")
    return result


def published_round(value: Decimal, digits: int) -> Decimal:
    unit = Decimal("1").scaleb(-digits)
    return value.quantize(unit, rounding=ROUND_HALF_EVEN)


def read_reproduction(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != EXPECTED_FIELDS:
            raise ValueError("R1 reproduction CSV schema mismatch")
        rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError("R1 reproduction CSV has extra columns")
    return rows


def adjudicate(
    rows: list[dict[str, str]],
    published: dict,
    support: dict,
) -> dict:
    if published.get("schema_version") != (
        "BALANCE_PEUCEDANUM_2025_PUBLISHED_SUMMARY_RECEIPT_V1"
    ):
        raise ValueError("R1 published summary receipt mismatch")
    if support.get("schema_version") != (
        "BALANCE_PEUCEDANUM_2025_R1_ROW_SUPPORT_EXPECTATIONS_V1"
    ):
        raise ValueError("R1 candidate-row source receipt mismatch")
    if support.get("source_archive_sha256") != SOURCE_ARCHIVE_SHA256:
        raise ValueError("R1 source-row receipt archive mismatch")

    ordered = published["ordered_contexts"]
    if ordered != ["HA", "HL", "HC", "KD", "HD"]:
        raise ValueError("R1 published plot order changed")
    if [row.get("Plot") for row in rows] != ordered:
        raise ValueError("R1 plotted populations missing, extra, duplicated, or re-ordered")

    comparisons: list[dict] = []
    point_matched = 0
    se_matched = 0
    fitted_counts: dict[str, dict[str, int]] = {}
    for row in rows:
        plot = row["Plot"]
        counts = support["candidate_rows_by_plot"][plot]
        fitted_counts[plot] = {}
        for point_col, se_col, n_col, flag_col, group, key, digits in METRICS:
            pub = (published[group][key][plot] if group
                   else published[key][plot])
            target_point = number(pub["estimate"], f"{plot} {key} target")
            target_se = number(pub["se"], f"{plot} {key} SE target")
            point = number(row[point_col], f"{plot} {point_col}")
            se = number(row[se_col], f"{plot} {se_col}")
            if se <= 0:
                raise ValueError(f"R1 {plot} {se_col} must be positive")
            try:
                fitted_n = int(row[n_col])
            except (ValueError, TypeError) as exc:
                raise ValueError(f"R1 {plot} {n_col} is not integer") from exc
            if str(fitted_n) != str(row[n_col]) or fitted_n <= 0:
                raise ValueError(f"R1 {plot} {n_col} has invalid integer encoding")
            expected_n = counts[
                "gradient_candidate_rows" if key == "linear_selection_gradient_beta"
                else "differential_candidate_rows"
            ]
            if fitted_n != expected_n:
                raise ValueError(f"R1 {plot} {key} fitted N differs from source support")
            fitted_counts[plot][key] = fitted_n

            point_ok = published_round(point, digits) == target_point
            se_ok = published_round(se, digits) == target_se
            # R itself reports three published-value checks: independently verify
            # those flags against the exact numeric input (not the flags' truth).
            expected_flag = "TRUE" if point_ok else "FALSE"
            if row[flag_col] != expected_flag:
                raise ValueError(f"R1 {plot} {flag_col} disagrees with numeric value")
            if number(row["published_" + point_col.replace("female_gain_b", "b")],
                      f"{plot} embedded target") != target_point:
                raise ValueError(f"R1 {plot} embedded target differs from frozen source")
            point_matched += int(point_ok)
            se_matched += int(se_ok)
            comparisons.append({
                "plot": plot,
                "metric": key,
                "estimate": str(point),
                "published_estimate": str(target_point),
                "point_residual": str(point - target_point),
                "point_matches_published_precision": point_ok,
                "se": str(se),
                "published_se": str(target_se),
                "se_residual": str(se - target_se),
                "se_matches_published_precision": se_ok,
                "published_decimals": digits,
                "actual_fitted_n": fitted_n,
            })

    if sum(r["S_fitted_n"] for r in
           [{"S_fitted_n": int(row["S_fitted_n"])} for row in rows]) != 608:
        raise ValueError("R1 global source-fit support drift")
    all_pass = point_matched == 15 and se_matched == 15
    return {
        "schema_version": "BALANCE_PEUCEDANUM_2025_R1_NUMERIC_AUDIT_V1",
        "status": (
            "NUMERICALLY_CONCORDANT_PENDING_SOURCE_MODEL_VERIFICATION" if all_pass
            else "R1_NOT_FULLY_REPRODUCED"
        ),
        "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
        "source_r_sha256": SOURCE_R_SHA256,
        "matched_point_estimates": point_matched,
        "total_point_estimates": 15,
        "matched_standard_errors": se_matched,
        "total_standard_errors": 15,
        "fitted_counts": fitted_counts,
        "comparisons": comparisons,
        "claim_ceiling": (
            "source_model_numeric_reproduction_audit_only_not_causal_"
            "architectural_tradeoff_or_direct_BALANCE_occupancy"
        ),
    }


def run(
    fit_csv: Path,
    source_archive: Path,
    original_r: Path,
    session_info: Path,
    published_path: Path,
    support_path: Path,
    output_path: Path,
) -> dict:
    if output_path.exists():
        raise ValueError("R1 numeric audit output already exists")
    if sha256(source_archive) != SOURCE_ARCHIVE_SHA256:
        raise ValueError("R1 unverified source archive bytes")
    if sha256(original_r) != SOURCE_R_SHA256:
        raise ValueError("R1 unverified source R-script bytes")
    session = session_info.read_text(encoding="utf-8")
    if "R version 4.4.2" not in session:
        raise ValueError("R1 source-environment reproduction requires R 4.4.2")
    result = adjudicate(
        read_reproduction(fit_csv),
        json.loads(published_path.read_text(encoding="utf-8")),
        json.loads(support_path.read_text(encoding="utf-8")),
    )
    result["fit_csv_sha256"] = sha256(fit_csv)
    result["session_info_sha256"] = sha256(session_info)
    result["r_version"] = "4.4.2"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=output_path.parent,
        prefix=".peucedanum-r1-", suffix=".tmp", delete=False,
    ) as handle:
        temp = Path(handle.name)
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    try:
        os.replace(temp, output_path)
    finally:
        if temp.exists():
            temp.unlink()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fit-csv", type=Path, required=True)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--original-r", type=Path, required=True)
    parser.add_argument("--session-info", type=Path, required=True)
    parser.add_argument("--published", type=Path, default=ROOT /
        "empirical/peucedanum/PEUCEDANUM_2025_PUBLISHED_SUMMARY_RECEIPT_V1.json")
    parser.add_argument("--row-support", type=Path, default=ROOT /
        "empirical/peucedanum/PEUCEDANUM_2025_R1_ROW_SUPPORT_EXPECTATIONS_V1.json")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.fit_csv, args.source_archive, args.original_r,
                 args.session_info, args.published, args.row_support, args.out)
    print(json.dumps({key: report[key] for key in
        ("status", "matched_point_estimates", "matched_standard_errors")},
        sort_keys=True))


if __name__ == "__main__":
    main()

"""Prospective U2 predictor-receipt expansion for V4 temporal generality.

This module creates and validates a new predictor-coding stage for the 12 U2 reliability
groups whose V1 predictor receipts are frozen UNRESOLVED. It is intentionally separate
from architecture coding and from predictor adjudication.

The expansion is prospective and all-or-population: every frozen unresolved U2 group and
all three predictors must be reviewed. Selective gap filling is not permitted.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .plant_confirmatory import (
    EVIDENCE_TYPES,
    FIELDS as RECEIPT_FIELDS,
    INDEPENDENCE,
    PREDICTORS,
    VALUES,
    load_plant_predictor_receipts,
)


FIELDS = (
    "receipt_id",
    "cluster_id",
    "predictor",
    "source_id",
    "reported_value",
    "evidence_type",
    "outcome_independence",
    "coding_status",
    "notes",
)

CODING_STATUS = {"UNSTARTED", "CODED", "EVIDENCE_CEILING"}
FINAL_CODING_STATUS = {"CODED", "EVIDENCE_CEILING"}
SOURCE_SIDE_EVIDENCE_TYPES = EVIDENCE_TYPES - {"OUTCOME_DERIVED", "UNCLEAR"}

IMMUTABLE_CODING_FIELDS = (
    "receipt_id",
    "cluster_id",
    "predictor",
    "source_id",
)


def load_expansion_coding(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U2 predictor expansion columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("U2 predictor expansion must contain at least one row")

    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside expansion schema")
        clean = {field: (row.get(field) or "").strip() for field in FIELDS}
        for field in FIELDS[:-1]:
            if not clean[field]:
                raise ValueError(f"row {row_number} {field} must be non-empty")

        receipt_id = clean["receipt_id"]
        if receipt_id in seen:
            raise ValueError(f"duplicate expansion receipt_id {receipt_id!r}")
        seen.add(receipt_id)

        predictor = clean["predictor"]
        if predictor not in PREDICTORS:
            raise ValueError(f"row {row_number} invalid predictor")
        if clean["reported_value"] not in VALUES[predictor]:
            raise ValueError(
                f"row {row_number} invalid value {clean['reported_value']!r} "
                f"for predictor {predictor!r}"
            )
        if clean["evidence_type"] not in EVIDENCE_TYPES:
            raise ValueError(f"row {row_number} invalid evidence_type")
        if clean["outcome_independence"] not in INDEPENDENCE:
            raise ValueError(f"row {row_number} invalid outcome_independence")
        if clean["coding_status"] not in CODING_STATUS:
            raise ValueError(f"row {row_number} invalid coding_status")
        out.append(clean)

    groups = sorted({row["cluster_id"] for row in out})
    if len(groups) != 12:
        raise ValueError("U2 predictor expansion must contain exactly 12 frozen groups")
    if len(out) != 36:
        raise ValueError("U2 predictor expansion must contain exactly 36 predictor slots")
    for group in groups:
        predictors = {
            row["predictor"] for row in out if row["cluster_id"] == group
        }
        if predictors != set(PREDICTORS):
            raise ValueError(
                f"U2 predictor expansion group {group!r} must contain all three predictors"
            )
    return out


def validate_expansion_template(
    rows: Iterable[dict[str, str]],
) -> list[dict[str, str]]:
    rows = [dict(row) for row in rows]
    if any(row["coding_status"] != "UNSTARTED" for row in rows):
        raise ValueError("frozen expansion template must be entirely UNSTARTED")
    for row in rows:
        if row["reported_value"] != "UNRESOLVED":
            raise ValueError("frozen expansion template values must be UNRESOLVED")
        if row["evidence_type"] != "UNCLEAR":
            raise ValueError("frozen expansion template evidence_type must be UNCLEAR")
        if row["outcome_independence"] != "UNCERTAIN":
            raise ValueError(
                "frozen expansion template outcome_independence must be UNCERTAIN"
            )
    return rows


def validate_expansion_return(
    frozen_rows: list[dict[str, str]],
    returned_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Validate one complete outcome-blind predictor-coding return.

    CODED rows must be fully resolved using source-side evidence and must explicitly
    certify outcome_independence=TRUE. If the source cannot support all of those
    requirements, the coder must use EVIDENCE_CEILING and leave reported_value
    UNRESOLVED. No slot may remain UNSTARTED.
    """
    frozen = {row["receipt_id"]: row for row in frozen_rows}
    returned = {row["receipt_id"]: row for row in returned_rows}
    if len(frozen) != len(frozen_rows) or len(returned) != len(returned_rows):
        raise ValueError("U2 predictor expansion contains duplicate receipt_id")
    if set(returned) != set(frozen):
        raise ValueError(
            "U2 predictor expansion return IDs must exactly match the frozen template"
        )

    out = []
    for receipt_id in sorted(frozen):
        before = frozen[receipt_id]
        after = returned[receipt_id]

        for field in IMMUTABLE_CODING_FIELDS:
            if after[field] != before[field]:
                raise ValueError(
                    f"U2 predictor expansion {receipt_id!r} cannot modify frozen {field}"
                )

        if after["coding_status"] not in FINAL_CODING_STATUS:
            raise ValueError(
                f"U2 predictor expansion {receipt_id!r} must end CODED or EVIDENCE_CEILING"
            )

        if after["coding_status"] == "CODED":
            if after["reported_value"] == "UNRESOLVED":
                raise ValueError(
                    f"U2 predictor expansion {receipt_id!r} CODED requires resolved value"
                )
            if after["evidence_type"] not in SOURCE_SIDE_EVIDENCE_TYPES:
                raise ValueError(
                    f"U2 predictor expansion {receipt_id!r} CODED requires source-side evidence"
                )
            if after["outcome_independence"] != "TRUE":
                raise ValueError(
                    f"U2 predictor expansion {receipt_id!r} CODED requires "
                    "outcome_independence=TRUE"
                )
            if not after["notes"] or after["notes"] == before["notes"]:
                raise ValueError(
                    f"U2 predictor expansion {receipt_id!r} CODED requires "
                    "coder-specific source-basis notes"
                )
        else:
            if after["reported_value"] != "UNRESOLVED":
                raise ValueError(
                    f"U2 predictor expansion {receipt_id!r} EVIDENCE_CEILING must "
                    "remain UNRESOLVED"
                )
            if not after["notes"] or after["notes"] == before["notes"]:
                raise ValueError(
                    f"U2 predictor expansion {receipt_id!r} EVIDENCE_CEILING requires "
                    "coder-specific ceiling notes"
                )

        out.append(after)

    if len({row["cluster_id"] for row in out}) != 12 or len(out) != 36:
        raise ValueError("U2 predictor expansion return must preserve all 12 groups / 36 slots")
    return out


def load_expansion_return(
    returned_path: Path,
    frozen_template_path: Path,
) -> list[dict[str, str]]:
    frozen = validate_expansion_template(load_expansion_coding(frozen_template_path))
    returned = load_expansion_coding(returned_path)
    return validate_expansion_return(frozen, returned)


def build_v2_predictor_receipts(
    *,
    v1_rows: list[dict[str, str]],
    expansion_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Freeze the V2 receipt frame after expansion coding, before adjudication."""
    expansion = {row["receipt_id"]: row for row in expansion_rows}
    unresolved_v1 = {
        row["receipt_id"]
        for row in v1_rows
        if row["reported_value"] == "UNRESOLVED"
    }
    if set(expansion) != unresolved_v1:
        raise ValueError(
            "U2 V2 receipt freeze requires expansion rows for every and only V1 unresolved slot"
        )

    out = []
    for row in v1_rows:
        clean = dict(row)
        if row["receipt_id"] in expansion:
            coded = expansion[row["receipt_id"]]
            if coded["coding_status"] == "CODED":
                clean["reported_value"] = coded["reported_value"]
                clean["evidence_type"] = coded["evidence_type"]
                clean["outcome_independence"] = coded["outcome_independence"]
                clean["notes"] = (
                    "V2_PROSPECTIVE_EXPANSION_CODING: " + coded["notes"]
                ).strip()
            else:
                clean["reported_value"] = "UNRESOLVED"
                clean["evidence_type"] = "UNCLEAR"
                clean["outcome_independence"] = "UNCERTAIN"
                clean["notes"] = (
                    "V2_EXPANSION_EVIDENCE_CEILING: " + coded["notes"]
                ).strip()
            clean["adjudication_status"] = "SCREENED"
        out.append(clean)

    # Reuse the canonical receipt loader's field/value semantics by writing only
    # canonical receipt fields downstream.
    if any(set(row) != set(RECEIPT_FIELDS) for row in out):
        raise ValueError("U2 V2 receipt freeze drifted from canonical receipt schema")
    return out


def write_v2_predictor_receipts(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RECEIPT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_v2_from_files(
    *,
    v1_receipts_path: Path,
    frozen_template_path: Path,
    returned_expansion_path: Path,
) -> list[dict[str, str]]:
    v1 = load_plant_predictor_receipts(v1_receipts_path)
    expansion = load_expansion_return(returned_expansion_path, frozen_template_path)
    return build_v2_predictor_receipts(v1_rows=v1, expansion_rows=expansion)

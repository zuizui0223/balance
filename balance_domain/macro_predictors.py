"""Outcome-independent predictor receipts for the BALANCE macro programme."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Iterable


FIELDS = (
    "receipt_id",
    "cluster_id",
    "predictor",
    "reported_value",
    "source_id",
    "evidence_type",
    "outcome_independence",
    "adjudication_status",
    "notes",
)

PREDICTORS = {
    "alternative_accessibility",
    "functional_coupling",
    "temporal_heterogeneity",
    "spatial_heterogeneity",
    "alternative_repertoire",
    "conflict_strength_proxy",
}

VALUES = {
    "alternative_accessibility": {"LOW", "MEDIUM", "HIGH", "UNRESOLVED", "NA"},
    "functional_coupling": {"LOW", "MEDIUM", "HIGH", "UNRESOLVED", "NA"},
    "temporal_heterogeneity": {"LOW", "MEDIUM", "HIGH", "UNRESOLVED", "NA"},
    "spatial_heterogeneity": {"LOW", "MEDIUM", "HIGH", "UNRESOLVED", "NA"},
    "alternative_repertoire": {"NONE", "ONE", "MULTIPLE", "UNRESOLVED", "NA"},
    "conflict_strength_proxy": {"LOW", "MEDIUM", "HIGH", "UNRESOLVED", "NA"},
}

EVIDENCE_TYPES = {
    "PRE_OUTCOME_MEASUREMENT",
    "INTEGRATED_STATE_EXPERIMENT",
    "ANCESTRAL_RECONSTRUCTION",
    "SISTER_LINEAGE_COMPARATOR",
    "EXPERIMENTAL_ALTERNATIVE_GENERATION",
    "DEVELOPMENTAL_MECHANISM",
    "OUTCOME_DERIVED",
    "UNCLEAR",
}

INDEPENDENCE = {"TRUE", "FALSE", "UNCERTAIN"}
ADJUDICATION = {"SCREENED", "ADJUDICATED", "REJECTED"}

_MISSING = {"", "none", "null", "nan", "required_before_use"}


def _text(value: object, field: str, row_number: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"row {row_number} {field} must be a string")
    value = value.strip()
    if value.casefold() in _MISSING:
        raise ValueError(f"row {row_number} {field} must be frozen")
    return value


def load_predictor_receipts(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        if fields != FIELDS:
            raise ValueError("predictor receipt columns must match the canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("predictor receipt ledger must contain at least one receipt")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside the receipt schema")
        clean = dict(row)
        for field in ("receipt_id", "cluster_id", "predictor", "reported_value", "source_id",
                      "evidence_type", "outcome_independence", "adjudication_status"):
            clean[field] = _text(row.get(field), field, row_number)

        if clean["receipt_id"] in seen:
            raise ValueError(f"duplicate receipt_id {clean['receipt_id']!r}")
        seen.add(clean["receipt_id"])

        predictor = clean["predictor"]
        if predictor not in PREDICTORS:
            raise ValueError(f"row {row_number} unknown predictor {predictor!r}")
        if clean["reported_value"] not in VALUES[predictor]:
            raise ValueError(
                f"row {row_number} invalid value {clean['reported_value']!r} for {predictor}"
            )
        if clean["evidence_type"] not in EVIDENCE_TYPES:
            raise ValueError(f"row {row_number} invalid evidence_type")
        if clean["outcome_independence"] not in INDEPENDENCE:
            raise ValueError(f"row {row_number} invalid outcome_independence")
        if clean["adjudication_status"] not in ADJUDICATION:
            raise ValueError(f"row {row_number} invalid adjudication_status")

        if (
            clean["evidence_type"] == "OUTCOME_DERIVED"
            and clean["outcome_independence"] != "FALSE"
        ):
            raise ValueError(
                f"row {row_number} OUTCOME_DERIVED evidence must be marked outcome_independence=FALSE"
            )

        clean["notes"] = (row.get("notes") or "").strip()
        out.append(clean)
    return out


def adjudicated_independent_values(
    receipts: Iterable[dict[str, str]],
) -> dict[tuple[str, str], str]:
    """Return cluster/predictor values only when independent adjudicated receipts agree."""
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for receipt in receipts:
        grouped[(receipt["cluster_id"], receipt["predictor"])].append(receipt)

    out: dict[tuple[str, str], str] = {}
    for key, group in grouped.items():
        valid = [
            r
            for r in group
            if r["adjudication_status"] == "ADJUDICATED"
            and r["outcome_independence"] == "TRUE"
        ]
        if not valid:
            continue
        values = {r["reported_value"] for r in valid}
        if len(values) != 1:
            cluster_id, predictor = key
            raise ValueError(
                "conflicting independent adjudicated predictor receipts for "
                f"{cluster_id!r} / {predictor!r}: {sorted(values)}"
            )
        out[key] = next(iter(values))
    return out


def confirmatory_h1_h2_clusters(
    macro_rows: Iterable[dict[str, str]],
    receipts: Iterable[dict[str, str]],
) -> list[str]:
    """Return clusters passing outcome and non-circular H1/H2 predictor gates."""
    values = adjudicated_independent_values(receipts)
    accepted: list[str] = []

    for row in macro_rows:
        if row["adjudication_status"] != "ADJUDICATED":
            continue
        if row["multifunctionality_status"] != "YES":
            continue
        if row["conflict_status"] != "POSITIVE":
            continue
        if row["structural_differentiation"] not in {"true", "false"}:
            continue

        cluster_id = row["cluster_id"]
        ok = True
        for predictor in ("alternative_accessibility", "functional_coupling"):
            receipt_value = values.get((cluster_id, predictor))
            if receipt_value is None or receipt_value in {"UNRESOLVED", "NA"}:
                ok = False
                break
            if row[predictor] != receipt_value:
                raise ValueError(
                    f"macro ledger and independent receipt disagree for "
                    f"{cluster_id!r} / {predictor!r}: "
                    f"{row[predictor]!r} != {receipt_value!r}"
                )
        if ok:
            accepted.append(cluster_id)

    return sorted(accepted)

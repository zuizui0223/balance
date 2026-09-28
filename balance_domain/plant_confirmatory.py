"""Confirmatory gates for the BALANCE flowering-plant macro programme.

The confirmatory plant model uses three predictors that must be licensed by
outcome-independent source receipts: module substrate, conflict timing geometry,
and conflict spatial geometry. The architecture response is kept separate from
those predictor receipts.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .plant_macro import MODULE_SUBSTRATE, SPATIAL, TIMING, primary_architecture_class


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

PREDICTORS = (
    "module_substrate",
    "conflict_timing_geometry",
    "conflict_spatial_geometry",
)

VALUES = {
    "module_substrate": MODULE_SUBSTRATE,
    "conflict_timing_geometry": TIMING,
    "conflict_spatial_geometry": SPATIAL,
}

EVIDENCE_TYPES = {
    "PRE_OUTCOME_MEASUREMENT",
    "INTEGRATED_STATE_EXPERIMENT",
    "INTEGRATED_STATE_DESCRIPTION",
    "DEVELOPMENTAL_MECHANISM",
    "ANCESTRAL_RECONSTRUCTION",
    "SISTER_LINEAGE_COMPARATOR",
    "OUTCOME_DERIVED",
    "UNCLEAR",
}

INDEPENDENCE = {"TRUE", "FALSE", "UNCERTAIN"}
ADJUDICATION = {"SCREENED", "ADJUDICATED", "REJECTED"}
_MISSING = {"", "none", "null", "nan", "required_before_use"}


def _text(value: object, field: str, row_number: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"row {row_number} {field} must be a string")
    out = value.strip()
    if out.casefold() in _MISSING:
        raise ValueError(f"row {row_number} {field} must be frozen")
    return out


def load_plant_predictor_receipts(path: Path) -> list[dict[str, str]]:
    """Load predictor evidence without allowing the focal architecture outcome to license it."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("plant predictor receipt columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("plant predictor receipt ledger must contain at least one receipt")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside canonical schema")
        clean = dict(row)
        for field in FIELDS[:-1]:
            clean[field] = _text(row.get(field), field, row_number)

        if clean["receipt_id"] in seen:
            raise ValueError(f"duplicate receipt_id {clean['receipt_id']!r}")
        seen.add(clean["receipt_id"])

        predictor = clean["predictor"]
        if predictor not in PREDICTORS:
            raise ValueError(f"row {row_number} unknown plant predictor {predictor!r}")
        if clean["reported_value"] not in VALUES[predictor]:
            raise ValueError(
                f"row {row_number} invalid value {clean['reported_value']!r} "
                f"for {predictor}"
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
                f"row {row_number} OUTCOME_DERIVED evidence must have "
                "outcome_independence=FALSE"
            )

        clean["notes"] = (row.get("notes") or "").strip()
        out.append(clean)

    return out


def adjudicated_independent_plant_values(
    receipts: Iterable[dict[str, str]],
) -> dict[tuple[str, str], str]:
    """Return one licensed value per cluster/predictor, failing on disagreement."""
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
                "conflicting independent adjudicated plant predictor receipts for "
                f"{cluster_id!r} / {predictor!r}: {sorted(values)}"
            )
        value = next(iter(values))
        if value == "UNRESOLVED":
            continue
        out[key] = value
    return out


def licensed_primary_clusters(
    macro_rows: Iterable[dict[str, str]],
    receipts: Iterable[dict[str, str]],
) -> list[str]:
    """Return declared primary rows that pass the independent-predictor receipt gate.

    A row declaring primary_model_eligible=true asserts that all confirmatory
    gates are closed. It fails closed if any required predictor receipt is absent,
    unresolved, outcome-derived, conflicting, or inconsistent with the macro ledger.
    """
    values = adjudicated_independent_plant_values(receipts)
    accepted: list[str] = []

    for row in macro_rows:
        if row["primary_model_eligible"] != "true":
            continue

        cluster_id = row["cluster_id"]
        if row["adjudication_status"] != "ADJUDICATED":
            raise ValueError(f"{cluster_id!r} primary row is not ADJUDICATED")
        if row["unit_type"] not in {"SPECIES", "SPECIES_CONTEXT"}:
            raise ValueError(f"{cluster_id!r} primary row is not species-level")
        if row["conflict_status"] != "POSITIVE":
            raise ValueError(f"{cluster_id!r} primary row is not conflict-positive")
        primary_architecture_class(row["architecture_mode"])

        for predictor in PREDICTORS:
            receipt_value = values.get((cluster_id, predictor))
            if receipt_value is None:
                raise ValueError(
                    f"{cluster_id!r} lacks an independent adjudicated receipt "
                    f"for {predictor}"
                )
            if row[predictor] != receipt_value:
                raise ValueError(
                    "plant macro ledger and independent receipt disagree for "
                    f"{cluster_id!r} / {predictor!r}: "
                    f"{row[predictor]!r} != {receipt_value!r}"
                )

        accepted.append(cluster_id)

    return sorted(accepted)


def build_confirmatory_gate_report(
    macro_rows: Iterable[dict[str, str]],
    receipts: Iterable[dict[str, str]],
) -> dict:
    """Build an inspectable readout for the pre-model confirmatory gate."""
    rows = list(macro_rows)
    licensed = licensed_primary_clusters(rows, receipts)
    return {
        "analysis": "balance_plant_confirmatory_predictor_gate",
        "primary_response": "architecture_class4",
        "primary_classes": [
            "SHARED",
            "NONSTRUCTURAL_SEPARATION",
            "STRUCTURAL_MODULE_DIVISION",
            "MOSAIC",
        ],
        "required_predictors": list(PREDICTORS),
        "declared_primary_rows": sum(
            row["primary_model_eligible"] == "true" for row in rows
        ),
        "licensed_primary_clusters": licensed,
        "n_licensed_primary_clusters": len(licensed),
        "claim_ceiling": (
            "predictor_independence_and_model_entry_only_not_causal_identification"
        ),
    }



def build_receipt_screening_coverage(
    receipts: Iterable[dict[str, str]],
) -> dict:
    """Summarize predictor-screening progress without promoting SCREENED values."""
    rows = list(receipts)
    by_predictor = {}
    for predictor in PREDICTORS:
        subset = [r for r in rows if r["predictor"] == predictor]
        by_predictor[predictor] = {
            "n_receipts": len(subset),
            "n_resolved": sum(r["reported_value"] != "UNRESOLVED" for r in subset),
            "n_outcome_independent_resolved": sum(
                r["reported_value"] != "UNRESOLVED"
                and r["outcome_independence"] == "TRUE"
                for r in subset
            ),
            "n_adjudicated_independent_resolved": sum(
                r["reported_value"] != "UNRESOLVED"
                and r["outcome_independence"] == "TRUE"
                and r["adjudication_status"] == "ADJUDICATED"
                for r in subset
            ),
        }

    grouped: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        grouped[row["cluster_id"]][row["predictor"]] = row

    def _complete(group: dict[str, dict[str, str]], *, adjudicated: bool) -> bool:
        for predictor in PREDICTORS:
            row = group.get(predictor)
            if row is None:
                return False
            if row["reported_value"] == "UNRESOLVED":
                return False
            if row["outcome_independence"] != "TRUE":
                return False
            if adjudicated and row["adjudication_status"] != "ADJUDICATED":
                return False
        return True

    complete_screened = sorted(
        cluster_id
        for cluster_id, group in grouped.items()
        if _complete(group, adjudicated=False)
    )
    complete_adjudicated = sorted(
        cluster_id
        for cluster_id, group in grouped.items()
        if _complete(group, adjudicated=True)
    )

    return {
        "analysis": "balance_plant_predictor_receipt_screening_coverage",
        "n_receipts": len(rows),
        "n_clusters": len(grouped),
        "by_predictor": by_predictor,
        "complete_outcome_independent_clusters": complete_screened,
        "complete_adjudicated_clusters": complete_adjudicated,
        "n_complete_outcome_independent_clusters": len(complete_screened),
        "n_complete_adjudicated_clusters": len(complete_adjudicated),
        "promotion_rule": "SCREENED values do not license confirmatory model entry",
    }

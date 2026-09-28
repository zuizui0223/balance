"""Blinded reconstruction contract for the BALANCE U6 pollen-theft universe."""
from __future__ import annotations

import csv
import json
from pathlib import Path


FIELDS = (
    "reference_id",
    "reference_citation",
    "reference_year",
    "reference_type_status",
    "plant_taxon_raw",
    "dependency_group",
    "primary_source_status",
    "inclusion_status",
    "exclusion_reason",
    "classification_basis",
    "notes",
)

FORBIDDEN_PASS1_FIELDS = {
    "architecture_mode",
    "heteranthery_status",
    "dichogamy_status",
    "herkogamy_status",
    "poricidal_anther_status",
    "module_substrate",
    "conflict_timing_geometry",
    "conflict_spatial_geometry",
}

REFERENCE_STATUS = {
    "EMPIRICAL_POLLEN_THEFT_CANDIDATE",
    "EMPIRICAL_BUT_NOT_POLLEN_THEFT",
    "REVIEW_OR_THEORY",
    "NONPLANT_OR_METHODS",
    "UNRESOLVED",
}
INCLUSION_STATUS = {"INCLUDE", "EXCLUDE", "UNRESOLVED"}
PRIMARY_SOURCE_STATUS = {"RESOLVED", "UNRESOLVED", "NOT_REQUIRED"}


def load_u6_anchor(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "BALANCE_PLANT_U6_REVIEW_ANCHOR_V1":
        raise ValueError("U6 anchor schema mismatch")
    forbidden = set(data.get("forbidden_during_pass1", []))
    if forbidden != FORBIDDEN_PASS1_FIELDS:
        raise ValueError("U6 Pass-1 forbidden-field contract drifted")
    if data.get("primary_model_admission") != (
        "FORBIDDEN_UNTIL_PASS2_INDEPENDENT_CODING_AND_DEPENDENCE_AUDIT"
    ):
        raise ValueError("U6 primary-model admission must remain closed")
    return data


def load_u6_reference_classification(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        if fields != FIELDS:
            extras = set(fields) & FORBIDDEN_PASS1_FIELDS
            if extras:
                raise ValueError(
                    f"U6 Pass-1 classification contains forbidden architecture fields: {sorted(extras)}"
                )
            raise ValueError("U6 reference classification columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("U6 reference classification must contain at least one row")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside canonical schema")
        clean = {key: (row.get(key) or "").strip() for key in FIELDS}
        if not clean["reference_id"] or not clean["reference_citation"]:
            raise ValueError(f"row {row_number} reference identity must be non-empty")
        if clean["reference_id"] in seen:
            raise ValueError(f"duplicate U6 reference_id {clean['reference_id']!r}")
        seen.add(clean["reference_id"])

        if clean["reference_type_status"] not in REFERENCE_STATUS:
            raise ValueError(f"row {row_number} invalid reference_type_status")
        if clean["primary_source_status"] not in PRIMARY_SOURCE_STATUS:
            raise ValueError(f"row {row_number} invalid primary_source_status")
        if clean["inclusion_status"] not in INCLUSION_STATUS:
            raise ValueError(f"row {row_number} invalid inclusion_status")
        if clean["classification_basis"] != "ANCHOR_REVIEW_REFERENCE_CLASSIFICATION":
            raise ValueError(f"row {row_number} invalid classification_basis")
        out.append(clean)
    return out

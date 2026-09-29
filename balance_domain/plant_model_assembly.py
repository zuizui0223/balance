"""Final model-assembly contract for BALANCE plant confirmatory analysis v4."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Iterable

from .plant_confirmatory import primary_contrast_row
from .plant_macro import (
    CONFLICT_FAMILIES,
    MODULE_SUBSTRATE,
    RESOLUTION,
    SPATIAL,
    TIMING,
    primary_architecture_class,
)
from .plant_model_v4 import build_v4_estimability_report


FIELDS = (
    "analysis_row_id",
    "universe_id",
    "dependency_group",
    "dependence_block",
    "system_taxon",
    "conflict_family",
    "conflict_receipt_status",
    "architecture_mode",
    "module_substrate",
    "conflict_timing_geometry",
    "conflict_spatial_geometry",
    "architecture_adjudication_status",
    "predictor_receipt_status",
    "source_basis",
    "claim_ceiling",
)

PRIMARY_UNIVERSES = {
    "U2_BARRETT_2002",
    "U6_POLLEN_THEFT_HARGREAVES_2009",
}

CONFLICT_RECEIPT_STATUS = {"ADJUDICATED_POSITIVE"}
ARCHITECTURE_ADJUDICATION_STATUS = {"ADJUDICATED"}
PREDICTOR_RECEIPT_STATUS = {"THREE_ADJUDICATED_OUTCOME_INDEPENDENT"}


def validate_model_assembly_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    """Validate fully licensed rows before any v4 estimability/model fit."""
    rows = [dict(row) for row in rows]
    if not rows:
        raise ValueError("plant confirmatory assembly requires at least one row")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        clean = {field: (row.get(field) or "").strip() for field in FIELDS}
        for field, value in clean.items():
            if not value:
                raise ValueError(f"row {row_number} {field} must be non-empty")

        row_id = clean["analysis_row_id"]
        if row_id in seen:
            raise ValueError(f"duplicate analysis_row_id {row_id!r}")
        seen.add(row_id)

        if clean["universe_id"] not in PRIMARY_UNIVERSES:
            raise ValueError(
                f"row {row_number} universe {clean['universe_id']!r} is not licensed "
                "for the primary confirmatory denominator"
            )
        if clean["conflict_family"] not in CONFLICT_FAMILIES - {"UNRESOLVED"}:
            raise ValueError(f"row {row_number} invalid conflict_family")
        if clean["conflict_receipt_status"] not in CONFLICT_RECEIPT_STATUS:
            raise ValueError(f"row {row_number} requires adjudicated positive conflict")
        if clean["architecture_mode"] not in RESOLUTION - {"UNRESOLVED", "NA"}:
            raise ValueError(f"row {row_number} requires resolved architecture_mode")
        if clean["module_substrate"] not in MODULE_SUBSTRATE - {"UNRESOLVED"}:
            raise ValueError(f"row {row_number} requires resolved module_substrate")
        if clean["conflict_timing_geometry"] not in TIMING - {"UNRESOLVED"}:
            raise ValueError(f"row {row_number} requires resolved conflict_timing_geometry")
        if clean["conflict_spatial_geometry"] not in SPATIAL - {"UNRESOLVED"}:
            raise ValueError(f"row {row_number} requires resolved conflict_spatial_geometry")
        if (
            clean["architecture_adjudication_status"]
            not in ARCHITECTURE_ADJUDICATION_STATUS
        ):
            raise ValueError(f"row {row_number} architecture is not adjudicated")
        if clean["predictor_receipt_status"] not in PREDICTOR_RECEIPT_STATUS:
            raise ValueError(
                f"row {row_number} lacks three adjudicated outcome-independent predictors"
            )

        # Force every raw value through the frozen v4 mappings before admission.
        primary_architecture_class(clean["architecture_mode"])
        primary_contrast_row(clean)
        out.append(clean)

    return out


def load_model_assembly(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("plant confirmatory assembly columns must match canonical order")
        return validate_model_assembly_rows(reader)


def build_model_assembly_readout(rows: Iterable[dict[str, str]]) -> dict:
    """Summarize licensed rows and run the frozen v4 estimability gate."""
    rows = validate_model_assembly_rows(rows)
    fit_rows = []
    for row in rows:
        fit_row = dict(row)
        fit_row.update(primary_contrast_row(row))
        fit_rows.append(fit_row)

    estimability = build_v4_estimability_report(fit_rows)
    return {
        "analysis": "balance_plant_confirmatory_model_assembly_v4",
        "n_rows": len(rows),
        "n_dependency_groups": len({row["dependency_group"] for row in rows}),
        "n_dependence_blocks": len({row["dependence_block"] for row in rows}),
        "universe_counts": dict(sorted(Counter(row["universe_id"] for row in rows).items())),
        "conflict_family_counts": dict(
            sorted(Counter(row["conflict_family"] for row in rows).items())
        ),
        "architecture_class_counts": dict(
            sorted(Counter(primary_architecture_class(row["architecture_mode"]) for row in rows).items())
        ),
        "v4_estimability": estimability,
        "ready_for_primary_fit": estimability["ready_for_primary_fit"],
        "u3_u4_primary_denominator_allowed": False,
        "claim_ceiling": (
            "licensed_model_assembly_and_estimability_only_not_fitted_effect_or_causality"
        ),
    }

"""Plant-specific comparative-macro schema for BALANCE."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "cluster_id",
    "dependency_group",
    "sampling_frame_id",
    "unit_type",
    "source_id",
    "publication_year",
    "system_taxon",
    "conflict_family",
    "shared_structure",
    "function_a",
    "function_b",
    "conflict_status",
    "architecture_mode",
    "structural_module_division",
    "module_substrate",
    "conflict_timing_geometry",
    "conflict_spatial_geometry",
    "self_compatibility",
    "autonomous_selfing",
    "pollinator_dependence",
    "life_history",
    "study_design",
    "evidence_quality",
    "adjudication_status",
    "primary_model_eligible",
    "exclusion_reason",
    "source_basis",
    "claim_ceiling",
    "notes",
)

UNIT_TYPES = {"SPECIES", "SPECIES_CONTEXT", "COMPARATIVE_CLADE", "REVIEW_ONLY"}
CONFLICT_FAMILIES = {
    "POLLINATOR_ANTAGONIST",
    "SEXUAL_INTERFERENCE",
    "POLLEN_REWARD_GAMETE",
    "POLLINATOR_PREY",
    "POLLINATION_ABIOTIC",
    "OTHER",
    "UNRESOLVED",
}
CONFLICT = {
    "POSITIVE",
    "ALIGNED_NO_CONFLICT",
    "NO_DEMONSTRATED_CONFLICT",
    "UNRESOLVED",
}
RESOLUTION = {
    "SHARED_INTEGRATED",
    "TEMPORAL_SEPARATION",
    "SPATIAL_SEPARATION",
    "TEMPORAL_AND_SPATIAL_SEPARATION",
    "WITHIN_FLOWER_DIVISION_OF_LABOUR",
    "AMONG_FLOWER_MODULE_DIVISION",
    "POLYMORPHIC_OR_MOSAIC",
    "UNRESOLVED",
    "NA",
}
STRUCTURAL = {"true", "false", "unresolved", "na"}
STRUCTURAL_TRUE = {
    "WITHIN_FLOWER_DIVISION_OF_LABOUR",
    "AMONG_FLOWER_MODULE_DIVISION",
}
STRUCTURAL_FALSE = {
    "SHARED_INTEGRATED",
    "TEMPORAL_SEPARATION",
    "SPATIAL_SEPARATION",
    "TEMPORAL_AND_SPATIAL_SEPARATION",
}
MODULE_SUBSTRATE = {
    "SINGLE_OR_CONTINUOUS",
    "SERIAL_WITHIN_FLOWER",
    "REPEATED_FLOWERS",
    "PREEXISTING_SEPARATE_ORGANS",
    "MULTILEVEL",
    "UNRESOLVED",
}
TIMING = {
    "SIMULTANEOUS",
    "SEQUENTIAL_WITHIN_UNIT",
    "SEASONALLY_ALTERNATING",
    "CONTEXT_DEPENDENT",
    "MIXED",
    "UNRESOLVED",
}
SPATIAL = {
    "SAME_UNIT",
    "BETWEEN_MODULES",
    "AMONG_INDIVIDUALS",
    "AMONG_POPULATIONS",
    "ENVIRONMENTAL_MOSAIC",
    "MIXED",
    "UNRESOLVED",
}
SELF_COMPAT = {"SELF_COMPATIBLE", "SELF_INCOMPATIBLE", "MIXED", "UNRESOLVED"}
AUTO_SELF = {"ABSENT_OR_LOW", "PRESENT", "MIXED", "UNRESOLVED"}
POLLINATOR_DEP = {"LOW", "MEDIUM", "HIGH", "UNRESOLVED"}
LIFE_HISTORY = {"ANNUAL", "BIENNIAL", "PERENNIAL", "MIXED", "UNRESOLVED"}
EVIDENCE = {"HIGH", "MODERATE", "LOW", "UNREVIEWED"}
ADJUDICATION = {"UNSCREENED", "SCREENED", "ADJUDICATED", "EXCLUDED"}

_MISSING = {"", "none", "null", "nan", "required_before_use"}


def _text(value: object, field: str, row_number: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"row {row_number} {field} must be a string")
    text = value.strip()
    if text.casefold() in _MISSING:
        raise ValueError(f"row {row_number} {field} must be frozen")
    return text


def _cat(value: object, field: str, allowed: set[str], row_number: int, *, fold=False) -> str:
    text = _text(value, field, row_number)
    if fold:
        text = text.casefold()
    if text not in allowed:
        raise ValueError(f"row {row_number} invalid {field} {text!r}")
    return text


def _year(value: object, row_number: int) -> str:
    text = _text(value, "publication_year", row_number)
    if text == "UNRESOLVED":
        return text
    try:
        year = int(text)
    except ValueError as exc:
        raise ValueError(
            f"row {row_number} publication_year must be integer or UNRESOLVED"
        ) from exc
    if not 1800 <= year <= 2100:
        raise ValueError(f"row {row_number} publication_year out of range")
    return str(year)


def _validated_rows(reader: csv.DictReader) -> list[dict[str, str]]:
    rows = list(reader)
    if not rows:
        raise ValueError("plant macro ledger must contain at least one screened record")

    seen: set[str] = set()
    out: list[dict[str, str]] = []

    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside canonical schema")
        clean = dict(row)

        for field in (
            "cluster_id",
            "dependency_group",
            "sampling_frame_id",
            "source_id",
            "system_taxon",
            "shared_structure",
            "function_a",
            "function_b",
            "study_design",
            "source_basis",
            "claim_ceiling",
        ):
            clean[field] = _text(row.get(field), field, row_number)

        if clean["cluster_id"] in seen:
            raise ValueError(f"duplicate cluster_id {clean['cluster_id']!r}")
        seen.add(clean["cluster_id"])

        if clean["function_a"].casefold() == clean["function_b"].casefold():
            raise ValueError(f"row {row_number} function_a and function_b must differ")

        clean["publication_year"] = _year(row.get("publication_year"), row_number)
        clean["unit_type"] = _cat(row.get("unit_type"), "unit_type", UNIT_TYPES, row_number)
        clean["conflict_family"] = _cat(
            row.get("conflict_family"), "conflict_family", CONFLICT_FAMILIES, row_number
        )
        clean["conflict_status"] = _cat(
            row.get("conflict_status"), "conflict_status", CONFLICT, row_number
        )
        clean["architecture_mode"] = _cat(
            row.get("architecture_mode"), "architecture_mode", RESOLUTION, row_number
        )
        clean["structural_module_division"] = _cat(
            row.get("structural_module_division"),
            "structural_module_division",
            STRUCTURAL,
            row_number,
            fold=True,
        )
        clean["module_substrate"] = _cat(
            row.get("module_substrate"), "module_substrate", MODULE_SUBSTRATE, row_number
        )
        clean["conflict_timing_geometry"] = _cat(
            row.get("conflict_timing_geometry"),
            "conflict_timing_geometry",
            TIMING,
            row_number,
        )
        clean["conflict_spatial_geometry"] = _cat(
            row.get("conflict_spatial_geometry"),
            "conflict_spatial_geometry",
            SPATIAL,
            row_number,
        )
        clean["self_compatibility"] = _cat(
            row.get("self_compatibility"), "self_compatibility", SELF_COMPAT, row_number
        )
        clean["autonomous_selfing"] = _cat(
            row.get("autonomous_selfing"), "autonomous_selfing", AUTO_SELF, row_number
        )
        clean["pollinator_dependence"] = _cat(
            row.get("pollinator_dependence"),
            "pollinator_dependence",
            POLLINATOR_DEP,
            row_number,
        )
        clean["life_history"] = _cat(
            row.get("life_history"), "life_history", LIFE_HISTORY, row_number
        )
        clean["evidence_quality"] = _cat(
            row.get("evidence_quality"), "evidence_quality", EVIDENCE, row_number
        )
        clean["adjudication_status"] = _cat(
            row.get("adjudication_status"), "adjudication_status", ADJUDICATION, row_number
        )
        clean["primary_model_eligible"] = _cat(
            row.get("primary_model_eligible"),
            "primary_model_eligible",
            {"true", "false"},
            row_number,
            fold=True,
        )

        mode = clean["architecture_mode"]
        structural = clean["structural_module_division"]
        if mode in STRUCTURAL_TRUE and structural != "true":
            raise ValueError(
                f"row {row_number} structural_module_division must be true for {mode}"
            )
        if mode in STRUCTURAL_FALSE and structural != "false":
            raise ValueError(
                f"row {row_number} structural_module_division must be false for {mode}"
            )
        if mode in {"POLYMORPHIC_OR_MOSAIC", "UNRESOLVED"} and structural not in {
            "unresolved",
            "na",
        }:
            raise ValueError(
                f"row {row_number} structural outcome must remain unresolved for {mode}"
            )
        if mode == "NA" and structural != "na":
            raise ValueError(
                f"row {row_number} structural outcome must be na when architecture_mode is NA"
            )

        if clean["primary_model_eligible"] == "true":
            if clean["adjudication_status"] != "ADJUDICATED":
                raise ValueError(
                    f"row {row_number} primary eligibility requires ADJUDICATED status"
                )
            if clean["unit_type"] not in {"SPECIES", "SPECIES_CONTEXT"}:
                raise ValueError(
                    f"row {row_number} primary eligibility requires species-level grain"
                )
            if clean["conflict_status"] != "POSITIVE":
                raise ValueError(
                    f"row {row_number} primary eligibility requires POSITIVE conflict"
                )
            if structural not in {"true", "false"}:
                raise ValueError(
                    f"row {row_number} primary eligibility requires resolved binary outcome"
                )
            if clean["module_substrate"] == "UNRESOLVED":
                raise ValueError(
                    f"row {row_number} primary eligibility requires resolved module substrate"
                )
            if clean["conflict_timing_geometry"] == "UNRESOLVED":
                raise ValueError(
                    f"row {row_number} primary eligibility requires resolved timing geometry"
                )
            if clean["conflict_spatial_geometry"] == "UNRESOLVED":
                raise ValueError(
                    f"row {row_number} primary eligibility requires resolved spatial geometry"
                )

        clean["exclusion_reason"] = (row.get("exclusion_reason") or "").strip()
        clean["notes"] = (row.get("notes") or "").strip()
        out.append(clean)

    return out


def load_plant_macro_ledger(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        if fields != FIELDS:
            raise ValueError("plant macro ledger columns must match canonical order")
        return _validated_rows(reader)


def build_plant_macro_readout_from_rows(rows: list[dict[str, str]]) -> dict:
    return {
        "analysis": "balance_plant_macro_screening_readout",
        "n_records": len(rows),
        "n_dependency_groups": len({r["dependency_group"] for r in rows}),
        "unit_type_counts": dict(sorted(Counter(r["unit_type"] for r in rows).items())),
        "conflict_family_counts": dict(
            sorted(Counter(r["conflict_family"] for r in rows).items())
        ),
        "conflict_status_counts": dict(
            sorted(Counter(r["conflict_status"] for r in rows).items())
        ),
        "architecture_mode_counts": dict(
            sorted(Counter(r["architecture_mode"] for r in rows).items())
        ),
        "module_substrate_counts": dict(
            sorted(Counter(r["module_substrate"] for r in rows).items())
        ),
        "n_primary_model_eligible": sum(
            r["primary_model_eligible"] == "true" for r in rows
        ),
        "claim_ceiling": (
            "screening_and_comparative_architecture_associations_only_"
            "not_direct_R_K_Phi_rho_xi_dB_identification"
        ),
    }


def build_plant_macro_readout(path: Path) -> dict:
    return build_plant_macro_readout_from_rows(load_plant_macro_ledger(path))

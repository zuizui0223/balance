"""Validation and derived outcomes for the BALANCE comparative-macro ledger."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "cluster_id",
    "sampling_frame_id",
    "source_id",
    "publication_year",
    "system_taxon",
    "domain",
    "shared_structure",
    "function_a",
    "function_b",
    "multifunctionality_status",
    "conflict_status",
    "conflict_strength_proxy",
    "architecture_state",
    "structural_differentiation",
    "alternative_accessibility",
    "functional_coupling",
    "temporal_heterogeneity",
    "spatial_heterogeneity",
    "alternative_repertoire",
    "context_axis",
    "study_design",
    "evidence_quality",
    "source_count",
    "adjudication_status",
    "primary_model_eligible",
    "exclusion_reason",
    "source_basis",
    "claim_ceiling",
    "notes",
)
REQUIRED = set(FIELDS)

MULTIFUNCTIONALITY = {"YES", "NO", "UNRESOLVED"}
CONFLICT = {
    "POSITIVE",
    "ALIGNED_NO_CONFLICT",
    "NO_DEMONSTRATED_CONFLICT",
    "UNRESOLVED",
}
ORDINAL = {"LOW", "MEDIUM", "HIGH", "UNRESOLVED", "NA"}
ARCHITECTURE = {
    "SHARED_INTEGRATED",
    "REGULATORY_TEMPORAL_SEPARATION",
    "SPATIAL_COMPARTMENTALIZATION",
    "PARTIAL_STRUCTURAL_DIFFERENTIATION",
    "SEPARATE_MODULES",
    "POLYMORPHIC",
    "UNRESOLVED",
    "NA",
}
STRUCTURAL = {"true", "false", "unresolved", "na"}
ALTERNATIVE_REPERTOIRE = {"NONE", "ONE", "MULTIPLE", "UNRESOLVED", "NA"}
EVIDENCE = {"HIGH", "MODERATE", "LOW", "UNREVIEWED"}
ADJUDICATION = {"UNSCREENED", "SCREENED", "ADJUDICATED", "EXCLUDED"}

STRUCTURAL_TRUE = {
    "PARTIAL_STRUCTURAL_DIFFERENTIATION",
    "SEPARATE_MODULES",
}
STRUCTURAL_FALSE = {
    "SHARED_INTEGRATED",
    "REGULATORY_TEMPORAL_SEPARATION",
    "SPATIAL_COMPARTMENTALIZATION",
}
RESOLUTION_LEVEL = {
    "SHARED_INTEGRATED": 0,
    "REGULATORY_TEMPORAL_SEPARATION": 1,
    "SPATIAL_COMPARTMENTALIZATION": 2,
    "PARTIAL_STRUCTURAL_DIFFERENTIATION": 3,
    "SEPARATE_MODULES": 4,
}

_MISSING = {"", "none", "null", "nan", "required_before_use"}


def _required_text(value: object, field: str, row_number: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"row {row_number} {field} must be a string")
    text = value.strip()
    if text.casefold() in _MISSING:
        raise ValueError(f"row {row_number} {field} must be frozen before analysis")
    return text


def _category(
    value: object,
    field: str,
    allowed: set[str],
    row_number: int,
    *,
    casefold: bool = False,
) -> str:
    text = _required_text(value, field, row_number)
    if casefold:
        text = text.casefold()
    if text not in allowed:
        raise ValueError(
            f"row {row_number} {field} {text!r} is not one of {sorted(allowed)}"
        )
    return text


def _year(value: object, row_number: int) -> str:
    text = _required_text(value, "publication_year", row_number)
    if text == "UNRESOLVED":
        return text
    try:
        year = int(text)
    except ValueError as exc:
        raise ValueError(
            f"row {row_number} publication_year must be an integer or UNRESOLVED"
        ) from exc
    if not 1800 <= year <= 2100:
        raise ValueError(
            f"row {row_number} publication_year must fall between 1800 and 2100"
        )
    return str(year)


def _source_count(value: object, row_number: int) -> str:
    text = _required_text(value, "source_count", row_number)
    if text == "UNRESOLVED":
        return text
    try:
        count = int(text)
    except ValueError as exc:
        raise ValueError(
            f"row {row_number} source_count must be a nonnegative integer or UNRESOLVED"
        ) from exc
    if count < 0:
        raise ValueError(f"row {row_number} source_count must be nonnegative")
    return str(count)


def derive_resolution_level(architecture_state: str) -> int | None:
    """Return the registered 0-4 comparative resolution level when defined."""
    return RESOLUTION_LEVEL.get(architecture_state)


def _validated_rows(reader: csv.DictReader) -> list[dict[str, str]]:
    rows = list(reader)
    if not rows:
        raise ValueError("macro ledger must contain at least one screened cluster")

    seen: set[str] = set()
    out: list[dict[str, str]] = []

    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(
                f"row {row_number} has fields outside the canonical macro schema"
            )
        clean = dict(row)

        for field in (
            "cluster_id",
            "sampling_frame_id",
            "source_id",
            "system_taxon",
            "domain",
            "shared_structure",
            "function_a",
            "function_b",
            "context_axis",
            "study_design",
            "source_basis",
            "claim_ceiling",
        ):
            clean[field] = _required_text(row.get(field), field, row_number)

        cluster_id = clean["cluster_id"]
        if cluster_id in seen:
            raise ValueError(
                f"duplicate cluster_id {cluster_id!r}: one independent biological cluster must occupy one row"
            )
        seen.add(cluster_id)

        if clean["function_a"].casefold() == clean["function_b"].casefold():
            raise ValueError(
                f"row {row_number} function_a and function_b must be biologically distinct"
            )

        clean["publication_year"] = _year(row.get("publication_year"), row_number)
        clean["source_count"] = _source_count(row.get("source_count"), row_number)

        clean["multifunctionality_status"] = _category(
            row.get("multifunctionality_status"),
            "multifunctionality_status",
            MULTIFUNCTIONALITY,
            row_number,
        )
        clean["conflict_status"] = _category(
            row.get("conflict_status"), "conflict_status", CONFLICT, row_number
        )
        clean["conflict_strength_proxy"] = _category(
            row.get("conflict_strength_proxy"),
            "conflict_strength_proxy",
            ORDINAL,
            row_number,
        )
        clean["architecture_state"] = _category(
            row.get("architecture_state"),
            "architecture_state",
            ARCHITECTURE,
            row_number,
        )
        clean["structural_differentiation"] = _category(
            row.get("structural_differentiation"),
            "structural_differentiation",
            STRUCTURAL,
            row_number,
            casefold=True,
        )
        for field in (
            "alternative_accessibility",
            "functional_coupling",
            "temporal_heterogeneity",
            "spatial_heterogeneity",
        ):
            clean[field] = _category(row.get(field), field, ORDINAL, row_number)
        clean["alternative_repertoire"] = _category(
            row.get("alternative_repertoire"),
            "alternative_repertoire",
            ALTERNATIVE_REPERTOIRE,
            row_number,
        )
        clean["evidence_quality"] = _category(
            row.get("evidence_quality"),
            "evidence_quality",
            EVIDENCE,
            row_number,
        )
        clean["adjudication_status"] = _category(
            row.get("adjudication_status"),
            "adjudication_status",
            ADJUDICATION,
            row_number,
        )
        clean["primary_model_eligible"] = _category(
            row.get("primary_model_eligible"),
            "primary_model_eligible",
            {"true", "false"},
            row_number,
            casefold=True,
        )

        state = clean["architecture_state"]
        structural = clean["structural_differentiation"]
        if state in STRUCTURAL_TRUE and structural != "true":
            raise ValueError(
                f"row {row_number} structural_differentiation must be true for {state}"
            )
        if state in STRUCTURAL_FALSE and structural != "false":
            raise ValueError(
                f"row {row_number} structural_differentiation must be false for {state}"
            )
        if state in {"POLYMORPHIC", "UNRESOLVED"} and structural not in {
            "unresolved",
            "na",
        }:
            raise ValueError(
                f"row {row_number} structural_differentiation must remain unresolved for {state}"
            )
        if state == "NA" and structural != "na":
            raise ValueError(
                f"row {row_number} structural_differentiation must be na when architecture_state is NA"
            )

        if clean["primary_model_eligible"] == "true":
            if clean["adjudication_status"] != "ADJUDICATED":
                raise ValueError(
                    f"row {row_number} primary_model_eligible requires ADJUDICATED status"
                )
            if clean["multifunctionality_status"] != "YES":
                raise ValueError(
                    f"row {row_number} primary_model_eligible requires confirmed multifunctionality"
                )
            if clean["conflict_status"] != "POSITIVE":
                raise ValueError(
                    f"row {row_number} primary_model_eligible requires POSITIVE conflict"
                )
            if structural not in {"true", "false"}:
                raise ValueError(
                    f"row {row_number} primary_model_eligible requires a resolved binary architecture outcome"
                )

        clean["exclusion_reason"] = (row.get("exclusion_reason") or "").strip()
        clean["notes"] = (row.get("notes") or "").strip()
        out.append(clean)

    return out


def load_macro_ledger(path: Path) -> list[dict[str, str]]:
    """Load a macro ledger only if it satisfies the frozen schema and gate rules."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        missing = sorted(REQUIRED - set(fields))
        if missing:
            raise ValueError("missing required columns: " + ", ".join(missing))
        extra = sorted(set(fields) - REQUIRED)
        if extra:
            raise ValueError(
                "unexpected columns outside canonical macro schema: "
                + ", ".join(extra)
            )
        if fields != FIELDS:
            raise ValueError("macro ledger columns must match the canonical order")
        return _validated_rows(reader)


def build_macro_readout_from_rows(rows: list[dict[str, str]]) -> dict:
    """Build a descriptive screening readout without estimating natural prevalence."""
    conflict = Counter(r["conflict_status"] for r in rows)
    architecture = Counter(r["architecture_state"] for r in rows)
    domain = Counter(r["domain"] for r in rows)
    adjudication = Counter(r["adjudication_status"] for r in rows)
    eligible = [r for r in rows if r["primary_model_eligible"] == "true"]

    eligible_structural = Counter(
        r["structural_differentiation"] for r in eligible
    )

    return {
        "analysis": "balance_macro_screening_readout",
        "n_records": len(rows),
        "n_independent_clusters": len({r["cluster_id"] for r in rows}),
        "conflict_status_counts": dict(sorted(conflict.items())),
        "architecture_state_counts": dict(sorted(architecture.items())),
        "domain_counts": dict(sorted(domain.items())),
        "adjudication_status_counts": dict(sorted(adjudication.items())),
        "n_primary_model_eligible": len(eligible),
        "primary_structural_outcome_counts": dict(
            sorted(eligible_structural.items())
        ),
        "claim_ceiling": (
            "screened_comparative_associations_only_not_natural_prevalence_"
            "and_not_direct_R_K_Phi_rho_xi_dB_identification"
        ),
    }


def build_macro_readout(path: Path) -> dict:
    return build_macro_readout_from_rows(load_macro_ledger(path))

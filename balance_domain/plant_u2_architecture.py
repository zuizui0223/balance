"""Architecture handoff for U2 conflict-positive systems."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "dependency_group",
    "taxon_raw",
    "conflict_status",
    "natural_architecture_mode",
    "architecture_evidence_type",
    "experimental_alternative_mode",
    "resolution_causal_status",
    "module_substrate",
    "conflict_timing_geometry",
    "conflict_spatial_geometry",
    "source_basis",
    "claim_ceiling",
    "notes",
)

ARCHITECTURE = {
    "SHARED_INTEGRATED",
    "TEMPORAL_SEPARATION",
    "SPATIAL_SEPARATION",
    "SIGNAL_SEPARATION",
    "TEMPORAL_AND_SPATIAL_SEPARATION",
    "WITHIN_FLOWER_DIVISION_OF_LABOUR",
    "AMONG_FLOWER_MODULE_DIVISION",
    "POLYMORPHIC_OR_MOSAIC",
    "UNRESOLVED",
    "NA",
}
EVIDENCE_TYPE = {
    "CONFLICT_ONLY",
    "NATURAL_STATE",
    "EXPERIMENTAL_ALTERNATIVE",
    "NATURAL_AND_EXPERIMENTAL",
}
CAUSAL_STATUS = {
    "DIRECT_CAUSAL_RESOLUTION",
    "DIRECT_EXPERIMENTAL_ALTERNATIVE",
    "CONCORDANT_NOT_CAUSAL",
    "NOT_IDENTIFIED",
}
MODULE = {
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
EXPECTED_ROWS = 8


def load_u2_architecture_handoff(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U2 architecture-handoff columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_ROWS:
        raise ValueError("U2 architecture handoff must contain the eight positive-conflict groups")

    seen: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U2 architecture schema")
        if row["dependency_group"] in seen:
            raise ValueError(f"duplicate U2 architecture group {row['dependency_group']!r}")
        seen.add(row["dependency_group"])

        if row["conflict_status"] != "POSITIVE":
            raise ValueError(f"row {n} architecture handoff requires positive conflict")
        if row["natural_architecture_mode"] not in ARCHITECTURE:
            raise ValueError(f"row {n} invalid natural_architecture_mode")
        if row["experimental_alternative_mode"] not in ARCHITECTURE:
            raise ValueError(f"row {n} invalid experimental_alternative_mode")
        if row["architecture_evidence_type"] not in EVIDENCE_TYPE:
            raise ValueError(f"row {n} invalid architecture_evidence_type")
        if row["resolution_causal_status"] not in CAUSAL_STATUS:
            raise ValueError(f"row {n} invalid resolution_causal_status")
        if row["module_substrate"] not in MODULE:
            raise ValueError(f"row {n} invalid module_substrate")
        if row["conflict_timing_geometry"] not in TIMING:
            raise ValueError(f"row {n} invalid conflict_timing_geometry")
        if row["conflict_spatial_geometry"] not in SPATIAL:
            raise ValueError(f"row {n} invalid conflict_spatial_geometry")

        if row["architecture_evidence_type"] == "CONFLICT_ONLY":
            if row["natural_architecture_mode"] != "UNRESOLVED":
                raise ValueError(f"row {n} conflict-only evidence cannot assign natural architecture")
            if row["experimental_alternative_mode"] != "NA":
                raise ValueError(f"row {n} conflict-only evidence cannot assign experimental alternative")
            if row["resolution_causal_status"] != "NOT_IDENTIFIED":
                raise ValueError(f"row {n} conflict-only evidence cannot claim resolution")

        if row["resolution_causal_status"] == "DIRECT_CAUSAL_RESOLUTION":
            if row["architecture_evidence_type"] not in {
                "NATURAL_AND_EXPERIMENTAL",
                "EXPERIMENTAL_ALTERNATIVE",
            }:
                raise ValueError(f"row {n} direct causal resolution requires experimental evidence")

        if row["resolution_causal_status"] == "DIRECT_EXPERIMENTAL_ALTERNATIVE":
            if row["experimental_alternative_mode"] in {"NA", "UNRESOLVED"}:
                raise ValueError(f"row {n} experimental resolution requires a declared alternative")

    return rows


def build_u2_architecture_readout_from_rows(rows: list[dict[str, str]]) -> dict:
    natural = Counter(r["natural_architecture_mode"] for r in rows)
    causal = Counter(r["resolution_causal_status"] for r in rows)
    evidence = Counter(r["architecture_evidence_type"] for r in rows)
    return {
        "analysis": "balance_plant_u2_architecture_handoff",
        "n_positive_conflict_groups": len(rows),
        "natural_architecture_mode_counts": dict(sorted(natural.items())),
        "architecture_evidence_type_counts": dict(sorted(evidence.items())),
        "resolution_causal_status_counts": dict(sorted(causal.items())),
        "n_direct_resolution_evidence": sum(
            r["resolution_causal_status"]
            in {"DIRECT_CAUSAL_RESOLUTION", "DIRECT_EXPERIMENTAL_ALTERNATIVE"}
            for r in rows
        ),
        "n_architecture_unresolved": natural.get("UNRESOLVED", 0),
        "claim_ceiling": (
            "architecture_handoff_conditional_on_positive_conflict_"
            "natural_state_separated_from_experimental_alternative"
        ),
    }


def build_u2_architecture_readout(path: Path) -> dict:
    return build_u2_architecture_readout_from_rows(load_u2_architecture_handoff(path))

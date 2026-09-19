"""Guards for the Barrett-2002 sexual-interference discovery universe."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "universe_record_id",
    "universe_id",
    "dependency_group",
    "taxon_raw",
    "review_reference",
    "primary_source_id",
    "primary_source_doi",
    "evidence_family",
    "screening_status",
    "source_resolution_status",
    "notes",
)

COVERAGE_FIELDS = (
    "reference_id",
    "citation_short",
    "reference_class",
    "dependency_groups",
    "coverage_status",
    "notes",
)

SCREENING = {"UNSCREENED", "SCREENED", "ADJUDICATED", "EXCLUDED"}
SOURCE = {"RESOLVED_PRIMARY", "TAXON_RESOLUTION_PENDING", "SOURCE_RESOLUTION_PENDING"}
REFERENCE_CLASS = {
    "TAXON_EMPIRICAL",
    "SYNTHESIS_REVIEW",
    "THEORY_GENERAL",
    "HISTORICAL_SYNTHESIS",
    "BROAD_COMPARATIVE_DATASET",
}
COVERAGE_STATUS = {"MAPPED", "NO_NEW_GROUP_REQUIRED", "PENDING"}

EXPECTED_GROUPS = 22
EXPECTED_REFERENCES = 37


def load_u2_universe(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U2 universe columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_GROUPS:
        raise ValueError(
            f"U2 universe must contain {EXPECTED_GROUPS} registered dependency groups"
        )

    ids: set[str] = set()
    deps: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U2 schema")
        for field in (
            "universe_record_id",
            "universe_id",
            "dependency_group",
            "taxon_raw",
            "review_reference",
            "primary_source_id",
            "evidence_family",
            "screening_status",
            "source_resolution_status",
        ):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"row {n} {field} must be frozen")

        if row["universe_id"] != "U2_BARRETT_2002":
            raise ValueError(f"row {n} has wrong U2 universe_id")
        if row["screening_status"] not in SCREENING:
            raise ValueError(f"row {n} invalid screening_status")
        if row["source_resolution_status"] not in SOURCE:
            raise ValueError(f"row {n} invalid source_resolution_status")
        if row["universe_record_id"] in ids:
            raise ValueError(f"duplicate U2 record id {row['universe_record_id']!r}")
        ids.add(row["universe_record_id"])

        if row["dependency_group"] in deps:
            raise ValueError(
                f"duplicate U2 dependency_group {row['dependency_group']!r}: "
                "merge repeated studies instead of counting bibliographic replication"
            )
        deps.add(row["dependency_group"])

        if row["source_resolution_status"] == "TAXON_RESOLUTION_PENDING":
            if "spp." not in row["taxon_raw"] and "program" not in row["dependency_group"].lower():
                raise ValueError(
                    f"row {n} taxon-resolution-pending record must visibly preserve non-species grain"
                )

    return rows


def load_u2_reference_coverage(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != COVERAGE_FIELDS:
            raise ValueError("U2 reference-coverage columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_REFERENCES:
        raise ValueError(
            f"Barrett 2002 reference coverage must contain all {EXPECTED_REFERENCES} references"
        )

    ids: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"coverage row {n} has fields outside schema")
        for field in ("reference_id", "citation_short", "reference_class", "coverage_status"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"coverage row {n} {field} must be frozen")
        if row["reference_id"] in ids:
            raise ValueError(f"duplicate Barrett reference id {row['reference_id']!r}")
        ids.add(row["reference_id"])
        if row["reference_class"] not in REFERENCE_CLASS:
            raise ValueError(f"coverage row {n} invalid reference_class")
        if row["coverage_status"] not in COVERAGE_STATUS:
            raise ValueError(f"coverage row {n} invalid coverage_status")

        if row["reference_class"] == "TAXON_EMPIRICAL":
            if row["coverage_status"] != "MAPPED":
                raise ValueError(
                    f"coverage row {n} taxon-empirical reference must be MAPPED"
                )
            if not row["dependency_groups"].strip():
                raise ValueError(
                    f"coverage row {n} taxon-empirical reference requires dependency groups"
                )
        else:
            if row["coverage_status"] == "MAPPED" and not row["dependency_groups"].strip():
                raise ValueError(
                    f"coverage row {n} mapped non-empirical reference needs explicit group mapping"
                )
    return rows


def validate_u2_reference_handoff(
    universe_rows: list[dict[str, str]],
    coverage_rows: list[dict[str, str]],
) -> dict:
    deps = {r["dependency_group"] for r in universe_rows}
    mapped_empirical: set[str] = set()

    for row in coverage_rows:
        if row["reference_class"] != "TAXON_EMPIRICAL":
            continue
        for dep in (x.strip() for x in row["dependency_groups"].split(";")):
            if dep not in deps:
                raise ValueError(
                    f"Barrett reference {row['reference_id']} maps to absent U2 group {dep!r}"
                )
            mapped_empirical.add(dep)

    # Every dependency group in this review-defined universe must have at least one
    # taxon-specific empirical citation in the review coverage ledger.
    unmapped_groups = sorted(deps - mapped_empirical)
    if unmapped_groups:
        raise ValueError(
            "U2 dependency groups lack taxon-specific Barrett reference mapping: "
            + ", ".join(unmapped_groups)
        )

    pending = [r["reference_id"] for r in coverage_rows if r["coverage_status"] == "PENDING"]
    unresolved_sources = [
        r["dependency_group"]
        for r in universe_rows
        if r["source_resolution_status"] != "RESOLVED_PRIMARY"
    ]

    return {
        "analysis": "balance_plant_u2_reference_handoff",
        "n_registered_dependency_groups": len(universe_rows),
        "n_barrett_references": len(coverage_rows),
        "n_taxon_empirical_references": sum(
            r["reference_class"] == "TAXON_EMPIRICAL" for r in coverage_rows
        ),
        "n_mapped_empirical_dependency_groups": len(mapped_empirical),
        "n_pending_reference_classifications": len(pending),
        "pending_reference_ids": sorted(pending),
        "n_unresolved_primary_sources": len(unresolved_sources),
        "unresolved_dependency_groups": sorted(unresolved_sources),
        "review_reference_coverage_closed": not pending,
        "species_source_resolution_closed": not unresolved_sources,
        "discovery_universe_source_closed": not pending and not unresolved_sources,
        "claim_ceiling": (
            "barrett_reference_coverage_and_species_source_resolution_only_"
            "not_conflict_status_not_architecture_mode_not_confirmatory"
        ),
    }


def build_u2_readout_from_rows(rows: list[dict[str, str]]) -> dict:
    source = Counter(r["source_resolution_status"] for r in rows)
    families = Counter(r["evidence_family"] for r in rows)
    screening = Counter(r["screening_status"] for r in rows)
    return {
        "analysis": "balance_plant_u2_review_universe",
        "n_registered_dependency_groups": len(rows),
        "source_resolution_counts": dict(sorted(source.items())),
        "evidence_family_counts": dict(sorted(families.items())),
        "screening_status_counts": dict(sorted(screening.items())),
        "n_species_level_source_resolved": sum(
            r["source_resolution_status"] == "RESOLVED_PRIMARY"
            and "spp." not in r["taxon_raw"]
            for r in rows
        ),
        "n_taxon_resolution_pending": source.get("TAXON_RESOLUTION_PENDING", 0),
        "claim_ceiling": (
            "review_defined_discovery_universe_only_"
            "not_conflict_positive_not_architecture_resolution_not_confirmatory"
        ),
    }


def build_u2_readout(path: Path) -> dict:
    return build_u2_readout_from_rows(load_u2_universe(path))


def build_u2_reference_handoff(universe_path: Path, coverage_path: Path) -> dict:
    return validate_u2_reference_handoff(
        load_u2_universe(universe_path),
        load_u2_reference_coverage(coverage_path),
    )

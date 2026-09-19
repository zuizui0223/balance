"""Guards for the provisional Barrett-2002 sexual-interference discovery universe."""
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

SCREENING = {"UNSCREENED", "SCREENED", "ADJUDICATED", "EXCLUDED"}
SOURCE = {"RESOLVED_PRIMARY", "TAXON_RESOLUTION_PENDING", "SOURCE_RESOLUTION_PENDING"}

EXPECTED_PROVISIONAL_GROUPS = 16


def load_u2_universe(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U2 universe columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_PROVISIONAL_GROUPS:
        raise ValueError(
            f"provisional U2 universe must contain {EXPECTED_PROVISIONAL_GROUPS} registered groups"
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

        # U2 is already collapsed to one biological dependency group per row.
        if row["dependency_group"] in deps:
            raise ValueError(
                f"duplicate U2 dependency_group {row['dependency_group']!r}: "
                "merge multiple review-cited studies rather than count them as replication"
            )
        deps.add(row["dependency_group"])

        # Genus-level unresolved records must stay outside species-level inference.
        if row["source_resolution_status"] == "TAXON_RESOLUTION_PENDING":
            if "spp." not in row["taxon_raw"] and "program" not in row["dependency_group"].lower():
                raise ValueError(
                    f"row {n} taxon-resolution-pending record must visibly preserve non-species grain"
                )

    return rows


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
        "review_universe_closed": False,
        "claim_ceiling": (
            "review_defined_discovery_universe_only_"
            "not_conflict_positive_not_architecture_resolution_not_confirmatory"
        ),
    }


def build_u2_readout(path: Path) -> dict:
    return build_u2_readout_from_rows(load_u2_universe(path))

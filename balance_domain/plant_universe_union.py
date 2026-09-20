"""Cross-universe dependency-group deduplication for BALANCE plant macro screening."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "dependency_group",
    "taxon_raw",
    "universe_membership",
    "u1_record_id",
    "u1_screening_status",
    "u1_source_status",
    "u2_record_id",
    "u2_screening_status",
    "u2_source_status",
    "overlap_status",
    "union_frame_status",
)

MEMBERSHIP = {"U1", "U2", "U1;U2"}
OVERLAP = {"SINGLE_UNIVERSE", "MULTI_UNIVERSE_SAME_DEPENDENCY_GROUP"}
EXPECTED_U1_NETWORK_VISIBLE = 44
EXPECTED_U2_SOURCE_CLOSED = 22
EXPECTED_OVERLAPS = 2
EXPECTED_UNION = (
    EXPECTED_U1_NETWORK_VISIBLE + EXPECTED_U2_SOURCE_CLOSED - EXPECTED_OVERLAPS
)


def load_cross_universe_map(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("cross-universe map columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_UNION:
        raise ValueError(
            f"cross-universe map must contain {EXPECTED_UNION} unique dependency groups"
        )

    seen: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside canonical schema")
        dep = (row.get("dependency_group") or "").strip()
        taxon = (row.get("taxon_raw") or "").strip()
        membership = (row.get("universe_membership") or "").strip()
        overlap = (row.get("overlap_status") or "").strip()
        if not dep or not taxon:
            raise ValueError(f"row {n} dependency_group and taxon_raw must be frozen")
        if dep in seen:
            raise ValueError(f"duplicate dependency_group {dep!r}")
        seen.add(dep)
        if membership not in MEMBERSHIP:
            raise ValueError(f"row {n} invalid universe_membership {membership!r}")
        if overlap not in OVERLAP:
            raise ValueError(f"row {n} invalid overlap_status {overlap!r}")

        both = membership == "U1;U2"
        if both != (overlap == "MULTI_UNIVERSE_SAME_DEPENDENCY_GROUP"):
            raise ValueError(f"row {n} overlap_status disagrees with membership")

        if "U1" in membership:
            if not row["u1_record_id"].strip():
                raise ValueError(f"row {n} U1 membership requires u1_record_id")
            if row["u1_screening_status"] == "NOT_IN_U1":
                raise ValueError(f"row {n} U1 membership cannot have NOT_IN_U1 status")
        else:
            if row["u1_record_id"].strip():
                raise ValueError(f"row {n} non-U1 row must not carry u1_record_id")

        if "U2" in membership:
            if not row["u2_record_id"].strip():
                raise ValueError(f"row {n} U2 membership requires u2_record_id")
            if row["u2_screening_status"] == "NOT_IN_U2":
                raise ValueError(f"row {n} U2 membership cannot have NOT_IN_U2 status")
        else:
            if row["u2_record_id"].strip():
                raise ValueError(f"row {n} non-U2 row must not carry u2_record_id")

    return rows


def build_cross_universe_readout_from_rows(rows: list[dict[str, str]]) -> dict:
    membership = Counter(r["universe_membership"] for r in rows)
    overlap = [r for r in rows if r["universe_membership"] == "U1;U2"]
    screened_any = [
        r
        for r in rows
        if r["u1_screening_status"] in {"SCREENED", "EXCLUDED", "ADJUDICATED"}
        or r["u2_screening_status"] in {"SCREENED", "EXCLUDED", "ADJUDICATED"}
    ]
    return {
        "analysis": "balance_plant_cross_universe_dependency_map",
        "n_unique_dependency_groups": len(rows),
        "membership_counts": dict(sorted(membership.items())),
        "n_multi_universe_overlap_groups": len(overlap),
        "multi_universe_overlap_groups": sorted(r["dependency_group"] for r in overlap),
        "n_groups_with_any_source_screen": len(screened_any),
        "claim_ceiling": (
            "deduplicated_discovery_universe_accounting_only_"
            "not_prevalence_not_independent_replication_not_confirmatory"
        ),
    }


def build_cross_universe_readout(path: Path) -> dict:
    return build_cross_universe_readout_from_rows(load_cross_universe_map(path))

"""Fail-closed candidate registry for the three unresolved U3 Table-S1 families."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

FIELDS = (
    "candidate_id",
    "family",
    "candidate_taxon",
    "candidate_role",
    "candidate_grain",
    "heteranthery_morphology_status",
    "review_connection_status",
    "selection_status",
    "source_id",
    "blocker",
    "notes",
)

TARGET_FAMILIES = {"Malvaceae", "Bixaceae", "Scrophulariaceae"}
ROLE = {"LINEAGE_CANDIDATE", "SPECIES_CANDIDATE", "SPECIES_ALTERNATIVE", "NEGATIVE_EXCLUSION"}
GRAIN = {"SPECIES", "GENUS"}
MORPH = {"PASS", "FAIL", "OPEN"}
SELECTION = {"OPEN", "REJECTED"}


def load_u3_table_s1_candidates(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 Table-S1 candidate columns must match canonical order")
        rows = list(reader)
    if not rows:
        raise ValueError("U3 Table-S1 candidate registry must not be empty")

    seen = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside candidate schema")
        clean = {k: (v or "").strip() for k, v in row.items()}
        row.update(clean)
        if not clean["candidate_id"] or clean["candidate_id"] in seen:
            raise ValueError(f"row {n} candidate_id must be unique and frozen")
        seen.add(clean["candidate_id"])
        if clean["family"] not in TARGET_FAMILIES:
            raise ValueError(f"row {n} is outside the three unresolved families")
        if clean["candidate_role"] not in ROLE:
            raise ValueError(f"row {n} invalid candidate_role")
        if clean["candidate_grain"] not in GRAIN:
            raise ValueError(f"row {n} invalid candidate_grain")
        if clean["heteranthery_morphology_status"] not in MORPH:
            raise ValueError(f"row {n} invalid morphology status")
        if clean["selection_status"] not in SELECTION:
            raise ValueError(f"row {n} invalid selection status")
        if not clean["candidate_taxon"] or not clean["source_id"]:
            raise ValueError(f"row {n} candidate taxon/source must be frozen")

        if clean["selection_status"] == "OPEN":
            if clean["heteranthery_morphology_status"] == "FAIL":
                raise ValueError(f"row {n} OPEN candidate cannot fail morphology")
            if not clean["blocker"]:
                raise ValueError(f"row {n} OPEN candidate requires exact-identity blocker")
        else:
            if clean["heteranthery_morphology_status"] != "FAIL":
                raise ValueError(f"row {n} REJECTED candidate requires morphology FAIL")
            if not clean["blocker"]:
                raise ValueError(f"row {n} REJECTED candidate requires blocker")

    open_families = {r["family"] for r in rows if r["selection_status"] == "OPEN"}
    if open_families != TARGET_FAMILIES:
        raise ValueError("candidate registry must retain at least one OPEN route for every pending family")
    return rows


def build_u3_table_s1_candidate_readout(path: Path) -> dict:
    rows = load_u3_table_s1_candidates(path)
    open_rows = [r for r in rows if r["selection_status"] == "OPEN"]
    rejected = [r for r in rows if r["selection_status"] == "REJECTED"]
    exact_species_open = [
        r for r in open_rows if r["candidate_grain"] == "SPECIES"
    ]
    return {
        "analysis": "balance_u3_table_s1_candidate_reduction_v1",
        "n_rows": len(rows),
        "status_counts": dict(sorted(Counter(r["selection_status"] for r in rows).items())),
        "open_families": sorted({r["family"] for r in open_rows}),
        "open_lineages": sorted({r["candidate_taxon"] for r in open_rows}),
        "rejected_taxa": sorted({r["candidate_taxon"] for r in rejected}),
        "n_open_species_level_candidates": len(exact_species_open),
        "exact_representative_identity_closed": False,
        "claim_ceiling": (
            "candidate_space_reduction_only_not_table_s1_identity_"
            "not_representative_promotion_not_prevalence"
        ),
    }

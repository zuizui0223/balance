"""Fail-closed candidate audit for the three unresolved U3 family representatives."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "candidate_id",
    "family",
    "candidate_taxon",
    "candidate_role",
    "taxonomy_status",
    "heteranthery_evidence_status",
    "pre2010_evidence_status",
    "table_s1_linkage_status",
    "review_uniqueness_status",
    "selection_status",
    "source_id",
    "blocker",
    "notes",
)

TARGET_FAMILIES = {"Malvaceae", "Bixaceae", "Scrophulariaceae"}
CANDIDATE_ROLE = {
    "DISCOVERY_CANDIDATE",
    "HISTORICAL_CIRCUMSCRIPTION_CANDIDATE",
    "POST2010_DISCOVERY_CANDIDATE",
}
TAXONOMY = {"PASS", "FAIL", "OPEN"}
HETERANTHERY = {"PASS", "PARTIAL", "CONFLICT", "NEGATIVE", "OPEN"}
PRE2010 = {"PASS", "FAIL", "OPEN"}
TABLE_S1 = {"EXACT", "UNRESOLVED"}
UNIQUENESS = {"SINGLE_SPECIES_REPORTED", "MULTIPLE_OR_UNSPECIFIED"}
SELECTION = {"OPEN", "REJECTED", "SELECTED"}


def load_u3_representative_candidate_audit(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 representative-candidate columns must match canonical order")
        rows = list(reader)
    if not rows:
        raise ValueError("U3 representative-candidate audit cannot be empty")

    seen: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside representative-candidate schema")
        clean = {k: (v or "").strip() for k, v in row.items()}
        row.update(clean)
        if not clean["candidate_id"] or clean["candidate_id"] in seen:
            raise ValueError(f"row {n} candidate_id must be unique and frozen")
        seen.add(clean["candidate_id"])
        if clean["family"] not in TARGET_FAMILIES:
            raise ValueError(f"row {n} family is outside the three unresolved U3 families")
        if clean["candidate_role"] not in CANDIDATE_ROLE:
            raise ValueError(f"row {n} invalid candidate_role")
        if clean["taxonomy_status"] not in TAXONOMY:
            raise ValueError(f"row {n} invalid taxonomy_status")
        if clean["heteranthery_evidence_status"] not in HETERANTHERY:
            raise ValueError(f"row {n} invalid heteranthery_evidence_status")
        if clean["pre2010_evidence_status"] not in PRE2010:
            raise ValueError(f"row {n} invalid pre2010_evidence_status")
        if clean["table_s1_linkage_status"] not in TABLE_S1:
            raise ValueError(f"row {n} invalid table_s1_linkage_status")
        if clean["review_uniqueness_status"] not in UNIQUENESS:
            raise ValueError(f"row {n} invalid review_uniqueness_status")
        if clean["selection_status"] not in SELECTION:
            raise ValueError(f"row {n} invalid selection_status")
        if not clean["candidate_taxon"] or not clean["source_id"] or not clean["blocker"]:
            raise ValueError(f"row {n} source, taxon and blocker fields must be frozen")

        if clean["selection_status"] == "SELECTED":
            exact_table = clean["table_s1_linkage_status"] == "EXACT"
            independent_unique = (
                clean["review_uniqueness_status"] == "SINGLE_SPECIES_REPORTED"
                and clean["taxonomy_status"] == "PASS"
                and clean["heteranthery_evidence_status"] == "PASS"
                and clean["pre2010_evidence_status"] == "PASS"
            )
            if not (exact_table or independent_unique):
                raise ValueError(
                    f"row {n} SELECTED requires exact Table S1 linkage or "
                    "a review-unique species with independent pre-2010 heteranthery evidence"
                )
            if clean["blocker"] != "NONE":
                raise ValueError(f"row {n} SELECTED candidate cannot retain a blocker")

        if clean["selection_status"] == "REJECTED" and clean["blocker"] == "NONE":
            raise ValueError(f"row {n} REJECTED candidate requires a blocker")

    return rows


def build_u3_representative_candidate_readout(path: Path) -> dict:
    rows = load_u3_representative_candidate_audit(path)
    selected = [r for r in rows if r["selection_status"] == "SELECTED"]
    selected_families = {r["family"] for r in selected}
    open_families = sorted(TARGET_FAMILIES - selected_families)
    strongest_open = {
        family: sorted(
            (
                r["candidate_taxon"]
                for r in rows
                if r["family"] == family
                and r["selection_status"] == "OPEN"
                and r["heteranthery_evidence_status"] == "PASS"
                and r["taxonomy_status"] == "PASS"
                and r["pre2010_evidence_status"] == "PASS"
            ),
            key=str.casefold,
        )
        for family in sorted(TARGET_FAMILIES)
    }
    return {
        "analysis": "balance_u3_representative_candidate_audit",
        "n_candidates": len(rows),
        "selection_status_counts": dict(
            sorted(Counter(r["selection_status"] for r in rows).items())
        ),
        "selected_representatives": {
            r["family"]: r["candidate_taxon"] for r in sorted(selected, key=lambda x: x["family"])
        },
        "strongest_open_candidates": strongest_open,
        "open_families": open_families,
        "n_open_families": len(open_families),
        "representative_identity_closed": not open_families,
        "claim_ceiling": (
            "representative_candidate_search_and_exclusion_receipts_only_"
            "not_table_s1_identity_without_exact_linkage_or_review_unique_independent_resolution"
        ),
    }

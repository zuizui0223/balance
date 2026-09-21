"""Evidence-state guard for U1 full-review taxon reconstruction."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "reference_id",
    "citation_short",
    "taxon_raw",
    "review_signal",
    "figure4_status",
    "primary_scope",
    "coverage_status",
    "full47_promotion_status",
    "notes",
)

REVIEW_SIGNAL = {
    "FIGURE4_MAPPED",
    "ARTICLE_BODY_INCLUDED",
    "ARTICLE_MECHANISTIC_CITATION",
    "REFERENCE_ONLY",
    "NO_DIRECT_REVIEW_MAPPING_RECOVERED",
}
FIGURE4 = {"PRESENT", "ABSENT"}
COVERAGE = {
    "FIGURE4_MAPPED_INCLUDED",
    "ARTICLE_BODY_INCLUDED_NONNETWORK",
    "ARTICLE_TRIANGULATED_NONNETWORK",
    "BACKGROUND_OR_INCLUDED_UNRESOLVED",
    "NO_DIRECT_MAPPING",
    "SUPPLEMENT_CONFIRMED_NONNETWORK",
}
PROMOTION = {
    "CANONICAL_NETWORK_VISIBLE",
    "SUPPLEMENT_CONFIRMATION_REQUIRED",
    "CANONICAL_SUPPLEMENT_ONLY",
}


def load_u1_reference_coverage(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U1 reference coverage columns must match canonical order")
        rows = list(reader)
    if not rows:
        raise ValueError("U1 reference coverage must contain at least one row")

    seen: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U1 reference schema")
        for field in FIELDS[:-1]:
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"row {n} {field} must be frozen")
        if row["reference_id"] in seen:
            raise ValueError(f"duplicate reference_id {row['reference_id']!r}")
        seen.add(row["reference_id"])
        if row["review_signal"] not in REVIEW_SIGNAL:
            raise ValueError(f"row {n} invalid review_signal")
        if row["figure4_status"] not in FIGURE4:
            raise ValueError(f"row {n} invalid figure4_status")
        if row["coverage_status"] not in COVERAGE:
            raise ValueError(f"row {n} invalid coverage_status")
        if row["full47_promotion_status"] not in PROMOTION:
            raise ValueError(f"row {n} invalid full47_promotion_status")

        if row["full47_promotion_status"] == "CANONICAL_NETWORK_VISIBLE":
            if row["figure4_status"] != "PRESENT":
                raise ValueError(f"row {n} network-visible promotion requires PRESENT")
            if row["coverage_status"] != "FIGURE4_MAPPED_INCLUDED":
                raise ValueError(f"row {n} network-visible promotion requires mapped coverage")

        if row["full47_promotion_status"] == "CANONICAL_SUPPLEMENT_ONLY":
            if row["figure4_status"] != "ABSENT":
                raise ValueError(f"row {n} supplement-only promotion requires ABSENT")
            if row["coverage_status"] != "SUPPLEMENT_CONFIRMED_NONNETWORK":
                raise ValueError(
                    f"row {n} supplement-only promotion requires direct supplement confirmation"
                )

        if (
            row["figure4_status"] == "ABSENT"
            and row["coverage_status"] != "SUPPLEMENT_CONFIRMED_NONNETWORK"
            and row["full47_promotion_status"] != "SUPPLEMENT_CONFIRMATION_REQUIRED"
        ):
            raise ValueError(
                f"row {n} absent non-supplement-confirmed taxon must fail closed"
            )
    return rows


def build_u1_reference_readout_from_rows(rows: list[dict[str, str]]) -> dict:
    supplement_only = [
        r for r in rows
        if r["full47_promotion_status"] == "CANONICAL_SUPPLEMENT_ONLY"
    ]
    pending = [
        r for r in rows
        if r["full47_promotion_status"] == "SUPPLEMENT_CONFIRMATION_REQUIRED"
    ]
    leading = [
        r["taxon_raw"]
        for r in rows
        if r["coverage_status"] in {
            "ARTICLE_BODY_INCLUDED_NONNETWORK",
            "ARTICLE_TRIANGULATED_NONNETWORK",
        }
    ]
    return {
        "analysis": "balance_plant_u1_reference_coverage",
        "n_rows": len(rows),
        "coverage_status_counts": dict(
            sorted(Counter(r["coverage_status"] for r in rows).items())
        ),
        "n_canonical_supplement_only_taxa": len(supplement_only),
        "canonical_supplement_only_taxa": sorted(r["taxon_raw"] for r in supplement_only),
        "n_pending_supplement_confirmation": len(pending),
        "leading_nonnetwork_candidates": sorted(leading),
        "full47_supplement_gap_closed": len(supplement_only) == 3,
        "claim_ceiling": (
            "article_and_figure4_evidence_triage_only_"
            "supplement_only_taxa_require_direct_supplement_confirmation"
        ),
    }


def build_u1_reference_readout(path: Path) -> dict:
    return build_u1_reference_readout_from_rows(load_u1_reference_coverage(path))

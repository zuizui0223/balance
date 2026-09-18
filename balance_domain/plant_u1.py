"""Outcome-blind U1 plant review-universe reconciliation and source-resolution guards."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


UNIVERSE_FIELDS = (
    "universe_record_id",
    "universe_id",
    "dependency_group",
    "taxon_raw",
    "source_review",
    "source_review_doi",
    "source_surface",
    "screening_status",
    "primary_source_status",
    "existing_balance_overlap",
    "notes",
)

SAMPLE_FIELDS = (
    "sample_order",
    "universe_record_id",
    "dependency_group",
    "taxon_raw",
    "selection_rule",
    "primary_source_status",
    "double_code_status",
)

RESOLUTION_FIELDS = (
    "sample_order",
    "universe_record_id",
    "dependency_group",
    "taxon_raw",
    "source_status",
    "primary_citation",
    "doi",
    "evidence_surface",
    "taxon_reconciliation",
    "screen_ready",
    "notes",
)

SOURCE_STATUS = {
    "RESOLVED_PRIMARY",
    "CANDIDATE_SOURCE_FOUND",
    "SOURCE_RESOLUTION_PENDING",
}
SCREEN_READY = {"true", "false"}

EXPECTED_REVIEW_TAXA = 47
EXPECTED_NETWORK_VISIBLE_LABELS = 44
EXPECTED_PROVISIONAL_SAMPLE_SIZE = 20


def _load_exact(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.name} columns must match canonical order")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path.name} must contain at least one row")
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"{path.name} row {n} has fields outside schema")
    return rows


def load_u1_universe(path: Path) -> list[dict[str, str]]:
    rows = _load_exact(path, UNIVERSE_FIELDS)
    ids = [r["universe_record_id"].strip() for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("U1 universe_record_id must be unique")
    if {r["universe_id"] for r in rows} != {"U1_HAAS_LORTIE_2020"}:
        raise ValueError("U1 universe must use one frozen source-universe id")
    if len(rows) != EXPECTED_NETWORK_VISIBLE_LABELS:
        raise ValueError(
            "U1 network-visible extraction must remain at 44 labels until "
            "supplement-only taxa are explicitly recovered rather than silently mixed in"
        )
    return rows


def load_u1_sample(path: Path) -> list[dict[str, str]]:
    rows = _load_exact(path, SAMPLE_FIELDS)
    if len(rows) != EXPECTED_PROVISIONAL_SAMPLE_SIZE:
        raise ValueError("U1 provisional double-code sample must contain 20 rows")
    orders = [int(r["sample_order"]) for r in rows]
    if orders != list(range(1, EXPECTED_PROVISIONAL_SAMPLE_SIZE + 1)):
        raise ValueError("U1 sample_order must be exactly 1..20")
    if len({r["universe_record_id"] for r in rows}) != len(rows):
        raise ValueError("U1 sample universe_record_id must be unique")
    return rows


def load_u1_source_resolution(path: Path) -> list[dict[str, str]]:
    rows = _load_exact(path, RESOLUTION_FIELDS)
    if len(rows) != EXPECTED_PROVISIONAL_SAMPLE_SIZE:
        raise ValueError(
            "U1 source-resolution ledger must contain the full 20-row provisional sample"
        )
    for n, row in enumerate(rows, start=2):
        if row["source_status"] not in SOURCE_STATUS:
            raise ValueError(f"row {n} has invalid source_status")
        ready = row["screen_ready"].casefold()
        if ready not in SCREEN_READY:
            raise ValueError(f"row {n} screen_ready must be literal true or false")
        row["screen_ready"] = ready
        if ready == "true":
            if row["source_status"] != "RESOLVED_PRIMARY":
                raise ValueError(f"row {n} screen_ready requires RESOLVED_PRIMARY")
            if not row["primary_citation"].strip():
                raise ValueError(f"row {n} screen_ready requires a primary citation")
            if row["taxon_reconciliation"] != "CLEAR":
                raise ValueError(
                    f"row {n} screen_ready requires CLEAR taxon reconciliation"
                )
    return rows


def validate_u1_handoff(
    universe_rows: list[dict[str, str]],
    sample_rows: list[dict[str, str]],
    resolution_rows: list[dict[str, str]],
) -> dict:
    """Validate the provisional U1 network-visible sample without overclaiming the full review frame."""
    universe_by_id = {r["universe_record_id"]: r for r in universe_rows}
    resolution_by_id = {r["universe_record_id"]: r for r in resolution_rows}

    for sample in sample_rows:
        uid = sample["universe_record_id"]
        if uid not in universe_by_id:
            raise ValueError(f"sample row {uid!r} is absent from U1 network-visible universe")
        if uid not in resolution_by_id:
            raise ValueError(f"sample row {uid!r} lacks source-resolution row")
        universe = universe_by_id[uid]
        resolution = resolution_by_id[uid]
        for field in ("dependency_group", "taxon_raw"):
            if sample[field] != universe[field] or sample[field] != resolution[field]:
                raise ValueError(f"U1 handoff mismatch for {uid!r} field {field}")

        if sample["primary_source_status"] != resolution["source_status"]:
            raise ValueError(f"U1 sample source status drift for {uid!r}")

    # The current sample is deliberately the first 20 raw network-visible taxon labels
    # while the supplement-only taxa and taxonomic grain remain unresolved.
    expected = sorted(
        universe_rows,
        key=lambda r: (r["taxon_raw"].casefold(), r["universe_record_id"]),
    )[:EXPECTED_PROVISIONAL_SAMPLE_SIZE]
    if [r["universe_record_id"] for r in sample_rows] != [
        r["universe_record_id"] for r in expected
    ]:
        raise ValueError("U1 provisional sample no longer matches lexicographic rule")

    source_ready = sum(r["screen_ready"] == "true" for r in resolution_rows)
    taxon_conflicts = [
        r["universe_record_id"]
        for r in resolution_rows
        if r["taxon_reconciliation"].startswith("TAXON_GRAIN_CONFLICT")
    ]

    # Haas & Lortie report 47 taxa overall. Figure 4 omits plant species from studies
    # without actual herbivore/pollinator taxa (e.g. artificial damage/hand pollination),
    # so the current 44 labels are a network-visible subset, not an extraction-completeness claim.
    supplement_only_taxa_needed = EXPECTED_REVIEW_TAXA - len(universe_rows)
    if supplement_only_taxa_needed < 0:
        raise ValueError("U1 network-visible extraction exceeds review-reported taxon count")

    sample_frozen = (
        supplement_only_taxa_needed == 0
        and not taxon_conflicts
        and all(r["screen_ready"] == "true" for r in resolution_rows)
    )

    return {
        "analysis": "balance_plant_u1_handoff",
        "review_reported_taxa": EXPECTED_REVIEW_TAXA,
        "network_visible_taxon_labels": len(universe_rows),
        "network_visible_expected_labels": EXPECTED_NETWORK_VISIBLE_LABELS,
        "supplement_only_taxa_to_recover": supplement_only_taxa_needed,
        "provisional_sample_size": len(sample_rows),
        "source_status_counts": dict(
            sorted(Counter(r["source_status"] for r in resolution_rows).items())
        ),
        "n_source_ready": source_ready,
        "n_taxon_grain_conflicts": len(taxon_conflicts),
        "taxon_grain_conflict_records": sorted(taxon_conflicts),
        "double_code_sample_frozen": sample_frozen,
        "claim_ceiling": (
            "outcome_blind_network_visible_review_subset_only_"
            "not_confirmatory_until_supplement_taxa_taxon_grain_and_sources_reconcile"
        ),
    }


def build_u1_handoff(
    universe_path: Path,
    sample_path: Path,
    resolution_path: Path,
) -> dict:
    return validate_u1_handoff(
        load_u1_universe(universe_path),
        load_u1_sample(sample_path),
        load_u1_source_resolution(resolution_path),
    )

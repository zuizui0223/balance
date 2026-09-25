"""Prospective U3 routing-expansion queue frozen before control outcomes.

The queue is not a list of controls. It freezes which new heterantherous case
families are attempted, and in what order, before conflict or routing
architecture is extracted for any prospective control.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .plant_u3 import load_u3_universe


FIELDS = (
    "queue_order",
    "family",
    "case_taxon",
    "representative_status",
    "case_source_basis",
    "new_dependence_block_id",
    "selection_rule",
    "control_search_status",
    "predictor_blinding_status",
    "notes",
)

SELECTION_RULE = (
    "ALL_INDEPENDENT_SPECIES_REPRESENTATIVES_OUTSIDE_EXISTING_MATCHED_"
    "FAMILIES_SORT_FAMILY_LEXICOGRAPHIC"
)
BLINDING = "FROZEN_BEFORE_CONTROL_CONFLICT_OR_ROUTING_EXTRACTION"
CURRENT_MATCHED_FAMILIES = {
    "Fabaceae",
    "Melastomataceae",
    "Pontederiaceae",
    "Solanaceae",
}
REP_STATUS = "SOURCE_RESOLVED_INDEPENDENTLY"
CONTROL_SEARCH = {
    "NOT_STARTED",
    "IN_PROGRESS",
    "CLOSED",
    "FAILED",
    "EVIDENCE_CEILING_BLOCKED",
}
EXPECTED_FAMILIES = ["Bixaceae", "Brassicaceae", "Lythraceae", "Malvaceae"]


def _is_species_level(name: str) -> bool:
    lowered = name.casefold()
    return (
        " " in name.strip()
        and ";" not in name
        and " spp" not in lowered
        and not lowered.endswith(" sp.")
    )


def load_u3_routing_expansion_queue(
    path: Path,
    universe_path: Path,
) -> list[dict[str, str]]:
    universe = load_u3_universe(universe_path)
    by_family = {r["family"]: r for r in universe}

    eligible = sorted(
        (
            r
            for r in universe
            if r["family"] not in CURRENT_MATCHED_FAMILIES
            and r["representative_taxa_status"] == REP_STATUS
            and _is_species_level(r["representative_taxa"])
        ),
        key=lambda r: r["family"].casefold(),
    )
    eligible_families = [r["family"] for r in eligible]
    if eligible_families != EXPECTED_FAMILIES:
        raise ValueError(
            f"U3 routing expansion eligibility drift: {eligible_families!r}"
        )

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 routing expansion queue columns must match canonical order")
        rows = list(reader)

    if len(rows) != len(eligible):
        raise ValueError("U3 routing expansion queue must cover every eligible family once")

    orders = [int(r["queue_order"]) for r in rows]
    if orders != list(range(1, len(rows) + 1)):
        raise ValueError("U3 routing expansion queue_order must be exactly 1..N")

    seen_blocks: set[str] = set()
    for n, (row, expected) in enumerate(zip(rows, eligible), start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U3 routing queue schema")
        if row["family"] != expected["family"]:
            raise ValueError(f"row {n} family violates frozen lexicographic queue")
        if row["case_taxon"] != expected["representative_taxa"]:
            raise ValueError(f"row {n} case taxon disagrees with U3 representative")
        if row["representative_status"] != REP_STATUS:
            raise ValueError(f"row {n} must use independent representative status")
        if row["selection_rule"] != SELECTION_RULE:
            raise ValueError(f"row {n} selection_rule drift")
        if row["predictor_blinding_status"] != BLINDING:
            raise ValueError(f"row {n} predictor blinding drift")
        if row["control_search_status"] not in CONTROL_SEARCH:
            raise ValueError(f"row {n} invalid control_search_status")
        block = row["new_dependence_block_id"]
        if not block or block in seen_blocks:
            raise ValueError(f"row {n} dependence block must be unique and frozen")
        seen_blocks.add(block)
        if not row["case_source_basis"].strip():
            raise ValueError(f"row {n} case_source_basis must be frozen")
        if row["family"] not in by_family:
            raise ValueError(f"row {n} family absent from U3 universe")
    in_progress = [i for i, r in enumerate(rows) if r["control_search_status"] == "IN_PROGRESS"]
    if len(in_progress) > 1:
        raise ValueError("U3 routing expansion queue allows at most one IN_PROGRESS case")
    if in_progress:
        active_i = in_progress[0]
        terminal = {"CLOSED", "FAILED", "EVIDENCE_CEILING_BLOCKED"}
        if any(r["control_search_status"] not in terminal for r in rows[:active_i]):
            raise ValueError(
                "all cases before the active queue row must have a frozen terminal/blocking receipt"
            )
        if any(r["control_search_status"] != "NOT_STARTED" for r in rows[active_i + 1 :]):
            raise ValueError("cases after the active queue row must remain NOT_STARTED")

    return rows


def build_u3_routing_expansion_readout(path: Path, universe_path: Path) -> dict:
    rows = load_u3_routing_expansion_queue(path, universe_path)
    active = [r for r in rows if r["control_search_status"] == "IN_PROGRESS"]
    return {
        "analysis": "balance_u3_prospective_routing_expansion_queue",
        "n_queued_families": len(rows),
        "queued_families": [r["family"] for r in rows],
        "queued_case_taxa": [r["case_taxon"] for r in rows],
        "first_case_family": rows[0]["family"],
        "first_case_taxon": rows[0]["case_taxon"],
        "n_new_dependence_blocks": len({r["new_dependence_block_id"] for r in rows}),
        "queue_frozen_before_control_outcomes": True,
        "n_control_search_not_started": sum(
            r["control_search_status"] == "NOT_STARTED" for r in rows
        ),
        "n_evidence_ceiling_blocked": sum(
            r["control_search_status"] == "EVIDENCE_CEILING_BLOCKED" for r in rows
        ),
        "next_active_case": active[0]["case_taxon"] if active else None,
        "progression_rule": (
            "advance_only_after_prior_case_has_CLOSED_FAILED_or_"
            "EVIDENCE_CEILING_BLOCKED_matching_stage_receipt; retain_blocked_cases_"
            "as_missing_dependence_blocks_and_never_drop_them_for_outcome_convenience"
        ),
        "claim_ceiling": (
            "prospective_case_order_and_blinded_control_acquisition_only_"
            "not_control_eligibility_not_conflict_status_not_routing_effect"
        ),
    }

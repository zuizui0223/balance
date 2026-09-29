"""Search ledger for replacement nonheterantherous Senna controls in U3."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


FIELDS = (
    "case_taxon",
    "candidate_control",
    "phylogenetic_proximity_status",
    "heteranthery_absence_status",
    "animal_pollination_status",
    "candidate_status",
    "source_basis",
    "notes",
)

PHYLO = {"SISTER_RELATIVE", "CLOSE_RELATIVE", "PHYLOGENETIC_DISTANCE_OPEN"}
HET = {"PASS", "FAIL"}
POLL = {"CONFIRMED_BUZZ_POLLINATION", "FLORAL_RESOURCE_ONLY", "UNRESOLVED"}
STATUS = {"EXCLUDED_HETERANTHEROUS", "CANDIDATE_OPEN", "ELIGIBLE_NOT_SELECTED"}
CASES = {"Senna alata", "Senna bicapsularis"}


def load_u3_senna_control_search(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 Senna control-search columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("U3 Senna control search must contain candidates")

    seen: set[tuple[str, str]] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U3 Senna search schema")
        key = (row["case_taxon"], row["candidate_control"])
        if key in seen:
            raise ValueError(f"duplicate Senna candidate pair {key!r}")
        seen.add(key)

        if row["case_taxon"] not in CASES:
            raise ValueError(f"row {n} unknown Senna case")
        if row["phylogenetic_proximity_status"] not in PHYLO:
            raise ValueError(f"row {n} invalid phylogenetic_proximity_status")
        if row["heteranthery_absence_status"] not in HET:
            raise ValueError(f"row {n} invalid heteranthery_absence_status")
        if row["animal_pollination_status"] not in POLL:
            raise ValueError(f"row {n} invalid animal_pollination_status")
        if row["candidate_status"] not in STATUS:
            raise ValueError(f"row {n} invalid candidate_status")
        if not row["source_basis"].strip():
            raise ValueError(f"row {n} source_basis must be frozen")

        if row["candidate_status"] == "EXCLUDED_HETERANTHEROUS":
            if row["heteranthery_absence_status"] != "FAIL":
                raise ValueError(
                    f"row {n} excluded heterantherous candidate must fail absence gate"
                )
        if row["candidate_status"] == "ELIGIBLE_NOT_SELECTED":
            if row["heteranthery_absence_status"] != "PASS":
                raise ValueError(f"row {n} eligible candidate must pass heteranthery absence")
            if row["animal_pollination_status"] != "CONFIRMED_BUZZ_POLLINATION":
                raise ValueError(f"row {n} eligible candidate requires confirmed animal pollination")
            if row["phylogenetic_proximity_status"] == "PHYLOGENETIC_DISTANCE_OPEN":
                raise ValueError(f"row {n} eligible candidate requires closed phylogenetic distance")

    return rows


def build_u3_senna_control_search_readout(path: Path) -> dict:
    rows = load_u3_senna_control_search(path)
    by_case: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_case[row["case_taxon"]].append(row)

    return {
        "analysis": "balance_plant_u3_senna_control_search",
        "n_candidates": len(rows),
        "candidate_status_counts": dict(
            sorted(Counter(r["candidate_status"] for r in rows).items())
        ),
        "excluded_close_relative_counts": {
            case: sum(
                r["candidate_status"] == "EXCLUDED_HETERANTHEROUS"
                and r["phylogenetic_proximity_status"] in {"SISTER_RELATIVE", "CLOSE_RELATIVE"}
                for r in group
            )
            for case, group in sorted(by_case.items())
        },
        "open_homantherous_candidates": {
            case: sorted(
                r["candidate_control"]
                for r in group
                if r["candidate_status"] == "CANDIDATE_OPEN"
                and r["heteranthery_absence_status"] == "PASS"
            )
            for case, group in sorted(by_case.items())
        },
        "n_eligible_not_selected": sum(
            r["candidate_status"] == "ELIGIBLE_NOT_SELECTED" for r in rows
        ),
        "claim_ceiling": (
            "replacement_control_search_audit_only_"
            "no_control_selection_until_phylogeny_pollination_and_absence_gates_close"
        ),
    }

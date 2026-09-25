"""Fail-closed prospective Bixaceae control search for Amoreuxia wrightii."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "candidate_id",
    "case_taxon",
    "candidate_control",
    "candidate_role",
    "taxonomic_relation",
    "heteranthery_absence_status",
    "animal_pollination_status",
    "phylogenetic_proximity_status",
    "closest_eligible_search_status",
    "selection_status",
    "source_id",
    "blocker",
    "notes",
)

ROLE = {"INCUMBENT", "FALLBACK"}
GATE = {"PASS", "OPEN", "FAIL"}
STATUS = {"OPEN", "SCREENED", "REJECTED"}
EXPECTED = {
    "Cochlospermum tetraporum",
    "Cochlospermum orinocense",
    "Cochlospermum vitifolium",
}


def load_u3_bixaceae_control_search(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 Bixaceae control-search columns must match canonical order")
        rows = list(reader)

    if {r["candidate_control"] for r in rows} != EXPECTED:
        raise ValueError("U3 Bixaceae search must retain the three frozen candidate receipts")

    seen: set[str] = set()
    incumbents = 0
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside Bixaceae search schema")
        clean = {k: (v or "").strip() for k, v in row.items()}
        if clean["candidate_id"] in seen:
            raise ValueError(f"duplicate candidate_id {clean['candidate_id']!r}")
        seen.add(clean["candidate_id"])
        if clean["case_taxon"] != "Amoreuxia wrightii":
            raise ValueError(f"row {n} wrong prospective case taxon")
        if clean["candidate_role"] not in ROLE:
            raise ValueError(f"row {n} invalid candidate role")
        incumbents += clean["candidate_role"] == "INCUMBENT"
        for field in (
            "heteranthery_absence_status",
            "animal_pollination_status",
            "phylogenetic_proximity_status",
            "closest_eligible_search_status",
        ):
            if clean[field] not in GATE:
                raise ValueError(f"row {n} invalid {field}")
        if clean["selection_status"] not in STATUS:
            raise ValueError(f"row {n} invalid selection_status")
        if clean["selection_status"] == "OPEN":
            if "FAIL" in (
                clean["heteranthery_absence_status"],
                clean["animal_pollination_status"],
                clean["phylogenetic_proximity_status"],
                clean["closest_eligible_search_status"],
            ):
                raise ValueError(f"row {n} OPEN candidate cannot contain FAIL")
            if not clean["blocker"]:
                raise ValueError(f"row {n} OPEN candidate requires blocker")
        if not clean["source_id"]:
            raise ValueError(f"row {n} source_id must be frozen")
        row.update(clean)

    if incumbents != 1:
        raise ValueError("U3 Bixaceae search requires exactly one incumbent nearest candidate")

    incumbent = next(r for r in rows if r["candidate_role"] == "INCUMBENT")
    if incumbent["candidate_control"] != "Cochlospermum tetraporum":
        raise ValueError("C. tetraporum must remain the frozen nearest incumbent")
    if incumbent["phylogenetic_proximity_status"] != "PASS":
        raise ValueError("nearest C. tetraporum phylogenetic gate must remain PASS")
    if incumbent["heteranthery_absence_status"] != "PASS":
        raise ValueError("nearest C. tetraporum absence gate must remain PASS")
    if incumbent["animal_pollination_status"] != "OPEN":
        raise ValueError("C. tetraporum animal-pollination gate is not source-closed")
    if incumbent["selection_status"] != "OPEN":
        raise ValueError("Bixaceae control cannot close while nearest eligibility is OPEN")

    for row in rows:
        if row["candidate_role"] == "FALLBACK":
            if row["selection_status"] != "OPEN":
                raise ValueError("fallbacks stay OPEN while nearer candidate eligibility is OPEN")
            if row["closest_eligible_search_status"] != "OPEN":
                raise ValueError("fallback closest-search gate must stay OPEN")
            if row["blocker"] != "CLOSER_C_TETRAPORUM_ELIGIBILITY_OPEN":
                raise ValueError("fallback must be blocked by the nearer candidate")

    return rows


def build_u3_bixaceae_control_search_readout(path: Path) -> dict:
    rows = load_u3_bixaceae_control_search(path)
    incumbent = next(r for r in rows if r["candidate_role"] == "INCUMBENT")
    return {
        "analysis": "balance_u3_bixaceae_prospective_control_search",
        "n_candidates": len(rows),
        "status_counts": dict(sorted(Counter(r["selection_status"] for r in rows).items())),
        "nearest_candidate": incumbent["candidate_control"],
        "nearest_candidate_animal_pollination_status": incumbent["animal_pollination_status"],
        "fallbacks_with_animal_pollination_pass": sorted(
            r["candidate_control"]
            for r in rows
            if r["candidate_role"] == "FALLBACK"
            and r["animal_pollination_status"] == "PASS"
        ),
        "control_selected": False,
        "search_closed": False,
        "blocker": "CLOSEST_C_TETRAPORUM_ANIMAL_POLLINATION_ELIGIBILITY_OPEN",
        "claim_ceiling": (
            "blinded_control_candidate_search_only_not_control_selection_"
            "not_conflict_extraction_not_routing_architecture"
        ),
    }

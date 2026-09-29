"""Fail-closed prospective Brassicaceae control search for Brassica rapa."""
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

ROLE = {"NEAR_RELATIVE", "FAMILY_LEVEL_CANDIDATE"}
GATE = {"PASS", "OPEN", "FAIL"}
STATUS = {"OPEN", "SCREENED", "REJECTED"}
EXPECTED = {
    "Brassica oleracea",
    "Brassica napus",
    "Diplotaxis erucoides",
    "Raphanus raphanistrum",
    "Stanleya elata",
    "Stanleya pinnata",
}


def load_u3_brassicaceae_control_search(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 Brassicaceae control-search columns must match canonical order")
        rows = list(reader)

    if {r["candidate_control"] for r in rows} != EXPECTED:
        raise ValueError("U3 Brassicaceae search must retain the frozen candidate set")

    seen: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside Brassicaceae search schema")
        clean = {k: (v or "").strip() for k, v in row.items()}
        if clean["candidate_id"] in seen:
            raise ValueError(f"duplicate candidate_id {clean['candidate_id']!r}")
        seen.add(clean["candidate_id"])
        if clean["case_taxon"] != "Brassica rapa":
            raise ValueError(f"row {n} wrong prospective case taxon")
        if clean["candidate_role"] not in ROLE:
            raise ValueError(f"row {n} invalid candidate role")
        for field in (
            "heteranthery_absence_status",
            "animal_pollination_status",
            "phylogenetic_proximity_status",
            "closest_eligible_search_status",
        ):
            if clean[field] not in GATE:
                raise ValueError(f"row {n} invalid {field}")
        if clean["selection_status"] not in STATUS:
            raise ValueError(f"row {n} invalid selection status")
        if clean["selection_status"] == "REJECTED":
            if "FAIL" not in (
                clean["heteranthery_absence_status"],
                clean["animal_pollination_status"],
                clean["phylogenetic_proximity_status"],
                clean["closest_eligible_search_status"],
            ):
                raise ValueError(f"row {n} REJECTED candidate requires a failed gate")
        elif clean["selection_status"] == "OPEN":
            if "FAIL" in (
                clean["heteranthery_absence_status"],
                clean["animal_pollination_status"],
                clean["phylogenetic_proximity_status"],
                clean["closest_eligible_search_status"],
            ):
                raise ValueError(f"row {n} OPEN candidate cannot contain a failed gate")
            if "OPEN" not in (
                clean["heteranthery_absence_status"],
                clean["animal_pollination_status"],
                clean["phylogenetic_proximity_status"],
                clean["closest_eligible_search_status"],
            ):
                raise ValueError(f"row {n} OPEN candidate requires an open gate")
        if not clean["source_id"] or not clean["blocker"]:
            raise ValueError(f"row {n} source_id and blocker must be frozen")
        row.update(clean)

    near = [r for r in rows if r["candidate_role"] == "NEAR_RELATIVE"]
    if not near or any(r["selection_status"] != "REJECTED" for r in near):
        raise ValueError("all frozen close Brassiceae candidates must remain rejected")
    if any(r["heteranthery_absence_status"] != "FAIL" for r in near):
        raise ValueError("close Brassiceae candidates are rejected by the absence gate")

    family = [r for r in rows if r["candidate_role"] == "FAMILY_LEVEL_CANDIDATE"]
    if len(family) < 2:
        raise ValueError("retain multiple family-level equal-stamen candidates")
    if any(r["heteranthery_absence_status"] != "PASS" for r in family):
        raise ValueError("family-level candidates must pass the negative morphology gate")
    if any(r["animal_pollination_status"] != "PASS" for r in family):
        raise ValueError("family-level candidates must pass animal-pollination eligibility")
    if any(r["phylogenetic_proximity_status"] != "OPEN" for r in family):
        raise ValueError("family-level candidate ranking must remain source-open")
    if any(r["selection_status"] != "OPEN" for r in family):
        raise ValueError("no family-level control can be promoted before common ranking closes")
    return rows


def build_u3_brassicaceae_control_search_readout(path: Path) -> dict:
    rows = load_u3_brassicaceae_control_search(path)
    near = [r for r in rows if r["candidate_role"] == "NEAR_RELATIVE"]
    family = [r for r in rows if r["candidate_role"] == "FAMILY_LEVEL_CANDIDATE"]
    return {
        "analysis": "balance_u3_brassicaceae_prospective_control_search",
        "n_candidates": len(rows),
        "status_counts": dict(sorted(Counter(r["selection_status"] for r in rows).items())),
        "n_close_candidates_rejected_by_absence_gate": sum(
            r["heteranthery_absence_status"] == "FAIL" for r in near
        ),
        "biologically_eligible_family_level_candidates": sorted(
            r["candidate_control"] for r in family
        ),
        "control_selected": False,
        "search_closed": False,
        "blocker": "FAMILY_LEVEL_EQUAL_STAMEN_CLOSEST_PHYLOGENETIC_RANKING_OPEN",
        "claim_ceiling": (
            "blinded_control_candidate_search_only_not_control_selection_"
            "not_conflict_extraction_not_routing_architecture"
        ),
    }

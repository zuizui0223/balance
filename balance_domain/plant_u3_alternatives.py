"""Fail-closed alternative-control registry for U3 replacement searches."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .plant_u3_cases import load_u3_case_candidates


FIELDS = (
    "candidate_id",
    "case_taxon",
    "candidate_control",
    "candidate_role",
    "heteranthery_absence_status",
    "animal_pollination_status",
    "phylogenetic_proximity_status",
    "closest_eligible_search_status",
    "evidence_tier",
    "selection_status",
    "source_id",
    "blocker",
    "notes",
)

ROLE = {"INCUMBENT", "ALTERNATIVE", "REPLACEMENT"}
GATE = {"PASS", "OPEN", "FAIL"}
EVIDENCE_TIER = {"PRIMARY", "SECONDARY", "MIXED"}
STATUS = {"SCREENED", "OPEN", "REJECTED"}

GATE_FIELDS = (
    "heteranthery_absence_status",
    "animal_pollination_status",
    "phylogenetic_proximity_status",
    "closest_eligible_search_status",
)


def load_u3_control_alternatives(
    path: Path,
    case_path: Path,
    universe_path: Path,
) -> list[dict[str, str]]:
    cases = load_u3_case_candidates(case_path, universe_path)
    case_taxa = {r["case_taxon"] for r in cases}

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 alternative-control columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("U3 alternative-control registry must contain at least one row")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U3 alternative-control schema")
        clean = {k: (v or "").strip() for k, v in row.items()}

        candidate_id = clean["candidate_id"]
        if not candidate_id or candidate_id in seen:
            raise ValueError(f"row {n} candidate_id must be unique and frozen")
        seen.add(candidate_id)

        if clean["case_taxon"] not in case_taxa:
            raise ValueError(f"row {n} case taxon is absent from U3 case registry")
        if not clean["candidate_control"] or clean["candidate_control"] == clean["case_taxon"]:
            raise ValueError(f"row {n} candidate control must be a different frozen taxon")
        if clean["candidate_role"] not in ROLE:
            raise ValueError(f"row {n} invalid candidate_role")
        for field in GATE_FIELDS:
            if clean[field] not in GATE:
                raise ValueError(f"row {n} invalid {field}")
        if clean["evidence_tier"] not in EVIDENCE_TIER:
            raise ValueError(f"row {n} invalid evidence_tier")
        if clean["selection_status"] not in STATUS:
            raise ValueError(f"row {n} invalid selection_status")
        if not clean["source_id"]:
            raise ValueError(f"row {n} source_id must be frozen")

        gates = tuple(clean[field] for field in GATE_FIELDS)
        if clean["selection_status"] == "SCREENED":
            if any(g != "PASS" for g in gates):
                raise ValueError(f"row {n} SCREENED candidate requires all gates PASS")
            if clean["blocker"]:
                raise ValueError(f"row {n} SCREENED candidate cannot retain a blocker")
        elif clean["selection_status"] == "OPEN":
            if "FAIL" in gates:
                raise ValueError(f"row {n} OPEN candidate cannot contain a FAIL gate")
            if "OPEN" not in gates or not clean["blocker"]:
                raise ValueError(
                    f"row {n} OPEN candidate requires an open gate and explicit blocker"
                )
        else:
            if "FAIL" not in gates:
                raise ValueError(f"row {n} REJECTED candidate requires a FAIL gate")
            if not clean["blocker"]:
                raise ValueError(f"row {n} REJECTED candidate requires explicit blocker")

        out.append(clean)

    return out


def build_u3_control_alternatives_readout(
    path: Path,
    case_path: Path,
    universe_path: Path,
) -> dict:
    rows = load_u3_control_alternatives(path, case_path, universe_path)
    status = Counter(r["selection_status"] for r in rows)
    unresolved_cases = sorted(
        {r["case_taxon"] for r in rows if r["selection_status"] == "OPEN"}
    )
    rejected_controls = sorted(
        {r["candidate_control"] for r in rows if r["selection_status"] == "REJECTED"}
    )
    phylo_pass_search_open = [
        r
        for r in rows
        if r["phylogenetic_proximity_status"] == "PASS"
        and r["closest_eligible_search_status"] == "OPEN"
        and r["selection_status"] != "REJECTED"
    ]
    biologically_pass_search_open = [
        r
        for r in rows
        if all(
            r[field] == "PASS"
            for field in (
                "heteranthery_absence_status",
                "animal_pollination_status",
                "phylogenetic_proximity_status",
            )
        )
        and r["closest_eligible_search_status"] == "OPEN"
    ]
    return {
        "analysis": "balance_plant_u3_control_alternatives",
        "n_candidates": len(rows),
        "status_counts": dict(sorted(status.items())),
        "n_screened": status.get("SCREENED", 0),
        "n_open": status.get("OPEN", 0),
        "n_rejected": status.get("REJECTED", 0),
        "open_case_taxa": unresolved_cases,
        "rejected_controls": rejected_controls,
        "n_phylogenetic_pass_closest_search_open": len(phylo_pass_search_open),
        "n_biological_gates_pass_closest_search_open": len(
            biologically_pass_search_open
        ),
        "biological_pass_but_unselected_candidates": sorted(
            r["candidate_control"] for r in biologically_pass_search_open
        ),
        "candidate_search_closed": status.get("OPEN", 0) == 0,
        "claim_ceiling": (
            "candidate_search_receipts_only_not_matched_control_selection_"
            "not_effect_estimate_not_prevalence"
        ),
    }

"""Fail-closed adjudication receipts for U3 matched controls."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .plant_u3_controls import load_u3_matched_controls


FIELDS = (
    "pair_id",
    "case_taxon",
    "control_taxon",
    "phylogenetic_proximity_status",
    "heteranthery_absence_status",
    "animal_pollination_status",
    "closer_eligible_alternative_search",
    "tie_break_status",
    "predictor_blinding_status",
    "decision",
    "blocker",
    "evidence_receipt",
)

GATE = {"PASS", "OPEN", "FAIL"}
DECISION = {"PASS", "OPEN", "FAIL"}


def load_u3_control_adjudication(
    path: Path,
    pair_path: Path,
    case_path: Path,
    universe_path: Path,
) -> list[dict[str, str]]:
    pairs = load_u3_matched_controls(pair_path, case_path, universe_path)
    pair_by_id = {r["pair_id"]: r for r in pairs}

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 adjudication columns must match canonical order")
        rows = list(reader)

    if len(rows) != len(pair_by_id):
        raise ValueError(
            "U3 adjudication ledger must contain exactly one row for every registered pair"
        )

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    gate_fields = (
        "phylogenetic_proximity_status",
        "heteranthery_absence_status",
        "animal_pollination_status",
        "closer_eligible_alternative_search",
        "tie_break_status",
        "predictor_blinding_status",
    )

    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U3 adjudication schema")
        clean = {k: (v or "").strip() for k, v in row.items()}

        pair_id = clean["pair_id"]
        if not pair_id:
            raise ValueError(f"row {n} pair_id must be frozen")
        if pair_id in seen:
            raise ValueError(f"duplicate U3 adjudication pair_id {pair_id!r}")
        seen.add(pair_id)
        if pair_id not in pair_by_id:
            raise ValueError(f"row {n} adjudicates unknown pair {pair_id!r}")

        pair = pair_by_id[pair_id]
        if clean["case_taxon"] != pair["case_taxon"]:
            raise ValueError(f"row {n} case taxon disagrees with pair registry")
        if clean["control_taxon"] != pair["control_taxon"]:
            raise ValueError(f"row {n} control taxon disagrees with pair registry")

        for field in gate_fields:
            if clean[field] not in GATE:
                raise ValueError(f"row {n} invalid {field} {clean[field]!r}")
        if clean["decision"] not in DECISION:
            raise ValueError(f"row {n} invalid decision")

        gates = [clean[field] for field in gate_fields]
        if clean["decision"] == "PASS":
            if any(g != "PASS" for g in gates):
                raise ValueError(f"row {n} PASS decision requires all gates PASS")
            if clean["blocker"]:
                raise ValueError(f"row {n} PASS decision cannot retain a blocker")
            if pair["selection_status"] != "ADJUDICATED":
                raise ValueError(
                    f"row {n} PASS adjudication requires pair registry ADJUDICATED"
                )
        elif clean["decision"] == "OPEN":
            if "FAIL" in gates:
                raise ValueError(f"row {n} OPEN decision cannot contain a FAIL gate")
            if not clean["blocker"]:
                raise ValueError(f"row {n} OPEN decision requires an explicit blocker")
            if pair["selection_status"] != "SCREENED":
                raise ValueError(
                    f"row {n} OPEN adjudication requires pair registry SCREENED"
                )
        else:
            if "FAIL" not in gates:
                raise ValueError(f"row {n} FAIL decision requires at least one FAIL gate")
            if pair["selection_status"] != "REJECTED":
                raise ValueError(
                    f"row {n} FAIL adjudication requires pair registry REJECTED"
                )

        if not clean["evidence_receipt"]:
            raise ValueError(f"row {n} evidence_receipt must be frozen")
        out.append(clean)

    if seen != set(pair_by_id):
        raise ValueError("U3 adjudication pair coverage does not match pair registry")
    return out


def build_u3_control_adjudication_readout(
    path: Path,
    pair_path: Path,
    case_path: Path,
    universe_path: Path,
) -> dict:
    rows = load_u3_control_adjudication(
        path, pair_path, case_path, universe_path
    )
    decisions = Counter(r["decision"] for r in rows)
    open_rows = [r for r in rows if r["decision"] == "OPEN"]
    return {
        "analysis": "balance_plant_u3_control_adjudication",
        "n_pairs": len(rows),
        "decision_counts": dict(sorted(decisions.items())),
        "n_pass": decisions.get("PASS", 0),
        "n_open": decisions.get("OPEN", 0),
        "n_fail": decisions.get("FAIL", 0),
        "open_pair_ids": sorted(r["pair_id"] for r in open_rows),
        "open_blockers": {
            r["pair_id"]: r["blocker"] for r in sorted(open_rows, key=lambda x: x["pair_id"])
        },
        "adjudication_closed": decisions.get("OPEN", 0) == 0
        and decisions.get("FAIL", 0) == 0,
        "claim_ceiling": (
            "matched_control_selection_adjudication_only_"
            "not_effect_estimate_not_prevalence_not_historical_causation"
        ),
    }

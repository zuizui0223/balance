"""Strict conflict-screen guards for the Barrett-2002 U2 sexual-interference universe."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "universe_record_id",
    "dependency_group",
    "taxon_raw",
    "conflict_status",
    "same_coordinate_evidence",
    "opposing_demand_evidence",
    "screen_decision",
    "reason_code",
    "source_basis",
    "claim_ceiling",
    "notes",
)

CONFLICT = {
    "POSITIVE",
    "ALIGNED_NO_CONFLICT",
    "NO_DEMONSTRATED_CONFLICT",
    "UNRESOLVED_CANDIDATE",
}
COORDINATE = {"YES", "PARTIAL", "NO", "UNRESOLVED"}
OPPOSING = {"YES", "NO", "INDIRECT_OR_AMBIGUOUS"}
DECISION = {"PASS_CONFLICT_GATE", "FAIL_CONFLICT_GATE", "HOLD_FOR_FULL_TEXT"}
EXPECTED_ROWS = 22


def load_u2_conflict_screen(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U2 conflict-screen columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_ROWS:
        raise ValueError("U2 conflict screen must contain all 22 dependency groups")

    seen: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U2 conflict-screen schema")
        if row["universe_record_id"] in seen:
            raise ValueError(f"duplicate U2 conflict-screen id {row['universe_record_id']!r}")
        seen.add(row["universe_record_id"])

        if row["conflict_status"] not in CONFLICT:
            raise ValueError(f"row {n} invalid conflict_status")
        if row["same_coordinate_evidence"] not in COORDINATE:
            raise ValueError(f"row {n} invalid same_coordinate_evidence")
        if row["opposing_demand_evidence"] not in OPPOSING:
            raise ValueError(f"row {n} invalid opposing_demand_evidence")
        if row["screen_decision"] not in DECISION:
            raise ValueError(f"row {n} invalid screen_decision")

        if row["conflict_status"] == "POSITIVE":
            if row["same_coordinate_evidence"] != "YES":
                raise ValueError(f"row {n} positive U2 conflict requires same-coordinate evidence")
            if row["opposing_demand_evidence"] != "YES":
                raise ValueError(f"row {n} positive U2 conflict requires opposing-demand evidence")
            if row["screen_decision"] != "PASS_CONFLICT_GATE":
                raise ValueError(f"row {n} positive U2 conflict must pass the gate")
        elif row["conflict_status"] in {
            "ALIGNED_NO_CONFLICT",
            "NO_DEMONSTRATED_CONFLICT",
        }:
            if row["screen_decision"] != "FAIL_CONFLICT_GATE":
                raise ValueError(f"row {n} negative U2 conflict status must fail the gate")
        else:
            if row["screen_decision"] != "HOLD_FOR_FULL_TEXT":
                raise ValueError(f"row {n} unresolved U2 candidate must be held")

    return rows


def build_u2_conflict_screen_readout_from_rows(rows: list[dict[str, str]]) -> dict:
    conflict = Counter(r["conflict_status"] for r in rows)
    decision = Counter(r["screen_decision"] for r in rows)
    return {
        "analysis": "balance_plant_u2_strict_conflict_screen",
        "n_dependency_groups": len(rows),
        "conflict_status_counts": dict(sorted(conflict.items())),
        "screen_decision_counts": dict(sorted(decision.items())),
        "n_positive_conflict": conflict.get("POSITIVE", 0),
        "n_no_demonstrated_conflict": conflict.get("NO_DEMONSTRATED_CONFLICT", 0),
        "n_unresolved_candidate": conflict.get("UNRESOLVED_CANDIDATE", 0),
        "claim_ceiling": (
            "source_adjudicated_barrett_review_conflict_screen_"
            "not_architecture_causation_not_prevalence_not_final_macro_model"
        ),
    }


def build_u2_conflict_screen_readout(path: Path) -> dict:
    return build_u2_conflict_screen_readout_from_rows(load_u2_conflict_screen(path))

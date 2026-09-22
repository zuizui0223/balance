"""Strict blind conflict-screen guards for the provisional U1 review sample."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "sample_order",
    "universe_record_id",
    "dependency_group",
    "taxon_raw",
    "conflict_status",
    "same_coordinate_evidence",
    "opposing_demand_evidence",
    "architecture_status",
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
ARCHITECTURE = {"IDENTIFIED", "NOT_IDENTIFIED", "UNRESOLVED"}
DECISION = {"PASS_CONFLICT_GATE", "FAIL_CONFLICT_GATE", "HOLD_FOR_FULL_TEXT"}

EXPECTED_ROWS = 20


def load_u1_blind_screen(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U1 blind-screen columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_ROWS:
        raise ValueError("U1 provisional blind screen must contain exactly 20 rows")

    seen: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside blind-screen schema")
        for field in FIELDS:
            if not isinstance(row.get(field), str):
                raise ValueError(f"row {n} {field} must be a string")
        if row["universe_record_id"] in seen:
            raise ValueError(f"duplicate U1 blind-screen id {row['universe_record_id']!r}")
        seen.add(row["universe_record_id"])

        if row["conflict_status"] not in CONFLICT:
            raise ValueError(f"row {n} invalid conflict_status")
        if row["same_coordinate_evidence"] not in COORDINATE:
            raise ValueError(f"row {n} invalid same_coordinate_evidence")
        if row["opposing_demand_evidence"] not in OPPOSING:
            raise ValueError(f"row {n} invalid opposing_demand_evidence")
        if row["architecture_status"] not in ARCHITECTURE:
            raise ValueError(f"row {n} invalid architecture_status")
        if row["screen_decision"] not in DECISION:
            raise ValueError(f"row {n} invalid screen_decision")

        if row["conflict_status"] == "POSITIVE":
            if row["same_coordinate_evidence"] != "YES":
                raise ValueError(f"row {n} positive conflict requires same-coordinate evidence")
            if row["opposing_demand_evidence"] != "YES":
                raise ValueError(f"row {n} positive conflict requires opposing-demand evidence")
            if row["screen_decision"] != "PASS_CONFLICT_GATE":
                raise ValueError(f"row {n} positive conflict must pass the conflict gate")

        if row["conflict_status"] in {
            "ALIGNED_NO_CONFLICT",
            "NO_DEMONSTRATED_CONFLICT",
        } and row["screen_decision"] != "FAIL_CONFLICT_GATE":
            raise ValueError(f"row {n} negative/aligned conflict status must fail the gate")

        if row["conflict_status"] == "UNRESOLVED_CANDIDATE":
            if row["screen_decision"] != "HOLD_FOR_FULL_TEXT":
                raise ValueError(f"row {n} unresolved candidate must be held for full text")

    orders = [int(r["sample_order"]) for r in rows]
    if orders != list(range(1, EXPECTED_ROWS + 1)):
        raise ValueError("U1 blind-screen sample_order must be exactly 1..20")
    return rows


def build_u1_blind_screen_readout_from_rows(rows: list[dict[str, str]]) -> dict:
    conflict = Counter(r["conflict_status"] for r in rows)
    decisions = Counter(r["screen_decision"] for r in rows)
    return {
        "analysis": "balance_plant_u1_strict_conflict_blind_screen",
        "n_records": len(rows),
        "conflict_status_counts": dict(sorted(conflict.items())),
        "screen_decision_counts": dict(sorted(decisions.items())),
        "n_positive_conflict": conflict.get("POSITIVE", 0),
        "n_aligned_no_conflict": conflict.get("ALIGNED_NO_CONFLICT", 0),
        "n_no_demonstrated_conflict": conflict.get("NO_DEMONSTRATED_CONFLICT", 0),
        "n_unresolved_candidate": conflict.get("UNRESOLVED_CANDIDATE", 0),
        "claim_ceiling": (
            "provisional_network_visible_first20_strict_conflict_screen_"
            "not_final_double_code_not_full47_universe_not_architecture_analysis"
        ),
    }


def build_u1_blind_screen_readout(path: Path) -> dict:
    return build_u1_blind_screen_readout_from_rows(load_u1_blind_screen(path))

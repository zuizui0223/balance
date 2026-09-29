"""Strict blind conflict-screen guards for U1 production taxa U1_021..U1_047."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .plant_u1_screen import (
    ARCHITECTURE,
    CONFLICT,
    COORDINATE,
    DECISION,
    FIELDS,
    OPPOSING,
)


EXPECTED_IDS = {f"U1_{i:03d}" for i in range(21, 48)}


def load_u1_production_blind_screen(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U1 production blind-screen columns must match canonical order")
        rows = list(reader)

    if len(rows) != 27:
        raise ValueError("U1 production blind screen must contain exactly U1_021..U1_047")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside production blind-screen schema")
        clean = {field: (row.get(field) or "").strip() for field in FIELDS}
        for field in FIELDS:
            if not clean[field]:
                raise ValueError(f"row {n} {field} must be non-empty")

        uid = clean["universe_record_id"]
        if uid not in EXPECTED_IDS or uid in seen:
            raise ValueError(f"row {n} universe_record_id must be unique within U1_021..U1_047")
        seen.add(uid)

        if clean["conflict_status"] not in CONFLICT:
            raise ValueError(f"row {n} invalid conflict_status")
        if clean["same_coordinate_evidence"] not in COORDINATE:
            raise ValueError(f"row {n} invalid same_coordinate_evidence")
        if clean["opposing_demand_evidence"] not in OPPOSING:
            raise ValueError(f"row {n} invalid opposing_demand_evidence")
        if clean["architecture_status"] not in ARCHITECTURE:
            raise ValueError(f"row {n} invalid architecture_status")
        if clean["screen_decision"] not in DECISION:
            raise ValueError(f"row {n} invalid screen_decision")

        if clean["architecture_status"] != "NOT_IDENTIFIED":
            raise ValueError(
                f"row {n} U1 production conflict screen cannot infer architecture"
            )

        if clean["conflict_status"] == "POSITIVE":
            if clean["same_coordinate_evidence"] != "YES":
                raise ValueError(f"row {n} positive conflict requires same-coordinate evidence")
            if clean["opposing_demand_evidence"] != "YES":
                raise ValueError(f"row {n} positive conflict requires opposing-demand evidence")
            if clean["screen_decision"] != "PASS_CONFLICT_GATE":
                raise ValueError(f"row {n} positive conflict must pass the conflict gate")

        if clean["conflict_status"] in {
            "ALIGNED_NO_CONFLICT",
            "NO_DEMONSTRATED_CONFLICT",
        } and clean["screen_decision"] != "FAIL_CONFLICT_GATE":
            raise ValueError(f"row {n} negative/aligned conflict status must fail the gate")

        if clean["conflict_status"] == "UNRESOLVED_CANDIDATE":
            if clean["screen_decision"] != "HOLD_FOR_FULL_TEXT":
                raise ValueError(f"row {n} unresolved candidate must be held for full text")

        out.append(clean)

    if seen != EXPECTED_IDS:
        raise ValueError("U1 production blind screen does not cover U1_021..U1_047 exactly")
    orders = [int(row["sample_order"]) for row in out]
    if orders != list(range(21, 48)):
        raise ValueError("U1 production blind-screen sample_order must be exactly 21..47")
    return out


def build_u1_production_blind_screen_readout(path: Path) -> dict:
    rows = load_u1_production_blind_screen(path)
    conflict = Counter(row["conflict_status"] for row in rows)
    decisions = Counter(row["screen_decision"] for row in rows)
    held = sorted(
        row["universe_record_id"]
        for row in rows
        if row["screen_decision"] == "HOLD_FOR_FULL_TEXT"
    )
    return {
        "analysis": "balance_plant_u1_production_strict_conflict_blind_screen",
        "n_records": len(rows),
        "conflict_status_counts": dict(sorted(conflict.items())),
        "screen_decision_counts": dict(sorted(decisions.items())),
        "n_positive_conflict": conflict.get("POSITIVE", 0),
        "n_no_demonstrated_conflict": conflict.get("NO_DEMONSTRATED_CONFLICT", 0),
        "n_unresolved_candidate": conflict.get("UNRESOLVED_CANDIDATE", 0),
        "held_for_full_text_ids": held,
        "architecture_inferred": False,
        "claim_ceiling": (
            "primary_abstract_or_public_text_production_conflict_screen_"
            "not_independent_double_code_not_architecture_analysis"
        ),
    }

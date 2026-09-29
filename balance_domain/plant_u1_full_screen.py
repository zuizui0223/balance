"""Full 47-taxon U1 conflict-screen aggregation without architecture inference."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from .plant_u1_production_screen import load_u1_production_blind_screen
from .plant_u1_screen import load_u1_blind_screen


def build_u1_full47_conflict_screen(
    first20_path: Path,
    production27_path: Path,
) -> dict:
    first20 = load_u1_blind_screen(first20_path)
    production = load_u1_production_blind_screen(production27_path)
    rows = first20 + production

    expected_ids = [f"U1_{i:03d}" for i in range(1, 48)]
    ids = [row["universe_record_id"] for row in rows]
    if ids != expected_ids:
        raise ValueError("U1 full-47 screen must cover U1_001..U1_047 in order")

    if any(row["architecture_status"] != "NOT_IDENTIFIED" for row in rows):
        raise ValueError("U1 conflict screen cannot infer architecture")

    conflict = Counter(row["conflict_status"] for row in rows)
    decisions = Counter(row["screen_decision"] for row in rows)
    unresolved = [
        row["universe_record_id"]
        for row in rows
        if row["conflict_status"] == "UNRESOLVED_CANDIDATE"
    ]
    positives = [
        row["universe_record_id"]
        for row in rows
        if row["conflict_status"] == "POSITIVE"
    ]
    return {
        "analysis": "balance_plant_u1_full47_strict_conflict_source_screen",
        "n_records": len(rows),
        "n_dependency_groups": len({row["dependency_group"] for row in rows}),
        "conflict_status_counts": dict(sorted(conflict.items())),
        "screen_decision_counts": dict(sorted(decisions.items())),
        "positive_conflict_ids": positives,
        "unresolved_candidate_ids": unresolved,
        "n_positive_conflict": len(positives),
        "n_unresolved_candidate": len(unresolved),
        "architecture_inferred": False,
        "independent_reliability_completed": False,
        "claim_ceiling": (
            "complete_source_screen_of_frozen_u1_review_universe_"
            "not_independent_adjudication_not_prevalence"
        ),
    }

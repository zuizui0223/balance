"""Outcome-blind deletion robustness of the frozen BALANCE plant V4 design.

No architecture classes, effect sizes, human coder returns or fitted outcomes are read.
The enumeration concerns source-screened predictor support, NOT ecological effect size.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from pathlib import Path

from .plant_confirmatory import load_plant_predictor_receipts
from .plant_model_v4 import _matrix_rank
from .plant_preoutcome_generality import _complete_screened
from .plant_u2_screen import load_u2_conflict_screen


MODULE_LEVELS = ("SINGLE", "MODULAR")
TIME_LEVELS = ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING", "VARIABLE_CONTEXT")
MIN_PRIMARY_LEVEL_BLOCKS = 2
FULL_V4_COLUMN_COUNT = 5


def _source_screened_rows(
    u2_conflict_path: Path,
    u2_receipt_path: Path,
    u6_receipt_path: Path,
) -> list[dict[str, str]]:
    screen = load_u2_conflict_screen(u2_conflict_path)
    u2_positive = {
        row["dependency_group"]
        for row in screen
        if row["conflict_status"] == "POSITIVE"
    }
    receipts_u2 = load_plant_predictor_receipts(u2_receipt_path)
    receipts_u6 = load_plant_predictor_receipts(u6_receipt_path)
    if any(row["adjudication_status"] != "SCREENED" for row in receipts_u2 + receipts_u6):
        raise ValueError("This frozen V1 audit accepts SCREENED receipts only")

    u2 = _complete_screened(receipts_u2, u2_positive)
    u6 = _complete_screened(receipts_u6)
    if len(u2_positive) != 8 or {r["dependency_group"] for r in u2} != u2_positive:
        raise ValueError("Frozen U2 requires all eight positive groups with full predictors")
    if len(u6) != 21:
        raise ValueError("Frozen U6 requires all 21 complete predictor groups")

    rows = [
        {**row, "universe": "U2"} for row in u2
    ] + [
        {**row, "universe": "U6"} for row in u6
    ]
    if len({r["dependency_group"] for r in rows}) != len(rows):
        raise ValueError("Cross-universe dependency group reused; block identity unresolved")
    if any(r["module"] not in MODULE_LEVELS or r["timing"] not in TIME_LEVELS
           for r in rows):
        raise ValueError("Unrecognized frozen primary predictor level")
    return rows


def _full_design_rank(rows: list[dict[str, str]]) -> int:
    # Duplicate predictor vectors add sample rows but do not change rank.
    vectors = {
        (
            int(r["universe"] == "U2"),
            int(r["universe"] == "U6"),
            int(r["module"] == "MODULAR"),
            int(r["timing"] == "ORDERED_OR_ALTERNATING"),
            int(r["timing"] == "VARIABLE_CONTEXT"),
        )
        for r in rows
    }
    return _matrix_rank([list(v) for v in sorted(vectors)])


def _primary_level_support(rows: list[dict[str, str]]) -> dict[str, bool]:
    modules = Counter(r["module"] for r in rows)
    times = Counter(r["timing"] for r in rows)
    return {
        "module": all(modules[level] >= MIN_PRIMARY_LEVEL_BLOCKS for level in MODULE_LEVELS),
        "timing": all(times[level] >= MIN_PRIMARY_LEVEL_BLOCKS for level in TIME_LEVELS),
    }


def build_v4_preoutcome_attrition_audit(
    u2_conflict_path: Path,
    u2_receipt_path: Path,
    u6_receipt_path: Path,
    *,
    max_deleted: int = 3,
) -> dict:
    """Enumerate every group deletion through k=3, without viewing outcomes.

    Each deletion removes one source-screened species/dependence group. These
    enumerations are deterministic stress tests; they are not randomization
    distributions, leave-one-study-out tests, or outcome-model refits.
    """
    if not isinstance(max_deleted, int) or not 0 <= max_deleted <= 3:
        raise ValueError("max_deleted must be an integer from 0 to 3")
    rows = _source_screened_rows(u2_conflict_path, u2_receipt_path, u6_receipt_path)
    if _full_design_rank(rows) != FULL_V4_COLUMN_COUNT:
        raise ValueError("Expected the frozen V4 predictor design to have full rank")
    if not all(_primary_level_support(rows).values()):
        raise ValueError("Original frozen primary level support failed")

    report = []
    for deleted in range(max_deleted + 1):
        n_rank_deficient = 0
        n_level_support_fail = 0
        n_module_support_fail = 0
        n_timing_support_fail = 0
        n_both_support_fail = 0
        rank_witnesses: list[list[str]] = []
        n_combinations = 0

        for dropped in combinations(range(len(rows)), deleted):
            n_combinations += 1
            excluded = set(dropped)
            kept = [row for i, row in enumerate(rows) if i not in excluded]
            if _full_design_rank(kept) < FULL_V4_COLUMN_COUNT:
                n_rank_deficient += 1
                rank_witnesses.append(sorted(rows[i]["dependency_group"] for i in dropped))
            support = _primary_level_support(kept)
            module_fail = not support["module"]
            timing_fail = not support["timing"]
            n_module_support_fail += int(module_fail)
            n_timing_support_fail += int(timing_fail)
            n_both_support_fail += int(module_fail and timing_fail)
            n_level_support_fail += int(module_fail or timing_fail)

        report.append({
            "groups_deleted": deleted,
            "subsets_checked": n_combinations,
            "rank_deficient_subsets": n_rank_deficient,
            "primary_level_support_failure_subsets": n_level_support_fail,
            "module_level_support_failure_subsets": n_module_support_fail,
            "timing_level_support_failure_subsets": n_timing_support_fail,
            "both_level_support_failure_subsets": n_both_support_fail,
            "rank_deficiency_witnesses": sorted(rank_witnesses),
        })

    joint = Counter((r["universe"], r["module"], r["timing"]) for r in rows)
    shared_single = {
        universe: {
            timing: joint[(universe, "SINGLE", timing)]
            for timing in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
        }
        for universe in ("U2", "U6")
    }
    return {
        "analysis": "BALANCE_V4_PREOUTCOME_EXACT_GROUP_ATTRITION",
        "status": "SOURCE_SCREENED_ONLY_NOT_HUMAN_ADJUDICATED",
        "source_universes": {"U2": 8, "U6": 21},
        "n_screened_groups": len(rows),
        "full_v4_design_rank": FULL_V4_COLUMN_COUNT,
        "registered_minimum_groups_per_primary_level": MIN_PRIMARY_LEVEL_BLOCKS,
        "shared_single_module_timing_counts": shared_single,
        "strict_cross_universe_g1_ready_under_frozen_v1": all(
            shared_single[u][t] >= 2
            for u in ("U2", "U6")
            for t in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
        ),
        "attrition_enumeration": report,
        "architecture_outcomes_used": False,
        "independent_adjudication_complete": False,
        "model_fit_performed": False,
        "claim_ceiling": (
            "source_screened_preoutcome_design_rank_and_support_fragility_only_"
            "not_a_biological_architecture_association_or_randomization_p_value"
        ),
    }

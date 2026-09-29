"""Cross-universe predictor-overlap audit before BALANCE plant architecture outcomes."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from .plant_confirmatory import (
    PREDICTORS,
    load_plant_predictor_receipts,
    primary_module_opportunity,
    primary_spatial_exposure,
    primary_temporal_exposure,
)
from .plant_u2_screen import load_u2_conflict_screen


def _complete_screened(
    rows: list[dict[str, str]],
    groups: set[str] | None = None,
) -> list[dict[str, str]]:
    by_group: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        group = row["cluster_id"]
        if groups is not None and group not in groups:
            continue
        by_group.setdefault(group, {})[row["predictor"]] = row

    out = []
    for group, vals in by_group.items():
        if not all(p in vals for p in PREDICTORS):
            continue
        if not all(
            vals[p]["reported_value"] != "UNRESOLVED"
            and vals[p]["outcome_independence"] == "TRUE"
            for p in PREDICTORS
        ):
            continue
        out.append({
            "dependency_group": group,
            "module": primary_module_opportunity(
                vals["module_substrate"]["reported_value"]
            ),
            "timing": primary_temporal_exposure(
                vals["conflict_timing_geometry"]["reported_value"]
            ),
            "spatial": primary_spatial_exposure(
                vals["conflict_spatial_geometry"]["reported_value"]
            ),
        })
    return sorted(out, key=lambda row: row["dependency_group"])


def build_preoutcome_generality_audit(
    u2_conflict_path: Path,
    u2_receipt_path: Path,
    u6_receipt_path: Path,
) -> dict:
    """Identify predictor contrasts replicated across independent literature universes."""
    u2_conflict = load_u2_conflict_screen(u2_conflict_path)
    u2_positive = {
        row["dependency_group"]
        for row in u2_conflict
        if row["conflict_status"] == "POSITIVE"
    }
    u2 = _complete_screened(
        load_plant_predictor_receipts(u2_receipt_path),
        u2_positive,
    )
    u6 = _complete_screened(load_plant_predictor_receipts(u6_receipt_path))

    if {row["dependency_group"] for row in u2} != u2_positive:
        raise ValueError("U2 generality audit lacks complete predictor support")
    if len(u6) != 21:
        raise ValueError("U6 generality audit requires all 21 frozen groups")

    by_universe = {"U2": u2, "U6": u6}
    counts = {}
    levels = {}
    for universe, rows in by_universe.items():
        counts[universe] = {
            "module_opportunity2": dict(sorted(Counter(r["module"] for r in rows).items())),
            "temporal_exposure3": dict(sorted(Counter(r["timing"] for r in rows).items())),
            "spatial_exposure2": dict(sorted(Counter(r["spatial"] for r in rows).items())),
        }
        levels[universe] = {
            axis: set(axis_counts)
            for axis, axis_counts in counts[universe].items()
        }

    shared = {
        axis: sorted(levels["U2"][axis] & levels["U6"][axis])
        for axis in (
            "module_opportunity2",
            "temporal_exposure3",
            "spatial_exposure2",
        )
    }

    replicated = {
        "module_SINGLE_vs_MODULAR": all(
            level in shared["module_opportunity2"] for level in ("SINGLE", "MODULAR")
        ),
        "timing_SIMULTANEOUS_vs_ORDERED": all(
            level in shared["temporal_exposure3"]
            for level in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
        ),
        "timing_VARIABLE_CONTEXT_contrast": (
            "VARIABLE_CONTEXT" in shared["temporal_exposure3"]
        ),
        "spatial_SAME_UNIT_vs_DISTRIBUTED": all(
            level in shared["spatial_exposure2"]
            for level in ("SAME_UNIT", "DISTRIBUTED")
        ),
    }

    return {
        "analysis": "balance_plant_preoutcome_cross_universe_generality",
        "universe_counts": {"U2": len(u2), "U6": len(u6)},
        "predictor_counts_by_universe": counts,
        "shared_predictor_levels": shared,
        "cross_universe_replicated_contrasts": replicated,
        "only_current_cross_universe_two_level_contrast": (
            "timing_SIMULTANEOUS_vs_ORDERED"
            if sum(replicated.values()) == 1
            and replicated["timing_SIMULTANEOUS_vs_ORDERED"]
            else None
        ),
        "sampling_universe_adjustment_recommended": True,
        "generality_claim_rule": (
            "only contrasts with both levels represented in more than one independent "
            "sampling universe may be described as cross-universe replicated"
        ),
        "architecture_outcomes_used": False,
        "claim_ceiling": "preoutcome_generality_design_audit_only",
    }

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
from .plant_model_v4 import _matrix_rank
from .plant_predictor_adjudication import IMMUTABLE_RECEIPT_FIELDS


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
    u2_receipts = load_plant_predictor_receipts(u2_receipt_path)
    u2 = _complete_screened(
        u2_receipts,
        u2_positive,
    )
    u2_all_complete = _complete_screened(u2_receipts)
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

    joint_module_timing = {}
    for universe, rows in by_universe.items():
        joint = Counter((r["module"], r["timing"]) for r in rows)
        joint_module_timing[universe] = {
            f"{module}__{timing}": joint.get((module, timing), 0)
            for module in ("SINGLE", "MODULAR")
            for timing in (
                "SIMULTANEOUS",
                "ORDERED_OR_ALTERNATING",
                "VARIABLE_CONTEXT",
            )
        }

    u2_all_complete_groups = {
        row["dependency_group"] for row in u2_all_complete
    }
    u2_complete_groups_equal_source_positive = (
        u2_all_complete_groups == u2_positive
    )
    if "reported_value" not in IMMUTABLE_RECEIPT_FIELDS:
        raise ValueError(
            "U2 predictor receipt reported_value must remain immutable for reachability audit"
        )

    shared_module_levels = sorted(
        levels["U2"]["module_opportunity2"] & levels["U6"]["module_opportunity2"]
    )
    common_support_strata = []
    for module in shared_module_levels:
        if all(
            joint_module_timing[universe][f"{module}__SIMULTANEOUS"] >= 2
            and joint_module_timing[universe][f"{module}__ORDERED_OR_ALTERNATING"] >= 2
            for universe in ("U2", "U6")
        ):
            common_support_strata.append(module)

    # With frozen reported predictor values, final U2 model rows can only
    # retain a subset of groups that already have complete outcome-independent
    # predictor receipts. Subsetting cannot increase any module x timing cell
    # count, so a currently failed common-support threshold is unreachable
    # unless the predictor receipt surface is prospectively versioned/expanded.
    subset_only_u2_admission = u2_complete_groups_equal_source_positive
    common_support_reachable_without_receipt_expansion = bool(
        common_support_strata
    )
    reachability_shortfall = {}
    for module in shared_module_levels:
        reachability_shortfall[module] = {
            universe: {
                timing: max(
                    0,
                    2 - joint_module_timing[universe][f"{module}__{timing}"],
                )
                for timing in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
            }
            for universe in ("U2", "U6")
        }

    slope_matrix = []
    full_matrix = []
    for universe_name, rows in by_universe.items():
        for row in rows:
            slopes = [
                int(row["module"] == "MODULAR"),
                int(row["timing"] == "ORDERED_OR_ALTERNATING"),
                int(row["timing"] == "VARIABLE_CONTEXT"),
            ]
            slope_matrix.append(slopes)
            full_matrix.append([
                int(universe_name == "U2"),
                int(universe_name == "U6"),
                *slopes,
            ])
    slope_rank = _matrix_rank(slope_matrix)
    full_rank = _matrix_rank(full_matrix)

    return {
        "analysis": "balance_plant_preoutcome_cross_universe_generality",
        "universe_counts": {"U2": len(u2), "U6": len(u6)},
        "predictor_counts_by_universe": counts,
        "shared_predictor_levels": shared,
        "cross_universe_replicated_contrasts": replicated,
        "module_timing_joint_counts_by_universe": joint_module_timing,
        "shared_module_levels": shared_module_levels,
        "temporal_common_support_module_strata": common_support_strata,
        "temporal_cross_universe_common_support_ready": bool(common_support_strata),
        "u2_complete_outcome_independent_predictor_groups": len(
            u2_all_complete_groups
        ),
        "u2_complete_predictor_groups_equal_source_positive": (
            u2_complete_groups_equal_source_positive
        ),
        "final_u2_licensed_rows_are_subset_only_under_frozen_receipts": (
            subset_only_u2_admission
        ),
        "temporal_common_support_reachable_without_predictor_receipt_expansion": (
            common_support_reachable_without_receipt_expansion
        ),
        "temporal_common_support_reachability_shortfall": reachability_shortfall,
        "prospective_reopening_rule": (
            "strict temporal generality can be reopened only by a versioned "
            "outcome-independent predictor-receipt expansion completed before "
            "independent architecture outcomes are opened; final adjudication alone "
            "cannot increase frozen module-by-timing support"
        ),
        "v4_preoutcome_slope_design_rank": slope_rank,
        "v4_preoutcome_slope_design_column_count": 3,
        "v4_preoutcome_slope_design_full_rank": slope_rank == 3,
        "v4_preoutcome_full_design_rank": full_rank,
        "v4_preoutcome_full_design_column_count": 5,
        "v4_preoutcome_full_design_full_rank": full_rank == 5,
        "v4_main_predictor_design_viable": slope_rank == 3 and full_rank == 5,
        "only_current_cross_universe_two_level_contrast": (
            "timing_SIMULTANEOUS_vs_ORDERED"
            if sum(replicated.values()) == 1
            and replicated["timing_SIMULTANEOUS_vs_ORDERED"]
            else None
        ),
        "sampling_universe_adjustment_recommended": True,
        "generality_claim_rule": (
            "cross-universe timing generality requires both marginal timing replication "
            "and at least one shared module-opportunity stratum with >=2 independent "
            "SIMULTANEOUS and >=2 ORDERED_OR_ALTERNATING blocks in each U2 and U6"
        ),
        "architecture_outcomes_used": False,
        "claim_ceiling": "preoutcome_generality_design_audit_only",
    }

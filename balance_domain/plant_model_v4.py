"""Pre-fit estimability checks for BALANCE plant confirmatory model v4."""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from typing import Iterable

from .plant_confirmatory import (
    primary_module_opportunity,
    primary_spatial_exposure,
    primary_temporal_exposure,
)
from .plant_macro import PRIMARY_ARCHITECTURE_CLASSES, primary_architecture_class


PRIMARY_UNIVERSES = (
    "U2_BARRETT_2002",
    "U6_POLLEN_THEFT_HARGREAVES_2009",
)
RESPONSE_CLASSES = tuple(PRIMARY_ARCHITECTURE_CLASSES)
MODULE_LEVELS = ("SINGLE", "MODULAR")
TEMPORAL_LEVELS = ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING", "VARIABLE_CONTEXT")
SPATIAL_LEVELS = ("SAME_UNIT", "DISTRIBUTED")

MIN_BLOCKS_PER_RESPONSE_CLASS = 2
MIN_BLOCKS_PER_PRIMARY_PREDICTOR_LEVEL = 2
MIN_ROWS_PER_PRIMARY_UNIVERSE = 2
MIN_BLOCKS_PER_REPLICATED_TEMPORAL_LEVEL_WITHIN_UNIVERSE = 2


def _matrix_rank(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    a = [[Fraction(value) for value in row] for row in matrix]
    n_rows = len(a)
    n_cols = len(a[0])
    rank = 0
    col = 0
    while rank < n_rows and col < n_cols:
        pivot = next((r for r in range(rank, n_rows) if a[r][col] != 0), None)
        if pivot is None:
            col += 1
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        pivot_value = a[rank][col]
        a[rank] = [value / pivot_value for value in a[rank]]
        for r in range(n_rows):
            if r == rank or a[r][col] == 0:
                continue
            factor = a[r][col]
            a[r] = [
                a[r][c] - factor * a[rank][c]
                for c in range(n_cols)
            ]
        rank += 1
        col += 1
    return rank


def _resolved_fit_row(row: dict[str, str]) -> dict[str, str]:
    universe = row.get("universe_id")
    if universe not in PRIMARY_UNIVERSES:
        raise ValueError(
            f"v4 primary fit accepts U2/U6 only, found universe {universe!r}"
        )
    block = row.get("dependence_block") or row.get("dependency_group")
    if not block:
        raise ValueError("v4 estimability row requires dependence_block or dependency_group")
    return {
        "universe_id": universe,
        "dependency_group": row["dependency_group"],
        "dependence_block": block,
        "architecture_class4": primary_architecture_class(row["architecture_mode"]),
        "module_opportunity2": primary_module_opportunity(row["module_substrate"]),
        "temporal_exposure3": primary_temporal_exposure(row["conflict_timing_geometry"]),
        "spatial_exposure2": primary_spatial_exposure(row["conflict_spatial_geometry"]),
    }


def _block_counts_by_level(
    rows: list[dict[str, str]],
    field: str,
    levels: tuple[str, ...],
) -> dict[str, int]:
    blocks: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        blocks[row[field]].add(row["dependence_block"])
    return {level: len(blocks.get(level, set())) for level in levels}


def _design_matrices(
    rows: list[dict[str, str]],
) -> tuple[list[str], list[list[int]], list[str], list[list[int]]]:
    slope_columns = [
        "module_MODULAR",
        "temporal_ORDERED_OR_ALTERNATING",
        "temporal_VARIABLE_CONTEXT",
    ]
    slope_matrix = [
        [
            int(row["module_opportunity2"] == "MODULAR"),
            int(row["temporal_exposure3"] == "ORDERED_OR_ALTERNATING"),
            int(row["temporal_exposure3"] == "VARIABLE_CONTEXT"),
        ]
        for row in rows
    ]
    full_columns = [
        "intercept_U2",
        "intercept_U6",
        *slope_columns,
    ]
    full_matrix = [
        [
            int(row["universe_id"] == "U2_BARRETT_2002"),
            int(row["universe_id"] == "U6_POLLEN_THEFT_HARGREAVES_2009"),
            *slopes,
        ]
        for row, slopes in zip(rows, slope_matrix)
    ]
    return slope_columns, slope_matrix, full_columns, full_matrix


def build_v4_estimability_report(rows: Iterable[dict[str, str]]) -> dict:
    """Return the frozen pre-fit estimability and generality diagnostics for V4."""
    resolved = [_resolved_fit_row(row) for row in rows]
    if not resolved:
        raise ValueError("v4 estimability requires at least one resolved row")

    universe_blocks: dict[str, set[str]] = defaultdict(set)
    class_blocks: dict[str, set[str]] = defaultdict(set)
    for row in resolved:
        universe_blocks[row["universe_id"]].add(row["dependence_block"])
        class_blocks[row["architecture_class4"]].add(row["dependence_block"])

    universe_block_counts = {
        universe: len(universe_blocks.get(universe, set()))
        for universe in PRIMARY_UNIVERSES
    }
    class_block_counts = {
        response: len(class_blocks.get(response, set()))
        for response in RESPONSE_CLASSES
    }
    module_block_counts = _block_counts_by_level(
        resolved, "module_opportunity2", MODULE_LEVELS
    )
    temporal_block_counts = _block_counts_by_level(
        resolved, "temporal_exposure3", TEMPORAL_LEVELS
    )
    spatial_block_counts = _block_counts_by_level(
        resolved, "spatial_exposure2", SPATIAL_LEVELS
    )

    slope_columns, slope_matrix, full_columns, full_matrix = _design_matrices(resolved)
    slope_rank = _matrix_rank(slope_matrix)
    slope_full_rank = slope_rank == len(slope_columns)
    full_rank = _matrix_rank(full_matrix)
    full_design_full_rank = full_rank == len(full_columns)

    replicated_temporal_counts: dict[str, dict[str, int]] = {}
    module_timing_counts: dict[str, dict[str, int]] = {}
    for universe in PRIMARY_UNIVERSES:
        subset = [row for row in resolved if row["universe_id"] == universe]
        replicated_temporal_counts[universe] = {
            level: len({
                row["dependence_block"]
                for row in subset
                if row["temporal_exposure3"] == level
            })
            for level in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
        }
        module_timing_counts[universe] = {
            f"{module}__{timing}": len({
                row["dependence_block"]
                for row in subset
                if row["module_opportunity2"] == module
                and row["temporal_exposure3"] == timing
            })
            for module in MODULE_LEVELS
            for timing in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
        }

    temporal_marginal_replication_ready = all(
        count >= MIN_BLOCKS_PER_REPLICATED_TEMPORAL_LEVEL_WITHIN_UNIVERSE
        for universe_counts in replicated_temporal_counts.values()
        for count in universe_counts.values()
    )

    shared_module_levels = [
        module
        for module in MODULE_LEVELS
        if all(module_block_counts.get(module, 0) > 0 for _ in (0,))
        and all(
            any(
                row["module_opportunity2"] == module
                for row in resolved
                if row["universe_id"] == universe
            )
            for universe in PRIMARY_UNIVERSES
        )
    ]
    common_support_module_strata = [
        module
        for module in shared_module_levels
        if all(
            module_timing_counts[universe][f"{module}__SIMULTANEOUS"]
            >= MIN_BLOCKS_PER_REPLICATED_TEMPORAL_LEVEL_WITHIN_UNIVERSE
            and module_timing_counts[universe][
                f"{module}__ORDERED_OR_ALTERNATING"
            ] >= MIN_BLOCKS_PER_REPLICATED_TEMPORAL_LEVEL_WITHIN_UNIVERSE
            for universe in PRIMARY_UNIVERSES
        )
    ]
    temporal_common_support_ready = bool(common_support_module_strata)
    temporal_generality_ready = (
        temporal_marginal_replication_ready and temporal_common_support_ready
    )

    blockers: list[str] = []
    sparse_universes = [
        universe
        for universe, count in universe_block_counts.items()
        if count < MIN_ROWS_PER_PRIMARY_UNIVERSE
    ]
    if sparse_universes:
        blockers.append(
            "primary_universe_support_below_2_dependence_blocks:"
            + ",".join(sparse_universes)
        )

    sparse_classes = [
        response
        for response, count in class_block_counts.items()
        if count < MIN_BLOCKS_PER_RESPONSE_CLASS
    ]
    if sparse_classes:
        blockers.append(
            "response_class_support_below_2_dependence_blocks:"
            + ",".join(sparse_classes)
        )

    sparse_module = [
        level
        for level, count in module_block_counts.items()
        if count < MIN_BLOCKS_PER_PRIMARY_PREDICTOR_LEVEL
    ]
    if sparse_module:
        blockers.append(
            "module_level_support_below_2_dependence_blocks:"
            + ",".join(sparse_module)
        )

    sparse_temporal = [
        level
        for level, count in temporal_block_counts.items()
        if count < MIN_BLOCKS_PER_PRIMARY_PREDICTOR_LEVEL
    ]
    if sparse_temporal:
        blockers.append(
            "temporal_level_support_below_2_dependence_blocks:"
            + ",".join(sparse_temporal)
        )

    if not slope_full_rank:
        blockers.append("primary_common_slope_design_matrix_rank_deficient")
    if not full_design_full_rank:
        blockers.append("primary_universe_stratified_design_matrix_rank_deficient")

    spatial_secondary_estimable = all(
        count >= MIN_BLOCKS_PER_PRIMARY_PREDICTOR_LEVEL
        for count in spatial_block_counts.values()
    )

    return {
        "analysis": "balance_plant_confirmatory_model_v4_estimability",
        "n_rows": len(resolved),
        "n_dependency_groups": len({row["dependency_group"] for row in resolved}),
        "n_dependence_blocks": len({row["dependence_block"] for row in resolved}),
        "primary_universe_dependence_block_counts": universe_block_counts,
        "response_class_dependence_block_counts": class_block_counts,
        "module_level_dependence_block_counts": module_block_counts,
        "temporal_level_dependence_block_counts": temporal_block_counts,
        "spatial_secondary_dependence_block_counts": spatial_block_counts,
        "slope_design_columns": slope_columns,
        "slope_design_rank": slope_rank,
        "slope_design_column_count": len(slope_columns),
        "slope_design_full_rank": slope_full_rank,
        "full_design_columns": full_columns,
        "full_design_rank": full_rank,
        "full_design_column_count": len(full_columns),
        "full_design_full_rank": full_design_full_rank,
        "temporal_cross_universe_support": replicated_temporal_counts,
        "temporal_cross_universe_marginal_replication_ready": (
            temporal_marginal_replication_ready
        ),
        "module_timing_joint_support_by_universe": module_timing_counts,
        "shared_module_levels_across_universes": shared_module_levels,
        "temporal_common_support_module_strata": common_support_module_strata,
        "temporal_cross_universe_common_support_ready": (
            temporal_common_support_ready
        ),
        "temporal_cross_universe_generality_ready": temporal_generality_ready,
        "spatial_secondary_estimable": spatial_secondary_estimable,
        "blockers": blockers,
        "ready_for_primary_fit": not blockers,
        "failure_action": "DO_NOT_FIT_OR_DROP_TERMS_POST_HOC",
        "generality_rule": (
            "cross-universe timing language requires marginal timing replication plus "
            "at least one shared module stratum with >=2 SIMULTANEOUS and >=2 ORDERED "
            "dependence blocks in each U2 and U6"
        ),
    }

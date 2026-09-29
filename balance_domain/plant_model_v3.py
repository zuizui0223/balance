"""Outcome-blind estimability checks for BALANCE plant confirmatory model v3."""
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


RESPONSE_CLASSES = tuple(PRIMARY_ARCHITECTURE_CLASSES)
MIN_BLOCKS_PER_RESPONSE_CLASS = 2
MIN_BLOCKS_PER_PRIMARY_PREDICTOR_LEVEL = 2

MODULE_LEVELS = ("SINGLE", "MODULAR")
TEMPORAL_LEVELS = ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING", "VARIABLE_CONTEXT")
SPATIAL_LEVELS = ("SAME_UNIT", "DISTRIBUTED")


def _matrix_rank(matrix: list[list[int]]) -> int:
    """Exact Gaussian-elimination rank for the small 0/1 design matrix."""
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
    block = row.get("dependence_block") or row.get("dependency_group")
    if not block:
        raise ValueError("v3 estimability row requires dependence_block or dependency_group")
    return {
        "dependency_group": row["dependency_group"],
        "dependence_block": block,
        "architecture_class4": primary_architecture_class(row["architecture_mode"]),
        "module_opportunity2": primary_module_opportunity(row["module_substrate"]),
        "temporal_exposure3": primary_temporal_exposure(row["conflict_timing_geometry"]),
        "spatial_exposure2": primary_spatial_exposure(row["conflict_spatial_geometry"]),
    }


def _design_matrix(rows: list[dict[str, str]]) -> tuple[list[str], list[list[int]]]:
    columns = [
        "intercept",
        "module_MODULAR",
        "temporal_ORDERED_OR_ALTERNATING",
        "temporal_VARIABLE_CONTEXT",
    ]
    matrix = []
    for row in rows:
        matrix.append([
            1,
            int(row["module_opportunity2"] == "MODULAR"),
            int(row["temporal_exposure3"] == "ORDERED_OR_ALTERNATING"),
            int(row["temporal_exposure3"] == "VARIABLE_CONTEXT"),
        ])
    return columns, matrix


def _block_counts_by_level(
    rows: list[dict[str, str]],
    field: str,
    levels: tuple[str, ...],
) -> dict[str, int]:
    blocks: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        blocks[row[field]].add(row["dependence_block"])
    return {level: len(blocks.get(level, set())) for level in levels}


def build_v3_estimability_report(rows: Iterable[dict[str, str]]) -> dict:
    """Return the frozen pre-fit estimability decision for model v3."""
    resolved = [_resolved_fit_row(row) for row in rows]
    if not resolved:
        raise ValueError("v3 estimability requires at least one resolved row")

    class_blocks: dict[str, set[str]] = defaultdict(set)
    for row in resolved:
        class_blocks[row["architecture_class4"]].add(row["dependence_block"])
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

    columns, matrix = _design_matrix(resolved)
    rank = _matrix_rank(matrix)
    full_rank = rank == len(columns)

    blockers: list[str] = []
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
        level for level, count in module_block_counts.items()
        if count < MIN_BLOCKS_PER_PRIMARY_PREDICTOR_LEVEL
    ]
    if sparse_module:
        blockers.append(
            "module_level_support_below_2_dependence_blocks:"
            + ",".join(sparse_module)
        )

    sparse_temporal = [
        level for level, count in temporal_block_counts.items()
        if count < MIN_BLOCKS_PER_PRIMARY_PREDICTOR_LEVEL
    ]
    if sparse_temporal:
        blockers.append(
            "temporal_level_support_below_2_dependence_blocks:"
            + ",".join(sparse_temporal)
        )

    if not full_rank:
        blockers.append("primary_design_matrix_rank_deficient")

    spatial_secondary_estimable = all(
        count >= MIN_BLOCKS_PER_PRIMARY_PREDICTOR_LEVEL
        for count in spatial_block_counts.values()
    )

    return {
        "analysis": "balance_plant_confirmatory_model_v3_estimability",
        "n_rows": len(resolved),
        "n_dependency_groups": len({row["dependency_group"] for row in resolved}),
        "n_dependence_blocks": len({row["dependence_block"] for row in resolved}),
        "response_class_dependence_block_counts": class_block_counts,
        "minimum_dependence_blocks_per_response_class": MIN_BLOCKS_PER_RESPONSE_CLASS,
        "module_level_dependence_block_counts": module_block_counts,
        "temporal_level_dependence_block_counts": temporal_block_counts,
        "minimum_dependence_blocks_per_primary_predictor_level": (
            MIN_BLOCKS_PER_PRIMARY_PREDICTOR_LEVEL
        ),
        "spatial_secondary_dependence_block_counts": spatial_block_counts,
        "spatial_secondary_estimable": spatial_secondary_estimable,
        "design_columns": columns,
        "design_rank": rank,
        "design_column_count": len(columns),
        "design_full_rank": full_rank,
        "blockers": blockers,
        "ready_for_primary_fit": not blockers,
        "failure_action": "DO_NOT_FIT_OR_DROP_TERMS_POST_HOC",
    }

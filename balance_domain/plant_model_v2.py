"""Outcome-blind estimability checks for BALANCE plant confirmatory model v2."""
from __future__ import annotations

from collections import Counter, defaultdict
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
        raise ValueError("v2 estimability row requires dependence_block or dependency_group")
    return {
        "dependency_group": row["dependency_group"],
        "dependence_block": block,
        "architecture_class4": primary_architecture_class(row["architecture_mode"]),
        "module_opportunity2": primary_module_opportunity(row["module_substrate"]),
        "temporal_exposure3": primary_temporal_exposure(row["conflict_timing_geometry"]),
        "spatial_exposure2": primary_spatial_exposure(row["conflict_spatial_geometry"]),
    }


def _design_matrix(rows: list[dict[str, str]]) -> tuple[list[str], list[list[int]]]:
    """Dummy-code the frozen v2 contrasts using fixed reference levels.

    VARIABLE_CONTEXT is included only when observed. This does not drop a predictor:
    an unobserved category has no estimable coefficient.
    """
    observed_temporal = {row["temporal_exposure3"] for row in rows}
    columns = ["intercept", "module_MODULAR", "temporal_ORDERED_OR_ALTERNATING"]
    if "VARIABLE_CONTEXT" in observed_temporal:
        columns.append("temporal_VARIABLE_CONTEXT")
    columns.append("spatial_DISTRIBUTED")

    matrix: list[list[int]] = []
    for row in rows:
        values = [
            1,
            int(row["module_opportunity2"] == "MODULAR"),
            int(row["temporal_exposure3"] == "ORDERED_OR_ALTERNATING"),
        ]
        if "VARIABLE_CONTEXT" in observed_temporal:
            values.append(int(row["temporal_exposure3"] == "VARIABLE_CONTEXT"))
        values.append(int(row["spatial_exposure2"] == "DISTRIBUTED"))
        matrix.append(values)
    return columns, matrix


def build_v2_estimability_report(rows: Iterable[dict[str, str]]) -> dict:
    """Return the frozen pre-fit estimability decision for model v2."""
    resolved = [_resolved_fit_row(row) for row in rows]
    if not resolved:
        raise ValueError("v2 estimability requires at least one resolved row")

    class_blocks: dict[str, set[str]] = defaultdict(set)
    for row in resolved:
        class_blocks[row["architecture_class4"]].add(row["dependence_block"])
    class_block_counts = {
        response: len(class_blocks.get(response, set()))
        for response in RESPONSE_CLASSES
    }

    module_levels = sorted({row["module_opportunity2"] for row in resolved})
    temporal_levels = sorted({row["temporal_exposure3"] for row in resolved})
    spatial_levels = sorted({row["spatial_exposure2"] for row in resolved})

    required_contrast_support = {
        "module_SINGLE_vs_MODULAR": all(level in module_levels for level in MODULE_LEVELS),
        "temporal_SIMULTANEOUS_vs_ORDERED": all(
            level in temporal_levels
            for level in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
        ),
        "spatial_SAME_UNIT_vs_DISTRIBUTED": all(
            level in spatial_levels for level in SPATIAL_LEVELS
        ),
    }

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
    unsupported = [
        name for name, supported in required_contrast_support.items() if not supported
    ]
    if unsupported:
        blockers.append("planned_contrast_support_missing:" + ",".join(unsupported))
    if not full_rank:
        blockers.append("primary_design_matrix_rank_deficient")

    return {
        "analysis": "balance_plant_confirmatory_model_v2_estimability",
        "n_rows": len(resolved),
        "n_dependency_groups": len({row["dependency_group"] for row in resolved}),
        "n_dependence_blocks": len({row["dependence_block"] for row in resolved}),
        "response_class_dependence_block_counts": class_block_counts,
        "minimum_dependence_blocks_per_response_class": MIN_BLOCKS_PER_RESPONSE_CLASS,
        "module_levels_observed": module_levels,
        "temporal_levels_observed": temporal_levels,
        "spatial_levels_observed": spatial_levels,
        "planned_contrast_support": required_contrast_support,
        "design_columns": columns,
        "design_rank": rank,
        "design_column_count": len(columns),
        "design_full_rank": full_rank,
        "blockers": blockers,
        "ready_for_primary_fit": not blockers,
        "failure_action": "DO_NOT_FIT_OR_DROP_TERMS_POST_HOC",
    }

"""Pre-outcome predictor-support audit for BALANCE plant confirmatory design."""
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


def _screened_independent_rows(
    receipt_rows: list[dict[str, str]],
    allowed_groups: set[str] | None = None,
) -> list[dict[str, str]]:
    grouped: dict[str, dict[str, dict[str, str]]] = {}
    for row in receipt_rows:
        group = row["cluster_id"]
        if allowed_groups is not None and group not in allowed_groups:
            continue
        grouped.setdefault(group, {})[row["predictor"]] = row

    out: list[dict[str, str]] = []
    for group, values in grouped.items():
        if not all(predictor in values for predictor in PREDICTORS):
            continue
        if not all(
            values[predictor]["reported_value"] != "UNRESOLVED"
            and values[predictor]["outcome_independence"] == "TRUE"
            for predictor in PREDICTORS
        ):
            continue
        out.append({
            "dependency_group": group,
            "module_substrate": values["module_substrate"]["reported_value"],
            "conflict_timing_geometry": values["conflict_timing_geometry"]["reported_value"],
            "conflict_spatial_geometry": values["conflict_spatial_geometry"]["reported_value"],
        })
    return sorted(out, key=lambda row: row["dependency_group"])


def build_preoutcome_predictor_support(
    u2_conflict_path: Path,
    u2_receipt_path: Path,
    u6_receipt_path: Path,
) -> dict:
    """Recompute the predictor-support surface used to freeze model v3."""
    u2_conflict = load_u2_conflict_screen(u2_conflict_path)
    u2_positive = {
        row["dependency_group"]
        for row in u2_conflict
        if row["conflict_status"] == "POSITIVE"
    }
    u2 = _screened_independent_rows(
        load_plant_predictor_receipts(u2_receipt_path),
        u2_positive,
    )
    u6 = _screened_independent_rows(load_plant_predictor_receipts(u6_receipt_path))

    if {row["dependency_group"] for row in u2} != u2_positive:
        missing = sorted(u2_positive - {row["dependency_group"] for row in u2})
        raise ValueError(
            "U2 positive groups lack complete source-screened predictor receipts: "
            + ", ".join(missing)
        )
    if len(u6) != 21:
        raise ValueError("U6 predictor-support audit requires all 21 frozen groups")

    rows = [
        {**row, "universe": "U2"}
        for row in u2
    ] + [
        {**row, "universe": "U6"}
        for row in u6
    ]

    module = Counter(primary_module_opportunity(row["module_substrate"]) for row in rows)
    timing = Counter(
        primary_temporal_exposure(row["conflict_timing_geometry"]) for row in rows
    )
    spatial = Counter(
        primary_spatial_exposure(row["conflict_spatial_geometry"]) for row in rows
    )

    min_blocks = 2
    primary_support = {
        "module_opportunity2": all(
            module.get(level, 0) >= min_blocks for level in ("SINGLE", "MODULAR")
        ),
        "temporal_exposure3": all(
            timing.get(level, 0) >= min_blocks
            for level in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING", "VARIABLE_CONTEXT")
        ),
        "spatial_exposure2": all(
            spatial.get(level, 0) >= min_blocks for level in ("SAME_UNIT", "DISTRIBUTED")
        ),
    }

    return {
        "analysis": "balance_plant_preoutcome_predictor_support",
        "n_groups": len(rows),
        "universe_counts": {
            "U2": len(u2),
            "U6": len(u6),
        },
        "module_opportunity2_counts": dict(sorted(module.items())),
        "temporal_exposure3_counts": dict(sorted(timing.items())),
        "spatial_exposure2_counts": dict(sorted(spatial.items())),
        "minimum_blocks_per_primary_predictor_level": min_blocks,
        "axis_support_sufficient_for_primary_joint_model": primary_support,
        "recommended_primary_axes": [
            axis for axis in ("module_opportunity2", "temporal_exposure3")
            if primary_support[axis]
        ],
        "secondary_due_support_axis": (
            "spatial_exposure2"
            if not primary_support["spatial_exposure2"]
            else None
        ),
        "architecture_outcomes_used": False,
        "claim_ceiling": "preoutcome_predictor_support_design_audit_only",
    }

"""Stan-ready input builder for BALANCE plant confirmatory model v3."""
from __future__ import annotations

from typing import Iterable

from .plant_confirmatory import (
    primary_module_opportunity,
    primary_temporal_exposure,
)
from .plant_macro import primary_architecture_class
from .plant_model_assembly import validate_model_assembly_rows
from .plant_model_v3 import build_v3_estimability_report


RESPONSE_ORDER = (
    "SHARED",
    "NONSTRUCTURAL_SEPARATION",
    "STRUCTURAL_MODULE_DIVISION",
    "MOSAIC",
)
DESIGN_COLUMNS = (
    "intercept",
    "module_MODULAR",
    "temporal_ORDERED_OR_ALTERNATING",
    "temporal_VARIABLE_CONTEXT",
)


def _fit_row(row: dict[str, str]) -> dict[str, str]:
    return {
        **row,
        "architecture_class4": primary_architecture_class(row["architecture_mode"]),
        "module_opportunity2": primary_module_opportunity(row["module_substrate"]),
        "temporal_exposure3": primary_temporal_exposure(row["conflict_timing_geometry"]),
    }


def build_v3_stan_input(rows: Iterable[dict[str, str]]) -> dict:
    """Build a JSON-serializable Stan payload after every frozen gate closes."""
    licensed = validate_model_assembly_rows(rows)
    fit_rows = [_fit_row(row) for row in licensed]

    block_counts: dict[str, int] = {}
    for row in fit_rows:
        block = row["dependence_block"]
        block_counts[block] = block_counts.get(block, 0) + 1
    repeated = sorted(block for block, count in block_counts.items() if count > 1)
    if repeated:
        raise ValueError(
            "v3 initial fit requires one analysis row per dependence block; "
            "resolve/collapse repeated blocks before fitting: "
            + ", ".join(repeated)
        )

    estimability = build_v3_estimability_report(fit_rows)
    if not estimability["ready_for_primary_fit"]:
        raise ValueError(
            "v3 primary fit is not estimable under the frozen gate: "
            + " | ".join(estimability["blockers"])
        )

    response_index = {name: i + 1 for i, name in enumerate(RESPONSE_ORDER)}
    x: list[list[int]] = []
    y: list[int] = []
    row_ids: list[str] = []
    for row in fit_rows:
        x.append([
            1,
            int(row["module_opportunity2"] == "MODULAR"),
            int(row["temporal_exposure3"] == "ORDERED_OR_ALTERNATING"),
            int(row["temporal_exposure3"] == "VARIABLE_CONTEXT"),
        ])
        y.append(response_index[row["architecture_class4"]])
        row_ids.append(row["analysis_row_id"])

    return {
        "stan_data": {
            "N": len(fit_rows),
            "K": len(RESPONSE_ORDER),
            "P": len(DESIGN_COLUMNS),
            "X": x,
            "y": y,
            "slope_prior_sd": 0.75,
            "intercept_prior_sd": 1.5,
        },
        "metadata": {
            "analysis": "balance_plant_confirmatory_model_v3",
            "response_order": list(RESPONSE_ORDER),
            "reference_response": "SHARED",
            "design_columns": list(DESIGN_COLUMNS),
            "analysis_row_ids": row_ids,
            "n_dependence_blocks": len(block_counts),
            "dependence_policy": "one_analysis_row_per_dependence_block",
            "prior_sensitivity_slope_sd": 1.5,
            "spatial_axis_role": "secondary_not_in_primary_design_matrix",
            "estimability": estimability,
            "claim_ceiling": "model_input_only_no_fitted_result",
        },
    }


def build_v3_prior_sensitivity_input(rows: Iterable[dict[str, str]]) -> dict:
    """Return the identical design with the preregistered wider slope prior."""
    payload = build_v3_stan_input(rows)
    payload["stan_data"]["slope_prior_sd"] = 1.5
    payload["metadata"]["analysis"] = "balance_plant_confirmatory_model_v3_prior_sensitivity"
    return payload

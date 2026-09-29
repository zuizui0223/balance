"""Stan-ready input builder for BALANCE plant confirmatory model v4."""
from __future__ import annotations

from typing import Iterable

from .plant_confirmatory import (
    primary_module_opportunity,
    primary_temporal_exposure,
)
from .plant_macro import primary_architecture_class
from .plant_model_assembly import validate_model_assembly_rows
from .plant_model_v4 import PRIMARY_UNIVERSES, build_v4_estimability_report


RESPONSE_ORDER = (
    "SHARED",
    "NONSTRUCTURAL_SEPARATION",
    "STRUCTURAL_MODULE_DIVISION",
    "MOSAIC",
)
SLOPE_COLUMNS = (
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


def build_v4_stan_input(rows: Iterable[dict[str, str]]) -> dict:
    """Build the frozen two-universe V4 Stan payload after all entry gates close."""
    licensed = validate_model_assembly_rows(rows)
    fit_rows = [_fit_row(row) for row in licensed]

    block_counts: dict[str, int] = {}
    for row in fit_rows:
        block = row["dependence_block"]
        block_counts[block] = block_counts.get(block, 0) + 1
    repeated = sorted(block for block, count in block_counts.items() if count > 1)
    if repeated:
        raise ValueError(
            "v4 initial fit requires one analysis row per dependence block; "
            "resolve/collapse repeated blocks before fitting: "
            + ", ".join(repeated)
        )

    estimability = build_v4_estimability_report(fit_rows)
    if not estimability["ready_for_primary_fit"]:
        raise ValueError(
            "v4 primary fit is not estimable under the frozen gate: "
            + " | ".join(estimability["blockers"])
        )

    response_index = {name: i + 1 for i, name in enumerate(RESPONSE_ORDER)}
    universe_index = {name: i + 1 for i, name in enumerate(PRIMARY_UNIVERSES)}

    x: list[list[int]] = []
    y: list[int] = []
    universe: list[int] = []
    row_ids: list[str] = []
    for row in fit_rows:
        x.append([
            int(row["module_opportunity2"] == "MODULAR"),
            int(row["temporal_exposure3"] == "ORDERED_OR_ALTERNATING"),
            int(row["temporal_exposure3"] == "VARIABLE_CONTEXT"),
        ])
        y.append(response_index[row["architecture_class4"]])
        universe.append(universe_index[row["universe_id"]])
        row_ids.append(row["analysis_row_id"])

    return {
        "stan_data": {
            "N": len(fit_rows),
            "K": len(RESPONSE_ORDER),
            "U": len(PRIMARY_UNIVERSES),
            "P": len(SLOPE_COLUMNS),
            "X": x,
            "y": y,
            "universe": universe,
            "slope_prior_sd": 0.75,
            "intercept_prior_sd": 1.5,
        },
        "metadata": {
            "analysis": "balance_plant_confirmatory_model_v4",
            "response_order": list(RESPONSE_ORDER),
            "reference_response": "SHARED",
            "universe_order": list(PRIMARY_UNIVERSES),
            "slope_columns": list(SLOPE_COLUMNS),
            "analysis_row_ids": row_ids,
            "n_dependence_blocks": len(block_counts),
            "dependence_policy": "one_analysis_row_per_dependence_block",
            "prior_sensitivity_slope_sd": 1.5,
            "spatial_axis_role": "secondary_not_in_primary_design_matrix",
            "U1_role": "external_specificity_validation_not_primary_fit",
            "estimability": estimability,
            "claim_ceiling": "model_input_only_no_fitted_result",
        },
    }


def build_v4_prior_sensitivity_input(rows: Iterable[dict[str, str]]) -> dict:
    """Return the identical design with the preregistered wider common-slope prior."""
    payload = build_v4_stan_input(rows)
    payload["stan_data"]["slope_prior_sd"] = 1.5
    payload["metadata"]["analysis"] = (
        "balance_plant_confirmatory_model_v4_prior_sensitivity"
    )
    return payload



def build_v4_temporal_generality_input(rows: Iterable[dict[str, str]]) -> dict:
    """Build the preregistered U6 x ORDERED temporal-generalization sensitivity."""
    payload = build_v4_stan_input(rows)
    estimability = payload["metadata"]["estimability"]
    if not estimability["temporal_cross_universe_generality_ready"]:
        raise ValueError(
            "v4 temporal generality sensitivity lacks within-universe "
            "SIMULTANEOUS/ORDERED replication"
        )

    u6_index = list(PRIMARY_UNIVERSES).index(
        "U6_POLLEN_THEFT_HARGREAVES_2009"
    ) + 1
    ordered_col = list(SLOPE_COLUMNS).index(
        "temporal_ORDERED_OR_ALTERNATING"
    )
    u6_ordered = [
        int(
            universe == u6_index
            and x_row[ordered_col] == 1
        )
        for universe, x_row in zip(
            payload["stan_data"]["universe"],
            payload["stan_data"]["X"],
        )
    ]
    payload["stan_data"]["u6_ordered"] = u6_ordered
    payload["stan_data"]["interaction_prior_sd"] = 0.75
    payload["metadata"]["analysis"] = (
        "balance_plant_confirmatory_model_v4_temporal_generality"
    )
    payload["metadata"]["generality_interaction"] = (
        "U6_x_temporal_ORDERED_OR_ALTERNATING"
    )
    payload["metadata"]["practical_interaction_margin_log_odds"] = 1.0
    payload["metadata"]["generality_claim_rule"] = (
        "report within-universe ORDERED-vs-SIMULTANEOUS contrasts; "
        "do not infer cross-universe generality from the common-slope model alone"
    )
    return payload

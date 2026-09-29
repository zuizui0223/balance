"""Deterministic pre-fit analysis pipeline for BALANCE plant model V4."""
from __future__ import annotations

from typing import Iterable

from .plant_model_assembly import build_model_assembly_readout, validate_model_assembly_rows
from .plant_model_v4_fit import (
    build_v4_prior_sensitivity_input,
    build_v4_stan_input,
    build_v4_temporal_generality_input,
)


def build_v4_analysis_inputs(rows: Iterable[dict[str, str]]) -> dict:
    """Build all registered V4 model inputs from a licensed assembly.

    The main model and prior sensitivity are produced only when the frozen primary
    estimability gate passes. The stronger temporal-generality sensitivity is optional
    and remains absent when its stricter common-support/outcome-support gate is not met.
    """
    licensed = validate_model_assembly_rows(rows)
    readout = build_model_assembly_readout(licensed)
    if not readout["ready_for_primary_fit"]:
        blockers = readout["v4_estimability"]["blockers"]
        raise ValueError(
            "V4 licensed assembly is not ready for the primary fit: "
            + " | ".join(blockers)
        )

    main = build_v4_stan_input(licensed)
    prior = build_v4_prior_sensitivity_input(licensed)
    estimability = main["metadata"]["estimability"]

    generality = None
    generality_status = "NOT_READY"
    generality_blockers: list[str] = []
    if estimability["temporal_cross_universe_generality_ready"]:
        generality = build_v4_temporal_generality_input(licensed)
        generality_status = "READY"
    else:
        if not estimability.get(
            "temporal_cross_universe_marginal_replication_ready", False
        ):
            generality_blockers.append("marginal_timing_replication")
        if not estimability.get(
            "temporal_cross_universe_common_support_ready", False
        ):
            generality_blockers.append("shared_module_timing_common_support")
        if not estimability.get(
            "temporal_cross_universe_outcome_support_ready", False
        ):
            generality_blockers.append("per_universe_target_outcome_support")

    return {
        "analysis": "balance_plant_v4_prefit_pipeline",
        "assembly_readout": readout,
        "main_stan_input": main,
        "prior_sensitivity_stan_input": prior,
        "temporal_generality_status": generality_status,
        "temporal_generality_blockers": generality_blockers,
        "temporal_generality_stan_input": generality,
        "main_fit_ready": True,
        "standalone_reactivation_decision": "NOT_EVALUATED_BY_PREFIT_PIPELINE",
        "claim_ceiling": "prefit_inputs_only_no_fitted_effect",
    }

"""Readiness diagnostic for a conflict-conditioned U3 routing programme.

The current U3 matched lane is too small and incompletely resolved for a
confirmatory routing model. This module quantifies what is already resolved
without treating observed architecture as a matching variable or selecting new
controls from their outcomes.
"""
from __future__ import annotations

from pathlib import Path

from .plant_u3_dependence import load_u3_dependence
from .plant_u3_matched_extraction import load_u3_matched_extraction


def build_u3_routing_readiness(
    extraction_path: Path,
    dependence_path: Path,
    adjudication_path: Path,
    pair_path: Path,
    case_path: Path,
    universe_path: Path,
) -> dict:
    extraction = load_u3_matched_extraction(
        extraction_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )
    dependence = load_u3_dependence(
        dependence_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )
    dep_by_pair = {r["pair_id"]: r["dependence_block_id"] for r in dependence}

    controls = [r for r in extraction if r["taxon_role"] == "CONTROL"]
    positive_controls = [
        r for r in controls if r["pollen_fate_conflict_status"] == "POSITIVE"
    ]
    unresolved_conflict_controls = [
        r for r in controls if r["pollen_fate_conflict_status"] == "UNRESOLVED"
    ]
    positive_resolved_architecture = [
        r for r in positive_controls if r["architecture_mode"] != "UNRESOLVED"
    ]
    positive_unresolved_architecture = [
        r for r in positive_controls if r["architecture_mode"] == "UNRESOLVED"
    ]

    resolved_architectures = sorted(
        {r["architecture_mode"] for r in positive_resolved_architecture}
    )
    resolved_blocks = sorted(
        {dep_by_pair[r["pair_id"]] for r in positive_resolved_architecture}
    )

    n_positive = len(positive_controls)
    architecture_fraction = (
        len(positive_resolved_architecture) / n_positive if n_positive else 0.0
    )

    routing_measurement_complete = (
        not unresolved_conflict_controls
        and not positive_unresolved_architecture
    )
    # No arbitrary minimum-n threshold is invented here. A confirmatory routing
    # model requires a separately frozen prospective model/sample-size contract
    # after measurement completeness; that contract does not yet exist.
    routing_model_ready = False

    return {
        "analysis": "balance_u3_conflict_conditioned_routing_readiness",
        "n_controls": len(controls),
        "n_positive_conflict_controls": n_positive,
        "n_positive_controls_with_resolved_architecture": len(
            positive_resolved_architecture
        ),
        "positive_control_architecture_resolution_fraction": architecture_fraction,
        "positive_controls_with_unresolved_architecture": sorted(
            r["taxon"] for r in positive_unresolved_architecture
        ),
        "controls_with_unresolved_conflict": sorted(
            r["taxon"] for r in unresolved_conflict_controls
        ),
        "resolved_positive_control_architectures": resolved_architectures,
        "n_resolved_positive_control_dependence_blocks": len(resolved_blocks),
        "resolved_positive_control_dependence_blocks": resolved_blocks,
        "n_shared_integrated_positive_controls": sum(
            r["architecture_mode"] == "SHARED_INTEGRATED"
            for r in positive_controls
        ),
        "routing_measurement_complete": routing_measurement_complete,
        "prospective_routing_model_contract_frozen": False,
        "routing_model_ready": routing_model_ready,
        "public_retrieval_ceiling_ledger": "data/BALANCE_PLANT_U3_EVIDENCE_CEILING_V1.csv",
        "public_retrieval_ceilings_frozen_for_current_unresolved_targets": True,
        "next_evidence_targets": [
            "Senna_covesii_routing_requires_new_direct_primary_or_empirical_evidence",
            "Osbeckia_chinensis_conflict_requires_new_direct_primary_or_empirical_evidence",
            "expand_with_prospectively_matched_positive_conflict_controls_in_new_dependence_blocks",
        ],
        "acquisition_guard": (
            "new controls must be selected under the frozen predictor-blind matching "
            "protocol before conflict strength or routing architecture extraction"
        ),
        "model_readiness_rule": (
            "do not invent a minimum-n threshold post hoc; current unresolved targets "
            "have frozen public-retrieval ceilings, so new direct or empirical evidence "
            "or prospectively selected new dependence blocks are required; before fitting "
            "a confirmatory routing effect freeze a prospective model and estimability contract"
        ),
        "claim_ceiling": (
            "routing_readiness_and_acquisition_priority_only_not_fitted_routing_effect_"
            "not_population_prevalence_not_historical_causation"
        ),
    }

"""Readiness diagnostic for a conflict-conditioned U3 routing programme.

The current U3 matched lane is too small and incompletely resolved for a
confirmatory routing model. This module quantifies what is already resolved
without treating observed architecture as a matching variable or selecting new
controls from their outcomes.
"""
from __future__ import annotations

from pathlib import Path

from .plant_u3_conflict_identification import build_u3_binary_conflict_identification
from .plant_u3_dependence import load_u3_dependence
from .plant_u3_matched_extraction import load_u3_matched_extraction
from .plant_u3_routing_expansion import build_u3_routing_expansion_readout
from .plant_u3_routing_diversity import build_u3_routing_diversity_identification
from .plant_u3_morphology_routing_identification import (
    build_u3_morphology_routing_identification,
)
from .plant_u3_morphology_routing_nonidentifiability import (
    build_u3_morphology_routing_nonidentifiability,
)
from .plant_u3_sencov_prediction import build_sencov_prediction_readout
from .plant_u3_targeted_measurement import build_u3_targeted_measurement_readout


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
    expansion_path = (
        extraction_path.parent / "BALANCE_PLANT_U3_ROUTING_EXPANSION_QUEUE_V1.csv"
    )
    expansion = build_u3_routing_expansion_readout(expansion_path, universe_path)
    conflict_identification = build_u3_binary_conflict_identification(
        extraction_path,
        dependence_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )
    routing_diversity = build_u3_routing_diversity_identification(
        extraction_path,
        dependence_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )
    morphology_routing = build_u3_morphology_routing_identification(
        extraction_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )
    proxy_nonidentifiability = build_u3_morphology_routing_nonidentifiability(
        extraction_path,
        dependence_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )
    targeted_measurement_path = (
        extraction_path.parent / "BALANCE_PLANT_U3_TARGETED_MEASUREMENT_SPEC_V2.json"
    )
    targeted_measurement = build_u3_targeted_measurement_readout(
        targeted_measurement_path
    )
    sencov_prediction_path = (
        extraction_path.parent / "BALANCE_PLANT_U3_SENCOV_ROUTING_PREDICTION_V1.json"
    )
    sencov_prediction = build_sencov_prediction_readout(
        sencov_prediction_path,
        extraction_path,
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
        "binary_conflict_identification_certificate": (
            "docs/BALANCE_PLANT_U3_BINARY_CONFLICT_IDENTIFICATION_V1.md"
        ),
        "binary_conflict_discriminant_status": conflict_identification[
            "binary_conflict_discriminant_status"
        ],
        "binary_conflict_any_completion_finite_mle": conflict_identification[
            "any_completion_has_finite_matched_log_odds_mle"
        ],
        "binary_conflict_sufficiency_falsified": conflict_identification[
            "sufficiency_falsified_by_positive_controls"
        ],
        "routing_diversity_identification_certificate": (
            "docs/BALANCE_PLANT_U3_ROUTING_DIVERSITY_IDENTIFICATION_V1.md"
        ),
        "minimum_observed_positive_control_routing_states": routing_diversity[
            "minimum_observed_distinct_routing_states"
        ],
        "minimum_observed_routing_dependence_blocks": routing_diversity[
            "minimum_observed_dependence_blocks"
        ],
        "routing_non_degenerate_under_all_unresolved_completions": routing_diversity[
            "routing_non_degenerate_under_all_unresolved_completions"
        ],
        "morphology_routing_identification_certificate": (
            "docs/BALANCE_PLANT_U3_MORPHOLOGY_ROUTING_IDENTIFICATION_V1.md"
        ),
        "heteranthery_not_necessary_for_within_flower_division_of_labour": (
            morphology_routing[
                "heteranthery_not_necessary_for_within_flower_division_of_labour"
            ]
        ),
        "n_same_route_morphology_discordant_pairs": morphology_routing[
            "n_same_route_morphology_discordant_pairs"
        ],
        "morphology_routing_proxy_nonidentifiability_certificate": (
            "docs/BALANCE_PLANT_U3_MORPHOLOGY_ROUTING_NONIDENTIFIABILITY_V1.md"
        ),
        "morphology_does_not_uniquely_identify_routing": proxy_nonidentifiability[
            "morphology_does_not_uniquely_identify_routing"
        ],
        "routing_does_not_uniquely_identify_morphology": proxy_nonidentifiability[
            "routing_does_not_uniquely_identify_morphology"
        ],
        "bidirectional_proxy_equivalence_rejected": proxy_nonidentifiability[
            "bidirectional_proxy_equivalence_rejected"
        ],
        "routing_measurement_complete": routing_measurement_complete,
        "prospective_routing_model_contract_frozen": False,
        "routing_model_ready": routing_model_ready,
        "public_retrieval_ceiling_ledger": "data/BALANCE_PLANT_U3_EVIDENCE_CEILING_V1.csv",
        "public_retrieval_ceilings_frozen_for_current_unresolved_targets": True,
        "targeted_measurement_contract": "data/BALANCE_PLANT_U3_TARGETED_MEASUREMENT_SPEC_V2.json",
        "targeted_measurement_targets": targeted_measurement["target_taxa"],
        "senna_covesii_routing_contract_frozen": targeted_measurement[
            "senna_covesii_routing_contract_frozen"
        ],
        "senna_covesii_shared_integrated_requires_equivalence": targeted_measurement[
            "senna_covesii_shared_integrated_requires_equivalence"
        ],
        "senna_covesii_prediction_contract": (
            "data/BALANCE_PLANT_U3_SENCOV_ROUTING_PREDICTION_V1.json"
        ),
        "senna_covesii_prediction_status": sencov_prediction["status"],
        "senna_covesii_predicted_routing_state": sencov_prediction[
            "predicted_routing_state"
        ],
        "senna_covesii_prediction_is_independent_block_replication": (
            sencov_prediction["target_is_independent_new_dependence_block"]
        ),
        "prospective_expansion_queue": "data/BALANCE_PLANT_U3_ROUTING_EXPANSION_QUEUE_V1.csv",
        "prospective_expansion_queue_exhausted": expansion[
            "prospective_queue_exhausted"
        ],
        "n_prospective_expansion_blocks": expansion["n_new_dependence_blocks"],
        "n_prospective_expansion_evidence_ceiling_blocked": expansion[
            "n_evidence_ceiling_blocked"
        ],
        "next_evidence_targets": [
            "test_frozen_Senna_covesii_WITHIN_FLOWER_prediction_under_U3MEAS_SENCOV_001",
            "collect_or_adjudicate_Osbeckia_conflict_under_U3MEAS_OSBCHI_001",
            "collect_or_adjudicate_Monochoria_pollination_under_frozen_exact_species_routes",
            "reopen_frozen_expansion_blocks_only_with_new_matching_stage_evidence",
        ],
        "acquisition_guard": (
            "new controls must be selected under the frozen predictor-blind matching "
            "protocol before conflict strength or routing architecture extraction"
        ),
        "sencov_estimability_contract": (
            "docs/BALANCE_PLANT_U3_SENCOV_ROUTING_ESTIMABILITY_V1.md"
        ),
        "sencov_estimability_targets_template": (
            "data/BALANCE_PLANT_U3_SENCOV_ROUTING_POWER_TARGETS_TEMPLATE_V1.json"
        ),
        "sencov_stage0_nuisance_template": (
            "data/BALANCE_PLANT_U3_SENCOV_STAGE0_NUISANCE_TEMPLATE_V1.json"
        ),
        "model_readiness_rule": (
            "do not invent a minimum-n threshold post hoc; current unresolved targets "
            "have frozen public-retrieval ceilings and the prospective four-family "
            "expansion is exhausted at matching-stage evidence ceilings, so new direct "
            "or empirical measurement evidence or genuinely new matching evidence is "
            "required; before fitting a confirmatory routing effect freeze a prospective "
            "model and estimability contract"
        ),
        "claim_ceiling": (
            "routing_readiness_and_acquisition_priority_only_not_fitted_routing_effect_"
            "not_population_prevalence_not_historical_causation"
        ),
    }

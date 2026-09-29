"""Bidirectional non-identifiability certificate for U3 morphology and routing.

This combines two already source-adjudicated U3 facts without fitting a new
effect model:

1. the same nonheterantherous morphology occurs with more than one resolved
   routing architecture among conflict-positive controls; and
2. the same resolved within-flower routing state occurs on both sides of a
   matched heteranthery morphology contrast.

The result is a proxy-identification statement, not a transition or prevalence
estimate.
"""
from __future__ import annotations

from pathlib import Path

from .plant_u3_morphology_routing_identification import (
    build_u3_morphology_routing_identification,
)
from .plant_u3_routing_diversity import (
    build_u3_routing_diversity_identification,
)


def build_u3_morphology_routing_nonidentifiability(
    extraction_path: Path,
    dependence_path: Path,
    adjudication_path: Path,
    pair_path: Path,
    case_path: Path,
    universe_path: Path,
) -> dict:
    morphology = build_u3_morphology_routing_identification(
        extraction_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )
    routing = build_u3_routing_diversity_identification(
        extraction_path,
        dependence_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )

    same_morphology_different_routes = (
        routing["minimum_observed_distinct_routing_states"] >= 2
        and routing["minimum_observed_dependence_blocks"] >= 2
    )
    same_route_different_morphologies = (
        morphology["n_same_route_morphology_discordant_pairs"] >= 1
    )
    bidirectional = (
        same_morphology_different_routes
        and same_route_different_morphologies
    )

    absent_morphology_receipts = routing["resolved_route_receipts"]
    same_route_receipts = morphology["same_route_counterexamples"]

    return {
        "analysis": "balance_u3_morphology_routing_proxy_nonidentifiability_v1",
        "conditioning_population": (
            "pass_adjudicated_u3_matched_taxa_with_positive_pollen_fate_conflict_"
            "and_source_resolved_routing_where_required"
        ),
        "same_nonheterantherous_morphology_different_routing_states": (
            same_morphology_different_routes
        ),
        "nonheterantherous_resolved_route_receipts": absent_morphology_receipts,
        "minimum_nonheterantherous_routing_states": routing[
            "minimum_observed_distinct_routing_states"
        ],
        "minimum_nonheterantherous_routing_dependence_blocks": routing[
            "minimum_observed_dependence_blocks"
        ],
        "same_routing_state_different_heteranthery_morphologies": (
            same_route_different_morphologies
        ),
        "matched_same_route_morphology_contrast_receipts": same_route_receipts,
        "morphology_does_not_uniquely_identify_routing": (
            same_morphology_different_routes
        ),
        "routing_does_not_uniquely_identify_morphology": (
            same_route_different_morphologies
        ),
        "bidirectional_proxy_equivalence_rejected": bidirectional,
        "ecological_interpretation": (
            "Visible fertile-stamen heteranthery is one implementation layer, not "
            "a one-to-one readout of pollen-fate routing. Under positive pollen-use "
            "conflict, nonheterantherous controls already realize both within-flower "
            "and among-flower routing, while within-flower routing itself occurs "
            "with both heterantherous and nonheterantherous fertile-stamen morphology."
        ),
        "comparative_design_consequence": (
            "Do not use heteranthery morphology as a deterministic proxy for routing "
            "architecture, and do not infer heteranthery state from a routing label. "
            "Conflict, routing level and visible morphology must remain separate variables."
        ),
        "claim_ceiling": (
            "registered_matched_counterexample_and_minimum_route_diversity_only_"
            "not_population_frequency_not_transition_rate_not_historical_causation_"
            "not_morphology_effect_estimate"
        ),
    }

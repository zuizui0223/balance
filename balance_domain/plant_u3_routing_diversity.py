"""Identification certificate for minimum routing diversity in U3 controls."""
from __future__ import annotations

from pathlib import Path

from .plant_u3_dependence import load_u3_dependence
from .plant_u3_matched_extraction import load_u3_matched_extraction


def build_u3_routing_diversity_identification(
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
    resolved = [
        r for r in positive_controls if r["architecture_mode"] != "UNRESOLVED"
    ]
    unresolved_positive = [
        r for r in positive_controls if r["architecture_mode"] == "UNRESOLVED"
    ]

    routes = sorted({r["architecture_mode"] for r in resolved})
    blocks = sorted({dep_by_pair[r["pair_id"]] for r in resolved})
    route_receipts = sorted(
        [
            {
                "taxon": r["taxon"],
                "pair_id": r["pair_id"],
                "dependence_block_id": dep_by_pair[r["pair_id"]],
                "architecture_mode": r["architecture_mode"],
            }
            for r in resolved
        ],
        key=lambda x: (x["architecture_mode"], x["taxon"]),
    )

    minimum_routes = len(routes)
    minimum_blocks = len(blocks)
    nondegenerate = minimum_routes >= 2 and minimum_blocks >= 2

    return {
        "analysis": "balance_u3_routing_diversity_identification_v1",
        "population": "nonheterantherous_controls_with_positive_pollen_fate_conflict",
        "n_positive_controls": len(positive_controls),
        "n_resolved_positive_controls": len(resolved),
        "n_unresolved_positive_controls": len(unresolved_positive),
        "unresolved_positive_controls": sorted(r["taxon"] for r in unresolved_positive),
        "minimum_observed_distinct_routing_states": minimum_routes,
        "minimum_observed_dependence_blocks": minimum_blocks,
        "resolved_routing_states": routes,
        "resolved_dependence_blocks": blocks,
        "resolved_route_receipts": route_receipts,
        "routing_non_degenerate_under_all_unresolved_completions": nondegenerate,
        "binary_conflict_does_not_determine_unique_routing_state": nondegenerate,
        "heteranthery_absence_does_not_imply_shared_integration": all(
            r["architecture_mode"] != "SHARED_INTEGRATED" for r in resolved
        )
        and bool(resolved),
        "completion_argument": (
            "Unresolved controls can add routing states or repeat observed states, "
            "but cannot erase the two already source-resolved routing states in "
            "different frozen dependence blocks."
        ),
        "claim_ceiling": (
            "minimum_observed_conflict_conditioned_routing_diversity_only_"
            "not_population_frequency_not_transition_probability_not_causal_effect"
        ),
    }

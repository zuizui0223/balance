"""Identification certificate separating heteranthery morphology from routing state."""
from __future__ import annotations

from pathlib import Path

from .plant_u3_matched_extraction import load_u3_matched_extraction


def build_u3_morphology_routing_identification(
    extraction_path: Path,
    adjudication_path: Path,
    pair_path: Path,
    case_path: Path,
    universe_path: Path,
) -> dict:
    rows = load_u3_matched_extraction(
        extraction_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )
    grouped: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["pair_id"], {})[row["taxon_role"]] = row

    evaluable = []
    same_route = []
    different_route = []
    nonheteranthery_within_flower = []

    for pair_id, roles in sorted(grouped.items()):
        case = roles["CASE"]
        control = roles["CONTROL"]
        both_conflict_positive = (
            case["pollen_fate_conflict_status"] == "POSITIVE"
            and control["pollen_fate_conflict_status"] == "POSITIVE"
        )
        both_route_resolved = (
            case["architecture_mode"] != "UNRESOLVED"
            and control["architecture_mode"] != "UNRESOLVED"
        )
        if both_conflict_positive and both_route_resolved:
            receipt = {
                "pair_id": pair_id,
                "case_taxon": case["taxon"],
                "control_taxon": control["taxon"],
                "case_heteranthery": "PRESENT_BY_CASE_DEFINITION",
                "control_heteranthery": "ABSENT_BY_ADJUDICATED_CONTROL_DEFINITION",
                "case_route": case["architecture_mode"],
                "control_route": control["architecture_mode"],
                "same_route": case["architecture_mode"] == control["architecture_mode"],
            }
            evaluable.append(receipt)
            if receipt["same_route"]:
                same_route.append(receipt)
            else:
                different_route.append(receipt)

        if (
            control["pollen_fate_conflict_status"] == "POSITIVE"
            and control["architecture_mode"] == "WITHIN_FLOWER_DIVISION_OF_LABOUR"
        ):
            nonheteranthery_within_flower.append(
                {
                    "pair_id": pair_id,
                    "taxon": control["taxon"],
                    "architecture_mode": control["architecture_mode"],
                }
            )

    counterexample_exists = bool(nonheteranthery_within_flower)
    matched_same_route_counterexample_exists = bool(same_route)

    return {
        "analysis": "balance_u3_morphology_routing_identification_v1",
        "population": "pass_adjudicated_u3_matched_pairs",
        "n_evaluable_pairs_both_conflict_positive_and_route_resolved": len(evaluable),
        "n_same_route_morphology_discordant_pairs": len(same_route),
        "n_different_route_morphology_discordant_pairs": len(different_route),
        "evaluable_pair_receipts": evaluable,
        "same_route_counterexamples": same_route,
        "nonheterantherous_positive_controls_with_within_flower_division": (
            nonheteranthery_within_flower
        ),
        "heteranthery_not_necessary_for_within_flower_division_of_labour": (
            counterexample_exists
        ),
        "heteranthery_morphology_does_not_uniquely_identify_functional_routing": (
            matched_same_route_counterexample_exists
        ),
        "identification_argument": (
            "A PASS-adjudicated nonheterantherous control, Senna spectabilis, "
            "has positive pollen-fate conflict and source-resolved WITHIN_FLOWER_"
            "DIVISION_OF_LABOUR. In its matched pair, heterantherous Senna alata "
            "has the same resolved routing state. Therefore morphological "
            "heteranthery is not necessary for within-flower functional division, "
            "and the morphology contrast does not uniquely identify the routing state."
        ),
        "claim_ceiling": (
            "matched_counterexample_to_morphology_routing_equivalence_only_"
            "not_population_frequency_not_transition_probability_not_causal_effect"
        ),
    }

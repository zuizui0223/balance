"""Partial-identification diagnostic for binary pollen-fate conflict in U3.

This module does not estimate population prevalence or a causal effect. It asks
what the current four-pair matched extraction logically permits when unresolved
binary conflict states are allowed to take either admissible value.
"""
from __future__ import annotations

from pathlib import Path

from .plant_u3_matched_extraction import load_u3_matched_extraction


RESOLVED_POSITIVE = "POSITIVE"
RESOLVED_NEGATIVE = "NO_DEMONSTRATED_CONFLICT"
UNRESOLVED = "UNRESOLVED"


def _positive_fraction_bounds(rows: list[dict[str, str]]) -> tuple[float, float]:
    n = len(rows)
    if n == 0:
        raise ValueError("partial-identification group cannot be empty")
    positive = sum(r["pollen_fate_conflict_status"] == RESOLVED_POSITIVE for r in rows)
    unresolved = sum(r["pollen_fate_conflict_status"] == UNRESOLVED for r in rows)
    return positive / n, (positive + unresolved) / n


def build_u3_conflict_partial_identification(
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
    cases = [r for r in rows if r["taxon_role"] == "CASE"]
    controls = [r for r in rows if r["taxon_role"] == "CONTROL"]

    case_lower, case_upper = _positive_fraction_bounds(cases)
    control_lower, control_upper = _positive_fraction_bounds(controls)

    pair_roles: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        pair_roles.setdefault(row["pair_id"], {})[row["taxon_role"]] = row

    definite_case_positive_control_negative = 0
    possible_case_positive_control_negative = 0
    for roles in pair_roles.values():
        case_status = roles["CASE"]["pollen_fate_conflict_status"]
        control_status = roles["CONTROL"]["pollen_fate_conflict_status"]
        if case_status == RESOLVED_POSITIVE and control_status == RESOLVED_NEGATIVE:
            definite_case_positive_control_negative += 1
            possible_case_positive_control_negative += 1
        elif case_status == RESOLVED_POSITIVE and control_status == UNRESOLVED:
            possible_case_positive_control_negative += 1

    n_pairs = len(pair_roles)
    contrast_lower = case_lower - control_upper
    contrast_upper = case_upper - control_lower

    positive_controls = sorted(
        r["taxon"] for r in controls
        if r["pollen_fate_conflict_status"] == RESOLVED_POSITIVE
    )
    unresolved_controls = sorted(
        r["taxon"] for r in controls
        if r["pollen_fate_conflict_status"] == UNRESOLVED
    )

    return {
        "analysis": "balance_u3_binary_conflict_partial_identification",
        "n_pairs": n_pairs,
        "case_positive_fraction_bounds": [case_lower, case_upper],
        "control_positive_fraction_bounds": [control_lower, control_upper],
        "case_minus_control_positive_fraction_bounds": [
            contrast_lower,
            contrast_upper,
        ],
        "case_positive_control_negative_pair_count_bounds": [
            definite_case_positive_control_negative,
            possible_case_positive_control_negative,
        ],
        "case_positive_control_negative_pair_fraction_bounds": [
            definite_case_positive_control_negative / n_pairs,
            possible_case_positive_control_negative / n_pairs,
        ],
        "positive_control_taxa": positive_controls,
        "unresolved_control_taxa": unresolved_controls,
        "binary_conflict_presence_deterministically_separates_heteranthery": (
            len(positive_controls) == 0
        ),
        "interpretation": (
            "In the current matched sample, binary pollen-fate conflict presence "
            "cannot deterministically distinguish heteranthery because multiple "
            "nonheterantherous controls are directly conflict-positive. The single "
            "unresolved control can change the raw case-control positive-fraction "
            "contrast only within the reported bounds."
        ),
        "claim_ceiling": (
            "matched_sample_partial_identification_only_not_population_prevalence_"
            "not_causal_effect_not_conflict_strength_not_historical_causation"
        ),
    }

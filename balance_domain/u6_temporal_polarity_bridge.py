"""U6: source-backed visitor-order polarity versus reproductive-evidence support.

A post-open linkage of published source-order descriptions already assembled
in draft PR #252 and the untouched main-branch U6 admissions/SCREENED predictors.
It never infers an architectural response, modified V4 predictor, or true
reproductive-fitness effect from visitor chronology.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from .plant_confirmatory import load_plant_predictor_receipts
from .u6_source_coordinate_audit import (
    _audit_admissions, _load_csv, _load_postopen_flags,
    _scenario, _screened_design_rows,
)

ORDER_FIELDS = (
    "dependency_group", "original_timing_code", "postopen_visitor_order",
    "first_agent", "second_agent", "primary_doi", "source_evidence_level",
    "fitness_endpoint_ceiling", "independent_architecture_outcome",
    "source_lineage",
)
EXPECTED_ORDER = {
    "Clusia_arrudae": (
        "THEFT_BEFORE_EFFECTIVE_TRANSFER",
        "10.1111/j.1744-7429.2004.tb00329.x",
    ),
    "Crescentia_alata": (
        "THEFT_BEFORE_EFFECTIVE_TRANSFER",
        "10.17129/botsci.1377",
    ),
    "Tolmiea_menziesii": (
        "EFFECTIVE_TRANSFER_BEFORE_THEFT",
        "10.1007/s00606-003-0067-1",
    ),
}
EXPECTED_FITNESS_TAG_BY_ORDER = {
    "Clusia_arrudae": "DIRECT_REMOVAL_FITNESS_COST",
    "Crescentia_alata": "DIRECT_POLLEN_ROBBING_NO_POLLINATION",
    "Tolmiea_menziesii": "DIRECT_POLLEN_ROBBING_NO_POLLINATION",
}
POLES = (
    "THEFT_BEFORE_EFFECTIVE_TRANSFER",
    "EFFECTIVE_TRANSFER_BEFORE_THEFT",
)


def build_u6_temporal_polarity_bridge(
    pass1_path: Path,
    admission_batches: list[Path],
    order_crosswalk_path: Path,
    stage_flag_path: Path,
    u2_conflict_path: Path,
    u2_receipt_path: Path,
    u6_receipt_path: Path,
) -> dict:
    """Join three existing original visitor sequences to source-evidence tags.

    Notes:
      - The term EFFECTIVE_TRANSFER refers to a documented pollinator visit;
        transfer of **all** available pollen and realized paternity is NOT observed.
      - The crosswalk is a reuse of PR #252, not an independent new original study.
      - A primary-source fitness *tag* is not confirmed same-treatment mediation.
    """
    with pass1_path.open(encoding="utf-8") as fh:
        frozen = json.load(fh)
    if frozen.get("pass2", {}).get("primary_model_admission") is not False:
        raise ValueError("Cannot operate on an unfrozen or admitted U6 outcome surface")
    admitted, source_ref_map, dependency = _audit_admissions(frozen, admission_batches)
    universe = set(frozen["included_dependency_groups"])
    order_records = _load_csv(order_crosswalk_path, ORDER_FIELDS)
    if len(order_records) != 3:
        raise ValueError("Only three frozen source-side sequential groups may be linked")
    flagged = _load_postopen_flags(stage_flag_path, universe)
    if set(EXPECTED_ORDER) & set(flagged):
        raise ValueError("Source-stage review flags overlap sequential comparison")

    predictor_rows = load_plant_predictor_receipts(u6_receipt_path)
    by_cluster: dict[str, dict[str, dict[str, str]]] = {}
    for receipt in predictor_rows:
        group = receipt["cluster_id"]
        predictor = receipt["predictor"]
        if predictor in by_cluster.setdefault(group, {}):
            raise ValueError("Duplicate U6 source predictor within one group")
        by_cluster[group][predictor] = receipt
    if set(by_cluster) != universe:
        raise ValueError("U6 source predictor group roster differs from freeze")
    if any(row["adjudication_status"] != "SCREENED" for row in predictor_rows):
        raise ValueError("This linkage only accepts SCREENED source predictors")

    discovered = {}
    for row in order_records:
        group = row["dependency_group"]
        if group in discovered:
            raise ValueError("Duplicated visitor-order group")
        expected = EXPECTED_ORDER.get(group)
        if expected is None or (row["postopen_visitor_order"], row["primary_doi"]) != expected:
            raise ValueError("Visitor-order source identity or polarity mismatch")
        if row["original_timing_code"] != "SEQUENTIAL_WITHIN_UNIT":
            raise ValueError("Post-open crosswalk cannot revise the frozen timing code")
        if row["source_evidence_level"] != "ORIGINAL_PUBLISHED_ABSTRACT":
            raise ValueError("Incorrect evidentiary source level")
        if row["source_lineage"] != "PR252_SOURCE_ORDER_REUSE_NOT_NEW_REPLICATION":
            raise ValueError("Must preserve upstream PR #252 provenance")
        if row["independent_architecture_outcome"] != "NOT_OPENED":
            raise ValueError("Cannot claim architecture observations or coder outputs")
        for col in ("first_agent", "second_agent", "fitness_endpoint_ceiling"):
            if not row[col].strip():
                raise ValueError("Source-stage evidence limit must be explicit")
        actual = by_cluster[group]["conflict_timing_geometry"]
        if actual["reported_value"] != "SEQUENTIAL_WITHIN_UNIT":
            raise ValueError("Frozen source geometry differs from visitor-order crosswalk")
        if row["primary_doi"] not in actual["source_id"]:
            raise ValueError("Published primary DOI not found in frozen source receipt")
        if admitted.get(group) != EXPECTED_FITNESS_TAG_BY_ORDER[group]:
            raise ValueError("Original frozen admission evidence category changed")
        discovered[group] = row

    if set(discovered) != set(EXPECTED_ORDER):
        raise ValueError("No subset or extra sequential source is allowed")

    source_sequential = {
        group for group, v in by_cluster.items()
        if v["conflict_timing_geometry"]["reported_value"] == "SEQUENTIAL_WITHIN_UNIT"
    }
    if source_sequential != set(discovered):
        raise ValueError("Unaccounted frozen sequential source group")
    if len(universe) != 21 or len(source_sequential) != 3:
        raise ValueError("Frozen timing denominators changed")

    u2, u6 = _screened_design_rows(
        u2_conflict_path, u2_receipt_path, u6_receipt_path, universe
    )
    cases = {}
    for drop in (None, *sorted(discovered)):
        keep = universe - ({drop} if drop is not None else set())
        label = "FROZEN_ALL" if drop is None else "HYPOTHETICAL_REMOVE_" + drop.upper()
        scan = _scenario(u2, u6, keep)
        remaining_order = [discovered[g]["postopen_visitor_order"] for g in discovered if g in keep]
        remaining_fit = [
            g for g in discovered if g in keep
            and admitted[g] == "DIRECT_REMOVAL_FITNESS_COST"
        ]
        cases[label] = {
            "scenario_is_confirmatory": False,
            "removed_group": drop,
            "source_screened_v4_rank": scan["full_design_rank"],
            "u6_ordered_source_groups": scan["u6_screened_timing"]["ORDERED_OR_ALTERNATING"],
            "source_polarity_counts": {
                pole: remaining_order.count(pole) for pole in POLES
            },
            "ordered_groups_with_original_fitness_admission_tag": sorted(remaining_fit),
            "ordered_poles_each_with_min_two_sources": all(
                remaining_order.count(pole) >= 2 for pole in POLES
            ),
            "frozen_u6_ordered_min_two_sources": scan["u6_has_two_ordered_groups"],
            "frozen_g1_predictor_common_support_only": scan["g1_predictor_common_support_only"],
        }
    if len(source_ref_map) != 21 or dependency["included_unique_primary_reference_ids"] != 21:
        raise ValueError("Original admission-source dependence not retained")
    return {
        "analysis": "BALANCE_U6_VISITOR_ORDER_POLARITY_LINK_V1",
        "source_lineage": "PR252_PRIOR_SOURCE_LEDGER_REUSED_NOT_INDEPENDENT_REPLICATION",
        "status": "POSTOPEN_EXPLORATORY_SOURCE_ONLY",
        "original_u6_source_screened_group_count": len(universe),
        "original_u6_sequential_source_group_count": len(discovered),
        "source_poles": {
            p: sorted(g for g, row in discovered.items()
                      if row["postopen_visitor_order"] == p)
            for p in POLES
        },
        "original_admission_fitness_tag_within_sequential": [
            g for g in sorted(discovered)
            if admitted[g] == "DIRECT_REMOVAL_FITNESS_COST"
        ],
        "study_level_fitness_admission_tag_not_causal_pollen_specific_effect": True,
        "original_source_overlap_flagged_with_stage_mismatch": [],
        "exact_source_order_leave_one_out": cases,
        "biological_limit": (
            "Observed visitor order is not floral programmable timing, nor "
            "a same-fitness-scale benefit of a second architecture. A visitor "
            "arriving before a thief need not have exported all available pollen. "
            "Realized fitness requires within-flower pollen retention and "
            "subsequent legitimate pickup, stigma deposition and paternity/seed "
            "outcomes under matched treatment."
        ),
        "original_21_u6_admissions_changed": False,
        "source_predictor_values_modified": False,
        "architecture_outcomes_opened": False,
        "v4_model_fitted": False,
        "causal_study_contrast_estimated": False,
    }

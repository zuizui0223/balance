"""Best-case *binary* information benchmark for frozen V4 predictor design.

This is NOT a power analysis or a fit of V4's four-class multinomial outcome.
It only bounds the Fisher information of a hypothetical unpenalized Bernoulli
logistic regression with the same five predictor columns, assuming each
source-screened group is independent and has one binary outcome. Even under
this optimistic assumption, p*(1-p) <= 1/4 for each row.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from math import exp, sqrt
from pathlib import Path

from .plant_confirmatory import load_plant_predictor_receipts
from .plant_model_v4 import _design_matrices
from .plant_v4_preoutcome_attrition import (
    _full_design_rank,
    _primary_level_support,
    _source_screened_rows,
)


def _exact_inverse_of_gram(matrix: list[list[int]]) -> list[list[Fraction]]:
    if not matrix:
        raise ValueError("No design rows supplied")
    p = len(matrix[0])
    if p == 0 or any(len(r) != p for r in matrix):
        raise ValueError("Invalid rectangular design matrix")
    gram = [
        [sum(Fraction(r[i] * r[j]) for r in matrix) for j in range(p)]
        for i in range(p)
    ]
    augmented = [
        [*gram[i], *(Fraction(int(i == j)) for j in range(p))]
        for i in range(p)
    ]
    for col in range(p):
        pivot = next((j for j in range(col, p) if augmented[j][col]), None)
        if pivot is None:
            raise ValueError("Singular design matrix: binary information bound undefined")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        scale = augmented[col][col]
        augmented[col] = [x / scale for x in augmented[col]]
        for row in range(p):
            if row == col:
                continue
            factor = augmented[row][col]
            augmented[row] = [
                augmented[row][j] - factor * augmented[col][j]
                for j in range(2 * p)
            ]
    return [row[p:] for row in augmented]


def _binary_bound_summary(
    columns: list[str], matrix: list[list[int]]
) -> dict[str, dict[str, float | str]]:
    inverse = _exact_inverse_of_gram(matrix)
    return {
        name: {
            "gram_inverse_diagonal_exact": str(inverse[i][i]),
            "optimistic_binary_logit_se_floor": 2 * sqrt(float(inverse[i][i])),
            "illustrative_two_sided_95pct_wald_abs_log_odds_threshold": (
                1.96 * 2 * sqrt(float(inverse[i][i]))
            ),
            "illustrative_two_sided_95pct_wald_or_threshold": exp(
                1.96 * 2 * sqrt(float(inverse[i][i]))
            ),
        }
        for i, name in enumerate(columns)
    }


def _source_study_blocks(
    u2_receipt_path: Path, u6_receipt_path: Path,
    selected_groups: set[str],
) -> dict[str, list[str]]:
    """Audit only exact shared *admission-source* labels, never full paper graph.

    Source IDs are already frozen. Splitting on the explicit additional-source
    separator ' | ' keeps the *first admitting source*, not a later follow-up
    source. Shared primary-source keys indicate non-independent programmes.
    Distinct source keys are not proof of true biological independence.
    """
    group_to_source: dict[str, str] = {}
    for path in (u2_receipt_path, u6_receipt_path):
        for receipt in load_plant_predictor_receipts(path):
            group = receipt["cluster_id"]
            if group not in selected_groups:
                continue
            source = receipt["source_id"].split(" | ", 1)[0].strip()
            if not source:
                raise ValueError("Empty source key")
            if group in group_to_source and group_to_source[group] != source:
                raise ValueError("Conflicting source-key values in one biological group")
            group_to_source[group] = source
    if set(group_to_source) != selected_groups:
        raise ValueError("Source blocks do not cover all frozen predictor groups")
    blocks: dict[str, list[str]] = defaultdict(list)
    for group, source in group_to_source.items():
        blocks[source].append(group)
    return {
        source: sorted(groups)
        for source, groups in sorted(blocks.items())
    }


def build_v4_preoutcome_information_benchmark(
    u2_conflict_path: Path,
    u2_receipt_path: Path,
    u6_receipt_path: Path,
) -> dict:
    """Idealized binary regression information upper-bound using real frozen X."""
    rows = _source_screened_rows(
        u2_conflict_path, u2_receipt_path, u6_receipt_path
    )
    as_v4 = [
        {
            "universe_id": (
                "U2_BARRETT_2002" if r["universe"] == "U2"
                else "U6_POLLEN_THEFT_HARGREAVES_2009"
            ),
            "module_opportunity2": r["module"],
            "temporal_exposure3": r["timing"],
        }
        for r in rows
    ]
    _, _, full_columns, full_matrix = _design_matrices(as_v4)
    if len(full_columns) != 5:
        raise ValueError("V4 frozen five-column design has unexpectedly changed")

    primary_source_blocks = _source_study_blocks(
        u2_receipt_path,
        u6_receipt_path,
        {r["dependency_group"] for r in rows},
    )
    source_group_removal = []
    for source, dropped in primary_source_blocks.items():
        keep = [r for r in rows if r["dependency_group"] not in dropped]
        source_group_removal.append({
            "source_key": source,
            "dropped_groups": dropped,
            "removed_groups_count": len(dropped),
            "remaining_design_rank": _full_design_rank(keep),
            "remaining_primary_level_support": _primary_level_support(keep),
        })

    u2 = [r for r in rows if r["universe"] == "U2"]
    u6 = [r for r in rows if r["universe"] == "U6"]
    u2_binary = [
        [1, int(r["module"] == "MODULAR"),
         int(r["timing"] == "ORDERED_OR_ALTERNATING"),
         int(r["timing"] == "VARIABLE_CONTEXT")]
        for r in u2
    ]
    u6_binary = [
        [1, int(r["timing"] == "ORDERED_OR_ALTERNATING")]
        for r in u6
    ]

    return {
        "analysis": "BALANCE_V4_PREOUTCOME_INFORMATION_BENCHMARK",
        "status": "FROZEN_SOURCE_SCREENED_DESIGN_ONLY",
        "n_source_screened_biological_groups": len(rows),
        "source_key_block_count": len(primary_source_blocks),
        "multi_group_source_blocks": {
            source: groups for source, groups in primary_source_blocks.items()
            if len(groups) > 1
        },
        "leave_one_primary_source_key_out": {
            "n_blocks_checked": len(primary_source_blocks),
            "rank_deficient_deletions": sum(
                x["remaining_design_rank"] < len(full_columns)
                for x in source_group_removal
            ),
            "minimum_primary_level_support_failures": sum(
                not all(x["remaining_primary_level_support"].values())
                for x in source_group_removal
            ),
            "shared_source_multi_group_removals": [
                x for x in source_group_removal
                if x["removed_groups_count"] > 1
            ],
        },
        "optimistic_binary_logit_benchmarks": {
            "pooled_universe_adjusted": _binary_bound_summary(
                full_columns, full_matrix
            ),
            "u2_only": _binary_bound_summary(
                ["intercept", "module_MODULAR",
                 "temporal_ORDERED_OR_ALTERNATING",
                 "temporal_VARIABLE_CONTEXT"], u2_binary
            ),
            "u6_only": _binary_bound_summary(
                ["intercept", "temporal_ORDERED_OR_ALTERNATING"],
                u6_binary,
            ),
        },
        "information_assumptions": (
            "hypothetical independent binary outcomes; unpenalized logistic "
            "regression with the frozen predictor design; per-row Fisher weight "
            "p*(1-p) <= 1/4. The computed SE floors are lower bounds on the "
            "corresponding asymptotic unpenalized binary-logit SE, not the "
            "posterior uncertainty or detectable effect size of V4 multinomial."
        ),
        "architecture_outcomes_used": False,
        "fitted_effects": False,
        "statistical_power_estimated": False,
        "claim_ceiling": (
            "design_information_ceiling_only_no_observed_biological_effect_"
            "no_true_sample_power_no_multinomial_posterior_claim"
        ),
    }

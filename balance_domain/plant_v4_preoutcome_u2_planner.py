"""Outcome-blind, hypothetical U2 sampling-cell design scenarios.

These are not observed additional species, actual prospectively coded source
receipts, independent human returns, statistical power, or fitted outcomes.
Each artificial row is strictly a *future candidate design profile* and may
enter the model only after independent conflict/source/architecture gates.
"""
from __future__ import annotations

from collections import Counter
from math import sqrt
from pathlib import Path

from .plant_model_v4 import _design_matrices
from .plant_v4_preoutcome_attrition import _source_screened_rows
from .plant_v4_preoutcome_information import _exact_inverse_of_gram


MODULES = ("SINGLE", "MODULAR")
TIMINGS = ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING", "VARIABLE_CONTEXT")


def _design(rows: list[dict[str, str]]) -> list[list[int]]:
    _, _, cols, X = _design_matrices([
        {
            "universe_id": (
                "U2_BARRETT_2002" if r["universe"] == "U2"
                else "U6_POLLEN_THEFT_HARGREAVES_2009"
            ),
            "module_opportunity2": r["module"],
            "temporal_exposure3": r["timing"],
        }
        for r in rows
    ])
    if cols != [
        "intercept_U2", "intercept_U6", "module_MODULAR",
        "temporal_ORDERED_OR_ALTERNATING", "temporal_VARIABLE_CONTEXT",
    ]:
        raise ValueError("Frozen V4 design has changed")
    return X


def _floors(rows: list[dict[str, str]]) -> dict[str, float]:
    Gram_inverse = _exact_inverse_of_gram(_design(rows))
    return {
        "module_modular": 2 * sqrt(float(Gram_inverse[2][2])),
        "temporal_ordered": 2 * sqrt(float(Gram_inverse[3][3])),
        "temporal_variable": 2 * sqrt(float(Gram_inverse[4][4])),
    }


def _preoutcome_g1_support(rows: list[dict[str, str]]) -> bool:
    counts = Counter(
        (r["universe"], r["module"], r["timing"]) for r in rows
    )
    return all(
        counts[(universe, "SINGLE", timing)] >= 2
        for universe in ("U2", "U6")
        for timing in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
    )


def _hypothetical_row(module: str, timing: str) -> dict[str, str]:
    if module not in MODULES or timing not in TIMINGS:
        raise ValueError("Unsupported hypothetical U2 design cell")
    return {
        "universe": "U2",
        "module": module,
        "timing": timing,
        "spatial": "SAME_UNIT",
        "dependency_group": "FUTURE_HYPOTHETICAL_ONLY_NOT_AN_OBSERVED_SPECIES",
    }


def build_v4_preoutcome_u2_scenario_planner(
    u2_conflict_path: Path,
    u2_receipt_path: Path,
    u6_receipt_path: Path,
) -> dict:
    rows = _source_screened_rows(
        u2_conflict_path, u2_receipt_path, u6_receipt_path
    )
    baseline = _floors(rows)
    if _preoutcome_g1_support(rows):
        raise ValueError("Frozen V1 unexpectedly meets G1; do not silently replan")
    one_row = []
    for module in MODULES:
        for timing in TIMINGS:
            imagined = rows + [_hypothetical_row(module, timing)]
            result = _floors(imagined)
            one_row.append({
                "candidate_module": module,
                "candidate_timing": timing,
                "is_observed_addition": False,
                "ideal_binary_se_floors_after_1_hypothetical_group": result,
                "relative_improvement_temporal_ordered": (
                    1 - result["temporal_ordered"] / baseline["temporal_ordered"]
                ),
                "relative_improvement_module_modular": (
                    1 - result["module_modular"] / baseline["module_modular"]
                ),
                "g1_predictor_common_support_only_if_future_group_independently_qualifies": (
                    _preoutcome_g1_support(imagined)
                ),
            })
    one_row.sort(key=lambda r: (
        -r["relative_improvement_temporal_ordered"],
        -r["relative_improvement_module_modular"],
        r["candidate_module"],
        r["candidate_timing"],
    ))

    combined = rows + [
        _hypothetical_row("SINGLE", "SIMULTANEOUS"),
        _hypothetical_row("MODULAR", "ORDERED_OR_ALTERNATING"),
    ]
    robust_g1 = rows + [
        _hypothetical_row("SINGLE", "SIMULTANEOUS"),
        _hypothetical_row("SINGLE", "SIMULTANEOUS"),
        _hypothetical_row("SINGLE", "ORDERED_OR_ALTERNATING"),
    ]
    return {
        "analysis": "BALANCE_V4_PREOUTCOME_HYPOTHETICAL_U2_CELL_DESIGN",
        "status": "HYPOTHETICAL_PREDICTOR_PROFILES_NOT_REAL_SPECIES",
        "frozen_real_screened_group_count": len(rows),
        "baseline_optimistic_binary_se_floors": baseline,
        "single_qualifying_u2_group_scenarios": one_row,
        "specific_two_group_illustration": {
            "cells": ["SINGLE+SIMULTANEOUS", "MODULAR+ORDERED_OR_ALTERNATING"],
            "optimistic_binary_se_floors": _floors(combined),
            "g1_predictor_common_support_only": _preoutcome_g1_support(combined),
        },
        "specific_three_group_one_deletion_robust_g1_illustration": {
            "cells": [
                "SINGLE+SIMULTANEOUS",
                "SINGLE+SIMULTANEOUS",
                "SINGLE+ORDERED_OR_ALTERNATING",
            ],
            "optimistic_binary_se_floors": _floors(robust_g1),
            "nominal_g1_predictor_common_support_only": _preoutcome_g1_support(robust_g1),
            "one_deletion_robust_single_stratum": all(
                sum(
                    1 for r in robust_g1
                    if r["universe"] == u and r["module"] == "SINGLE"
                    and r["timing"] == t
                ) >= 3
                for u in ("U2", "U6")
                for t in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
            ),
        },
        "constraints": [
            "U2 V2 expansion has frozen 12 source-side groups and 36 predictor slots; none can be selectively filled or fabricated",
            "no artificial group is an independently verified source or a conflict-positive botanical system",
            "future source predictor values require independent blind coding and independent reviewer adjudication",
            "a genuinely new U2 record also needs independent conflict-positive admission",
            "G1 additionally requires independent outcome support and fitted directional concordance",
            "information calculations concern hypothetical binary logistic regression, not Bayesian multinomial V4 power",
        ],
        "architecture_outcomes_used": False,
        "source_admissions_changed": False,
        "claim_ceiling": "prospective_design_scenarios_not_evidence_of_biological_effect",
    }

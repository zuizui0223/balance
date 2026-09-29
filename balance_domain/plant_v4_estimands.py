"""Prospectively frozen post-fit estimands for BALANCE plant model V4.

The functions here do not fit a model. They freeze counterfactual standardization
surfaces and summarize already-computed posterior parameter draws.
"""
from __future__ import annotations

import math
from statistics import mean, median
from typing import Iterable

from .plant_confirmatory import (
    primary_module_opportunity,
    primary_temporal_exposure,
)
from .plant_macro import primary_architecture_class
from .plant_model_assembly import validate_model_assembly_rows
from .plant_model_v4 import PRIMARY_UNIVERSES, build_v4_estimability_report
from .plant_v4_decision import directional_label, temporal_generality_decision


RESPONSE_ORDER = (
    "SHARED",
    "NONSTRUCTURAL_SEPARATION",
    "STRUCTURAL_MODULE_DIVISION",
    "MOSAIC",
)
MODULE_LEVELS = ("SINGLE", "MODULAR")
TEMPORAL_LEVELS = (
    "SIMULTANEOUS",
    "ORDERED_OR_ALTERNATING",
    "VARIABLE_CONTEXT",
)
SLOPE_COLUMNS = (
    "module_MODULAR",
    "temporal_ORDERED_OR_ALTERNATING",
    "temporal_VARIABLE_CONTEXT",
)
NEGATIVE_INTERACTION_MARGIN = -1.0


def _fit_row(row: dict[str, str]) -> dict[str, str]:
    return {
        **row,
        "architecture_class4": primary_architecture_class(row["architecture_mode"]),
        "module_opportunity2": primary_module_opportunity(row["module_substrate"]),
        "temporal_exposure3": primary_temporal_exposure(row["conflict_timing_geometry"]),
    }


def _x(module: str, timing: str) -> list[int]:
    if module not in MODULE_LEVELS:
        raise ValueError(f"unsupported module level {module!r}")
    if timing not in TEMPORAL_LEVELS:
        raise ValueError(f"unsupported temporal level {timing!r}")
    return [
        int(module == "MODULAR"),
        int(timing == "ORDERED_OR_ALTERNATING"),
        int(timing == "VARIABLE_CONTEXT"),
    ]


def build_v4_estimand_standardization(rows: Iterable[dict[str, str]]) -> dict:
    """Freeze equal-cell standardization surfaces from the licensed final assembly.

    H_T primary uses all observed universe x module cells, equally weighted.
    H_M uses all observed U2 timing levels, equally weighted.
    Cross-universe H_T uses only module strata that pass the preregistered
    >=2-per-timing-level/per-universe common-support gate, equally weighted
    within each universe.
    """
    licensed = validate_model_assembly_rows(rows)
    fit_rows = [_fit_row(row) for row in licensed]
    estimability = build_v4_estimability_report(fit_rows)

    temporal_cells = sorted(
        {
            (row["universe_id"], row["module_opportunity2"])
            for row in fit_rows
        },
        key=lambda x: (PRIMARY_UNIVERSES.index(x[0]), MODULE_LEVELS.index(x[1])),
    )
    if not temporal_cells:
        raise ValueError("H_T standardization requires at least one supported cell")

    h_t_primary = []
    temporal_weight = 1.0 / len(temporal_cells)
    for universe, module in temporal_cells:
        for timing in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING"):
            h_t_primary.append({
                "universe_id": universe,
                "module_opportunity2": module,
                "temporal_exposure3": timing,
                "X": _x(module, timing),
                "weight": temporal_weight,
            })

    u2_rows = [
        row for row in fit_rows
        if row["universe_id"] == "U2_BARRETT_2002"
    ]
    u2_timing = [
        level for level in TEMPORAL_LEVELS
        if any(row["temporal_exposure3"] == level for row in u2_rows)
    ]
    if not u2_timing:
        raise ValueError("H_M standardization requires U2 timing support")

    h_m_u2 = []
    module_weight = 1.0 / len(u2_timing)
    for timing in u2_timing:
        for module in MODULE_LEVELS:
            h_m_u2.append({
                "universe_id": "U2_BARRETT_2002",
                "module_opportunity2": module,
                "temporal_exposure3": timing,
                "X": _x(module, timing),
                "weight": module_weight,
            })

    common_modules = list(estimability["temporal_common_support_module_strata"])
    h_t_generality = []
    if common_modules:
        common_weight = 1.0 / len(common_modules)
        for universe in PRIMARY_UNIVERSES:
            for module in common_modules:
                for timing in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING"):
                    h_t_generality.append({
                        "universe_id": universe,
                        "module_opportunity2": module,
                        "temporal_exposure3": timing,
                        "X": _x(module, timing),
                        "weight": common_weight,
                    })

    return {
        "analysis": "balance_plant_v4_estimand_standardization",
        "unit": "licensed_dependence_block_support_cells",
        "weighting_rule": "equal_weight_per_supported_standardization_cell",
        "H_T_primary": h_t_primary,
        "H_M_U2": h_m_u2,
        "H_T_cross_universe": h_t_generality,
        "temporal_common_support_module_strata": common_modules,
        "temporal_generality_ready": estimability[
            "temporal_cross_universe_generality_ready"
        ],
        "claim_ceiling": "postfit_standardization_contract_only_no_observed_effect",
    }


def _finite_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{label} must be a finite number")
    return numeric


def _validate_draw(draw: dict, *, require_gamma: bool) -> None:
    alpha = draw.get("alpha")
    beta = draw.get("beta")
    if not isinstance(alpha, list) or len(alpha) != 2:
        raise ValueError("draw alpha must have two universe rows")
    if any(not isinstance(row, list) or len(row) != 3 for row in alpha):
        raise ValueError("draw alpha must be 2 x 3")
    if not isinstance(beta, list) or len(beta) != 3:
        raise ValueError("draw beta must have three predictor rows")
    if any(not isinstance(row, list) or len(row) != 3 for row in beta):
        raise ValueError("draw beta must be 3 x 3")

    for i, row in enumerate(alpha):
        for j, value in enumerate(row):
            _finite_number(value, f"alpha[{i}][{j}]")
    for i, row in enumerate(beta):
        for j, value in enumerate(row):
            _finite_number(value, f"beta[{i}][{j}]")

    if require_gamma:
        gamma = draw.get("gamma_u6_ordered")
        if not isinstance(gamma, list) or len(gamma) != 3:
            raise ValueError("generality draw gamma_u6_ordered must have length 3")
        for j, value in enumerate(gamma):
            _finite_number(value, f"gamma_u6_ordered[{j}]")


def _softmax(logits: list[float]) -> list[float]:
    top = max(logits)
    ex = [math.exp(value - top) for value in logits]
    total = sum(ex)
    return [value / total for value in ex]


def _probability(
    draw: dict,
    *,
    universe_id: str,
    X: list[int],
    target_response: str,
    generality: bool,
) -> float:
    _validate_draw(draw, require_gamma=generality)
    if universe_id not in PRIMARY_UNIVERSES:
        raise ValueError(f"unknown universe {universe_id!r}")
    if target_response not in RESPONSE_ORDER:
        raise ValueError(f"unknown response {target_response!r}")
    if len(X) != 3:
        raise ValueError("X must have three frozen V4 slope columns")

    u = PRIMARY_UNIVERSES.index(universe_id)
    alpha = draw["alpha"]
    beta = draw["beta"]
    logits = [0.0]
    for k in range(3):
        eta = float(alpha[u][k])
        eta += sum(float(X[p]) * float(beta[p][k]) for p in range(3))
        if generality and universe_id == "U6_POLLEN_THEFT_HARGREAVES_2009" and X[1] == 1:
            eta += float(draw["gamma_u6_ordered"][k])
        logits.append(eta)
    return _softmax(logits)[RESPONSE_ORDER.index(target_response)]


def _arm_mean(
    draw: dict,
    grid: list[dict],
    *,
    target_response: str,
    arm_field: str,
    arm_value: str,
    universe_id: str | None,
    generality: bool,
) -> float:
    selected = [
        row for row in grid
        if row[arm_field] == arm_value
        and (universe_id is None or row["universe_id"] == universe_id)
    ]
    if not selected:
        raise ValueError("standardization arm has no registered cells")
    weight_total = sum(float(row["weight"]) for row in selected)
    if weight_total <= 0:
        raise ValueError("standardization weights must be positive")
    return sum(
        float(row["weight"]) * _probability(
            draw,
            universe_id=row["universe_id"],
            X=row["X"],
            target_response=target_response,
            generality=generality,
        )
        for row in selected
    ) / weight_total


def contrast_draws(
    draws: Iterable[dict],
    grid: list[dict],
    *,
    target_response: str,
    arm_field: str,
    positive_arm: str,
    negative_arm: str,
    universe_id: str | None = None,
    generality: bool = False,
) -> list[float]:
    """Return posterior draws of a registered standardized probability contrast."""
    out = []
    for draw in draws:
        positive = _arm_mean(
            draw,
            grid,
            target_response=target_response,
            arm_field=arm_field,
            arm_value=positive_arm,
            universe_id=universe_id,
            generality=generality,
        )
        negative = _arm_mean(
            draw,
            grid,
            target_response=target_response,
            arm_field=arm_field,
            arm_value=negative_arm,
            universe_id=universe_id,
            generality=generality,
        )
        out.append(positive - negative)
    if not out:
        raise ValueError("posterior contrast requires at least one draw")
    return out


def posterior_contrast_summary(values: Iterable[float]) -> dict:
    values = [float(value) for value in values]
    if not values:
        raise ValueError("posterior summary requires at least one draw")
    return {
        "n_draws": len(values),
        "mean": mean(values),
        "median": median(values),
        "p_positive": sum(value > 0 for value in values) / len(values),
        "p_negative": sum(value < 0 for value in values) / len(values),
    }


def gamma_negative_margin_probability(
    draws: Iterable[dict],
    *,
    target_response: str = "NONSTRUCTURAL_SEPARATION",
    margin: float = NEGATIVE_INTERACTION_MARGIN,
) -> float:
    """Return P(gamma_target < margin) for the generality interaction."""
    if target_response == "SHARED":
        raise ValueError("SHARED is the reference response and has no gamma parameter")
    k = RESPONSE_ORDER.index(target_response) - 1
    values = []
    for draw in draws:
        _validate_draw(draw, require_gamma=True)
        values.append(float(draw["gamma_u6_ordered"][k]))
    if not values:
        raise ValueError("interaction tail probability requires at least one draw")
    return sum(value < margin for value in values) / len(values)



def summarize_v4_primary_postfit(
    rows: Iterable[dict[str, str]],
    *,
    primary_draws: Iterable[dict],
    sensitivity_draws: Iterable[dict],
) -> dict:
    """Summarize the two frozen primary directional contrasts under both priors."""
    grid = build_v4_estimand_standardization(rows)
    primary_draws = list(primary_draws)
    sensitivity_draws = list(sensitivity_draws)

    h_t_primary = posterior_contrast_summary(
        contrast_draws(
            primary_draws,
            grid["H_T_primary"],
            target_response="NONSTRUCTURAL_SEPARATION",
            arm_field="temporal_exposure3",
            positive_arm="ORDERED_OR_ALTERNATING",
            negative_arm="SIMULTANEOUS",
        )
    )
    h_t_sensitivity = posterior_contrast_summary(
        contrast_draws(
            sensitivity_draws,
            grid["H_T_primary"],
            target_response="NONSTRUCTURAL_SEPARATION",
            arm_field="temporal_exposure3",
            positive_arm="ORDERED_OR_ALTERNATING",
            negative_arm="SIMULTANEOUS",
        )
    )
    h_m_primary = posterior_contrast_summary(
        contrast_draws(
            primary_draws,
            grid["H_M_U2"],
            target_response="STRUCTURAL_MODULE_DIVISION",
            arm_field="module_opportunity2",
            positive_arm="MODULAR",
            negative_arm="SINGLE",
            universe_id="U2_BARRETT_2002",
        )
    )
    h_m_sensitivity = posterior_contrast_summary(
        contrast_draws(
            sensitivity_draws,
            grid["H_M_U2"],
            target_response="STRUCTURAL_MODULE_DIVISION",
            arm_field="module_opportunity2",
            positive_arm="MODULAR",
            negative_arm="SINGLE",
            universe_id="U2_BARRETT_2002",
        )
    )

    return {
        "analysis": "balance_plant_v4_primary_postfit_summary",
        "H_T_ORDERED_NONSTRUCTURAL": {
            "primary_prior": h_t_primary,
            "sensitivity_prior": h_t_sensitivity,
            "directional_label": directional_label(
                p_positive_primary=h_t_primary["p_positive"],
                p_positive_sensitivity=h_t_sensitivity["p_positive"],
            ),
        },
        "H_M_MODULAR_STRUCTURAL": {
            "primary_prior": h_m_primary,
            "sensitivity_prior": h_m_sensitivity,
            "directional_label": directional_label(
                p_positive_primary=h_m_primary["p_positive"],
                p_positive_sensitivity=h_m_sensitivity["p_positive"],
            ),
        },
        "claim_ceiling": "postfit_primary_reporting_not_causal_or_publication_decision",
    }


def summarize_v4_temporal_generality_postfit(
    rows: Iterable[dict[str, str]],
    *,
    primary_draws: Iterable[dict],
    sensitivity_draws: Iterable[dict],
) -> dict:
    """Apply the frozen U2/U6 timing-generality decision to posterior draws."""
    grid = build_v4_estimand_standardization(rows)
    if not grid["temporal_generality_ready"]:
        raise ValueError(
            "temporal generality postfit summary is forbidden until the frozen "
            "common-support and per-universe outcome-support gates pass"
        )

    primary_draws = list(primary_draws)
    sensitivity_draws = list(sensitivity_draws)
    surface = grid["H_T_cross_universe"]

    summaries: dict[str, dict[str, dict]] = {}
    p_positive: dict[str, tuple[float, float]] = {}
    for universe in PRIMARY_UNIVERSES:
        primary = posterior_contrast_summary(
            contrast_draws(
                primary_draws,
                surface,
                target_response="NONSTRUCTURAL_SEPARATION",
                arm_field="temporal_exposure3",
                positive_arm="ORDERED_OR_ALTERNATING",
                negative_arm="SIMULTANEOUS",
                universe_id=universe,
                generality=True,
            )
        )
        sensitivity = posterior_contrast_summary(
            contrast_draws(
                sensitivity_draws,
                surface,
                target_response="NONSTRUCTURAL_SEPARATION",
                arm_field="temporal_exposure3",
                positive_arm="ORDERED_OR_ALTERNATING",
                negative_arm="SIMULTANEOUS",
                universe_id=universe,
                generality=True,
            )
        )
        summaries[universe] = {
            "primary_prior": primary,
            "sensitivity_prior": sensitivity,
        }
        p_positive[universe] = (
            primary["p_positive"],
            sensitivity["p_positive"],
        )

    gamma_primary = gamma_negative_margin_probability(primary_draws)
    gamma_sensitivity = gamma_negative_margin_probability(sensitivity_draws)
    decision = temporal_generality_decision(
        preoutcome_common_support_ready=True,
        per_universe_outcome_support_ready=True,
        u2_p_positive_primary=p_positive["U2_BARRETT_2002"][0],
        u2_p_positive_sensitivity=p_positive["U2_BARRETT_2002"][1],
        u6_p_positive_primary=p_positive["U6_POLLEN_THEFT_HARGREAVES_2009"][0],
        u6_p_positive_sensitivity=p_positive["U6_POLLEN_THEFT_HARGREAVES_2009"][1],
        p_gamma_below_negative_margin_primary=gamma_primary,
        p_gamma_below_negative_margin_sensitivity=gamma_sensitivity,
    )

    return {
        "analysis": "balance_plant_v4_temporal_generality_postfit_summary",
        "standardization_module_strata": grid[
            "temporal_common_support_module_strata"
        ],
        "universe_contrasts": summaries,
        "interaction_negative_margin_probability": {
            "primary_prior": gamma_primary,
            "sensitivity_prior": gamma_sensitivity,
            "margin_log_odds": NEGATIVE_INTERACTION_MARGIN,
        },
        "decision": decision,
        "claim_ceiling": "postfit_generality_reporting_not_publication_decision",
    }

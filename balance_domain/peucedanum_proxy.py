"""Observational Peucedanum proxy-criticality sensitivity analysis.

This module belongs to Chapter 2 BALANCE. It compares definition-specific
critical locations on a descriptive antagonist-pressure proxy. It is not a
causal calibration of the architecture boundary.
"""

from __future__ import annotations

import math
import random


def _required_text(value: object, name: str) -> str:
    if value is None:
        raise ValueError(f"{name} must be non-empty")
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} must be non-empty")
    return text


def _integer_value(value: object, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer-valued finite number")
    numeric = float(value)
    if not math.isfinite(numeric) or not numeric.is_integer():
        raise ValueError(f"{name} must be an integer-valued finite number")
    return int(numeric)


def _quantile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("cannot take quantile of empty values")
    if not 0.0 <= q <= 1.0:
        raise ValueError("quantile probability must lie in [0,1]")
    if not all(math.isfinite(value) for value in values):
        raise ValueError("quantile values must be finite")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    w = pos - lo
    return ordered[lo] * (1.0 - w) + ordered[hi] * w


def _crossing(e_left: float, e_right: float, m_left: float, m_right: float) -> float:
    values = (e_left, e_right, m_left, m_right)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("crossing inputs must be finite")
    if not (m_left < 0.0 < m_right):
        raise ValueError("registered crossing requires left margin < 0 < right margin")
    crossing = e_left + (0.0 - m_left) * (e_right - e_left) / (m_right - m_left)
    if not math.isfinite(crossing):
        raise ValueError("interpolated proxy crossing must be finite")
    return crossing


def analyze_peucedanum_proxy_criticality(config: dict) -> dict:
    """Run the registered observational proxy-criticality analysis.

    The registered Monte Carlo inputs are validated before sampling so malformed
    uncertainty metadata cannot become an apparently finite observational
    critical-region receipt. Draw count and seed are exact integers; published
    means/SEs and every retained interpolated crossing must be finite.
    """
    system = _required_text(config["system"], "system")
    input_version = _required_text(config["input_version"], "input_version")

    axis = config["proxy_axis"]
    axis_name = _required_text(axis["name"], "proxy_axis.name")
    axis_units = _required_text(axis["units"], "proxy_axis.units")
    left_context = _required_text(axis["left_context"], "proxy_axis.left_context")
    right_context = _required_text(axis["right_context"], "proxy_axis.right_context")
    if left_context == right_context:
        raise ValueError("proxy-axis contexts must be distinct")

    e_left = float(axis["left_value"])
    e_right = float(axis["right_value"])
    if not all(math.isfinite(value) for value in (e_left, e_right)):
        raise ValueError("proxy-axis endpoints must be finite")
    axis_span = e_right - e_left
    if not math.isfinite(axis_span) or axis_span == 0.0:
        raise ValueError("proxy-axis endpoints must define a finite nonzero span")

    registered = config["registered_sensitivity_model"]
    draws = _integer_value(registered["draws"], "draws")
    if draws < 1000:
        raise ValueError("draws must be >= 1000")
    random_seed = _integer_value(registered["random_seed"], "random_seed")
    rng = random.Random(random_seed)

    definitions = config["definitions"]
    if not isinstance(definitions, dict) or not definitions:
        raise ValueError("definitions must be a non-empty mapping")

    definitions_out = {}
    point_estimates = []
    ci_intervals = []
    for raw_name, definition in definitions.items():
        name = _required_text(raw_name, "definition name")
        zero_semantics = _required_text(
            definition["zero_semantics"], f"{name}.zero_semantics"
        )
        lm = float(definition["left_mean"])
        ls = float(definition["left_se"])
        rm = float(definition["right_mean"])
        rs = float(definition["right_se"])
        if not all(math.isfinite(value) for value in (lm, ls, rm, rs)):
            raise ValueError(f"published mean/SE values for {name} must be finite")
        if ls < 0 or rs < 0:
            raise ValueError("published SE values must be >= 0")
        point = _crossing(e_left, e_right, lm, rm)
        point_estimates.append(point)

        sampled = []
        sign_consistent = 0
        for _ in range(draws):
            left = rng.gauss(lm, ls)
            right = rng.gauss(rm, rs)
            if not math.isfinite(left) or not math.isfinite(right):
                raise ValueError(f"non-finite Monte Carlo coefficient draw for {name}")
            if left < 0.0 < right:
                sign_consistent += 1
                sampled.append(_crossing(e_left, e_right, left, right))
        valid_fraction = sign_consistent / draws
        if len(sampled) < max(100, int(0.05 * draws)):
            raise ValueError(f"too few sign-consistent draws for {name}")
        ci = [_quantile(sampled, 0.025), _quantile(sampled, 0.975)]
        ci_intervals.append(ci)
        definitions_out[name] = {
            "point_critical_proxy": point,
            "conditional_median_critical_proxy": _quantile(sampled, 0.5),
            "conditional_95_interval": ci,
            "sign_consistent_draw_fraction": valid_fraction,
            "n_sign_consistent_draws": len(sampled),
            "zero_semantics": zero_semantics,
        }

    common_lo = max(interval[0] for interval in ci_intervals)
    common_hi = min(interval[1] for interval in ci_intervals)
    common_overlap = common_lo <= common_hi
    spread = max(point_estimates) - min(point_estimates)
    bracket_width = abs(axis_span)

    return {
        "analysis": "balance_peucedanum_antagonist_proxy_criticality",
        "system": system,
        "input_version": input_version,
        "proxy_axis": {
            "name": axis_name,
            "units": axis_units,
            "left_context": left_context,
            "left_value": e_left,
            "right_context": right_context,
            "right_value": e_right,
            "observed_bracket_width": bracket_width,
        },
        "definitions": definitions_out,
        "point_estimate_spread": spread,
        "point_estimate_spread_fraction_of_observed_bracket": spread / bracket_width,
        "common_conditional_95_interval": [common_lo, common_hi] if common_overlap else None,
        "classification": (
            "SAME_NUMERIC_PROXY_CRITICAL_CONTEXT_COMPATIBLE"
            if common_overlap
            else "PARALLEL_NUMERIC_PROXY_CRITICAL_CONTEXTS"
        ),
        "interpretation": (
            "The operational definitions do not give identical point estimates under the local-linear proxy model. "
            "A non-null common_conditional_95_interval means one latent numeric proxy-critical context remains compatible "
            "with the coefficient-uncertainty model. This is a Chapter-2 observational critical-region check, not a "
            "causal SCH/BALANCE/BITA architecture threshold."
        ),
        "claim_ceiling": (
            "conditional_proxy_interpolation_only; egg_load_not_calibrated_functional_weight; "
            "axis_uncertainty_not_propagated; not_direct_middle_world_receipt; not_causal_architecture_threshold; "
            "not_parallel_world_proof"
        ),
    }


# Backward-compatible short name for the CLI/tests.
analyze = analyze_peucedanum_proxy_criticality

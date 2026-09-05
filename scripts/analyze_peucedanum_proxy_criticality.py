from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path


def _quantile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("cannot take quantile of empty values")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    w = pos - lo
    return ordered[lo] * (1.0 - w) + ordered[hi] * w


def _crossing(e_left: float, e_right: float, m_left: float, m_right: float) -> float:
    if not (m_left < 0.0 < m_right):
        raise ValueError("registered crossing requires left margin < 0 < right margin")
    return e_left + (0.0 - m_left) * (e_right - e_left) / (m_right - m_left)


def analyze(config: dict) -> dict:
    axis = config["proxy_axis"]
    e_left = float(axis["left_value"])
    e_right = float(axis["right_value"])
    if not all(math.isfinite(value) for value in (e_left, e_right)) or e_left == e_right:
        raise ValueError("proxy-axis endpoints must be finite and distinct")

    registered = config["registered_sensitivity_model"]
    draws = int(registered["draws"])
    if draws < 1000:
        raise ValueError("draws must be >= 1000")
    rng = random.Random(int(registered["random_seed"]))

    definitions_out = {}
    point_estimates = []
    ci_intervals = []
    for name, definition in config["definitions"].items():
        lm = float(definition["left_mean"])
        ls = float(definition["left_se"])
        rm = float(definition["right_mean"])
        rs = float(definition["right_se"])
        if ls < 0 or rs < 0:
            raise ValueError("published SE values must be >= 0")
        point = _crossing(e_left, e_right, lm, rm)
        point_estimates.append(point)

        sampled = []
        sign_consistent = 0
        for _ in range(draws):
            left = rng.gauss(lm, ls)
            right = rng.gauss(rm, rs)
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
            "zero_semantics": definition["zero_semantics"],
        }

    common_lo = max(interval[0] for interval in ci_intervals)
    common_hi = min(interval[1] for interval in ci_intervals)
    common_overlap = common_lo <= common_hi
    spread = max(point_estimates) - min(point_estimates)
    bracket_width = abs(e_left - e_right)

    return {
        "analysis": "balance_peucedanum_antagonist_proxy_criticality",
        "system": config["system"],
        "input_version": config["input_version"],
        "proxy_axis": {
            "name": axis["name"],
            "units": axis["units"],
            "left_context": axis["left_context"],
            "left_value": e_left,
            "right_context": axis["right_context"],
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = analyze(config)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()

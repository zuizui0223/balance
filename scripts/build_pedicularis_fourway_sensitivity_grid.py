#!/usr/bin/env python3
"""Build a conservative pre-dry-run sensitivity grid for the Pedicularis 2^4 design.

This uses the current complete-plant contrast approximation. It is deliberately
simple and dependency-free. It is not the final hierarchical power engine.
"""

from __future__ import annotations

import argparse
import math
import statistics


def required_complete_plants(effect_over_residual_sd: float, alpha: float, power: float) -> float:
    if effect_over_residual_sd <= 0:
        raise ValueError("effect_over_residual_sd must be positive")
    if not (0 < alpha < 1):
        raise ValueError("alpha must be between 0 and 1")
    if not (0 < power < 1):
        raise ValueError("power must be between 0 and 1")

    nd = statistics.NormalDist()
    z_alpha = nd.inv_cdf(1 - alpha / 2)
    z_power = nd.inv_cdf(power)
    # In a balanced 2^4 signed contrast with independent cell residual SD sigma,
    # Var(sum(sign*y)) = 16*sigma^2, hence contrast SD = 4*sigma.
    return ((z_alpha + z_power) * 4 / effect_over_residual_sd) ** 2


def complete_probability(cell_attrition: float) -> float:
    if not (0 <= cell_attrition < 1):
        raise ValueError("cell_attrition must be in [0, 1)")
    return (1 - cell_attrition) ** 16


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--effects", default="0.5,0.75,1.0,1.25,1.5,2.0")
    p.add_argument("--attrition", default="0,0.02,0.05,0.10")
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--power", type=float, default=0.80)
    args = p.parse_args()

    effects = [float(x) for x in args.effects.split(",")]
    attritions = [float(x) for x in args.attrition.split(",")]

    print("effect_over_residual_sd,cell_attrition,complete_probability,complete_plants,assigned_plants")
    for effect in effects:
        n_complete = required_complete_plants(effect, args.alpha, args.power)
        for attrition in attritions:
            p_complete = complete_probability(attrition)
            assigned = math.ceil(n_complete / p_complete)
            print(
                f"{effect:.4f},{attrition:.4f},{p_complete:.6f},"
                f"{math.ceil(n_complete)},{assigned}"
            )


if __name__ == "__main__":
    main()

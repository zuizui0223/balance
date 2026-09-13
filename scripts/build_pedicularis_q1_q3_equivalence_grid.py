#!/usr/bin/env python3
"""Pre-dry-run sample-size grid for Pedicularis Q1/Q3 qualification.

This is a normal-approximation planning tool for a paired/matched equivalence
qualification design. It sizes the pilot to conclude that an off-target effect
is inside a symmetric equivalence margin when the true off-target effect is 0.

The calculation is deliberately a planning envelope, not the final analysis.
Dry-run paired-difference SDs and the exact analysis model must replace these
standardized assumptions before execution decisions.
"""

from __future__ import annotations

import argparse
import math
import statistics


def required_pairs(std_margin: float, alpha_one_sided: float, power: float) -> int:
    if std_margin <= 0:
        raise ValueError("std_margin must be positive")
    if not (0 < alpha_one_sided < 1):
        raise ValueError("alpha_one_sided must be in (0,1)")
    if not (0 < power < 1):
        raise ValueError("power must be in (0,1)")
    nd = statistics.NormalDist()
    z_alpha = nd.inv_cdf(1 - alpha_one_sided)
    z_power = nd.inv_cdf(power)
    return math.ceil(((z_alpha + z_power) / std_margin) ** 2)


def inflate_for_loss(n: int, attrition: float) -> int:
    if not (0 <= attrition < 1):
        raise ValueError("attrition must be in [0,1)")
    return math.ceil(n / (1 - attrition))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--margins", default="0.20,0.25,0.30,0.40,0.50")
    p.add_argument("--attrition", default="0,0.05,0.10")
    p.add_argument("--alpha-one-sided", type=float, default=0.05)
    p.add_argument("--power", type=float, default=0.80)
    args = p.parse_args()

    margins = [float(x) for x in args.margins.split(",")]
    attritions = [float(x) for x in args.attrition.split(",")]

    print("std_equivalence_margin,attrition,required_complete_pairs,assigned_pairs")
    for margin in margins:
        complete = required_pairs(margin, args.alpha_one_sided, args.power)
        for loss in attritions:
            assigned = inflate_for_loss(complete, loss)
            print(f"{margin:.3f},{loss:.3f},{complete},{assigned}")


if __name__ == "__main__":
    main()

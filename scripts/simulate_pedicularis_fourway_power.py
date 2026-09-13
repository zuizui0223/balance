#!/usr/bin/env python3
"""Dependency-free simulation scaffold for the Pedicularis 2^4 blocked factorial.

Purpose
-------
Estimate design power for the A:D:E_G:E_P four-way contrast when each plant
contributes one observation to every factorial cell. This is a qualification
scaffold, not a final analysis model. Dry-run estimates should replace all
placeholder values before use for design decisions.

The simulation works on plant-level factorial contrasts, preserving plant-level
shared random variation without pretending flowers are independent plants.
"""

from __future__ import annotations

import argparse
import itertools
import math
import random
import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    n_plants: int
    simulations: int
    baseline: float
    four_way_effect: float
    plant_sd: float
    residual_sd: float
    attrition: float
    alpha: float
    seed: int


CELLS = list(itertools.product((-1, 1), repeat=4))


def four_way_sign(cell: tuple[int, int, int, int]) -> int:
    a, d, eg, ep = cell
    return a * d * eg * ep


def simulate_one(cfg: Config, rng: random.Random) -> tuple[float, float, int] | None:
    plant_contrasts: list[float] = []

    for _ in range(cfg.n_plants):
        plant_re = rng.gauss(0.0, cfg.plant_sd)
        weighted = []
        complete = True

        for cell in CELLS:
            if rng.random() < cfg.attrition:
                complete = False
                break

            sign = four_way_sign(cell)
            # Coding is chosen so the signed 16-cell contrast equals
            # approximately cfg.four_way_effect in expectation.
            mu = cfg.baseline + sign * cfg.four_way_effect / 16.0
            y = mu + plant_re + rng.gauss(0.0, cfg.residual_sd)
            weighted.append(sign * y)

        if complete:
            plant_contrasts.append(sum(weighted))

    n = len(plant_contrasts)
    if n < 3:
        return None

    mean_c = statistics.mean(plant_contrasts)
    sd_c = statistics.stdev(plant_contrasts)
    if sd_c == 0:
        return mean_c, math.inf, n

    se = sd_c / math.sqrt(n)
    z = mean_c / se
    return mean_c, z, n


def normal_critical(alpha: float) -> float:
    # Two-sided normal critical value via statistics.NormalDist (stdlib).
    return statistics.NormalDist().inv_cdf(1.0 - alpha / 2.0)


def estimate_power(cfg: Config) -> dict[str, float]:
    rng = random.Random(cfg.seed)
    critical = normal_critical(cfg.alpha)
    tested = 0
    rejected = 0
    complete_counts: list[int] = []

    for _ in range(cfg.simulations):
        result = simulate_one(cfg, rng)
        if result is None:
            continue
        _, z, n_complete = result
        tested += 1
        complete_counts.append(n_complete)
        if abs(z) >= critical:
            rejected += 1

    if tested == 0:
        raise RuntimeError("No simulation retained at least three complete plants.")

    return {
        "n_plants_assigned": float(cfg.n_plants),
        "simulations_tested": float(tested),
        "estimated_power": rejected / tested,
        "mean_complete_plants": statistics.mean(complete_counts),
        "critical_abs_z": critical,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--n-plants", type=int, required=True)
    p.add_argument("--simulations", type=int, default=5000)
    p.add_argument("--baseline", type=float, default=20.0)
    p.add_argument("--four-way-effect", type=float, required=True)
    p.add_argument("--plant-sd", type=float, required=True)
    p.add_argument("--residual-sd", type=float, required=True)
    p.add_argument("--attrition", type=float, default=0.0)
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--seed", type=int, default=20260913)
    return p.parse_args()


def main() -> None:
    a = parse_args()
    cfg = Config(
        n_plants=a.n_plants,
        simulations=a.simulations,
        baseline=a.baseline,
        four_way_effect=a.four_way_effect,
        plant_sd=a.plant_sd,
        residual_sd=a.residual_sd,
        attrition=a.attrition,
        alpha=a.alpha,
        seed=a.seed,
    )
    result = estimate_power(cfg)
    for key, value in result.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()

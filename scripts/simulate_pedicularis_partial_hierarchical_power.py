#!/usr/bin/env python3
"""Partial-data hierarchical power scaffold for the Pedicularis 2^4 factorial.

This replaces the conservative complete-case approximation used in the first
sensitivity pass. Each plant may contribute any subset of the 16 cells. The
working covariance for the observed cells is

    V = sigma_e^2 I + sigma_plant^2 J,

and generalized least-squares information is accumulated across plants. The
four-way estimand uses full effect coding; the signed 16-cell contrast equals
16 times the A:D:E_G:E_P coefficient.

This is still a design scaffold. Dry-run estimates should replace placeholder
variance and attrition values before a final power-qualified design is frozen.
"""

from __future__ import annotations

import argparse
import itertools
import math
import random
import statistics


CELLS = list(itertools.product((-1, 1), repeat=4))


def design_row(cell: tuple[int, int, int, int]) -> list[float]:
    a, d, g, p = cell
    return [
        1.0,
        a, d, g, p,
        a*d, a*g, a*p, d*g, d*p, g*p,
        a*d*g, a*d*p, a*g*p, d*g*p,
        a*d*g*p,
    ]


def invert(matrix: list[list[float]]) -> list[list[float]]:
    n = len(matrix)
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("singular matrix")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        s = aug[col][col]
        aug[col] = [x / s for x in aug[col]]
        for r in range(n):
            if r == col:
                continue
            f = aug[r][col]
            if f:
                aug[r] = [x - f*y for x, y in zip(aug[r], aug[col])]
    return [row[n:] for row in aug]


def xt_vinv_x(observed: list[int], plant_sd: float, residual_sd: float) -> list[list[float]]:
    q = 16
    out = [[0.0]*q for _ in range(q)]
    m = len(observed)
    if m == 0:
        return out
    se2 = residual_sd**2
    sp2 = plant_sd**2
    # V^-1 = a I - b J for compound symmetry.
    a = 1.0 / se2
    b = 0.0 if sp2 == 0 else sp2 / (se2 * (se2 + m*sp2))
    rows = [design_row(CELLS[i]) for i in observed]
    col_sums = [sum(r[j] for r in rows) for j in range(q)]
    for j in range(q):
        for k in range(q):
            diag = sum(r[j]*r[k] for r in rows)
            out[j][k] = a*diag - b*col_sums[j]*col_sums[k]
    return out


def add_inplace(a: list[list[float]], b: list[list[float]]) -> None:
    for i in range(len(a)):
        for j in range(len(a)):
            a[i][j] += b[i][j]


def one_missingness_information(
    n_plants: int,
    attrition: float,
    plant_sd: float,
    residual_sd: float,
    rng: random.Random,
) -> list[list[float]]:
    info = [[0.0]*16 for _ in range(16)]
    for _ in range(n_plants):
        observed = [i for i in range(16) if rng.random() >= attrition]
        add_inplace(info, xt_vinv_x(observed, plant_sd, residual_sd))
    return info


def conditional_power(se_beta: float, four_way_contrast: float, alpha: float) -> float:
    nd = statistics.NormalDist()
    zcrit = nd.inv_cdf(1.0 - alpha/2.0)
    beta = four_way_contrast / 16.0
    mu = beta / se_beta
    return (1.0 - nd.cdf(zcrit - mu)) + nd.cdf(-zcrit - mu)


def estimate_power(
    n_plants: int,
    simulations: int,
    four_way_effect: float,
    plant_sd: float,
    residual_sd: float,
    attrition: float,
    alpha: float,
    seed: int,
) -> dict[str, float]:
    rng = random.Random(seed)
    powers: list[float] = []
    usable = 0
    for _ in range(simulations):
        info = one_missingness_information(n_plants, attrition, plant_sd, residual_sd, rng)
        try:
            cov = invert(info)
        except ValueError:
            continue
        var_beta = cov[15][15]
        if var_beta <= 0:
            continue
        usable += 1
        powers.append(conditional_power(math.sqrt(var_beta), four_way_effect, alpha))
    if not powers:
        raise RuntimeError("No invertible simulated design matrices")
    return {
        "n_plants_assigned": float(n_plants),
        "simulations_usable": float(usable),
        "mean_conditional_power": statistics.mean(powers),
        "median_conditional_power": statistics.median(powers),
        "min_conditional_power": min(powers),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n-plants", type=int, required=True)
    p.add_argument("--simulations", type=int, default=1000)
    p.add_argument("--four-way-effect", type=float, required=True)
    p.add_argument("--plant-sd", type=float, required=True)
    p.add_argument("--residual-sd", type=float, required=True)
    p.add_argument("--attrition", type=float, default=0.0)
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--seed", type=int, default=20260913)
    a = p.parse_args()
    result = estimate_power(
        a.n_plants, a.simulations, a.four_way_effect,
        a.plant_sd, a.residual_sd, a.attrition, a.alpha, a.seed,
    )
    for k, v in result.items():
        print(f"{k}={v}")


if __name__ == "__main__":
    main()

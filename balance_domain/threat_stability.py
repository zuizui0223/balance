from __future__ import annotations

from dataclasses import dataclass
from math import inf, sqrt
from typing import Sequence


@dataclass(frozen=True)
class ThreatStability:
    radius: float
    limiting_competitor: int


def lipschitz_threat_radius(
    gaps: Sequence[float],
    pairwise_lipschitz: Sequence[float],
) -> ThreatStability:
    """Certified radius on which the current best alternative cannot change.

    ``gaps[k]`` is current best-alternative fitness minus competitor-k fitness.
    All gaps must be strictly positive. ``pairwise_lipschitz[k]`` bounds the
    environmental change of that pairwise fitness difference per unit norm.
    """

    if len(gaps) != len(pairwise_lipschitz) or not gaps:
        raise ValueError("gaps and pairwise_lipschitz must have the same nonzero length")
    if any(g <= 0 for g in gaps):
        raise ValueError("a unique active threat requires strictly positive pairwise gaps")
    if any(L < 0 for L in pairwise_lipschitz):
        raise ValueError("Lipschitz constants must be nonnegative")

    radii = [inf if L == 0 else g / L for g, L in zip(gaps, pairwise_lipschitz)]
    idx = min(range(len(radii)), key=radii.__getitem__)
    return ThreatStability(radius=radii[idx], limiting_competitor=idx)


def diagonal_affine_threat_distance(
    *,
    gap: float,
    gradient_difference: Sequence[float],
    metric_diag: Sequence[float],
) -> float:
    """Exact Q-metric distance to an affine pairwise-threat tie hyperplane.

    ``metric_diag`` contains the positive diagonal of Q.  The distance is
    ``gap / sqrt(a^T Q^-1 a)``.
    """

    if gap < 0:
        raise ValueError("gap must be nonnegative")
    if len(gradient_difference) != len(metric_diag) or not gradient_difference:
        raise ValueError("gradient_difference and metric_diag must have the same nonzero length")
    if any(q <= 0 for q in metric_diag):
        raise ValueError("metric diagonal must be positive")

    denom_sq = sum((a * a) / q for a, q in zip(gradient_difference, metric_diag))
    if denom_sq == 0:
        return inf if gap > 0 else 0.0
    return gap / sqrt(denom_sq)


def threat_fragility_index(*, threat_radius: float, state_depth: float) -> float:
    if threat_radius < 0 or state_depth <= 0:
        raise ValueError("threat_radius must be nonnegative and state_depth positive")
    return threat_radius / state_depth

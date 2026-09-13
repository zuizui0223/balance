from __future__ import annotations

from dataclasses import dataclass
from math import inf, isfinite, isnan, sqrt
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
    gaps = tuple(float(g) for g in gaps)
    constants = tuple(float(value) for value in pairwise_lipschitz)
    if len(gaps) != len(constants) or not gaps:
        raise ValueError("gaps and pairwise_lipschitz must have the same nonzero length")
    if not all(isfinite(value) for value in gaps + constants):
        raise ValueError("gaps and Lipschitz constants must be finite")
    if any(g <= 0 for g in gaps):
        raise ValueError("a unique active threat requires strictly positive pairwise gaps")
    if any(value < 0 for value in constants):
        raise ValueError("Lipschitz constants must be nonnegative")

    radii = [inf if value == 0 else gap / value for gap, value in zip(gaps, constants)]
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
    gap = float(gap)
    gradient = tuple(float(value) for value in gradient_difference)
    metric = tuple(float(value) for value in metric_diag)
    if not isfinite(gap) or not all(isfinite(value) for value in gradient + metric):
        raise ValueError("gap, gradient difference, and metric diagonal must be finite")
    if gap < 0:
        raise ValueError("gap must be nonnegative")
    if len(gradient) != len(metric) or not gradient:
        raise ValueError("gradient_difference and metric_diag must have the same nonzero length")
    if any(q <= 0 for q in metric):
        raise ValueError("metric diagonal must be positive")

    denom_sq = sum((a * a) / q for a, q in zip(gradient, metric))
    if denom_sq == 0:
        return inf if gap > 0 else 0.0
    return gap / sqrt(denom_sq)


def diagonal_affine_gradient_from_minimum_switch(
    *,
    gap: float,
    switch_vector: Sequence[float],
    metric_diag: Sequence[float],
) -> tuple[float, ...]:
    """Recover the affine pairwise-gradient difference from the nearest tie move.

    Assumes ``switch_vector`` is the Q-metric shortest displacement from the
    current context to the pairwise tie hyperplane, and ``gap`` is current
    best-alternative fitness minus competitor fitness.  For diagonal Q,

        a = -gap * Q * delta / (delta^T Q delta).
    """
    gap = float(gap)
    switch = tuple(float(value) for value in switch_vector)
    metric = tuple(float(value) for value in metric_diag)
    if not isfinite(gap) or not all(isfinite(value) for value in switch + metric):
        raise ValueError("gap, switch vector, and metric diagonal must be finite")
    if gap <= 0:
        raise ValueError("gap must be positive for inverse recovery from a unique threat")
    if len(switch) != len(metric) or not switch:
        raise ValueError("switch_vector and metric_diag must have the same nonzero length")
    if any(q <= 0 for q in metric):
        raise ValueError("metric diagonal must be positive")

    radius_sq = sum(q * d * d for d, q in zip(switch, metric))
    if radius_sq <= 0:
        raise ValueError("switch_vector must be nonzero")
    return tuple(
        -gap * q * d / radius_sq
        for d, q in zip(switch, metric)
    )


def threat_fragility_index(*, threat_radius: float, state_depth: float) -> float:
    radius = float(threat_radius)
    depth = float(state_depth)
    # +inf is a meaningful certified radius when the pairwise difference is
    # constant, so allow it here while still failing closed on NaN/-inf.
    if isnan(radius) or radius == -inf or not isfinite(depth):
        raise ValueError("threat_radius must not be NaN/-inf and state_depth must be finite")
    if radius < 0 or depth <= 0:
        raise ValueError("threat_radius must be nonnegative and state_depth positive")
    return radius / depth

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from math import inf, isfinite, isnan
from typing import Sequence


@dataclass(frozen=True)
class ThreatStability:
    radius: float
    limiting_competitor: int


def _fraction(value: float) -> Fraction:
    return Fraction.from_float(value)


def _finite_fraction_result(value: Fraction, name: str) -> float:
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must remain finite; rescale units") from exc
    if not isfinite(out):
        raise ValueError(f"{name} must remain finite; rescale units")
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflowed to zero; rescale units")
    return out


def _finite_decimal_result(value: Decimal, name: str) -> float:
    out = float(value)
    if not isfinite(out):
        raise ValueError(f"{name} must remain finite; rescale units")
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflowed to zero; rescale units")
    return out


def lipschitz_threat_radius(
    gaps: Sequence[float],
    pairwise_lipschitz: Sequence[float],
) -> ThreatStability:
    """Certified radius on which the current best alternative cannot change.

    ``gaps[k]`` is current best-alternative fitness minus competitor-k fitness.
    All gaps must be strictly positive. ``pairwise_lipschitz[k]`` bounds the
    environmental change of that pairwise fitness difference per unit norm.

    An exact zero Lipschitz constant gives a structural ``+inf`` radius.  A
    finite nonzero ratio that merely overflows binary float is not the same
    statement and fails closed if it is the limiting radius.
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

    finite_candidates = [
        (_fraction(gap) / _fraction(value), idx)
        for idx, (gap, value) in enumerate(zip(gaps, constants))
        if value > 0.0
    ]
    if not finite_candidates:
        return ThreatStability(radius=inf, limiting_competitor=0)

    radius_exact, idx = min(finite_candidates, key=lambda item: (item[0], item[1]))
    radius = _finite_fraction_result(radius_exact, "limiting threat radius")
    if radius <= 0.0:
        raise ValueError("limiting threat radius must remain positive")
    return ThreatStability(radius=radius, limiting_competitor=idx)


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

    if all(value == 0.0 for value in gradient):
        return inf if gap > 0.0 else 0.0
    if gap == 0.0:
        return 0.0

    with localcontext() as ctx:
        ctx.prec = 80
        g_dec = tuple(Decimal.from_float(value) for value in gradient)
        q_dec = tuple(Decimal.from_float(value) for value in metric)
        denom_sq = sum(
            ((a * a) / q for a, q in zip(g_dec, q_dec)),
            Decimal(0),
        )
        if denom_sq <= 0:
            raise RuntimeError("nonzero affine threat gradient lost positive dual norm")
        distance = Decimal.from_float(gap) / ctx.sqrt(denom_sq)

    out = _finite_decimal_result(distance, "affine threat distance")
    if out <= 0.0:
        raise ValueError("positive affine threat distance must remain positive")
    return out


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

    gap_exact = _fraction(gap)
    switch_exact = tuple(_fraction(value) for value in switch)
    metric_exact = tuple(_fraction(value) for value in metric)
    radius_sq = sum(
        (q * d * d for d, q in zip(switch_exact, metric_exact)),
        Fraction(0),
    )
    if radius_sq <= 0:
        raise ValueError("switch_vector must be nonzero")

    recovered = tuple(
        -gap_exact * q * d / radius_sq
        for d, q in zip(switch_exact, metric_exact)
    )
    return tuple(
        _finite_fraction_result(value, f"recovered threat gradient[{i}]")
        for i, value in enumerate(recovered)
    )


def threat_fragility_index(*, threat_radius: float, state_depth: float) -> float:
    radius = float(threat_radius)
    depth = float(state_depth)
    # +inf is meaningful only as the structural certificate produced by a
    # constant pairwise difference.  Finite radii are divided exactly below so
    # numerical overflow cannot manufacture the same sentinel.
    if isnan(radius) or radius == -inf or not isfinite(depth):
        raise ValueError("threat_radius must not be NaN/-inf and state_depth must be finite")
    if radius < 0 or depth <= 0:
        raise ValueError("threat_radius must be nonnegative and state_depth positive")
    if radius == inf:
        return inf
    if radius == 0.0:
        return 0.0

    ratio = _fraction(radius) / _fraction(depth)
    out = _finite_fraction_result(ratio, "threat fragility index")
    if out <= 0.0:
        raise ValueError("positive threat fragility index must remain positive")
    return out

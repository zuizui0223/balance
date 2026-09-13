from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class CoveringCertificate:
    boundary_lower_bounds: tuple[float, ...]
    certified_global_depth: float
    whole_domain_balance_certified: bool


@dataclass(frozen=True)
class LipschitzZeroBracket:
    lower_distance_from_positive: float
    upper_distance_from_positive: float
    width: float


def _finite_scalar(value: float, name: str) -> float:
    out = float(value)
    if not isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def _finite_tuple(values: Sequence[float], name: str) -> tuple[float, ...]:
    out = tuple(float(value) for value in values)
    if not all(isfinite(value) for value in out):
        raise ValueError(f"{name} must contain only finite values")
    return out


def lipschitz_covering_certificate(
    *,
    sampled_min_margins: Sequence[float],
    lipschitz_constants: Sequence[float],
    covering_radius: float,
) -> CoveringCertificate:
    margins = _finite_tuple(sampled_min_margins, "sampled_min_margins")
    constants = _finite_tuple(lipschitz_constants, "lipschitz_constants")
    radius = _finite_scalar(covering_radius, "covering_radius")
    if radius < 0:
        raise ValueError("covering_radius must be nonnegative")
    if len(margins) != len(constants) or not margins:
        raise ValueError("sampled_min_margins and lipschitz_constants must have the same nonzero length")
    if any(k < 0 for k in constants):
        raise ValueError("lipschitz constants must be nonnegative")

    lowers = tuple(m - k * radius for m, k in zip(margins, constants))
    depth = min(lowers)
    return CoveringCertificate(
        boundary_lower_bounds=lowers,
        certified_global_depth=depth,
        whole_domain_balance_certified=depth > 0.0,
    )


def maximum_covering_radius_for_target_depth(
    *,
    sampled_min_margins: Sequence[float],
    lipschitz_constants: Sequence[float],
    target_depth: float = 0.0,
) -> float:
    """Return the largest non-negative covering radius certifying target depth.

    If a sampled minimum margin is already below ``target_depth``, no
    non-negative covering radius can certify that target, so the request fails
    closed instead of returning a physically meaningless negative radius.
    """
    margins = _finite_tuple(sampled_min_margins, "sampled_min_margins")
    constants = _finite_tuple(lipschitz_constants, "lipschitz_constants")
    target = _finite_scalar(target_depth, "target_depth")
    if len(margins) != len(constants) or not margins:
        raise ValueError("sampled_min_margins and lipschitz_constants must have the same nonzero length")
    if any(k < 0 for k in constants):
        raise ValueError("lipschitz constants must be nonnegative")

    radii: list[float] = []
    for margin, k in zip(margins, constants):
        slack = margin - target
        if slack < 0.0:
            raise ValueError(
                "target_depth exceeds a sampled minimum margin; no non-negative covering radius can certify it"
            )
        if k == 0.0:
            continue
        radii.append(slack / k)

    return min(radii) if radii else float("inf")


def lipschitz_lower_envelope(
    *,
    sampled_values: Sequence[float],
    distances_to_query: Sequence[float],
    lipschitz_constant: float,
) -> float:
    values = _finite_tuple(sampled_values, "sampled_values")
    distances = _finite_tuple(distances_to_query, "distances_to_query")
    k = _finite_scalar(lipschitz_constant, "lipschitz_constant")
    if len(values) != len(distances) or not values:
        raise ValueError("sampled_values and distances_to_query must have the same nonzero length")
    if k < 0:
        raise ValueError("lipschitz_constant must be nonnegative")
    if any(d < 0 for d in distances):
        raise ValueError("distances must be nonnegative")

    return max(v - k * d for v, d in zip(values, distances))


def multi_margin_lower_depth(
    *,
    sampled_values_by_margin: Sequence[Sequence[float]],
    distances_to_query: Sequence[float],
    lipschitz_constants: Sequence[float],
) -> float:
    constants = _finite_tuple(lipschitz_constants, "lipschitz_constants")
    if len(sampled_values_by_margin) != len(constants) or not sampled_values_by_margin:
        raise ValueError("one Lipschitz constant is required per margin")

    lowers = [
        lipschitz_lower_envelope(
            sampled_values=values,
            distances_to_query=distances_to_query,
            lipschitz_constant=k,
        )
        for values, k in zip(sampled_values_by_margin, constants)
    ]
    return min(lowers)


def certified_balance_ball_radius(
    *,
    margins: Sequence[float],
    lipschitz_constants: Sequence[float],
) -> float:
    margins = _finite_tuple(margins, "margins")
    constants = _finite_tuple(lipschitz_constants, "lipschitz_constants")
    if len(margins) != len(constants) or not margins:
        raise ValueError("margins and lipschitz_constants must have the same nonzero length")
    if any(k < 0 for k in constants):
        raise ValueError("lipschitz constants must be nonnegative")
    if any(m <= 0 for m in margins):
        return 0.0

    radii = [m / k for m, k in zip(margins, constants) if k > 0]
    return min(radii) if radii else float("inf")


def certified_outside_ball_radius(
    *,
    margins: Sequence[float],
    lipschitz_constants: Sequence[float],
) -> float:
    margins = _finite_tuple(margins, "margins")
    constants = _finite_tuple(lipschitz_constants, "lipschitz_constants")
    if len(margins) != len(constants) or not margins:
        raise ValueError("margins and lipschitz_constants must have the same nonzero length")
    if any(k < 0 for k in constants):
        raise ValueError("lipschitz constants must be nonnegative")

    radii: list[float] = []
    for margin, k in zip(margins, constants):
        if margin >= 0:
            continue
        if k == 0.0:
            return float("inf")
        radii.append(-margin / k)
    return max(radii) if radii else 0.0


def lipschitz_zero_bracket(
    *,
    positive_margin: float,
    negative_margin: float,
    path_length: float,
    lipschitz_constant: float,
    tolerance: float = 1e-12,
) -> LipschitzZeroBracket:
    """Bracket every zero between opposite-sign endpoint margins.

    The path is parameterized by metric arc length from the positive sample
    at 0 to the negative sample at ``path_length``. A K-Lipschitz margin
    forces any zero t* to satisfy ``p/K <= t* <= D-|n|/K``.
    """

    p = _finite_scalar(positive_margin, "positive_margin")
    n = _finite_scalar(negative_margin, "negative_margin")
    d = _finite_scalar(path_length, "path_length")
    k = _finite_scalar(lipschitz_constant, "lipschitz_constant")
    tol = _finite_scalar(tolerance, "tolerance")
    if p <= 0:
        raise ValueError("positive_margin must be strictly positive")
    if n >= 0:
        raise ValueError("negative_margin must be strictly negative")
    if d <= 0:
        raise ValueError("path_length must be strictly positive")
    if k <= 0:
        raise ValueError("lipschitz_constant must be strictly positive")
    if tol < 0:
        raise ValueError("tolerance must be nonnegative")
    if p + abs(n) > k * d + tol:
        raise ValueError("endpoint margins are inconsistent with the registered Lipschitz constant")

    lower = p / k
    upper = d - abs(n) / k
    return LipschitzZeroBracket(
        lower_distance_from_positive=lower,
        upper_distance_from_positive=upper,
        width=max(0.0, upper - lower),
    )

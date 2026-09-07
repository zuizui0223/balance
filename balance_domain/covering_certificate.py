from __future__ import annotations

from dataclasses import dataclass
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


def lipschitz_covering_certificate(
    *,
    sampled_min_margins: Sequence[float],
    lipschitz_constants: Sequence[float],
    covering_radius: float,
) -> CoveringCertificate:
    if covering_radius < 0:
        raise ValueError("covering_radius must be nonnegative")
    if len(sampled_min_margins) != len(lipschitz_constants) or not sampled_min_margins:
        raise ValueError("sampled_min_margins and lipschitz_constants must have the same nonzero length")
    if any(k < 0 for k in lipschitz_constants):
        raise ValueError("lipschitz constants must be nonnegative")

    lowers = tuple(
        float(m) - float(k) * covering_radius
        for m, k in zip(sampled_min_margins, lipschitz_constants)
    )
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
    if len(sampled_min_margins) != len(lipschitz_constants) or not sampled_min_margins:
        raise ValueError("sampled_min_margins and lipschitz_constants must have the same nonzero length")
    if any(k < 0 for k in lipschitz_constants):
        raise ValueError("lipschitz constants must be nonnegative")

    radii: list[float] = []
    for margin, k in zip(sampled_min_margins, lipschitz_constants):
        slack = float(margin) - target_depth
        if k == 0.0:
            if slack < 0.0:
                return slack
            continue
        radii.append(slack / float(k))

    return min(radii) if radii else float("inf")


def lipschitz_lower_envelope(
    *,
    sampled_values: Sequence[float],
    distances_to_query: Sequence[float],
    lipschitz_constant: float,
) -> float:
    if len(sampled_values) != len(distances_to_query) or not sampled_values:
        raise ValueError("sampled_values and distances_to_query must have the same nonzero length")
    if lipschitz_constant < 0:
        raise ValueError("lipschitz_constant must be nonnegative")
    if any(d < 0 for d in distances_to_query):
        raise ValueError("distances must be nonnegative")

    k = float(lipschitz_constant)
    return max(float(v) - k * float(d) for v, d in zip(sampled_values, distances_to_query))


def multi_margin_lower_depth(
    *,
    sampled_values_by_margin: Sequence[Sequence[float]],
    distances_to_query: Sequence[float],
    lipschitz_constants: Sequence[float],
) -> float:
    if len(sampled_values_by_margin) != len(lipschitz_constants) or not sampled_values_by_margin:
        raise ValueError("one Lipschitz constant is required per margin")

    lowers = [
        lipschitz_lower_envelope(
            sampled_values=values,
            distances_to_query=distances_to_query,
            lipschitz_constant=k,
        )
        for values, k in zip(sampled_values_by_margin, lipschitz_constants)
    ]
    return min(lowers)


def certified_balance_ball_radius(
    *,
    margins: Sequence[float],
    lipschitz_constants: Sequence[float],
) -> float:
    if len(margins) != len(lipschitz_constants) or not margins:
        raise ValueError("margins and lipschitz_constants must have the same nonzero length")
    if any(k < 0 for k in lipschitz_constants):
        raise ValueError("lipschitz constants must be nonnegative")
    if any(m <= 0 for m in margins):
        return 0.0

    radii = [float(m) / float(k) for m, k in zip(margins, lipschitz_constants) if k > 0]
    return min(radii) if radii else float("inf")


def certified_outside_ball_radius(
    *,
    margins: Sequence[float],
    lipschitz_constants: Sequence[float],
) -> float:
    if len(margins) != len(lipschitz_constants) or not margins:
        raise ValueError("margins and lipschitz_constants must have the same nonzero length")
    if any(k < 0 for k in lipschitz_constants):
        raise ValueError("lipschitz constants must be nonnegative")

    radii: list[float] = []
    for margin, k in zip(margins, lipschitz_constants):
        if margin >= 0:
            continue
        if k == 0.0:
            return float("inf")
        radii.append(-float(margin) / float(k))
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

    p = float(positive_margin)
    n = float(negative_margin)
    d = float(path_length)
    k = float(lipschitz_constant)
    if p <= 0:
        raise ValueError("positive_margin must be strictly positive")
    if n >= 0:
        raise ValueError("negative_margin must be strictly negative")
    if d <= 0:
        raise ValueError("path_length must be strictly positive")
    if k <= 0:
        raise ValueError("lipschitz_constant must be strictly positive")
    if p + abs(n) > k * d + tolerance:
        raise ValueError("endpoint margins are inconsistent with the registered Lipschitz constant")

    lower = p / k
    upper = d - abs(n) / k
    return LipschitzZeroBracket(
        lower_distance_from_positive=lower,
        upper_distance_from_positive=upper,
        width=max(0.0, upper - lower),
    )

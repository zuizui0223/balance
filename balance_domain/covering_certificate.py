from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
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


def _fraction(value: float) -> Fraction:
    return Fraction.from_float(value)


def _finite_exact_result(value: Fraction, name: str) -> float:
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must remain finite; rescale units") from exc
    if not isfinite(out):
        raise ValueError(f"{name} must remain finite; rescale units")
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflowed to zero; rescale units")
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

    r = _fraction(radius)
    lowers_exact = tuple(
        _fraction(m) - _fraction(k) * r
        for m, k in zip(margins, constants)
    )
    depth_exact = min(lowers_exact)
    lowers = tuple(
        _finite_exact_result(value, f"boundary lower bound[{i}]")
        for i, value in enumerate(lowers_exact)
    )
    depth = _finite_exact_result(depth_exact, "certified global depth")
    return CoveringCertificate(
        boundary_lower_bounds=lowers,
        certified_global_depth=depth,
        whole_domain_balance_certified=depth_exact > 0,
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

    target_exact = _fraction(target)
    radii: list[Fraction] = []
    for margin, k in zip(margins, constants):
        slack = _fraction(margin) - target_exact
        if slack < 0:
            raise ValueError(
                "target_depth exceeds a sampled minimum margin; no non-negative covering radius can certify it"
            )
        if k == 0.0:
            continue
        radii.append(slack / _fraction(k))

    if not radii:
        return float("inf")
    return _finite_exact_result(min(radii), "maximum covering radius")


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

    k_exact = _fraction(k)
    candidates = tuple(
        _fraction(v) - k_exact * _fraction(d)
        for v, d in zip(values, distances)
    )
    return _finite_exact_result(max(candidates), "Lipschitz lower envelope")


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

    radii = [
        _fraction(m) / _fraction(k)
        for m, k in zip(margins, constants)
        if k > 0.0
    ]
    if not radii:
        return float("inf")
    return _finite_exact_result(min(radii), "certified BALANCE ball radius")


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

    radii: list[Fraction] = []
    for margin, k in zip(margins, constants):
        if margin >= 0:
            continue
        if k == 0.0:
            return float("inf")
        radii.append(-_fraction(margin) / _fraction(k))
    if not radii:
        return 0.0
    return _finite_exact_result(max(radii), "certified outside-ball radius")


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

    p_exact = _fraction(p)
    n_abs = abs(_fraction(n))
    d_exact = _fraction(d)
    k_exact = _fraction(k)
    tol_exact = _fraction(tol)
    if p_exact + n_abs > k_exact * d_exact + tol_exact:
        raise ValueError("endpoint margins are inconsistent with the registered Lipschitz constant")

    lower_exact = p_exact / k_exact
    upper_exact = d_exact - n_abs / k_exact
    width_exact = max(Fraction(0), upper_exact - lower_exact)
    return LipschitzZeroBracket(
        lower_distance_from_positive=_finite_exact_result(lower_exact, "zero-bracket lower distance"),
        upper_distance_from_positive=_finite_exact_result(upper_exact, "zero-bracket upper distance"),
        width=_finite_exact_result(width_exact, "zero-bracket width"),
    )

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class CoveringCertificate:
    boundary_lower_bounds: tuple[float, ...]
    certified_global_depth: float
    whole_domain_balance_certified: bool


def lipschitz_covering_certificate(
    *,
    sampled_min_margins: Sequence[float],
    lipschitz_constants: Sequence[float],
    covering_radius: float,
) -> CoveringCertificate:
    """Certify continuous-domain BALANCE from finite sampled margins.

    Each status margin f_k is assumed K_k-Lipschitz in the registered
    environmental metric. If the sample set has covering radius h, then
    ``inf_E f_k >= min_sample f_k - K_k h``.
    """

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
    """Largest covering radius allowed by the Lipschitz certificate.

    Returns ``float('inf')`` only when every boundary is constant
    (K_k=0) and all sampled minima already exceed the requested target.
    If any constant boundary fails the target, returns a non-positive
    value, so callers should treat the requested certificate as impossible
    under the current sampled minima.
    """

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
    """Strongest pointwise lower bound from registered Lipschitz sample cones.

    For each sample s, ``f(query) >= f(s) - K d(query,s)``. The maximum
    across all sample cones is therefore a valid lower bound and is
    monotone non-decreasing as new samples are added.
    """

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
    """Lower-bound direct BALANCE depth at one query context.

    Builds a Lipschitz lower envelope for each registered status margin and
    returns their minimum, matching ``d_F = min_k f_k``.
    """

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

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

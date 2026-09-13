from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .boundary import classify_two_margin_point, positive_support_monotone


@dataclass(frozen=True)
class DomainExistenceResult:
    classification: str
    conflict_indices: tuple[int, ...]
    balance_indices: tuple[int, ...]
    crossing_indices: tuple[int, ...]
    delta_nondecreasing: bool
    conflict_support_monotone: bool


def classify_domain_path(conflict_load: Sequence[float], delta_worldline: Sequence[float]) -> DomainExistenceResult:
    """Classify sampled BALANCE-domain topology without interpolating hidden crossings.

    `conflict_load[i]` is L(e_i); `delta_worldline[i]` is W_D*(e_i)-W_S*(e_i)
    on the same ordered contexts. The function intentionally works only with the
    observed ordering and does not invent a continuous crossing location.

    Sampled BALANCE occupancy is delegated to the same two-margin primitive as
    the continuous path analyzers, using ``rho_direct=-Delta`` and zero numerical
    tolerance. The monotone trichotomy additionally requires Delta to be
    nondecreasing and positive conflict support, once entered, never to disappear.
    """

    if len(conflict_load) != len(delta_worldline) or len(conflict_load) < 2:
        raise ValueError("conflict_load and delta_worldline must have equal length >= 2")
    if not all(isfinite(float(x)) for x in (*conflict_load, *delta_worldline)):
        raise ValueError("all path values must be finite")
    if any(float(x) < 0 for x in conflict_load):
        raise ValueError("conflict load must be non-negative")

    L = [float(x) for x in conflict_load]
    D = [float(x) for x in delta_worldline]
    points = [
        classify_two_margin_point(li, -di, tolerance=0.0)
        for li, di in zip(L, D)
    ]
    conflict = tuple(i for i, point in enumerate(points) if point.conflict_active)
    balance = tuple(i for i, point in enumerate(points) if point.middle_active)
    crossings = tuple(i for i in range(1, len(D)) if D[i - 1] < 0 <= D[i])
    delta_nondecreasing = all(D[i] >= D[i - 1] for i in range(1, len(D)))
    conflict_support_monotone = positive_support_monotone(L, tolerance=0.0)

    if not conflict:
        classification = "NO_CONFLICT_ACTIVE_CONTEXT"
    elif not balance:
        classification = "NO_OBSERVED_POSITIVE_WIDTH_BALANCE"
    elif not delta_nondecreasing or not conflict_support_monotone:
        classification = "NONMONOTONE_PATH_REQUIRES_REENTRY_AUDIT"
    else:
        first_conflict = conflict[0]
        later_crossing = [i for i in crossings if i > first_conflict]
        if later_crossing:
            classification = "FINITE_BALANCE_DOMAIN_OBSERVED_ON_SAMPLED_PATH"
        elif all(D[i] < 0 for i in conflict):
            classification = "PERSISTENT_BALANCE_OVER_OBSERVED_PATH"
        else:
            classification = "BOUNDARY_OR_UNRESOLVED_SAMPLED_TOPOLOGY"

    return DomainExistenceResult(
        classification=classification,
        conflict_indices=conflict,
        balance_indices=balance,
        crossing_indices=crossings,
        delta_nondecreasing=delta_nondecreasing,
        conflict_support_monotone=conflict_support_monotone,
    )

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class DomainExistenceResult:
    classification: str
    conflict_indices: tuple[int, ...]
    balance_indices: tuple[int, ...]
    crossing_indices: tuple[int, ...]
    delta_nondecreasing: bool


def classify_domain_path(conflict_load: Sequence[float], delta_worldline: Sequence[float]) -> DomainExistenceResult:
    """Classify sampled BALANCE-domain topology without interpolating hidden crossings.

    `conflict_load[i]` is L(e_i); `delta_worldline[i]` is W_D*(e_i)-W_S*(e_i)
    on the same ordered contexts.  The function intentionally works only with the
    observed ordering and does not invent a continuous crossing location.
    """

    if len(conflict_load) != len(delta_worldline) or len(conflict_load) < 2:
        raise ValueError("conflict_load and delta_worldline must have equal length >= 2")
    if not all(isfinite(float(x)) for x in (*conflict_load, *delta_worldline)):
        raise ValueError("all path values must be finite")
    if any(float(x) < 0 for x in conflict_load):
        raise ValueError("conflict load must be non-negative")

    L = [float(x) for x in conflict_load]
    D = [float(x) for x in delta_worldline]
    conflict = tuple(i for i, value in enumerate(L) if value > 0)
    balance = tuple(i for i in conflict if D[i] < 0)
    crossings = tuple(i for i in range(1, len(D)) if D[i - 1] < 0 <= D[i])
    nondecreasing = all(D[i] >= D[i - 1] for i in range(1, len(D)))

    if not conflict:
        classification = "NO_CONFLICT_ACTIVE_CONTEXT"
    elif not balance:
        classification = "NO_OBSERVED_POSITIVE_WIDTH_BALANCE"
    elif not nondecreasing:
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
        delta_nondecreasing=nondecreasing,
    )

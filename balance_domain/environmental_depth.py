from dataclasses import dataclass
from math import sqrt
from typing import Iterable


@dataclass(frozen=True)
class EnvironmentalDepth:
    sch_distance: float
    bita_distance: float
    depth: float
    position: float


def _norm(values: Iterable[float]) -> float:
    vals = tuple(float(v) for v in values)
    value = sqrt(sum(v * v for v in vals))
    if value == 0:
        raise ValueError("boundary gradient norm must be nonzero")
    return value


def environmental_depth(
    *,
    conflict_margin: float,
    reserve_margin: float,
    conflict_gradient: Iterable[float],
    reserve_gradient: Iterable[float],
) -> EnvironmentalDepth:
    if conflict_margin <= 0:
        raise ValueError("conflict_margin must be positive inside BALANCE")
    if reserve_margin <= 0:
        raise ValueError("reserve_margin must be positive inside BALANCE")

    d0 = conflict_margin / _norm(conflict_gradient)
    d2 = reserve_margin / _norm(reserve_gradient)
    return EnvironmentalDepth(
        sch_distance=d0,
        bita_distance=d2,
        depth=min(d0, d2),
        position=d0 / (d0 + d2),
    )

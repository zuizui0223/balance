from dataclasses import dataclass
from math import hypot, isfinite
from typing import Iterable

from .boundary import _finite_numeric


@dataclass(frozen=True)
class EnvironmentalDepth:
    sch_distance: float
    bita_distance: float
    depth: float
    position: float


def _distance_to_boundary(margin: float, gradient: Iterable[float]) -> float:
    vals = tuple(
        _finite_numeric(value, f"boundary_gradient[{index}]")
        for index, value in enumerate(gradient)
    )
    if not vals:
        raise ValueError("boundary gradient must contain finite values")
    scale = max(abs(v) for v in vals)
    if scale == 0.0:
        raise ValueError("boundary gradient norm must be nonzero")

    # ||g|| = scale * ||g/scale||.  Evaluate margin/||g|| in the
    # normalized form so the gradient norm itself need not be representable.
    normalized_norm = hypot(*(v / scale for v in vals))
    if not isfinite(normalized_norm) or normalized_norm <= 0.0:
        raise ValueError("normalized boundary gradient norm must be finite and positive")
    distance = (margin / scale) / normalized_norm
    if not isfinite(distance) or distance <= 0.0:
        raise ValueError(
            "environmental boundary distance must remain finite and positive; rescale units"
        )
    return distance


def environmental_depth(
    *,
    conflict_margin: float,
    reserve_margin: float,
    conflict_gradient: Iterable[float],
    reserve_gradient: Iterable[float],
) -> EnvironmentalDepth:
    conflict_margin = _finite_numeric(conflict_margin, "conflict_margin")
    reserve_margin = _finite_numeric(reserve_margin, "reserve_margin")
    if conflict_margin <= 0:
        raise ValueError("conflict_margin must be positive inside BALANCE")
    if reserve_margin <= 0:
        raise ValueError("reserve_margin must be positive inside BALANCE")

    d0 = _distance_to_boundary(conflict_margin, conflict_gradient)
    d2 = _distance_to_boundary(reserve_margin, reserve_gradient)

    # Avoid d0+d2 overflow. Because both boundary distances are strictly
    # positive, the mathematical coordinate is strictly inside (0,1). If an
    # extreme ratio rounds one side to zero, fail closed rather than reporting
    # a boundary coordinate for an interior point.
    scale = max(d0, d2)
    d0_scaled = d0 / scale
    d2_scaled = d2 / scale
    position = d0_scaled / (d0_scaled + d2_scaled)
    if not isfinite(position) or not 0.0 < position < 1.0:
        raise ValueError(
            "environmental middle coordinate must remain strictly inside (0,1); rescale units"
        )

    return EnvironmentalDepth(
        sch_distance=d0,
        bita_distance=d2,
        depth=min(d0, d2),
        position=position,
    )

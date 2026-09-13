from dataclasses import dataclass
from math import hypot, isfinite
from typing import Iterable


@dataclass(frozen=True)
class EnvironmentalDepth:
    sch_distance: float
    bita_distance: float
    depth: float
    position: float


def _distance_to_boundary(margin: float, gradient: Iterable[float]) -> float:
    vals = tuple(float(v) for v in gradient)
    if not vals or not all(isfinite(v) for v in vals):
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
    conflict_margin = float(conflict_margin)
    reserve_margin = float(reserve_margin)
    if not isfinite(conflict_margin) or not isfinite(reserve_margin):
        raise ValueError("margins must be finite")
    if conflict_margin <= 0:
        raise ValueError("conflict_margin must be positive inside BALANCE")
    if reserve_margin <= 0:
        raise ValueError("reserve_margin must be positive inside BALANCE")

    d0 = _distance_to_boundary(conflict_margin, conflict_gradient)
    d2 = _distance_to_boundary(reserve_margin, reserve_gradient)

    # Avoid d0+d2 overflow.  The normalized ratio is algebraically identical
    # and remains in [0,1].
    scale = max(d0, d2)
    d0_scaled = d0 / scale
    d2_scaled = d2 / scale
    position = d0_scaled / (d0_scaled + d2_scaled)
    if not isfinite(position) or not 0.0 <= position <= 1.0:
        raise ValueError("environmental middle coordinate must remain finite in [0,1]")

    return EnvironmentalDepth(
        sch_distance=d0,
        bita_distance=d2,
        depth=min(d0, d2),
        position=position,
    )

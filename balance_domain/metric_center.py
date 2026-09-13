from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ConstantSlopeCenters:
    environmental_center: float
    fitness_center: float
    displacement: float


def metric_middle_coordinate(sch_metric_depth: float, bita_metric_depth: float) -> float:
    sch_metric_depth = float(sch_metric_depth)
    bita_metric_depth = float(bita_metric_depth)
    if not isfinite(sch_metric_depth) or not isfinite(bita_metric_depth):
        raise ValueError("metric depths must be finite")
    if sch_metric_depth <= 0 or bita_metric_depth <= 0:
        raise ValueError("metric depths must be positive inside BALANCE")

    # Normalize before summing so two large finite depths do not overflow the
    # denominator and spuriously collapse the coordinate toward zero.
    scale = max(sch_metric_depth, bita_metric_depth)
    sch_scaled = sch_metric_depth / scale
    bita_scaled = bita_metric_depth / scale
    coordinate = sch_scaled / (sch_scaled + bita_scaled)
    if not isfinite(coordinate) or not 0.0 <= coordinate <= 1.0:
        raise ValueError("metric middle coordinate must remain finite in [0,1]")
    return coordinate


def _midpoint(left: float, right: float) -> float:
    difference = right - left
    if isfinite(difference):
        midpoint = left + 0.5 * difference
    else:
        # Opposite-sign extreme endpoints can make right-left overflow although
        # their midpoint is representable.
        midpoint = 0.5 * left + 0.5 * right
    if not isfinite(midpoint):
        raise ValueError("center coordinate must remain finite; rescale environment units")
    return midpoint


def constant_slope_centers(
    left_boundary: float,
    right_boundary: float,
    left_margin_slope: float,
    right_margin_slope: float,
) -> ConstantSlopeCenters:
    left_boundary = float(left_boundary)
    right_boundary = float(right_boundary)
    left_margin_slope = float(left_margin_slope)
    right_margin_slope = float(right_margin_slope)
    values = (left_boundary, right_boundary, left_margin_slope, right_margin_slope)
    if not all(isfinite(value) for value in values):
        raise ValueError("boundaries and margin slopes must be finite")
    if right_boundary <= left_boundary:
        raise ValueError("right_boundary must exceed left_boundary")
    if left_margin_slope <= 0 or right_margin_slope <= 0:
        raise ValueError("margin slopes must be positive")

    environmental_center = _midpoint(left_boundary, right_boundary)

    # Only the slope ratio matters.  Normalizing the slopes prevents overflow
    # in both the slope sum and the slope*boundary products.
    slope_scale = max(left_margin_slope, right_margin_slope)
    left_weight = left_margin_slope / slope_scale
    right_weight = right_margin_slope / slope_scale
    right_fraction = right_weight / (left_weight + right_weight)

    boundary_difference = right_boundary - left_boundary
    if isfinite(boundary_difference):
        fitness_center = left_boundary + right_fraction * boundary_difference
    else:
        # With an unrepresentable full span, use a convex combination of the
        # finite endpoints rather than forming right-left.
        left_fraction = 1.0 - right_fraction
        fitness_center = left_fraction * left_boundary + right_fraction * right_boundary
    if not isfinite(fitness_center):
        raise ValueError("fitness center must remain finite; rescale environment units")

    displacement = fitness_center - environmental_center
    if not isfinite(displacement):
        raise ValueError("center displacement must remain finite; rescale environment units")

    return ConstantSlopeCenters(
        environmental_center=environmental_center,
        fitness_center=fitness_center,
        displacement=displacement,
    )

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConstantSlopeCenters:
    environmental_center: float
    fitness_center: float
    displacement: float


def metric_middle_coordinate(sch_metric_depth: float, bita_metric_depth: float) -> float:
    if sch_metric_depth <= 0 or bita_metric_depth <= 0:
        raise ValueError("metric depths must be positive inside BALANCE")
    return sch_metric_depth / (sch_metric_depth + bita_metric_depth)


def constant_slope_centers(
    left_boundary: float,
    right_boundary: float,
    left_margin_slope: float,
    right_margin_slope: float,
) -> ConstantSlopeCenters:
    if right_boundary <= left_boundary:
        raise ValueError("right_boundary must exceed left_boundary")
    if left_margin_slope <= 0 or right_margin_slope <= 0:
        raise ValueError("margin slopes must be positive")

    environmental_center = 0.5 * (left_boundary + right_boundary)
    fitness_center = (
        left_margin_slope * left_boundary
        + right_margin_slope * right_boundary
    ) / (left_margin_slope + right_margin_slope)
    return ConstantSlopeCenters(
        environmental_center=environmental_center,
        fitness_center=fitness_center,
        displacement=fitness_center - environmental_center,
    )

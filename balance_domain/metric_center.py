from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite

from .boundary import _finite_numeric


@dataclass(frozen=True)
class ConstantSlopeCenters:
    environmental_center: float
    fitness_center: float
    displacement: float


def _finite_exact_result(value: Fraction, name: str) -> float:
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must remain finite; rescale environment units") from exc
    if not isfinite(out):
        raise ValueError(f"{name} must remain finite; rescale environment units")
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflowed to zero; rescale environment units")
    return out


def metric_middle_coordinate(sch_metric_depth: float, bita_metric_depth: float) -> float:
    sch_metric_depth = _finite_numeric(sch_metric_depth, "sch_metric_depth")
    bita_metric_depth = _finite_numeric(bita_metric_depth, "bita_metric_depth")
    if sch_metric_depth <= 0 or bita_metric_depth <= 0:
        raise ValueError("metric depths must be positive inside BALANCE")

    sch_q = Fraction.from_float(sch_metric_depth)
    bita_q = Fraction.from_float(bita_metric_depth)
    coordinate_q = sch_q / (sch_q + bita_q)
    coordinate = _finite_exact_result(coordinate_q, "metric middle coordinate")
    if not 0.0 < coordinate < 1.0:
        raise ValueError(
            "metric middle coordinate is not representable strictly inside (0,1); rescale metric units"
        )
    return coordinate


def constant_slope_centers(
    left_boundary: float,
    right_boundary: float,
    left_margin_slope: float,
    right_margin_slope: float,
) -> ConstantSlopeCenters:
    left_boundary = _finite_numeric(left_boundary, "left_boundary")
    right_boundary = _finite_numeric(right_boundary, "right_boundary")
    left_margin_slope = _finite_numeric(left_margin_slope, "left_margin_slope")
    right_margin_slope = _finite_numeric(right_margin_slope, "right_margin_slope")
    if right_boundary <= left_boundary:
        raise ValueError("right_boundary must exceed left_boundary")
    if left_margin_slope <= 0 or right_margin_slope <= 0:
        raise ValueError("margin slopes must be positive")

    left_q = Fraction.from_float(left_boundary)
    right_q = Fraction.from_float(right_boundary)
    left_slope_q = Fraction.from_float(left_margin_slope)
    right_slope_q = Fraction.from_float(right_margin_slope)

    environmental_center_q = (left_q + right_q) / 2
    right_fraction_q = right_slope_q / (left_slope_q + right_slope_q)
    fitness_center_q = left_q + right_fraction_q * (right_q - left_q)
    displacement_q = fitness_center_q - environmental_center_q

    return ConstantSlopeCenters(
        environmental_center=_finite_exact_result(
            environmental_center_q, "environmental center"
        ),
        fitness_center=_finite_exact_result(fitness_center_q, "fitness center"),
        displacement=_finite_exact_result(displacement_q, "center displacement"),
    )

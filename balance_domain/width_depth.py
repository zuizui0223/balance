from dataclasses import dataclass
from fractions import Fraction
from math import isfinite


@dataclass(frozen=True)
class WidthDepthBounds:
    width_lower: float
    width_upper: float
    depth_lower_from_width: float
    depth_upper_from_width: float


def _fraction(value: float) -> Fraction:
    return Fraction.from_float(value)


def _positive_result(value: Fraction, name: str) -> float:
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must remain finite; rescale width/depth units") from exc
    if not isfinite(out):
        raise ValueError(f"{name} must remain finite; rescale width/depth units")
    if value > 0 and out == 0.0:
        raise ValueError(f"{name} underflowed to zero; rescale width/depth units")
    if out <= 0.0:
        raise ValueError(f"{name} must remain positive")
    return out


def width_depth_bounds(
    *,
    depth: float,
    width: float,
    left_slope_min: float,
    left_slope_max: float,
    right_slope_min: float,
    right_slope_max: float,
) -> WidthDepthBounds:
    values = [
        float(depth),
        float(width),
        float(left_slope_min),
        float(left_slope_max),
        float(right_slope_min),
        float(right_slope_max),
    ]
    if not all(isfinite(v) for v in values):
        raise ValueError("depth, width, and all slope bounds must be finite")
    depth, width, left_slope_min, left_slope_max, right_slope_min, right_slope_max = values
    if any(v <= 0 for v in values):
        raise ValueError("depth, width, and all slope bounds must be positive")
    if left_slope_min > left_slope_max:
        raise ValueError("left slope bounds are reversed")
    if right_slope_min > right_slope_max:
        raise ValueError("right slope bounds are reversed")

    d = _fraction(depth)
    w = _fraction(width)
    lmin = _fraction(left_slope_min)
    lmax = _fraction(left_slope_max)
    rmin = _fraction(right_slope_min)
    rmax = _fraction(right_slope_max)

    width_lower_exact = d * (1 / lmax + 1 / rmax)
    width_upper_exact = d * (1 / lmin + 1 / rmin)
    depth_lower_exact = w / (1 / lmin + 1 / rmin)
    depth_upper_exact = w / (1 / lmax + 1 / rmax)

    return WidthDepthBounds(
        width_lower=_positive_result(width_lower_exact, "width lower bound"),
        width_upper=_positive_result(width_upper_exact, "width upper bound"),
        depth_lower_from_width=_positive_result(depth_lower_exact, "depth lower bound"),
        depth_upper_from_width=_positive_result(depth_upper_exact, "depth upper bound"),
    )


def constant_slope_depth(*, width: float, left_slope: float, right_slope: float) -> float:
    width = float(width)
    left_slope = float(left_slope)
    right_slope = float(right_slope)
    if not all(isfinite(v) for v in (width, left_slope, right_slope)):
        raise ValueError("width and slopes must be finite")
    if width <= 0 or left_slope <= 0 or right_slope <= 0:
        raise ValueError("width and slopes must be positive")

    w = _fraction(width)
    left = _fraction(left_slope)
    right = _fraction(right_slope)
    depth_exact = w * left * right / (left + right)
    return _positive_result(depth_exact, "constant-slope depth")

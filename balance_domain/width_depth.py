from dataclasses import dataclass


@dataclass(frozen=True)
class WidthDepthBounds:
    width_lower: float
    width_upper: float
    depth_lower_from_width: float
    depth_upper_from_width: float


def width_depth_bounds(
    *,
    depth: float,
    width: float,
    left_slope_min: float,
    left_slope_max: float,
    right_slope_min: float,
    right_slope_max: float,
) -> WidthDepthBounds:
    values = [depth, width, left_slope_min, left_slope_max, right_slope_min, right_slope_max]
    if any(v <= 0 for v in values):
        raise ValueError("depth, width, and all slope bounds must be positive")
    if left_slope_min > left_slope_max:
        raise ValueError("left slope bounds are reversed")
    if right_slope_min > right_slope_max:
        raise ValueError("right slope bounds are reversed")

    width_lower = depth * (1.0 / left_slope_max + 1.0 / right_slope_max)
    width_upper = depth * (1.0 / left_slope_min + 1.0 / right_slope_min)
    depth_lower = width / (1.0 / left_slope_min + 1.0 / right_slope_min)
    depth_upper = width / (1.0 / left_slope_max + 1.0 / right_slope_max)
    return WidthDepthBounds(
        width_lower=width_lower,
        width_upper=width_upper,
        depth_lower_from_width=depth_lower,
        depth_upper_from_width=depth_upper,
    )


def constant_slope_depth(*, width: float, left_slope: float, right_slope: float) -> float:
    if width <= 0 or left_slope <= 0 or right_slope <= 0:
        raise ValueError("width and slopes must be positive")
    return width * left_slope * right_slope / (left_slope + right_slope)

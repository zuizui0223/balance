from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class MetricBoundaryDepth:
    margin: float
    depth: float
    displacement: tuple[float, ...]


def _decimal(value: float) -> Decimal:
    return Decimal.from_float(value)


def _finite_decimal_result(
    value: Decimal,
    name: str,
    *,
    require_positive: bool = False,
    preserve_nonzero: bool = True,
) -> float:
    out = float(value)
    if not isfinite(out):
        raise ValueError(f"{name} must remain finite; rescale coordinate or metric units")
    if require_positive and out <= 0.0:
        raise ValueError(f"{name} must remain positive; rescale coordinate or metric units")
    if preserve_nonzero and value != 0 and out == 0.0:
        raise ValueError(f"{name} underflowed to zero; rescale coordinate or metric units")
    return out


def diagonal_metric_boundary_depth(
    margin: float,
    gradient: Sequence[float],
    metric_diag: Sequence[float],
) -> MetricBoundaryDepth:
    """Local shortest distance to f=0 under diag(Q) perturbation metric.

    metric_diag contains the positive diagonal entries of Q in
    ||delta||_Q^2 = delta^T Q delta.
    """
    margin = float(margin)
    gradient = tuple(float(g) for g in gradient)
    metric_diag = tuple(float(q) for q in metric_diag)
    if not isfinite(margin) or not all(isfinite(v) for v in gradient + metric_diag):
        raise ValueError("margin, gradient, and metric diagonal must be finite")
    if margin <= 0:
        raise ValueError("margin must be positive inside the domain")
    if len(gradient) != len(metric_diag) or not gradient:
        raise ValueError("gradient and metric_diag must have the same nonzero length")
    if any(q <= 0 for q in metric_diag):
        raise ValueError("metric diagonal must be strictly positive")

    # g^T Q^-1 g can lie far outside binary-float range even when the final
    # metric distance and Euclidean displacement are representable.  Decimal
    # gives ample exponent range for every finite IEEE-754 input while keeping
    # enough precision to round the final outputs back to float accurately.
    with localcontext() as ctx:
        ctx.prec = 80
        m = _decimal(margin)
        g_dec = tuple(_decimal(g) for g in gradient)
        q_dec = tuple(_decimal(q) for q in metric_diag)
        dual_sq = sum(
            ((g * g) / q for g, q in zip(g_dec, q_dec)),
            Decimal(0),
        )
        if dual_sq <= 0:
            raise ValueError("gradient must be nonzero")

        dual_norm = ctx.sqrt(dual_sq)
        depth_dec = m / dual_norm
        displacement_dec = tuple(
            -m * (g / q) / dual_sq for g, q in zip(g_dec, q_dec)
        )

    depth = _finite_decimal_result(
        depth_dec,
        "metric boundary depth",
        require_positive=True,
    )
    displacement = tuple(
        _finite_decimal_result(
            value,
            f"metric displacement[{i}]",
            preserve_nonzero=True,
        )
        for i, value in enumerate(displacement_dec)
    )
    return MetricBoundaryDepth(margin=margin, depth=depth, displacement=displacement)


def metric_middle_world_depth(
    conflict_margin: float,
    conflict_gradient: Sequence[float],
    architecture_margin: float,
    architecture_gradient: Sequence[float],
    metric_diag: Sequence[float],
) -> tuple[MetricBoundaryDepth, MetricBoundaryDepth, float, str]:
    sch = diagonal_metric_boundary_depth(conflict_margin, conflict_gradient, metric_diag)
    bita = diagonal_metric_boundary_depth(architecture_margin, architecture_gradient, metric_diag)
    if sch.depth < bita.depth:
        nearest = "SCH_BOUNDARY"
    elif bita.depth < sch.depth:
        nearest = "BITA_BOUNDARY"
    else:
        nearest = "EQUAL_METRIC_DEPTH"
    return sch, bita, min(sch.depth, bita.depth), nearest

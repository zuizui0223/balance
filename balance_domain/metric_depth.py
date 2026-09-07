from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Sequence


@dataclass(frozen=True)
class MetricBoundaryDepth:
    margin: float
    depth: float
    displacement: tuple[float, ...]


def diagonal_metric_boundary_depth(
    margin: float,
    gradient: Sequence[float],
    metric_diag: Sequence[float],
) -> MetricBoundaryDepth:
    """Local shortest distance to f=0 under diag(Q) perturbation metric.

    metric_diag contains the positive diagonal entries of Q in
    ||delta||_Q^2 = delta^T Q delta.
    """
    if margin <= 0:
        raise ValueError("margin must be positive inside the domain")
    if len(gradient) != len(metric_diag) or not gradient:
        raise ValueError("gradient and metric_diag must have the same nonzero length")
    if any(q <= 0 for q in metric_diag):
        raise ValueError("metric diagonal must be strictly positive")

    dual_sq = sum((g * g) / q for g, q in zip(gradient, metric_diag))
    if dual_sq <= 0:
        raise ValueError("gradient must be nonzero")

    depth = margin / sqrt(dual_sq)
    displacement = tuple(
        -margin * (g / q) / dual_sq for g, q in zip(gradient, metric_diag)
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

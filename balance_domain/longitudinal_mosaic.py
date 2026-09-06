"""Longitudinal observational-mosaic classifier for Chapter 2 anchors.

This is not a BALANCE worldline test.  It asks whether repeated source layers
within one biological system are directionally concordant across time and
operational definitions before raw-data worldline inference is attempted.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence


@dataclass(frozen=True)
class LongitudinalMosaicResult:
    classification: str
    pressure_gradient_supported: bool
    allocation_tracking_supported: bool
    selection_reversal_supported: bool
    high_pressure_contexts: tuple[str, ...]
    low_pressure_contexts: tuple[str, ...]
    claim_ceiling: str


def classify_longitudinal_mosaic(
    *,
    flowering_time_predation_estimate: float,
    flowering_time_predation_p: float,
    predation_allocation_r2: float,
    predation_allocation_p: float,
    selection_margin_by_context: Mapping[str, float],
    ordered_contexts: Sequence[str],
    alpha: float = 0.05,
) -> LongitudinalMosaicResult:
    """Require pressure, allocation, and selection layers to agree in direction."""
    vals = [
        flowering_time_predation_estimate,
        flowering_time_predation_p,
        predation_allocation_r2,
        predation_allocation_p,
        alpha,
    ]
    if not all(math.isfinite(float(v)) for v in vals):
        raise ValueError("numeric inputs must be finite")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0,1)")
    if not 0 <= predation_allocation_r2 <= 1:
        raise ValueError("predation_allocation_r2 must lie in [0,1]")
    if not 0 <= flowering_time_predation_p <= 1 or not 0 <= predation_allocation_p <= 1:
        raise ValueError("p values must lie in [0,1]")
    if len(ordered_contexts) < 2 or len(set(ordered_contexts)) != len(ordered_contexts):
        raise ValueError("ordered_contexts must contain at least two unique contexts")

    margins = []
    for context in ordered_contexts:
        if context not in selection_margin_by_context:
            raise ValueError(f"missing selection margin for {context}")
        value = float(selection_margin_by_context[context])
        if not math.isfinite(value):
            raise ValueError(f"selection margin for {context} must be finite")
        margins.append(value)

    pressure = flowering_time_predation_estimate < 0 and flowering_time_predation_p < alpha
    allocation = predation_allocation_r2 > 0 and predation_allocation_p < alpha

    negative_indices = [i for i, value in enumerate(margins) if value < 0]
    positive_indices = [i for i, value in enumerate(margins) if value > 0]
    reversal = bool(negative_indices and positive_indices) and max(negative_indices) < min(positive_indices)

    if pressure and allocation and reversal:
        classification = "LONGITUDINAL_MOSAIC_CONCORDANT"
    else:
        classification = "LONGITUDINAL_MOSAIC_INCOMPLETE_OR_DISCORDANT"

    high = tuple(ordered_contexts[i] for i in negative_indices)
    low = tuple(ordered_contexts[i] for i in positive_indices)
    return LongitudinalMosaicResult(
        classification=classification,
        pressure_gradient_supported=pressure,
        allocation_tracking_supported=allocation,
        selection_reversal_supported=reversal,
        high_pressure_contexts=high,
        low_pressure_contexts=low,
        claim_ceiling=(
            "observational_longitudinal_mosaic_only; not_independent_studies_by_count; "
            "not_direct_BALANCE_worldline; not_causal_architecture_threshold"
        ),
    )

"""Longitudinal observational-mosaic classifier for Chapter 2 anchors.

This is not a BALANCE worldline test. It asks whether repeated source layers
within one biological system are directionally concordant across time and
operational definitions before raw-data worldline inference is attempted.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence


_ALLOWED_DIRECTIONS = {"positive", "negative", "unknown"}
_MISSING_CONTEXTS = {"none", "null", "nan", "required_before_use"}


@dataclass(frozen=True)
class LongitudinalMosaicResult:
    classification: str
    pressure_gradient_supported: bool
    allocation_tracking_supported: bool
    selection_reversal_supported: bool
    predation_allocation_direction: str
    high_pressure_contexts: tuple[str, ...]
    low_pressure_contexts: tuple[str, ...]
    claim_ceiling: str


def _finite_numeric(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric, not boolean")
    try:
        out = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite numeric value") from exc
    if not math.isfinite(out):
        raise ValueError(f"{name} must be a finite numeric value")
    return out


def _context_label(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("ordered_contexts must contain frozen string labels")
    label = value.strip()
    if not label or label.casefold() in _MISSING_CONTEXTS:
        raise ValueError("ordered_contexts must contain frozen non-missing context labels")
    return label


def classify_longitudinal_mosaic(
    *,
    flowering_time_predation_estimate: float,
    flowering_time_predation_p: float,
    predation_allocation_r2: float,
    predation_allocation_p: float,
    predation_allocation_direction: str,
    selection_margin_by_context: Mapping[str, float],
    ordered_contexts: Sequence[str],
    alpha: float = 0.05,
) -> LongitudinalMosaicResult:
    """Require pressure, allocation, and selection layers to agree in direction.

    ``predation_allocation_r2`` and its p-value establish strength/significance
    but cannot establish the sign of the association. A separate registered
    source direction is therefore required. Only a positive predation -> male
    allocation relation supports the directional chain used by this receipt.

    Booleans are not accepted as numerical evidence and placeholder context
    labels are rejected. These validation rules prevent coercion artifacts from
    creating a positive longitudinal-mosaic classification.
    """
    pressure_estimate = _finite_numeric(
        flowering_time_predation_estimate, "flowering_time_predation_estimate"
    )
    pressure_p = _finite_numeric(flowering_time_predation_p, "flowering_time_predation_p")
    allocation_r2 = _finite_numeric(predation_allocation_r2, "predation_allocation_r2")
    allocation_p = _finite_numeric(predation_allocation_p, "predation_allocation_p")
    alpha_value = _finite_numeric(alpha, "alpha")
    if not 0 < alpha_value < 1:
        raise ValueError("alpha must lie in (0,1)")
    if not 0 <= allocation_r2 <= 1:
        raise ValueError("predation_allocation_r2 must lie in [0,1]")
    if not 0 <= pressure_p <= 1 or not 0 <= allocation_p <= 1:
        raise ValueError("p values must lie in [0,1]")

    if not isinstance(predation_allocation_direction, str):
        raise ValueError("predation_allocation_direction must be a registered string direction")
    direction = predation_allocation_direction.strip().lower()
    if direction not in _ALLOWED_DIRECTIONS:
        allowed = ", ".join(sorted(_ALLOWED_DIRECTIONS))
        raise ValueError(f"predation_allocation_direction must be one of: {allowed}")

    contexts = tuple(_context_label(context) for context in ordered_contexts)
    if len(contexts) < 2 or len(set(contexts)) != len(contexts):
        raise ValueError("ordered_contexts must contain at least two unique contexts")
    if not isinstance(selection_margin_by_context, Mapping):
        raise ValueError("selection_margin_by_context must be a context-to-margin mapping")

    margins = []
    for context in contexts:
        if context not in selection_margin_by_context:
            raise ValueError(f"missing selection margin for {context}")
        value = _finite_numeric(
            selection_margin_by_context[context],
            f"selection margin for {context}",
        )
        margins.append(value)

    pressure = pressure_estimate < 0 and pressure_p < alpha_value
    allocation = (
        direction == "positive"
        and allocation_r2 > 0
        and allocation_p < alpha_value
    )

    negative_indices = [i for i, value in enumerate(margins) if value < 0]
    positive_indices = [i for i, value in enumerate(margins) if value > 0]
    reversal = bool(negative_indices and positive_indices) and max(negative_indices) < min(positive_indices)

    if pressure and allocation and reversal:
        classification = "LONGITUDINAL_MOSAIC_CONCORDANT"
    else:
        classification = "LONGITUDINAL_MOSAIC_INCOMPLETE_OR_DISCORDANT"

    high = tuple(contexts[i] for i in negative_indices)
    low = tuple(contexts[i] for i in positive_indices)
    return LongitudinalMosaicResult(
        classification=classification,
        pressure_gradient_supported=pressure,
        allocation_tracking_supported=allocation,
        selection_reversal_supported=reversal,
        predation_allocation_direction=direction,
        high_pressure_contexts=high,
        low_pressure_contexts=low,
        claim_ceiling=(
            "observational_longitudinal_mosaic_only; not_independent_studies_by_count; "
            "not_direct_BALANCE_worldline; not_causal_architecture_threshold"
        ),
    )

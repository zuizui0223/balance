"""Resolution bounds for switch points observed on monotone BALANCE forcing paths."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from balance_domain.stepwise_hysteresis import SwitchingPathResult


_MODEL_TOLERANCE = 1e-12


@dataclass(frozen=True)
class SwitchPointResolution:
    direction: str
    threshold: float
    observed_switch_phi: float
    previous_phi: float
    absolute_error: float
    jump_bound: float
    bracket_lower: float
    bracket_upper: float


@dataclass(frozen=True)
class HysteresisResolutionAudit:
    true_forward_threshold: float
    true_reverse_threshold: float
    true_hysteresis_width: float
    observed_forward_switch: float
    observed_reverse_switch: float
    observed_hysteresis_width: float
    width_overestimate: float
    overestimate_upper_bound: float
    forward: SwitchPointResolution
    reverse: SwitchPointResolution


def _single_switch(result: SwitchingPathResult):
    if not result.steps:
        raise ValueError("resolution audit requires a non-empty switching path")
    switched = [step for step in result.steps if step.switched]
    if len(switched) != 1:
        raise ValueError("resolution audit requires exactly one observed switch")
    step = switched[0]
    if step.index <= 0:
        raise ValueError("switch must have a preceding sampled phi for a resolution bound")
    return step, result.steps[step.index - 1]


def _threshold_pair(result: SwitchingPathResult) -> tuple[float, float]:
    """Return one constant finite ``(forward, reverse)`` model pair for a sweep."""
    if not result.steps:
        raise ValueError("resolution audit requires a non-empty switching path")
    pairs = tuple((float(step.forward_threshold), float(step.reverse_threshold)) for step in result.steps)
    if not all(isfinite(value) for pair in pairs for value in pair):
        raise ValueError("switching thresholds must be finite")
    forward, reverse = pairs[0]
    if forward < -_MODEL_TOLERANCE or reverse > _MODEL_TOLERANCE:
        raise ValueError("switching thresholds violate the non-negative cost sign constraints")
    if any(
        abs(f - forward) > _MODEL_TOLERANCE or abs(r - reverse) > _MODEL_TOLERANCE
        for f, r in pairs[1:]
    ):
        raise ValueError("each sweep must use one constant switching-threshold pair")
    return forward, reverse


def upward_switch_resolution(result: SwitchingPathResult) -> SwitchPointResolution:
    """Bound a shared->differentiated switch on a nondecreasing phi path."""
    values = tuple(float(step.phi) for step in result.steps)
    if not values or not all(isfinite(value) for value in values):
        raise ValueError("upward resolution requires a finite non-empty phi path")
    if any(b < a for a, b in zip(values, values[1:])):
        raise ValueError("upward resolution requires a nondecreasing phi path")
    step, previous = _single_switch(result)
    if not (
        step.state_before == "shared"
        and step.state_after == "differentiated"
    ):
        raise ValueError("observed switch is not shared->differentiated")
    threshold = float(step.forward_threshold)
    if not isfinite(threshold):
        raise ValueError("forward threshold must be finite")
    if not previous.phi <= threshold < step.phi:
        raise RuntimeError("switch samples do not bracket the forward threshold")
    jump = step.phi - previous.phi
    error = step.phi - threshold
    if jump <= 0.0:
        raise RuntimeError("strict forward switching requires a positive crossing jump")
    if error > jump + _MODEL_TOLERANCE:
        raise RuntimeError("forward switch error exceeded the crossing jump")
    return SwitchPointResolution(
        direction="upward",
        threshold=threshold,
        observed_switch_phi=step.phi,
        previous_phi=previous.phi,
        absolute_error=error,
        jump_bound=jump,
        bracket_lower=previous.phi,
        bracket_upper=step.phi,
    )


def downward_switch_resolution(result: SwitchingPathResult) -> SwitchPointResolution:
    """Bound a differentiated->shared switch on a nonincreasing phi path."""
    values = tuple(float(step.phi) for step in result.steps)
    if not values or not all(isfinite(value) for value in values):
        raise ValueError("downward resolution requires a finite non-empty phi path")
    if any(b > a for a, b in zip(values, values[1:])):
        raise ValueError("downward resolution requires a nonincreasing phi path")
    step, previous = _single_switch(result)
    if not (
        step.state_before == "differentiated"
        and step.state_after == "shared"
    ):
        raise ValueError("observed switch is not differentiated->shared")
    threshold = float(step.reverse_threshold)
    if not isfinite(threshold):
        raise ValueError("reverse threshold must be finite")
    if not step.phi < threshold <= previous.phi:
        raise RuntimeError("switch samples do not bracket the reverse threshold")
    jump = previous.phi - step.phi
    error = threshold - step.phi
    if jump <= 0.0:
        raise RuntimeError("strict reverse switching requires a positive crossing jump")
    if error > jump + _MODEL_TOLERANCE:
        raise RuntimeError("reverse switch error exceeded the crossing jump")
    return SwitchPointResolution(
        direction="downward",
        threshold=threshold,
        observed_switch_phi=step.phi,
        previous_phi=previous.phi,
        absolute_error=error,
        jump_bound=jump,
        bracket_lower=step.phi,
        bracket_upper=previous.phi,
    )


def hysteresis_resolution_audit(
    upward: SwitchingPathResult,
    downward: SwitchingPathResult,
) -> HysteresisResolutionAudit:
    """Bound finite-grid inflation for two sweeps of one switching model.

    With strict threshold crossing, the upward switch is observed on the outer
    side of the forward threshold and the downward switch on the outer side of
    the reverse threshold. Therefore the observed width overestimates the
    analytic width by at most the sum of the two crossing jumps.

    Both sweeps must encode the same full threshold pair ``(F,R)``. Checking
    only the threshold used by each observed switch would allow two different
    horizons/cost regimes to be spliced into a hysteresis width that belongs to
    neither experiment.
    """
    up = upward_switch_resolution(upward)
    down = downward_switch_resolution(downward)
    up_forward, up_reverse = _threshold_pair(upward)
    down_forward, down_reverse = _threshold_pair(downward)
    if (
        abs(up_forward - down_forward) > _MODEL_TOLERANCE
        or abs(up_reverse - down_reverse) > _MODEL_TOLERANCE
    ):
        raise ValueError(
            "upward and downward sweeps must share the same switching thresholds"
        )
    if abs(up.threshold - up_forward) > _MODEL_TOLERANCE:
        raise RuntimeError("upward switch threshold disagrees with its sweep model")
    if abs(down.threshold - up_reverse) > _MODEL_TOLERANCE:
        raise RuntimeError("downward switch threshold disagrees with its sweep model")

    true_width = up_forward - up_reverse
    observed_width = up.observed_switch_phi - down.observed_switch_phi
    overestimate = observed_width - true_width
    bound = up.jump_bound + down.jump_bound
    if overestimate < -_MODEL_TOLERANCE:
        raise RuntimeError("finite monotone sampling unexpectedly narrowed hysteresis")
    if overestimate > bound + _MODEL_TOLERANCE:
        raise RuntimeError("hysteresis-width error exceeded crossing-jump bound")
    return HysteresisResolutionAudit(
        true_forward_threshold=up_forward,
        true_reverse_threshold=up_reverse,
        true_hysteresis_width=true_width,
        observed_forward_switch=up.observed_switch_phi,
        observed_reverse_switch=down.observed_switch_phi,
        observed_hysteresis_width=observed_width,
        width_overestimate=overestimate,
        overestimate_upper_bound=bound,
        forward=up,
        reverse=down,
    )

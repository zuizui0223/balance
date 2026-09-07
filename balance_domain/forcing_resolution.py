"""Resolution bounds for switch points observed on monotone BALANCE forcing paths."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from balance_domain.stepwise_hysteresis import SwitchingPathResult


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
    switched = [step for step in result.steps if step.switched]
    if len(switched) != 1:
        raise ValueError("resolution audit requires exactly one observed switch")
    step = switched[0]
    if step.index <= 0:
        raise ValueError("switch must have a preceding sampled phi for a resolution bound")
    return step, result.steps[step.index - 1]


def upward_switch_resolution(result: SwitchingPathResult) -> SwitchPointResolution:
    """Bound a shared->differentiated switch on a nondecreasing phi path."""
    values = tuple(step.phi for step in result.steps)
    if any(b < a for a, b in zip(values, values[1:])):
        raise ValueError("upward resolution requires a nondecreasing phi path")
    step, previous = _single_switch(result)
    if not (
        step.state_before == "shared"
        and step.state_after == "differentiated"
    ):
        raise ValueError("observed switch is not shared->differentiated")
    threshold = step.forward_threshold
    if not previous.phi <= threshold < step.phi:
        raise RuntimeError("switch samples do not bracket the forward threshold")
    jump = step.phi - previous.phi
    error = step.phi - threshold
    if error > jump + 1e-12:
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
    values = tuple(step.phi for step in result.steps)
    if any(b > a for a, b in zip(values, values[1:])):
        raise ValueError("downward resolution requires a nonincreasing phi path")
    step, previous = _single_switch(result)
    if not (
        step.state_before == "differentiated"
        and step.state_after == "shared"
    ):
        raise ValueError("observed switch is not differentiated->shared")
    threshold = step.reverse_threshold
    if not step.phi < threshold <= previous.phi:
        raise RuntimeError("switch samples do not bracket the reverse threshold")
    jump = previous.phi - step.phi
    error = threshold - step.phi
    if error > jump + 1e-12:
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
    """Bound finite-grid inflation of the observed hysteresis width.

    With strict threshold crossing, the upward switch is observed on the outer
    side of the forward threshold and the downward switch on the outer side of
    the reverse threshold.  Therefore the observed width overestimates the
    analytic width by at most the sum of the two crossing jumps.
    """
    up = upward_switch_resolution(upward)
    down = downward_switch_resolution(downward)
    if not isfinite(up.threshold) or not isfinite(down.threshold):
        raise ValueError("thresholds must be finite")
    true_width = up.threshold - down.threshold
    observed_width = up.observed_switch_phi - down.observed_switch_phi
    overestimate = observed_width - true_width
    bound = up.jump_bound + down.jump_bound
    if overestimate < -1e-12:
        raise RuntimeError("finite monotone sampling unexpectedly narrowed hysteresis")
    if overestimate > bound + 1e-12:
        raise RuntimeError("hysteresis-width error exceeded crossing-jump bound")
    return HysteresisResolutionAudit(
        true_forward_threshold=up.threshold,
        true_reverse_threshold=down.threshold,
        true_hysteresis_width=true_width,
        observed_forward_switch=up.observed_switch_phi,
        observed_reverse_switch=down.observed_switch_phi,
        observed_hysteresis_width=observed_width,
        width_overestimate=overestimate,
        overestimate_upper_bound=bound,
        forward=up,
        reverse=down,
    )

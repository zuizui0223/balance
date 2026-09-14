"""Resolution bounds for switch points observed on monotone BALANCE forcing paths."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from math import inf, isfinite, nextafter

from balance_domain.stepwise_hysteresis import SwitchingPathResult


_MODEL_TOLERANCE = 1e-12
_MODEL_TOLERANCE_Q = F.from_float(_MODEL_TOLERANCE)


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


def _fraction_to_float(value: F, name: str) -> float:
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale forcing units"
        ) from exc
    if not isfinite(out):
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale forcing units"
        )
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision; rescale forcing units")
    return out


def _upper_bound_to_float(value: F, name: str) -> float:
    """Convert a non-negative exact upper bound without rounding inward."""
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    out = _fraction_to_float(value, name)
    if F.from_float(out) < value:
        out = nextafter(out, inf)
        if not isfinite(out):
            raise ValueError(
                f"{name} is finite mathematically but has no finite conservative float upper bound; rescale forcing units"
            )
    return out


def _within_model_tolerance(left: float, right: float) -> bool:
    return abs(F.from_float(left) - F.from_float(right)) <= _MODEL_TOLERANCE_Q


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
    forward_q = F.from_float(forward)
    reverse_q = F.from_float(reverse)
    if forward_q < -_MODEL_TOLERANCE_Q or reverse_q > _MODEL_TOLERANCE_Q:
        raise ValueError("switching thresholds violate the non-negative cost sign constraints")
    if any(
        not _within_model_tolerance(f, forward)
        or not _within_model_tolerance(r, reverse)
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

    step_q = F.from_float(step.phi)
    previous_q = F.from_float(previous.phi)
    threshold_q = F.from_float(threshold)
    jump_q = step_q - previous_q
    error_q = step_q - threshold_q
    if jump_q <= 0:
        raise RuntimeError("strict forward switching requires a positive crossing jump")
    if error_q > jump_q + _MODEL_TOLERANCE_Q:
        raise RuntimeError("forward switch error exceeded the crossing jump")
    jump = _upper_bound_to_float(jump_q, "forward crossing jump")
    error = _fraction_to_float(error_q, "forward switch absolute error")
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

    step_q = F.from_float(step.phi)
    previous_q = F.from_float(previous.phi)
    threshold_q = F.from_float(threshold)
    jump_q = previous_q - step_q
    error_q = threshold_q - step_q
    if jump_q <= 0:
        raise RuntimeError("strict reverse switching requires a positive crossing jump")
    if error_q > jump_q + _MODEL_TOLERANCE_Q:
        raise RuntimeError("reverse switch error exceeded the crossing jump")
    jump = _upper_bound_to_float(jump_q, "reverse crossing jump")
    error = _fraction_to_float(error_q, "reverse switch absolute error")
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
    neither experiment. Float-valued jump bounds are rounded outward so the
    reported bound cannot become smaller than the exact supplied-float bound.
    """
    up = upward_switch_resolution(upward)
    down = downward_switch_resolution(downward)
    up_forward, up_reverse = _threshold_pair(upward)
    down_forward, down_reverse = _threshold_pair(downward)
    if (
        not _within_model_tolerance(up_forward, down_forward)
        or not _within_model_tolerance(up_reverse, down_reverse)
    ):
        raise ValueError(
            "upward and downward sweeps must share the same switching thresholds"
        )
    if not _within_model_tolerance(up.threshold, up_forward):
        raise RuntimeError("upward switch threshold disagrees with its sweep model")
    if not _within_model_tolerance(down.threshold, up_reverse):
        raise RuntimeError("downward switch threshold disagrees with its sweep model")

    up_forward_q = F.from_float(up_forward)
    up_reverse_q = F.from_float(up_reverse)
    up_observed_q = F.from_float(up.observed_switch_phi)
    down_observed_q = F.from_float(down.observed_switch_phi)
    true_width_q = up_forward_q - up_reverse_q
    observed_width_q = up_observed_q - down_observed_q
    overestimate_q = observed_width_q - true_width_q
    # The individual jump bounds have already been rounded outward, so summing
    # their float representations remains conservative for the exact jumps.
    bound_q = F.from_float(up.jump_bound) + F.from_float(down.jump_bound)
    if overestimate_q < -_MODEL_TOLERANCE_Q:
        raise RuntimeError("finite monotone sampling unexpectedly narrowed hysteresis")
    if overestimate_q > bound_q + _MODEL_TOLERANCE_Q:
        raise RuntimeError("hysteresis-width error exceeded crossing-jump bound")

    true_width = _fraction_to_float(true_width_q, "true hysteresis width")
    observed_width = _fraction_to_float(observed_width_q, "observed hysteresis width")
    overestimate = _fraction_to_float(overestimate_q, "hysteresis width overestimate")
    bound = _upper_bound_to_float(bound_q, "hysteresis overestimate upper bound")
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

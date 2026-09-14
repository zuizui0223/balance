"""Stepwise forcing paths for BALANCE switching-cost hysteresis."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
import math
from typing import Literal, Sequence

from balance_domain.dynamics import switching_cost_state

ArchitectureState = Literal["shared", "differentiated"]


@dataclass(frozen=True)
class PathStep:
    index: int
    phi: float
    state_before: ArchitectureState
    state_after: ArchitectureState
    switched: bool
    forward_threshold: float
    reverse_threshold: float


@dataclass(frozen=True)
class SwitchingPathResult:
    initial_state: ArchitectureState
    final_state: ArchitectureState
    steps: tuple[PathStep, ...]
    max_observed_phi_jump: float
    declared_max_phi_jump: float | None


def _validate_state(state: str) -> ArchitectureState:
    if state not in {"shared", "differentiated"}:
        raise ValueError("initial_state must be 'shared' or 'differentiated'")
    return state  # type: ignore[return-value]


def _finite_path(phi_path: Sequence[float]) -> tuple[float, ...]:
    try:
        values = tuple(float(x) for x in phi_path)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("phi_path values must be finite numeric values") from exc
    if not values:
        raise ValueError("phi_path must be non-empty")
    if not all(math.isfinite(value) for value in values):
        raise ValueError("phi_path values must be finite")
    return values


def _nonnegative_fraction_to_float(value: F, name: str) -> float:
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale forcing units"
        ) from exc
    if not math.isfinite(out):
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale forcing units"
        )
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision; rescale forcing units")
    return out


def _max_path_jump_exact(values: Sequence[float]) -> F:
    if len(values) <= 1:
        return F(0, 1)
    exact = tuple(F.from_float(value) for value in values)
    return max(abs(b - a) for a, b in zip(exact, exact[1:]))


def max_path_jump(phi_path: Sequence[float]) -> float:
    values = _finite_path(phi_path)
    largest = _max_path_jump_exact(values)
    return _nonnegative_fraction_to_float(largest, "maximum observed phi jump")


def follow_switching_path(
    phi_path: Sequence[float],
    *,
    initial_state: ArchitectureState,
    horizon_per_step: float,
    cost_shared_to_diff: float,
    cost_diff_to_shared: float,
    max_phi_jump: float | None = None,
) -> SwitchingPathResult:
    """Follow the retained architecture along an ordered forcing path.

    ``max_phi_jump`` is an optional fail-closed declaration of the forcing
    small-step assumption. It constrains the *external phi path*, not mutation
    size in architecture space. A declared resolution bound must itself be a
    finite non-negative number; NaN/Inf do not represent an auditable sampling
    resolution.

    The actual maximum consecutive jump is compared to the declared bound in
    exact arithmetic at the supplied-float level before any result is rounded
    back onto the float-valued receipt surface. The historical ``1e-15``
    absolute numerical allowance is retained, but applied to exact values.
    """
    values = _finite_path(phi_path)
    state = _validate_state(initial_state)
    observed_q = _max_path_jump_exact(values)
    observed = _nonnegative_fraction_to_float(observed_q, "maximum observed phi jump")
    declared = None
    if max_phi_jump is not None:
        try:
            declared = float(max_phi_jump)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("max_phi_jump must be finite and non-negative or None") from exc
        if not math.isfinite(declared) or declared < 0.0:
            raise ValueError("max_phi_jump must be finite and non-negative or None")
        declared_q = F.from_float(declared)
        roundoff_q = F.from_float(1e-15)
        if observed_q > declared_q + roundoff_q:
            raise ValueError(
                f"forcing path violates declared max_phi_jump: {observed} > {declared}"
            )

    steps: list[PathStep] = []
    for index, phi in enumerate(values):
        receipt = switching_cost_state(
            phi,
            horizon_per_step,
            cost_shared_to_diff,
            cost_diff_to_shared,
        )
        before = state
        if state == "shared" and not receipt.shared_stays:
            state = "differentiated"
        elif state == "differentiated" and not receipt.differentiated_stays:
            state = "shared"
        steps.append(
            PathStep(
                index=index,
                phi=phi,
                state_before=before,
                state_after=state,
                switched=(state != before),
                forward_threshold=receipt.forward_threshold,
                reverse_threshold=receipt.reverse_threshold,
            )
        )

    return SwitchingPathResult(
        initial_state=initial_state,
        final_state=state,
        steps=tuple(steps),
        max_observed_phi_jump=observed,
        declared_max_phi_jump=declared,
    )


def linear_small_step_path(start: float, stop: float, *, max_phi_jump: float) -> tuple[float, ...]:
    """Construct a finite linear path whose consecutive forcing jumps are <= bound.

    The path is built from exact representations of the supplied floats so an
    extreme finite span such as ``-1e308 .. +1e308`` need not overflow the
    intermediate distance or interpolation expression.
    """
    try:
        a = float(start)
        b = float(stop)
        jump = float(max_phi_jump)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("start, stop, and max_phi_jump must be finite numeric values") from exc
    if not all(math.isfinite(value) for value in (a, b, jump)):
        raise ValueError("start, stop, and max_phi_jump must be finite")
    if jump <= 0.0:
        raise ValueError("max_phi_jump must be positive")

    aq = F.from_float(a)
    bq = F.from_float(b)
    jump_q = F.from_float(jump)
    distance_q = abs(bq - aq)
    if distance_q == 0:
        return (a,)

    ratio = distance_q / jump_q
    intervals = max(1, (ratio.numerator + ratio.denominator - 1) // ratio.denominator)
    delta = bq - aq
    path = []
    for i in range(intervals + 1):
        value_q = aq + delta * i / intervals
        try:
            value = float(value_q)
        except OverflowError as exc:
            raise ValueError(
                "interpolated forcing coordinate is not representable as float; rescale forcing units"
            ) from exc
        if not math.isfinite(value):
            raise ValueError(
                "interpolated forcing coordinate is not representable as float; rescale forcing units"
            )
        path.append(value)
    result = tuple(path)
    # Verify the promised resolution on the actual float path using the same
    # registered absolute numerical allowance as follow_switching_path().
    if _max_path_jump_exact(result) > jump_q + F.from_float(1e-15):
        raise RuntimeError("constructed forcing path exceeded max_phi_jump after float conversion")
    return result


def switch_points(result: SwitchingPathResult) -> tuple[float, ...]:
    return tuple(step.phi for step in result.steps if step.switched)

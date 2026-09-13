"""Stepwise forcing paths for BALANCE switching-cost hysteresis."""
from __future__ import annotations

from dataclasses import dataclass
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
    values = tuple(float(x) for x in phi_path)
    if not values:
        raise ValueError("phi_path must be non-empty")
    if not all(math.isfinite(value) for value in values):
        raise ValueError("phi_path values must be finite")
    return values


def max_path_jump(phi_path: Sequence[float]) -> float:
    values = _finite_path(phi_path)
    if len(values) == 1:
        return 0.0
    return max(abs(b - a) for a, b in zip(values, values[1:]))


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
    """
    values = _finite_path(phi_path)
    state = _validate_state(initial_state)
    observed = max_path_jump(values)
    declared = None
    if max_phi_jump is not None:
        declared = float(max_phi_jump)
        if not math.isfinite(declared) or declared < 0.0:
            raise ValueError("max_phi_jump must be finite and non-negative or None")
        if observed > declared + 1e-15:
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
    """Construct a finite linear path whose consecutive forcing jumps are <= bound."""
    a = float(start)
    b = float(stop)
    jump = float(max_phi_jump)
    if not all(math.isfinite(value) for value in (a, b, jump)):
        raise ValueError("start, stop, and max_phi_jump must be finite")
    if jump <= 0.0:
        raise ValueError("max_phi_jump must be positive")
    distance = abs(b - a)
    if distance == 0.0:
        return (a,)
    intervals = max(1, int(distance / jump))
    if distance / intervals > jump + 1e-15:
        intervals += 1
    return tuple(a + (b - a) * i / intervals for i in range(intervals + 1))


def switch_points(result: SwitchingPathResult) -> tuple[float, ...]:
    return tuple(step.phi for step in result.steps if step.switched)

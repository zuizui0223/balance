from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class EnvelopeComparison:
    equivalent: bool
    max_abs_gap: float
    envelope_a: tuple[float, ...]
    envelope_b: tuple[float, ...]


def upper_envelope(worldlines: Mapping[str, Sequence[float]]) -> tuple[float, ...]:
    if not worldlines:
        raise ValueError("at least one alternative worldline is required")
    lengths = {len(values) for values in worldlines.values()}
    if len(lengths) != 1:
        raise ValueError("all worldlines must have the same number of contexts")
    n = lengths.pop()
    if n == 0:
        raise ValueError("worldlines must contain at least one context")
    return tuple(max(values[i] for values in worldlines.values()) for i in range(n))


def compare_sampled_envelopes(
    registry_a: Mapping[str, Sequence[float]],
    registry_b: Mapping[str, Sequence[float]],
    *,
    atol: float = 0.0,
) -> EnvelopeComparison:
    if atol < 0:
        raise ValueError("atol must be nonnegative")
    env_a = upper_envelope(registry_a)
    env_b = upper_envelope(registry_b)
    if len(env_a) != len(env_b):
        raise ValueError("registries must be evaluated on the same context grid")
    max_gap = max(abs(a - b) for a, b in zip(env_a, env_b))
    return EnvelopeComparison(
        equivalent=max_gap <= atol,
        max_abs_gap=max_gap,
        envelope_a=env_a,
        envelope_b=env_b,
    )


def sampled_reserve(shared: Sequence[float], envelope: Sequence[float]) -> tuple[float, ...]:
    if len(shared) != len(envelope) or not shared:
        raise ValueError("shared and envelope must have the same nonzero length")
    return tuple(s - a for s, a in zip(shared, envelope))


def sampled_balance_state(
    conflict_load: Sequence[float],
    reserve: Sequence[float],
) -> tuple[bool, ...]:
    if len(conflict_load) != len(reserve) or not conflict_load:
        raise ValueError("conflict_load and reserve must have the same nonzero length")
    return tuple(l > 0.0 and rho > 0.0 for l, rho in zip(conflict_load, reserve))


def active_threats_at_context(
    worldlines: Mapping[str, Sequence[float]],
    context_index: int,
    *,
    atol: float = 0.0,
) -> tuple[str, ...]:
    if atol < 0:
        raise ValueError("atol must be nonnegative")
    envelope = upper_envelope(worldlines)
    if context_index < 0 or context_index >= len(envelope):
        raise IndexError("context_index is outside the registered context grid")
    target = envelope[context_index]
    return tuple(
        label
        for label, values in worldlines.items()
        if abs(values[context_index] - target) <= atol
    )


def identify_threats_with_auxiliary(
    active_threats: Sequence[str],
    auxiliary_codes: Mapping[str, object],
    observed_code: object,
) -> tuple[str, ...]:
    if not active_threats:
        raise ValueError("active_threats must be nonempty")
    missing = [label for label in active_threats if label not in auxiliary_codes]
    if missing:
        raise ValueError(f"missing auxiliary codes for active threats: {missing}")
    return tuple(
        label for label in active_threats if auxiliary_codes[label] == observed_code
    )

"""Validate the shared SCH -> BALANCE -> BITA context handoff."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .receipt import Interval


HANDOFF_SCHEMA = "THREE_WORLD_CONFLICT_HANDOFF_V1"


@dataclass(frozen=True)
class ConflictHandoff:
    context_id: str
    system: str
    population_id: str
    season_id: str
    fitness_scale_id: str
    conflict_load: Interval
    source_repository: str


def _required_text(value: object, name: str) -> str:
    out = str(value).strip()
    if not out:
        raise ValueError(f"{name} is required")
    return out


def consume_conflict_handoff(
    receipt: dict,
    *,
    expected_context_id: str | None = None,
    expected_fitness_scale_id: str | None = None,
) -> ConflictHandoff:
    """Validate one SCH conflict receipt before using it in Chapter 2.

    BALANCE never repairs a context or scale mismatch.  The same validator can
    be used by a worldline experiment before constructing a bounded
    ``MiddleWorldReceipt``.
    """
    if receipt.get("receipt_schema_version") != HANDOFF_SCHEMA:
        raise ValueError(f"handoff must use {HANDOFF_SCHEMA}")
    if receipt.get("status") != "THREE_WORLD_CONFLICT_CONTEXT_IDENTIFIED":
        raise ValueError("handoff status is not positive")

    context_id = _required_text(receipt.get("context_id"), "context_id")
    scale = _required_text(receipt.get("fitness_scale_id"), "fitness_scale_id")
    if expected_context_id is not None and context_id != expected_context_id:
        raise ValueError("context_id does not match the BALANCE worldline context")
    if expected_fitness_scale_id is not None and scale != expected_fitness_scale_id:
        raise ValueError("fitness_scale_id does not match the BALANCE worldline scale")

    try:
        raw = receipt["conflict_load"]
        point = float(raw["point"])
        lo = float(raw["lower_95"])
        hi = float(raw["upper_95"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("handoff lacks a valid conflict_load interval") from exc
    if not all(math.isfinite(v) and v >= 0 for v in (point, lo, hi)):
        raise ValueError("conflict_load values must be finite and non-negative")
    if not lo <= point <= hi:
        raise ValueError("conflict_load point must lie inside its interval")

    source = receipt.get("source", {})
    repository = _required_text(source.get("repository"), "source.repository")
    if repository != "sch":
        raise ValueError("three-world conflict handoff must originate from sch")

    return ConflictHandoff(
        context_id=context_id,
        system=_required_text(receipt.get("system"), "system"),
        population_id=_required_text(receipt.get("population_id"), "population_id"),
        season_id=_required_text(receipt.get("season_id"), "season_id"),
        fitness_scale_id=scale,
        conflict_load=Interval(lo, hi),
        source_repository=repository,
    )

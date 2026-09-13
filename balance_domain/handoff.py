"""Validate the shared SCH -> BALANCE -> BITA context handoff."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .receipt import Interval


HANDOFF_SCHEMA = "THREE_WORLD_CONFLICT_HANDOFF_V1"
SOURCE_SCHEMA = "SCH_COMPONENT_CONFLICT_BUDGET_V1"
SOURCE_FIELD = "criticality_export.L_S_component"
_MISSING_IDENTIFIERS = {"none", "null", "nan", "required_before_use"}


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
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a non-empty string identifier")
    out = value.strip()
    if not out or out.casefold() in _MISSING_IDENTIFIERS:
        raise ValueError(f"{name} must be frozen before use")
    return out


def _nonnegative_number(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric, not boolean")
    try:
        out = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite non-negative number") from exc
    if not math.isfinite(out) or out < 0:
        raise ValueError(f"{name} must be a finite non-negative number")
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
    ``MiddleWorldReceipt``.  A positive SCH handoff status identifies the
    registered conflict-budget context; the bounded interval itself still
    determines whether BALANCE can treat conflict as strictly positive.
    """
    if not isinstance(receipt, dict):
        raise ValueError("handoff receipt must be a mapping")
    if receipt.get("receipt_schema_version") != HANDOFF_SCHEMA:
        raise ValueError(f"handoff must use {HANDOFF_SCHEMA}")
    if receipt.get("status") != "THREE_WORLD_CONFLICT_CONTEXT_IDENTIFIED":
        raise ValueError("handoff status is not positive")

    context_id = _required_text(receipt.get("context_id"), "context_id")
    scale = _required_text(receipt.get("fitness_scale_id"), "fitness_scale_id")
    if expected_context_id is not None:
        expected_context = _required_text(expected_context_id, "expected_context_id")
        if context_id != expected_context:
            raise ValueError("context_id does not match the BALANCE worldline context")
    if expected_fitness_scale_id is not None:
        expected_scale = _required_text(expected_fitness_scale_id, "expected_fitness_scale_id")
        if scale != expected_scale:
            raise ValueError("fitness_scale_id does not match the BALANCE worldline scale")

    raw = receipt.get("conflict_load")
    if not isinstance(raw, dict):
        raise ValueError("handoff lacks a valid conflict_load interval")
    point = _nonnegative_number(raw.get("point"), "conflict_load.point")
    lo = _nonnegative_number(raw.get("lower_95"), "conflict_load.lower_95")
    hi = _nonnegative_number(raw.get("upper_95"), "conflict_load.upper_95")
    if not lo <= point <= hi:
        raise ValueError("conflict_load point must lie inside its interval")
    source_field = raw.get("source_field")
    if source_field is not None and source_field != SOURCE_FIELD:
        raise ValueError("conflict_load source_field does not match the SCH handoff contract")

    source = receipt.get("source")
    if not isinstance(source, dict):
        raise ValueError("handoff source provenance is required")
    repository = _required_text(source.get("repository"), "source.repository")
    if repository != "sch":
        raise ValueError("three-world conflict handoff must originate from sch")
    if source.get("receipt_schema_version") != SOURCE_SCHEMA:
        raise ValueError(f"SCH source receipt must use {SOURCE_SCHEMA}")

    return ConflictHandoff(
        context_id=context_id,
        system=_required_text(receipt.get("system"), "system"),
        population_id=_required_text(receipt.get("population_id"), "population_id"),
        season_id=_required_text(receipt.get("season_id"), "season_id"),
        fitness_scale_id=scale,
        conflict_load=Interval(lo, hi),
        source_repository=repository,
    )

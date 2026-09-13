"""Consume the shared Pedicularis x-y surface without conditioning on BITA success.

This is a functional-state Chapter-2 comparison.  The cupulate bract architecture
is present in both y states, so the output must not be promoted to a structural
architecture claim without a separate structural-y/cost lane.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from .boundary import two_margin_middle_position
from .handoff import consume_conflict_handoff

XY_SCHEMA = "PEDICULARIS_XY_SURFACE_HANDOFF_V1"
_MISSING_IDENTIFIERS = {"none", "null", "nan", "required_before_use"}


@dataclass(frozen=True)
class PedicularisXYBalanceReceipt:
    context_id: str
    fitness_scale_id: str
    conflict_load_point: float
    conflict_load_95: tuple[float, float]
    worldline_gap_point: float
    worldline_gap_95: tuple[float, float]
    state: str
    direct_reserve_point: float | None
    direct_middle_position: float | None
    direct_two_sided_depth: float | None
    dimensional_release_point: float
    bita_surface_status: str | None
    claim_level: str


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a non-empty string identifier")
    out = value.strip()
    if not out or out.casefold() in _MISSING_IDENTIFIERS:
        raise ValueError(f"{name} must be frozen before use")
    return out


def _finite(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric, not boolean")
    try:
        out = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def _three(obj: object, name: str) -> tuple[float, float, float]:
    if not isinstance(obj, dict):
        raise ValueError(f"{name} must be an interval mapping")
    point = _finite(obj.get("point"), f"{name}.point")
    lo = _finite(obj.get("lower_95"), f"{name}.lower_95")
    hi = _finite(obj.get("upper_95"), f"{name}.upper_95")
    if not lo <= point <= hi:
        raise ValueError(f"{name} point must lie inside its interval")
    return point, lo, hi


def consume_pedicularis_xy_surface(conflict: dict, xy: dict) -> PedicularisXYBalanceReceipt:
    if not isinstance(xy, dict):
        raise ValueError("x-y receipt must be a mapping")
    if xy.get("receipt_schema_version") != XY_SCHEMA:
        raise ValueError(f"x-y receipt must use {XY_SCHEMA}")
    if xy.get("status") != "PEDICULARIS_XY_SURFACE_ANALYZED":
        raise ValueError("Pedicularis x-y surface has not been analyzed")

    xy_context = _required_text(xy.get("context_id"), "x-y context_id")
    xy_population = _required_text(xy.get("population_id"), "x-y population_id")
    xy_season = _required_text(xy.get("season_id"), "x-y season_id")
    xy_scale = _required_text(xy.get("fitness_scale_id"), "x-y fitness_scale_id")
    xy_system = _required_text(xy.get("system"), "x-y system")
    if xy_system != "Pedicularis rex":
        raise ValueError("x-y receipt must be Pedicularis rex")
    if xy.get("functional_state_level") is not True:
        raise ValueError("Pedicularis x-y receipt must declare functional_state_level=true")

    source = xy.get("source")
    if not isinstance(source, dict) or _required_text(source.get("repository"), "x-y source.repository") != "bita":
        raise ValueError("x-y receipt must preserve BITA analysis provenance")

    conflict_handoff = consume_conflict_handoff(
        conflict,
        expected_context_id=xy_context,
        expected_fitness_scale_id=xy_scale,
    )
    if conflict_handoff.system != "Pedicularis rex":
        raise ValueError("SCH conflict handoff must be Pedicularis rex")
    if conflict_handoff.population_id != xy_population:
        raise ValueError("SCH and x-y receipts must exactly match population_id")
    if conflict_handoff.season_id != xy_season:
        raise ValueError("SCH and x-y receipts must exactly match season_id")

    L, Llo, Lhi = _three(conflict.get("conflict_load"), "conflict_load")
    if Llo < 0:
        raise ValueError("conflict interval must be non-negative")
    if (Llo, Lhi) != (conflict_handoff.conflict_load.lower, conflict_handoff.conflict_load.upper):
        raise RuntimeError("canonical SCH handoff and Pedicularis conflict interval disagree")

    worldlines = xy.get("worldlines")
    if not isinstance(worldlines, dict):
        raise ValueError("x-y receipt lacks worldlines")
    gap, glo, ghi = _three(worldlines.get("gap_y1_minus_y0"), "worldline_gap")

    rpoint, _, _ = _three(xy.get("dimensional_release"), "dimensional_release")

    bita_surface_status = xy.get("bita_surface_status")
    if bita_surface_status is not None:
        bita_surface_status = _required_text(bita_surface_status, "bita_surface_status")

    if Llo <= 0:
        state = "SCH_CONFLICT_UNRESOLVED"
    elif ghi < 0:
        state = "FUNCTIONAL_STATE_BALANCE_IDENTIFIED"
    elif glo > 0:
        state = "FUNCTIONAL_STATE_BITA_SIDE_IDENTIFIED"
    else:
        state = "FUNCTIONAL_STATE_ORDER_UNRESOLVED"

    reserve = xi = depth = None
    if state == "FUNCTIONAL_STATE_BALANCE_IDENTIFIED":
        reserve = -gap
        if reserve <= 0:
            raise ValueError("BALANCE point estimate requires positive direct reserve")
        xi = two_margin_middle_position(L, reserve)
        depth = min(L, reserve)

    return PedicularisXYBalanceReceipt(
        context_id=conflict_handoff.context_id,
        fitness_scale_id=conflict_handoff.fitness_scale_id,
        conflict_load_point=L,
        conflict_load_95=(Llo, Lhi),
        worldline_gap_point=gap,
        worldline_gap_95=(glo, ghi),
        state=state,
        direct_reserve_point=reserve,
        direct_middle_position=xi,
        direct_two_sided_depth=depth,
        dimensional_release_point=rpoint,
        bita_surface_status=bita_surface_status,
        claim_level="FUNCTIONAL_STATE_ONLY_NOT_STRUCTURAL_ARCHITECTURE",
    )

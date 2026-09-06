"""Consume the shared Pedicularis x-y surface without conditioning on BITA success.

This is a functional-state Chapter-2 comparison.  The cupulate bract architecture
is present in both y states, so the output must not be promoted to a structural
architecture claim without a separate structural-y/cost lane.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

CONFLICT_SCHEMA = "THREE_WORLD_CONFLICT_HANDOFF_V1"
XY_SCHEMA = "PEDICULARIS_XY_SURFACE_HANDOFF_V1"


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


def _finite(value: object, name: str) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def _three(obj: dict, name: str) -> tuple[float, float, float]:
    point = _finite(obj.get("point"), f"{name}.point")
    lo = _finite(obj.get("lower_95"), f"{name}.lower_95")
    hi = _finite(obj.get("upper_95"), f"{name}.upper_95")
    if not lo <= point <= hi:
        raise ValueError(f"{name} point must lie inside its interval")
    return point, lo, hi


def consume_pedicularis_xy_surface(conflict: dict, xy: dict) -> PedicularisXYBalanceReceipt:
    if conflict.get("receipt_schema_version") != CONFLICT_SCHEMA:
        raise ValueError(f"conflict receipt must use {CONFLICT_SCHEMA}")
    if xy.get("receipt_schema_version") != XY_SCHEMA:
        raise ValueError(f"x-y receipt must use {XY_SCHEMA}")
    if conflict.get("status") != "THREE_WORLD_CONFLICT_CONTEXT_IDENTIFIED":
        raise ValueError("SCH conflict handoff is not positive")
    if xy.get("status") != "PEDICULARIS_XY_SURFACE_ANALYZED":
        raise ValueError("Pedicularis x-y surface has not been analyzed")
    if conflict.get("system") != "Pedicularis rex" or xy.get("system") != "Pedicularis rex":
        raise ValueError("both receipts must be Pedicularis rex")

    for field in ("context_id", "population_id", "season_id", "fitness_scale_id"):
        if conflict.get(field) != xy.get(field):
            raise ValueError(f"SCH and x-y receipts must exactly match {field}")
    if xy.get("functional_state_level") is not True:
        raise ValueError("Pedicularis x-y receipt must declare functional_state_level=true")
    source = xy.get("source")
    if not isinstance(source, dict) or source.get("repository") != "bita":
        raise ValueError("x-y receipt must preserve BITA analysis provenance")

    L, Llo, Lhi = _three(conflict.get("conflict_load", {}), "conflict_load")
    if Llo < 0:
        raise ValueError("conflict interval must be non-negative")
    worldlines = xy.get("worldlines")
    if not isinstance(worldlines, dict):
        raise ValueError("x-y receipt lacks worldlines")
    gap, glo, ghi = _three(worldlines.get("gap_y1_minus_y0", {}), "worldline_gap")
    release = xy.get("dimensional_release")
    if not isinstance(release, dict):
        raise ValueError("x-y receipt lacks dimensional_release")
    rpoint = _finite(release.get("point"), "dimensional_release.point")

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
        xi = L / (L + reserve)
        depth = min(L, reserve)

    return PedicularisXYBalanceReceipt(
        context_id=str(conflict["context_id"]),
        fitness_scale_id=str(conflict["fitness_scale_id"]),
        conflict_load_point=L,
        conflict_load_95=(Llo, Lhi),
        worldline_gap_point=gap,
        worldline_gap_95=(glo, ghi),
        state=state,
        direct_reserve_point=reserve,
        direct_middle_position=xi,
        direct_two_sided_depth=depth,
        dimensional_release_point=rpoint,
        bita_surface_status=xy.get("bita_surface_status"),
        claim_level="FUNCTIONAL_STATE_ONLY_NOT_STRUCTURAL_ARCHITECTURE",
    )

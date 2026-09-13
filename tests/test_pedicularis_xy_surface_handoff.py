from __future__ import annotations

import math
import pytest

from balance_domain import consume_pedicularis_xy_surface


def _conflict(
    context_id: str = "PEDICULARIS_POP_A_2027",
    lower: float = 0.3,
    point: float = 0.4,
    upper: float = 0.5,
) -> dict:
    return {
        "receipt_schema_version": "THREE_WORLD_CONFLICT_HANDOFF_V1",
        "status": "THREE_WORLD_CONFLICT_CONTEXT_IDENTIFIED",
        "context_id": context_id,
        "system": "Pedicularis rex",
        "population_id": "POP_A",
        "season_id": "2027",
        "fitness_scale_id": "UNDAMAGED_SEEDS_PER_FOCAL_FLOWER",
        "conflict_load": {
            "point": point,
            "lower_95": lower,
            "upper_95": upper,
            "source_field": "criticality_export.L_S_component",
        },
        "source": {
            "repository": "sch",
            "receipt_schema_version": "SCH_COMPONENT_CONFLICT_BUDGET_V1",
        },
    }


def _xy(
    gap: float = -0.1,
    lo: float = -0.2,
    hi: float = -0.02,
    context_id: str = "PEDICULARIS_POP_A_2027",
) -> dict:
    return {
        "receipt_schema_version": "PEDICULARIS_XY_SURFACE_HANDOFF_V1",
        "status": "PEDICULARIS_XY_SURFACE_ANALYZED",
        "context_id": context_id,
        "system": "Pedicularis rex",
        "population_id": "POP_A",
        "season_id": "2027",
        "fitness_scale_id": "UNDAMAGED_SEEDS_PER_FOCAL_FLOWER",
        "functional_state_level": True,
        "worldlines": {
            "gap_y1_minus_y0": {"point": gap, "lower_95": lo, "upper_95": hi},
        },
        "dimensional_release": {"point": 0.5, "lower_95": 0.2, "upper_95": 0.8},
        "bita_surface_status": "FUNCTIONAL_DIFFERENTIATION_OUTCOME_NOT_SUPPORTED",
        "source": {"repository": "bita"},
    }


def test_negative_gap_identifies_functional_state_balance() -> None:
    out = consume_pedicularis_xy_surface(_conflict(), _xy())
    assert out.state == "FUNCTIONAL_STATE_BALANCE_IDENTIFIED"
    assert math.isclose(out.direct_reserve_point, 0.1)
    assert math.isclose(out.direct_middle_position, 0.4 / 0.5)
    assert math.isclose(out.direct_two_sided_depth, 0.1)
    assert out.claim_level == "FUNCTIONAL_STATE_ONLY_NOT_STRUCTURAL_ARCHITECTURE"


def test_positive_gap_identifies_bita_side_without_requiring_bita_status() -> None:
    out = consume_pedicularis_xy_surface(_conflict(), _xy(gap=0.1, lo=0.02, hi=0.2))
    assert out.state == "FUNCTIONAL_STATE_BITA_SIDE_IDENTIFIED"
    assert out.direct_middle_position is None


def test_zero_crossing_gap_stays_unresolved() -> None:
    out = consume_pedicularis_xy_surface(_conflict(), _xy(gap=0.0, lo=-0.1, hi=0.1))
    assert out.state == "FUNCTIONAL_STATE_ORDER_UNRESOLVED"


def test_conflict_interval_touching_zero_is_not_promoted() -> None:
    out = consume_pedicularis_xy_surface(_conflict(lower=0.0), _xy())
    assert out.state == "SCH_CONFLICT_UNRESOLVED"


def test_context_mismatch_fails_closed() -> None:
    with pytest.raises(ValueError, match="context_id"):
        consume_pedicularis_xy_surface(_conflict(), _xy(context_id="OTHER"))


def test_forged_conflict_source_cannot_bypass_canonical_handoff_validator() -> None:
    conflict = _conflict()
    conflict["source"]["repository"] = "bita"
    with pytest.raises(ValueError, match="originate from sch"):
        consume_pedicularis_xy_surface(conflict, _xy())

    conflict = _conflict()
    conflict["source"]["receipt_schema_version"] = "OTHER_SCHEMA"
    with pytest.raises(ValueError, match="SCH source receipt"):
        consume_pedicularis_xy_surface(conflict, _xy())


def test_missing_xy_identifiers_cannot_match_missing_conflict_identifiers():
    conflict = _conflict()
    xy = _xy()
    conflict["context_id"] = None
    xy["context_id"] = None
    with pytest.raises(ValueError, match="context_id"):
        consume_pedicularis_xy_surface(conflict, xy)


def test_dimensional_release_point_must_lie_inside_registered_interval():
    xy = _xy()
    xy["dimensional_release"] = {"point": 0.9, "lower_95": 0.2, "upper_95": 0.8}
    with pytest.raises(ValueError, match="dimensional_release point"):
        consume_pedicularis_xy_surface(_conflict(), xy)


def test_extreme_functional_balance_uses_canonical_half_position() -> None:
    conflict = _conflict(lower=1.0e308, point=1.0e308, upper=1.0e308)
    xy = _xy(gap=-1.0e308, lo=-1.0e308, hi=-1.0e308)
    out = consume_pedicularis_xy_surface(conflict, xy)
    assert out.state == "FUNCTIONAL_STATE_BALANCE_IDENTIFIED"
    assert out.direct_reserve_point == pytest.approx(1.0e308)
    assert out.direct_middle_position == pytest.approx(0.5)
    assert out.direct_two_sided_depth == pytest.approx(1.0e308)

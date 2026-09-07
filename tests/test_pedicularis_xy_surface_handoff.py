from __future__ import annotations

import math
import pytest

from balance_domain import consume_pedicularis_xy_surface


def _conflict(context_id: str = "PEDICULARIS_POP_A_2027", lower: float = 0.3) -> dict:
    return {
        "receipt_schema_version": "THREE_WORLD_CONFLICT_HANDOFF_V1",
        "status": "THREE_WORLD_CONFLICT_CONTEXT_IDENTIFIED",
        "context_id": context_id,
        "system": "Pedicularis rex",
        "population_id": "POP_A",
        "season_id": "2027",
        "fitness_scale_id": "UNDAMAGED_SEEDS_PER_FOCAL_FLOWER",
        "conflict_load": {"point": 0.4, "lower_95": lower, "upper_95": 0.5},
    }


def _xy(gap: float = -0.1, lo: float = -0.2, hi: float = -0.02, context_id: str = "PEDICULARIS_POP_A_2027") -> dict:
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

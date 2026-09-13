import pytest

from balance_domain import (
    classify_middle_world,
    normalized_phase_point,
    two_margin_middle_position,
)


def test_scalar_world_uses_canonical_half_position_at_extreme_equal_margins():
    result = classify_middle_world(
        conflict_load=1.0e308,
        decoupling=0.0,
        architecture_cost=1.0e308,
    )
    assert result.state == "BALANCE_MIDDLE_WORLD"
    assert result.middle_position == pytest.approx(0.5)
    assert result.sch_boundary_distance == pytest.approx(1.0e308)
    assert result.bita_boundary_distance == pytest.approx(1.0e308)


def test_normalized_phase_uses_same_canonical_coordinate():
    result = normalized_phase_point(
        conflict_load=1.0e308,
        decoupling=0.0,
        architecture_cost=1.0e308,
    )
    assert result.state == "BALANCE_MIDDLE_WORLD"
    assert result.normalized_conflict == pytest.approx(1.0)
    assert result.middle_position == pytest.approx(0.5)


def test_phase_does_not_round_strict_interior_position_to_boundary_one():
    with pytest.raises(ValueError, match="strictly inside"):
        normalized_phase_point(
            conflict_load=1.0e308,
            decoupling=0.0,
            architecture_cost=1.0,
        )


def test_public_canonical_position_matches_scalar_world_on_ordinary_case():
    expected = two_margin_middle_position(2.0, 1.0)
    result = classify_middle_world(
        conflict_load=2.0,
        decoupling=0.0,
        architecture_cost=1.0,
    )
    assert result.middle_position == pytest.approx(expected)

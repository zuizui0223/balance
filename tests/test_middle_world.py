import math

import pytest

from balance_domain.world import classify_middle_world


def test_balance_is_intersection_of_sch_positive_and_bita_negative_conditions():
    result = classify_middle_world(
        conflict_load=0.2,
        decoupling=0.5,
        architecture_cost=0.3,
    )
    assert result.sch_conflict_active
    assert not result.bita_differentiation_favoured
    assert result.state == "BALANCE_MIDDLE_WORLD"
    assert math.isclose(result.recoverable_loss, 0.1)
    assert math.isclose(result.architecture_margin, -0.2)


def test_middle_position_runs_from_sch_facing_to_bita_facing_boundary():
    centre = classify_middle_world(0.2, 0.5, 0.3)
    assert math.isclose(centre.sch_boundary_distance, 0.2)
    assert math.isclose(centre.bita_boundary_distance, 0.2)
    assert math.isclose(centre.middle_position, 0.5)
    assert math.isclose(centre.two_sided_depth, 0.2)

    sch_side = classify_middle_world(0.02, 0.5, 0.30)
    bita_side = classify_middle_world(0.40, 0.5, 0.21)
    assert sch_side.middle_position < centre.middle_position
    assert bita_side.middle_position > centre.middle_position


def test_boundaries_and_bita_world_are_distinct():
    sch_boundary = classify_middle_world(0.0, 0.5, 0.3)
    assert sch_boundary.state == "SCH_NO_CONFLICT_WORLD"

    architecture_boundary = classify_middle_world(0.4, 0.5, 0.2)
    assert architecture_boundary.state == "BALANCE_BITA_INTERFACE"

    bita_world = classify_middle_world(0.4, 0.75, 0.2)
    assert bita_world.state == "BITA_DIFFERENTIATION_WORLD"
    assert bita_world.bita_differentiation_favoured


def test_middle_coordinates_are_only_defined_on_common_fitness_scale_middle_world():
    for args in [
        (0.0, 0.5, 0.3),
        (0.4, 0.5, 0.2),
        (0.4, 0.75, 0.2),
    ]:
        result = classify_middle_world(*args)
        assert result.middle_position is None
        assert result.two_sided_depth is None


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        classify_middle_world(-0.1, 0.5, 0.2)
    with pytest.raises(ValueError):
        classify_middle_world(0.1, 1.1, 0.2)
    with pytest.raises(ValueError):
        classify_middle_world(0.1, 0.5, -0.2)

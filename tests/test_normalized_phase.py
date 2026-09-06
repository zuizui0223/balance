import math

import pytest

from balance_domain import normalized_phase_point


def test_phase_map_separates_sch_limited_deep_and_bita_limited_balance():
    sch_side = normalized_phase_point(0.1, 0.5, 0.3)
    deep = normalized_phase_point(0.2, 0.5, 0.3)
    bita_side = normalized_phase_point(0.4, 0.5, 0.3)

    assert sch_side.state == deep.state == bita_side.state == "BALANCE_MIDDLE_WORLD"
    assert sch_side.balance_subregion == "SCH_BOUNDARY_LIMITED_BALANCE"
    assert deep.balance_subregion == "DEEPEST_BALANCE_RIDGE"
    assert bita_side.balance_subregion == "BITA_BOUNDARY_LIMITED_BALANCE"
    assert sch_side.middle_position < 0.5
    assert math.isclose(deep.middle_position, 0.5)
    assert bita_side.middle_position > 0.5


def test_normalized_coordinates_are_invariant_to_common_positive_rescaling():
    base = normalized_phase_point(0.2, 0.5, 0.3)
    scaled = normalized_phase_point(2.0, 0.5, 3.0)
    assert math.isclose(base.normalized_conflict, scaled.normalized_conflict)
    assert math.isclose(base.recoverable_cost_ratio, scaled.recoverable_cost_ratio)
    assert math.isclose(base.middle_position, scaled.middle_position)
    assert base.balance_subregion == scaled.balance_subregion


def test_phase_map_recovers_architecture_boundary():
    critical = normalized_phase_point(0.6, 0.5, 0.3)
    assert critical.state == "BALANCE_BITA_INTERFACE"
    assert math.isclose(critical.normalized_conflict, 2.0)
    assert math.isclose(critical.critical_conflict_ratio, 2.0)


def test_zero_decoupling_never_reaches_bita_boundary_at_finite_conflict():
    point = normalized_phase_point(100.0, 0.0, 0.3)
    assert point.state == "BALANCE_MIDDLE_WORLD"
    assert point.critical_conflict_ratio is None


def test_normalized_phase_requires_positive_architecture_cost():
    with pytest.raises(ValueError):
        normalized_phase_point(0.2, 0.5, 0.0)

import math

import pytest

from balance_domain import balance_domain_geometry, classify_middle_world


def test_finite_balance_width_and_equal_margin_point():
    geometry = balance_domain_geometry(decoupling=0.5, architecture_cost=0.3)
    assert geometry.finite_bita_boundary
    assert math.isclose(geometry.critical_conflict_load, 0.6)
    assert math.isclose(geometry.equal_margin_conflict_load, 0.2)
    assert math.isclose(geometry.max_two_sided_depth, 0.2)
    assert math.isclose(geometry.equal_margin_fraction_of_conflict_width, 1.0 / 3.0)
    assert math.isclose(geometry.criticality_index_at_equal_margin, 1.0 / 3.0)

    centre = classify_middle_world(0.2, 0.5, 0.3)
    assert centre.state == "BALANCE_MIDDLE_WORLD"
    assert math.isclose(centre.middle_position, 0.5)
    assert math.isclose(centre.two_sided_depth, geometry.max_two_sided_depth)


def test_equal_margin_point_is_not_generally_half_the_conflict_interval():
    geometry = balance_domain_geometry(decoupling=0.2, architecture_cost=0.5)
    assert math.isclose(geometry.critical_conflict_load, 2.5)
    assert math.isclose(geometry.equal_margin_conflict_load, 0.5 / 1.2)
    assert not math.isclose(
        geometry.equal_margin_conflict_load,
        geometry.critical_conflict_load / 2.0,
    )


def test_zero_decoupling_has_no_finite_bita_boundary():
    geometry = balance_domain_geometry(decoupling=0.0, architecture_cost=0.3)
    assert not geometry.finite_bita_boundary
    assert geometry.critical_conflict_load is None
    assert geometry.equal_margin_conflict_load is None
    assert geometry.max_two_sided_depth is None


def test_positive_rescaling_preserves_middle_position():
    base = classify_middle_world(0.2, 0.5, 0.3)
    scaled = classify_middle_world(2.0, 0.5, 3.0)
    assert base.state == scaled.state == "BALANCE_MIDDLE_WORLD"
    assert math.isclose(base.middle_position, scaled.middle_position)
    assert math.isclose(scaled.two_sided_depth, 10.0 * base.two_sided_depth)


def test_invalid_geometry_inputs_fail_closed():
    with pytest.raises(ValueError):
        balance_domain_geometry(-0.1, 0.3)
    with pytest.raises(ValueError):
        balance_domain_geometry(1.1, 0.3)
    with pytest.raises(ValueError):
        balance_domain_geometry(0.5, -0.1)

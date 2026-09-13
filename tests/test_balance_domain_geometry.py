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
    assert math.isclose(geometry.criticality_index_at_equal_margin, 0.5)
    assert math.isclose(geometry.architecture_pressure_ratio_at_equal_margin, 1.0 / 3.0)
    assert math.isclose(geometry.sch_limited_width, 0.2)
    assert math.isclose(geometry.bita_limited_width, 0.4)
    assert math.isclose(geometry.bita_to_sch_width_ratio, 2.0)

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
    assert math.isclose(geometry.bita_to_sch_width_ratio, 5.0)
    assert math.isclose(geometry.criticality_index_at_equal_margin, 0.5)
    assert math.isclose(geometry.architecture_pressure_ratio_at_equal_margin, 1.0 / 6.0)


def test_architecture_cost_scales_width_but_not_normalized_shape():
    low_cost = balance_domain_geometry(decoupling=0.25, architecture_cost=0.2)
    high_cost = balance_domain_geometry(decoupling=0.25, architecture_cost=1.0)
    assert math.isclose(high_cost.critical_conflict_load, 5 * low_cost.critical_conflict_load)
    assert math.isclose(high_cost.sch_limited_width, 5 * low_cost.sch_limited_width)
    assert math.isclose(high_cost.bita_limited_width, 5 * low_cost.bita_limited_width)
    assert math.isclose(
        high_cost.bita_to_sch_width_ratio,
        low_cost.bita_to_sch_width_ratio,
    )
    assert math.isclose(
        high_cost.criticality_index_at_equal_margin,
        low_cost.criticality_index_at_equal_margin,
    )


def test_weaker_decoupling_increases_bita_side_skew():
    strong = balance_domain_geometry(decoupling=1.0, architecture_cost=0.4)
    weak = balance_domain_geometry(decoupling=0.2, architecture_cost=0.4)
    assert math.isclose(strong.bita_to_sch_width_ratio, 1.0)
    assert math.isclose(weak.bita_to_sch_width_ratio, 5.0)
    assert weak.equal_margin_fraction_of_conflict_width < strong.equal_margin_fraction_of_conflict_width
    assert math.isclose(strong.criticality_index_at_equal_margin, 0.5)
    assert math.isclose(weak.criticality_index_at_equal_margin, 0.5)


def test_zero_decoupling_has_no_finite_bita_boundary():
    geometry = balance_domain_geometry(decoupling=0.0, architecture_cost=0.3)
    assert not geometry.finite_bita_boundary
    assert geometry.critical_conflict_load is None
    assert geometry.equal_margin_conflict_load is None
    assert geometry.max_two_sided_depth is None
    assert geometry.criticality_index_at_equal_margin is None
    assert geometry.architecture_pressure_ratio_at_equal_margin is None
    assert geometry.bita_to_sch_width_ratio is None


def test_zero_architecture_cost_is_valid_for_state_but_not_positive_width_geometry():
    # Proposition 4/5 geometry assumes K>0. With s>0 and K=0 the putative
    # interval is 0<L<0, so L=0 must not be returned as an interior deepest point.
    with pytest.raises(ValueError):
        balance_domain_geometry(decoupling=0.5, architecture_cost=0.0)

    differentiated = classify_middle_world(1.0, 0.5, 0.0)
    assert differentiated.state == "BITA_DIFFERENTIATION_WORLD"
    assert differentiated.middle_position is None
    assert differentiated.two_sided_depth is None

    interface = classify_middle_world(1.0, 0.0, 0.0)
    assert interface.state == "BALANCE_BITA_INTERFACE"
    assert interface.middle_position is None
    assert interface.two_sided_depth is None


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
    with pytest.raises(ValueError):
        balance_domain_geometry(0.5, 0.0)

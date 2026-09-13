import math

import pytest

from balance_domain.environmental_depth import environmental_depth


def test_environmental_depth_differs_from_fitness_midpoint_when_slopes_differ():
    # Example from the theorem: L=e, rho=4-2e.
    # At the fitness-midpoint e=4/3, L=rho, but environmental distances differ.
    e = 4.0 / 3.0
    L = e
    rho = 4.0 - 2.0 * e
    result = environmental_depth(
        conflict_margin=L,
        reserve_margin=rho,
        conflict_gradient=[1.0],
        reserve_gradient=[-2.0],
    )
    assert math.isclose(L, rho)
    assert not math.isclose(result.position, 0.5)

    # At e=1, environmental distances are equal.
    e = 1.0
    result = environmental_depth(
        conflict_margin=e,
        reserve_margin=4.0 - 2.0 * e,
        conflict_gradient=[1.0],
        reserve_gradient=[-2.0],
    )
    assert math.isclose(result.sch_distance, result.bita_distance)
    assert math.isclose(result.position, 0.5)


def test_separate_margin_rescalings_leave_environmental_depth_invariant():
    base = environmental_depth(
        conflict_margin=2.0,
        reserve_margin=3.0,
        conflict_gradient=[1.0, 2.0],
        reserve_gradient=[-2.0, 1.0],
    )
    scaled = environmental_depth(
        conflict_margin=10.0,
        reserve_margin=21.0,
        conflict_gradient=[5.0, 10.0],
        reserve_gradient=[-14.0, 7.0],
    )
    assert math.isclose(base.sch_distance, scaled.sch_distance, rel_tol=1e-12)
    assert math.isclose(base.bita_distance, scaled.bita_distance, rel_tol=1e-12)
    assert math.isclose(base.position, scaled.position, rel_tol=1e-12)


def test_large_finite_gradients_do_not_collapse_depth_to_zero():
    result = environmental_depth(
        conflict_margin=1.7e308,
        reserve_margin=1.7e308,
        conflict_gradient=[1.7e308, 1.7e308],
        reserve_gradient=[-1.7e308, 1.7e308],
    )
    assert result.sch_distance == pytest.approx(1.0 / math.sqrt(2.0))
    assert result.bita_distance == pytest.approx(1.0 / math.sqrt(2.0))
    assert result.depth == pytest.approx(1.0 / math.sqrt(2.0))
    assert result.position == pytest.approx(0.5)


def test_large_finite_depths_keep_midpoint_coordinate():
    result = environmental_depth(
        conflict_margin=1.0e308,
        reserve_margin=1.0e308,
        conflict_gradient=[1.0],
        reserve_gradient=[1.0],
    )
    assert result.sch_distance == 1.0e308
    assert result.bita_distance == 1.0e308
    assert result.position == pytest.approx(0.5)


def test_unrepresentable_positive_distance_fails_closed_instead_of_returning_zero():
    with pytest.raises(ValueError, match="distance must remain finite and positive"):
        environmental_depth(
            conflict_margin=5e-324,
            reserve_margin=1.0,
            conflict_gradient=[1.0e308],
            reserve_gradient=[1.0],
        )


def test_invalid_margins_and_zero_gradients_fail_closed():
    bad_cases = [
        dict(conflict_margin=0.0, reserve_margin=1.0, conflict_gradient=[1.0], reserve_gradient=[1.0]),
        dict(conflict_margin=1.0, reserve_margin=-1.0, conflict_gradient=[1.0], reserve_gradient=[1.0]),
        dict(conflict_margin=1.0, reserve_margin=1.0, conflict_gradient=[0.0], reserve_gradient=[1.0]),
    ]
    for kwargs in bad_cases:
        with pytest.raises(ValueError):
            environmental_depth(**kwargs)

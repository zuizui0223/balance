import math

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


def test_invalid_margins_and_zero_gradients_fail_closed():
    bad_cases = [
        dict(conflict_margin=0.0, reserve_margin=1.0, conflict_gradient=[1.0], reserve_gradient=[1.0]),
        dict(conflict_margin=1.0, reserve_margin=-1.0, conflict_gradient=[1.0], reserve_gradient=[1.0]),
        dict(conflict_margin=1.0, reserve_margin=1.0, conflict_gradient=[0.0], reserve_gradient=[1.0]),
    ]
    for kwargs in bad_cases:
        try:
            environmental_depth(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid environmental-depth inputs should fail")

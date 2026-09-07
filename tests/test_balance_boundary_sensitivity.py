import math

from balance_domain.sensitivity import boundary_sensitivity, deepest_point_sensitivity


def test_linear_boundary_sensitivity_matches_exact_perturbation():
    # Baseline L=e-1, rho=4-e.  Boundaries: e0=1, e2=4, width=3.
    # Perturb L by +eps*0.2 and rho by +eps*0.3.
    result = boundary_sensitivity(a0=0.2, L_prime0=1.0, b2=0.3, rho_prime2=-1.0)
    assert math.isclose(result.sch_boundary_shift, -0.2)
    assert math.isclose(result.bita_boundary_shift, 0.3)
    assert math.isclose(result.width_shift, 0.5)


def test_deepest_point_shift_matches_linear_exact_solution():
    # Baseline equal-margin point solves e-1 = 4-e -> e=2.5.
    # With perturbations +eps*a and +eps*b, exact solution is
    # e=(5 + eps*(b-a))/2.
    a = 0.4
    b = -0.2
    result = deepest_point_sensitivity(a=a, b=b, L_prime=1.0, rho_prime=-1.0)
    expected_location = (b - a) / 2.0
    assert math.isclose(result.location_shift, expected_location)

    # Depth is L(e_d)+eps*a; exact first derivative = (a+b)/2.
    assert math.isclose(result.depth_shift, (a + b) / 2.0)


def test_equal_margin_shift_changes_depth_not_location():
    result = deepest_point_sensitivity(a=0.7, b=0.7, L_prime=2.0, rho_prime=-3.0)
    assert math.isclose(result.location_shift, 0.0, abs_tol=1e-15)
    assert math.isclose(result.depth_shift, 0.7)


def test_singular_slopes_fail_closed():
    try:
        boundary_sensitivity(a0=1.0, L_prime0=0.0, b2=1.0, rho_prime2=-1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero boundary slope should fail")

    try:
        deepest_point_sensitivity(a=1.0, b=0.0, L_prime=1.0, rho_prime=1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero deepest-point denominator should fail")

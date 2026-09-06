import math

import pytest

from balance_domain.covering_certificate import (
    certified_balance_ball_radius,
    certified_outside_ball_radius,
)


def test_positive_sample_certifies_inside_ball():
    radius = certified_balance_ball_radius(
        margins=(0.30, 0.20, 0.45),
        lipschitz_constants=(0.5, 0.4, 0.9),
    )
    assert radius == pytest.approx(min(0.30 / 0.5, 0.20 / 0.4, 0.45 / 0.9))


def test_nonpositive_margin_prevents_inside_ball():
    radius = certified_balance_ball_radius(
        margins=(0.30, 0.0),
        lipschitz_constants=(0.5, 0.4),
    )
    assert radius == 0.0


def test_negative_margin_certifies_outside_ball_using_largest_normalized_failure():
    radius = certified_outside_ball_radius(
        margins=(0.20, -0.10, -0.30),
        lipschitz_constants=(0.5, 0.2, 0.3),
    )
    assert radius == pytest.approx(max(0.10 / 0.2, 0.30 / 0.3))


def test_constant_negative_margin_certifies_unbounded_outside_region():
    radius = certified_outside_ball_radius(
        margins=(0.2, -0.1),
        lipschitz_constants=(0.5, 0.0),
    )
    assert math.isinf(radius)


def test_constant_positive_margins_do_not_limit_inside_radius():
    radius = certified_balance_ball_radius(
        margins=(0.2, 0.3),
        lipschitz_constants=(0.0, 0.0),
    )
    assert math.isinf(radius)

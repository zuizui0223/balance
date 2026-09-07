import pytest

from balance_domain.covering_certificate import (
    lipschitz_lower_envelope,
    multi_margin_lower_depth,
)


def test_lower_envelope_is_maximum_of_sample_cones():
    lower = lipschitz_lower_envelope(
        sampled_values=(0.20, 0.45, 0.30),
        distances_to_query=(0.10, 0.40, 0.05),
        lipschitz_constant=0.5,
    )
    expected = max(0.20 - 0.5 * 0.10, 0.45 - 0.5 * 0.40, 0.30 - 0.5 * 0.05)
    assert lower == pytest.approx(expected)


def test_adding_a_sample_cannot_lower_the_certificate_at_a_query():
    old = lipschitz_lower_envelope(
        sampled_values=(0.20, 0.35),
        distances_to_query=(0.20, 0.30),
        lipschitz_constant=0.5,
    )
    new = lipschitz_lower_envelope(
        sampled_values=(0.20, 0.35, 0.31),
        distances_to_query=(0.20, 0.30, 0.02),
        lipschitz_constant=0.5,
    )
    assert new >= old


def test_multi_margin_depth_uses_weakest_lower_envelope():
    depth = multi_margin_lower_depth(
        sampled_values_by_margin=(
            (0.30, 0.35),  # L
            (0.24, 0.28),  # rho_1
            (0.40, 0.32),  # rho_2
        ),
        distances_to_query=(0.10, 0.20),
        lipschitz_constants=(0.5, 0.4, 0.3),
    )
    l_lower = max(0.30 - 0.5 * 0.10, 0.35 - 0.5 * 0.20)
    rho1_lower = max(0.24 - 0.4 * 0.10, 0.28 - 0.4 * 0.20)
    rho2_lower = max(0.40 - 0.3 * 0.10, 0.32 - 0.3 * 0.20)
    assert depth == pytest.approx(min(l_lower, rho1_lower, rho2_lower))


def test_invalid_distance_fails_closed():
    with pytest.raises(ValueError):
        lipschitz_lower_envelope(
            sampled_values=(0.2,),
            distances_to_query=(-0.1,),
            lipschitz_constant=0.5,
        )

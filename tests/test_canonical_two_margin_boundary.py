import random

import pytest

from balance_domain.boundary import (
    analyze_two_margin_path,
    classify_two_margin_point,
    positive_support_monotone,
)
from balance_domain.domain_existence import classify_domain_path
from balance_domain.multi_alternative import classify_multi_alternative_middle_world
from balance_domain.phase import normalized_phase_point
from balance_domain.static import analyze_balance_path
from balance_domain.world import classify_middle_world
from balance_domain.worldline_path import analyze_worldline_path


def _assert_intervals_close(left, right):
    assert len(left) == len(right)
    for (la, lb), (ra, rb) in zip(left, right):
        assert la == pytest.approx(ra)
        assert lb == pytest.approx(rb)


def test_canonical_path_uses_later_entry_and_earlier_exit():
    # Entry segment: L becomes positive before rho does -> rho crossing controls.
    # Exit segment: L is lost before rho -> L crossing controls.
    result = analyze_two_margin_path(
        environment=[0.0, 1.0, 2.0, 3.0],
        conflict_margin=[0.0, 1.0, 1.0, 0.0],
        reserve_margin=[-1.0, 1.0, 1.0, 1.0],
        tolerance=0.0,
    )
    _assert_intervals_close(result.middle_intervals, ((0.5, 3.0),))
    assert result.middle_width == pytest.approx(2.5)


def test_point_classifier_uses_one_registered_tolerance_for_both_boundaries():
    tol = 1e-6
    assert not classify_two_margin_point(tol, 1.0, tolerance=tol).middle_active
    assert classify_two_margin_point(2 * tol, 2 * tol, tolerance=tol).middle_active
    assert classify_two_margin_point(1.0, 0.5 * tol, tolerance=tol).reserve_position == "INTERFACE"
    assert classify_two_margin_point(1.0, -2 * tol, tolerance=tol).reserve_position == "NEGATIVE"


def test_positive_support_monotone_tracks_support_not_magnitude():
    assert positive_support_monotone([0.0, 0.4, 0.3, 0.1])
    assert not positive_support_monotone([0.0, 0.4, 0.0, 0.2])


def test_all_fitness_scale_routes_share_canonical_node_occupancy_randomized():
    rng = random.Random(20260913)
    environment = [0.0, 1.0, 2.0, 3.0, 4.0]

    for _ in range(400):
        L = [0.0 if rng.random() < 0.2 else rng.uniform(0.05, 2.0) for _ in environment]
        s = [rng.uniform(0.0, 1.0) for _ in environment]
        K = [rng.uniform(0.05, 2.0) for _ in environment]
        reserve = [ki - si * li for li, si, ki in zip(L, s, K)]

        static = analyze_balance_path(environment, L, s, K)

        # Build matched direct worldlines with exactly the same reserve:
        # rho_direct = W_S* - W_D* = reserve.
        Ws = [10.0] * len(environment)
        Wd = [10.0 - rho for rho in reserve]
        direct = analyze_worldline_path(
            environment,
            Ws,
            Wd,
            L,
            tolerance=1e-12,
        )
        sampled = classify_domain_path(L, [-rho for rho in reserve])

        static_active = tuple(state == "BALANCE" for state in static.states)
        direct_active = tuple(state == "BALANCE_MIDDLE_WORLD" for state in direct.states)
        sampled_active = tuple(i in sampled.balance_indices for i in range(len(environment)))
        scalar_active = tuple(
            classify_middle_world(li, si, ki, tolerance=1e-12).state == "BALANCE_MIDDLE_WORLD"
            for li, si, ki in zip(L, s, K)
        )
        multi_active = tuple(
            classify_multi_alternative_middle_world(
                li,
                (rho, rho + 0.5),
                atol=1e-12,
            ).state == "MULTI_ALTERNATIVE_BALANCE"
            for li, rho in zip(L, reserve)
        )

        assert static_active == direct_active == sampled_active == scalar_active == multi_active
        _assert_intervals_close(static.balance_intervals, direct.balance_intervals)
        assert static.balance_width == pytest.approx(direct.balance_width)
        assert 0.0 <= static.balance_width <= environment[-1] - environment[0]


def test_normalized_phase_near_boundary_is_invariant_to_fitness_unit_rescaling():
    tol = 1e-6
    base = normalized_phase_point(0.5e-6, 0.5, 1.0, tolerance=tol)
    scaled = normalized_phase_point(0.5, 0.5, 1.0e6, tolerance=tol)
    assert base.normalized_conflict == pytest.approx(scaled.normalized_conflict)
    assert base.recoverable_cost_ratio == pytest.approx(scaled.recoverable_cost_ratio)
    assert base.state == scaled.state == "SCH_NO_CONFLICT_WORLD"

    # The same invariance must hold on the architecture interface.
    base_interface = normalized_phase_point(2.0, 0.5, 1.0, tolerance=tol)
    scaled_interface = normalized_phase_point(2.0e6, 0.5, 1.0e6, tolerance=tol)
    assert base_interface.state == scaled_interface.state == "BALANCE_BITA_INTERFACE"


def test_phi_and_direct_gap_sign_conventions_collapse_to_same_reserve_margin():
    L = 1.0
    rho = 0.25
    phi = -rho
    direct_gap = -rho
    from_phi = classify_two_margin_point(L, -phi)
    from_direct = classify_two_margin_point(L, -direct_gap)
    assert from_phi == from_direct
    assert from_phi.middle_active


def test_negative_conflict_is_invalid_across_canonical_scalar_routes():
    with pytest.raises(ValueError):
        classify_two_margin_point(-0.1, 1.0)
    with pytest.raises(ValueError):
        classify_middle_world(-0.1, 0.5, 1.0)
    with pytest.raises(ValueError):
        classify_multi_alternative_middle_world(-0.1, (1.0, 2.0))


def test_invalid_canonical_inputs_fail_closed():
    with pytest.raises(ValueError):
        classify_two_margin_point(float("nan"), 1.0)
    with pytest.raises(ValueError):
        classify_two_margin_point(1.0, 1.0, tolerance=-1.0)
    with pytest.raises(ValueError):
        analyze_two_margin_path([0, 0], [1, 1], [1, 1])
    with pytest.raises(ValueError):
        positive_support_monotone([0.0, float("inf")])

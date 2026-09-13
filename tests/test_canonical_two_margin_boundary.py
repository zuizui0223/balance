import random

import pytest

from balance_domain.boundary import (
    DEFAULT_BOUNDARY_TOLERANCE,
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
from balance_domain.worldlines import compare_worldlines


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
        direct = analyze_worldline_path(environment, Ws, Wd, L)
        sampled = classify_domain_path(L, [-rho for rho in reserve])

        static_active = tuple(state == "BALANCE" for state in static.states)
        direct_active = tuple(state == "BALANCE_MIDDLE_WORLD" for state in direct.states)
        sampled_active = tuple(i in sampled.balance_indices for i in range(len(environment)))
        scalar_active = tuple(
            classify_middle_world(li, si, ki).state == "BALANCE_MIDDLE_WORLD"
            for li, si, ki in zip(L, s, K)
        )
        multi_active = tuple(
            classify_multi_alternative_middle_world(
                li,
                (rho, rho + 0.5),
            ).state == "MULTI_ALTERNATIVE_BALANCE"
            for li, rho in zip(L, reserve)
        )
        scalar_direct_results = tuple(
            compare_worldlines(
                ws,
                wd,
                li,
                decoupling=si,
                architecture_cost=ki,
            )
            for ws, wd, li, si, ki in zip(Ws, Wd, L, s, K)
        )
        scalar_direct_active = tuple(
            result.state == "BALANCE_MIDDLE_WORLD"
            for result in scalar_direct_results
        )

        assert (
            static_active
            == direct_active
            == sampled_active
            == scalar_active
            == multi_active
            == scalar_direct_active
        )
        _assert_intervals_close(static.balance_intervals, direct.balance_intervals)
        assert static.balance_width == pytest.approx(direct.balance_width)
        assert 0.0 <= static.balance_width <= environment[-1] - environment[0]

        for active, rho, result in zip(static_active, reserve, scalar_direct_results):
            assert result.bridge_consistent is True
            if active:
                assert result.direct_reserve == pytest.approx(rho)
                assert result.decomposed_reserve == pytest.approx(rho)
                assert result.direct_middle_position == pytest.approx(result.decomposed_middle_position)
            else:
                assert result.direct_reserve is None
                assert result.decomposed_reserve is None


def test_default_tolerance_agrees_on_near_sch_boundary_across_routes():
    tol = DEFAULT_BOUNDARY_TOLERANCE
    tiny_L = 0.5 * tol
    L = [tiny_L, tiny_L]
    rho = 1.0
    environment = [0.0, 1.0]

    static = analyze_balance_path(environment, L, [0.0, 0.0], [rho, rho])
    direct = analyze_worldline_path(environment, [1.0, 1.0], [0.0, 0.0], L)
    sampled = classify_domain_path(L, [-rho, -rho])
    scalar = classify_middle_world(tiny_L, 0.0, rho)
    multi = classify_multi_alternative_middle_world(tiny_L, (rho, rho + 1.0))
    scalar_direct = compare_worldlines(1.0, 0.0, tiny_L)

    assert static.states == ("NO_CONFLICT", "NO_CONFLICT")
    assert direct.states == ("SCH_NO_CONFLICT_WORLD", "SCH_NO_CONFLICT_WORLD")
    assert sampled.balance_indices == ()
    assert scalar.state == "SCH_NO_CONFLICT_WORLD"
    assert multi.state == "NO_SHARED_CONFLICT"
    assert scalar_direct.state == "SCH_NO_CONFLICT_WORLD"


def test_default_tolerance_agrees_on_near_architecture_boundary_across_routes():
    tol = DEFAULT_BOUNDARY_TOLERANCE
    rho = 0.5 * tol
    L = [1.0, 1.0]
    environment = [0.0, 1.0]
    wd = 1.0 - rho

    static = analyze_balance_path(environment, L, [0.0, 0.0], [rho, rho])
    direct = analyze_worldline_path(environment, [1.0, 1.0], [wd, wd], L)
    sampled = classify_domain_path(L, [-rho, -rho])
    scalar = classify_middle_world(1.0, 0.0, rho)
    multi = classify_multi_alternative_middle_world(1.0, (rho, rho + 1.0))
    scalar_direct = compare_worldlines(1.0, wd, 1.0)

    assert static.states == ("CRITICAL", "CRITICAL")
    assert direct.states == ("ARCHITECTURE_CRITICAL_INTERFACE",) * 2
    assert sampled.balance_indices == ()
    assert scalar.state == "BALANCE_BITA_INTERFACE"
    assert multi.state == "ARCHITECTURE_ENVELOPE_BOUNDARY"
    assert scalar_direct.state == "ARCHITECTURE_CRITICAL_INTERFACE"


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


def test_extreme_reserve_crossing_recovers_midpoint_without_overflow():
    result = analyze_two_margin_path(
        environment=[0.0, 10.0],
        conflict_margin=[1.0, 1.0],
        reserve_margin=[-1.0e308, 1.0e308],
        tolerance=0.0,
    )
    _assert_intervals_close(result.middle_intervals, ((5.0, 10.0),))
    assert result.middle_width == pytest.approx(5.0)


def test_extreme_environment_span_can_still_return_finite_middle_interval():
    result = analyze_two_margin_path(
        environment=[-1.0e308, 1.0e308],
        conflict_margin=[0.0, 1.0e308],
        reserve_margin=[1.0e308, 1.0e308],
        tolerance=5.0e307,
    )
    _assert_intervals_close(result.middle_intervals, ((0.0, 1.0e308),))
    assert result.middle_width == pytest.approx(1.0e308)


def test_unrepresentable_middle_width_fails_closed():
    with pytest.raises(ValueError, match="width must remain finite"):
        analyze_two_margin_path(
            environment=[-1.0e308, 1.0e308],
            conflict_margin=[1.0, 1.0],
            reserve_margin=[1.0, 1.0],
            tolerance=0.0,
        )


def test_negative_conflict_is_invalid_across_canonical_scalar_routes():
    with pytest.raises(ValueError):
        classify_two_margin_point(-0.1, 1.0)
    with pytest.raises(ValueError):
        classify_middle_world(-0.1, 0.5, 1.0)
    with pytest.raises(ValueError):
        classify_multi_alternative_middle_world(-0.1, (1.0, 2.0))
    with pytest.raises(ValueError):
        compare_worldlines(10.0, 9.0, -0.1)


def test_invalid_canonical_inputs_fail_closed():
    with pytest.raises(ValueError):
        classify_two_margin_point(float("nan"), 1.0)
    with pytest.raises(ValueError):
        classify_two_margin_point(1.0, 1.0, tolerance=-1.0)
    with pytest.raises(ValueError):
        analyze_two_margin_path([0, 0], [1, 1], [1, 1])
    with pytest.raises(ValueError):
        positive_support_monotone([0.0, float("inf")])

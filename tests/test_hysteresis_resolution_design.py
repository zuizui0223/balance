from fractions import Fraction
from math import ceil, sqrt
import random

from balance_domain.hysteresis_resolution_design import (
    optimal_hysteresis_resolution_design,
)


def _exact_feasible(su: float, sd: float, eta: float, n_up: int, n_down: int) -> bool:
    su_exact = Fraction.from_float(float(su))
    sd_exact = Fraction.from_float(float(sd))
    eta_exact = Fraction.from_float(float(eta))
    return su_exact / n_up + sd_exact / n_down <= eta_exact


def _brute_lexicographic_optimum(su: float, sd: float, eta: float, max_total: int):
    for total in range(2, max_total + 1):
        for n_up in range(1, total):
            n_down = total - n_up
            if _exact_feasible(su, sd, eta, n_up, n_down):
                return total, n_up, n_down
    raise AssertionError("brute-force search did not reach a feasible design")


def test_equal_spans_recover_symmetric_error_allocation():
    result = optimal_hysteresis_resolution_design(
        forward_span=1.0,
        reverse_span=1.0,
        width_error_budget=0.1,
    )
    assert result.forward_intervals == 20
    assert result.reverse_intervals == 20
    assert result.total_intervals == 40
    assert abs(result.forward_step - 0.05) < 1e-12
    assert abs(result.reverse_step - 0.05) < 1e-12
    assert result.guaranteed_width_inflation <= 0.1
    assert abs(result.continuous_interval_lower_bound - 40.0) < 1e-12


def test_unequal_spans_allocate_larger_step_budget_to_larger_span_by_square_root_rule():
    result = optimal_hysteresis_resolution_design(
        forward_span=4.0,
        reverse_span=1.0,
        width_error_budget=0.3,
    )
    assert abs(
        result.continuous_optimal_forward_step
        / result.continuous_optimal_reverse_step
        - 2.0
    ) < 1e-12
    assert abs(result.continuous_interval_lower_bound - 30.0) < 1e-12
    assert result.guaranteed_width_inflation <= 0.3


def test_integer_design_preserves_historical_lexicographic_tie_break():
    result = optimal_hysteresis_resolution_design(
        forward_span=1.7,
        reverse_span=0.8,
        width_error_budget=0.12,
    )
    assert (result.total_intervals, result.forward_intervals, result.reverse_intervals) == (
        41,
        22,
        19,
    )
    assert _exact_feasible(1.7, 0.8, 0.12, 22, 19)


def test_exact_logarithmic_search_matches_brute_force_randomized_small_cases():
    rng = random.Random(20260913)
    for _ in range(120):
        su = rng.randint(1, 20) / 10.0
        sd = rng.randint(1, 20) / 10.0
        eta = rng.randint(1, 10) / 10.0
        result = optimal_hysteresis_resolution_design(
            forward_span=su,
            reverse_span=sd,
            width_error_budget=eta,
        )
        brute = _brute_lexicographic_optimum(su, sd, eta, result.total_intervals)
        assert (
            result.total_intervals,
            result.forward_intervals,
            result.reverse_intervals,
        ) == brute
        assert _exact_feasible(
            su,
            sd,
            eta,
            result.forward_intervals,
            result.reverse_intervals,
        )


def test_design_is_invariant_to_common_positive_unit_rescaling():
    base = optimal_hysteresis_resolution_design(
        forward_span=1.7,
        reverse_span=0.8,
        width_error_budget=0.12,
    )
    expected = (base.total_intervals, base.forward_intervals, base.reverse_intervals)
    for scale in (1e-150, 1e150):
        scaled = optimal_hysteresis_resolution_design(
            forward_span=1.7 * scale,
            reverse_span=0.8 * scale,
            width_error_budget=0.12 * scale,
        )
        assert (
            scaled.total_intervals,
            scaled.forward_intervals,
            scaled.reverse_intervals,
        ) == expected
        assert scaled.guaranteed_width_inflation <= scaled.width_error_budget


def test_high_resolution_design_does_not_scan_billions_of_allocations():
    # For equal unit spans and eta=2^-30, symmetry gives n_up=n_down=2^31,
    # hence a minimum total of 2^32 intervals. A linear scan over candidate
    # n_up values would be infeasible; the exact logarithmic search remains tiny.
    eta = 2.0 ** -30
    result = optimal_hysteresis_resolution_design(
        forward_span=1.0,
        reverse_span=1.0,
        width_error_budget=eta,
    )
    assert result.forward_intervals == 2**31
    assert result.reverse_intervals == 2**31
    assert result.total_intervals == 2**32
    assert result.guaranteed_width_inflation <= eta


def test_integer_total_respects_continuous_lower_bound():
    result = optimal_hysteresis_resolution_design(
        forward_span=2.0,
        reverse_span=0.5,
        width_error_budget=0.07,
    )
    assert result.total_intervals >= ceil(result.continuous_interval_lower_bound - 1e-12)

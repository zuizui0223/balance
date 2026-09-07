from math import ceil, sqrt

from balance_domain.hysteresis_resolution_design import (
    optimal_hysteresis_resolution_design,
)


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
    assert result.guaranteed_width_inflation <= 0.1 + 1e-12
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
    assert result.guaranteed_width_inflation <= 0.3 + 1e-12


def test_integer_design_is_globally_minimal_against_all_smaller_totals():
    su, sd, eta = 1.7, 0.8, 0.12
    result = optimal_hysteresis_resolution_design(
        forward_span=su,
        reverse_span=sd,
        width_error_budget=eta,
    )
    for total in range(2, result.total_intervals):
        feasible = False
        for n_up in range(1, total):
            n_down = total - n_up
            if su / n_up + sd / n_down <= eta + 1e-15:
                feasible = True
                break
        assert not feasible


def test_integer_total_respects_continuous_lower_bound():
    result = optimal_hysteresis_resolution_design(
        forward_span=2.0,
        reverse_span=0.5,
        width_error_budget=0.07,
    )
    assert result.total_intervals >= ceil(result.continuous_interval_lower_bound - 1e-12)

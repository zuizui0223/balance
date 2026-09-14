import math

import pytest

from balance_domain.hysteresis_resolution_design import (
    optimal_hysteresis_resolution_design,
)


def test_extreme_equal_spans_recover_finite_continuous_diagnostics():
    result = optimal_hysteresis_resolution_design(
        forward_span=1.0e308,
        reverse_span=1.0e308,
        width_error_budget=1.0e308,
    )
    assert (result.forward_intervals, result.reverse_intervals) == (2, 2)
    assert result.total_intervals == 4
    assert result.forward_step == pytest.approx(5.0e307)
    assert result.reverse_step == pytest.approx(5.0e307)
    assert result.continuous_optimal_forward_step == pytest.approx(5.0e307)
    assert result.continuous_optimal_reverse_step == pytest.approx(5.0e307)
    assert result.continuous_interval_lower_bound == pytest.approx(4.0)
    assert math.isfinite(result.guaranteed_width_inflation)
    assert result.guaranteed_width_inflation <= result.width_error_budget


def test_boolean_design_inputs_are_not_numeric_evidence():
    base = dict(
        forward_span=1.0,
        reverse_span=1.0,
        width_error_budget=0.1,
    )
    for field in base:
        malformed = dict(base)
        malformed[field] = True
        with pytest.raises(ValueError, match="not boolean"):
            optimal_hysteresis_resolution_design(**malformed)


def test_positive_resolution_step_cannot_underflow_to_zero():
    tiny = 5.0e-324
    with pytest.raises(ValueError, match="underflows float precision"):
        optimal_hysteresis_resolution_design(
            forward_span=tiny,
            reverse_span=tiny,
            width_error_budget=tiny,
        )

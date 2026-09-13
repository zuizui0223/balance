import math

import pytest

from balance_domain.multi_alternative import classify_multi_alternative_middle_world


def test_envelope_reserve_is_minimum_reserve_and_controls_balance():
    result = classify_multi_alternative_middle_world(
        conflict_margin=2.0,
        alternative_reserves=(3.0, 1.0, 4.0),
    )
    assert result.state == "MULTI_ALTERNATIVE_BALANCE"
    assert math.isclose(result.envelope_reserve, 1.0, abs_tol=1e-12)
    assert math.isclose(result.fitness_depth, 1.0, abs_tol=1e-12)
    assert result.threatening_alternatives == (1,)


def test_any_winning_alternative_breaks_balance():
    result = classify_multi_alternative_middle_world(
        conflict_margin=2.0,
        alternative_reserves=(3.0, -0.2, 4.0),
    )
    assert result.state == "ALTERNATIVE_ARCHITECTURE_SIDE"
    assert result.envelope_reserve < 0


def test_tied_best_alternatives_are_all_reported():
    result = classify_multi_alternative_middle_world(
        conflict_margin=2.0,
        alternative_reserves=(1.0, 1.0, 2.0),
    )
    assert result.threatening_alternatives == (0, 1)
    assert result.state == "MULTI_ALTERNATIVE_BALANCE"


def test_near_zero_envelope_uses_same_tolerance_as_threat_ties():
    tol = 1e-6
    for reserve in (0.5e-6, -0.5e-6, 0.0):
        result = classify_multi_alternative_middle_world(
            conflict_margin=1.0,
            alternative_reserves=(reserve, 0.2),
            atol=tol,
        )
        assert result.state == "ARCHITECTURE_ENVELOPE_BOUNDARY"
        assert result.fitness_depth == 0.0


def test_near_zero_conflict_is_not_called_multi_alternative_balance():
    result = classify_multi_alternative_middle_world(
        conflict_margin=0.5e-6,
        alternative_reserves=(0.3, 0.4),
        atol=1e-6,
    )
    assert result.state == "NO_SHARED_CONFLICT"
    assert result.fitness_depth == 0.0


def test_multi_alternative_inputs_fail_closed_on_bad_tolerance_or_nonfinite_values():
    with pytest.raises(ValueError):
        classify_multi_alternative_middle_world(1.0, (0.3, 0.4), atol=-1e-6)
    with pytest.raises(ValueError):
        classify_multi_alternative_middle_world(1.0, (0.3, math.nan))
    with pytest.raises(ValueError):
        classify_multi_alternative_middle_world(math.inf, (0.3, 0.4))

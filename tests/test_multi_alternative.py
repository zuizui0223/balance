import math

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

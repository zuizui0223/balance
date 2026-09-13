import math

import pytest

from balance_domain.receipt import Interval, classify_bounded_receipt


def test_direct_balance_receipt_can_be_identified_without_s_k():
    result = classify_bounded_receipt(
        context_id="ctx-1",
        fitness_scale_id="seed_set",
        conflict_load=Interval(0.20, 0.30),
        shared_optimum_fitness=Interval(9.9, 10.1),
        differentiated_optimum_fitness=Interval(9.4, 9.6),
    )
    assert result.direct_state == "BALANCE_IDENTIFIED"
    assert result.direct_gap.upper < 0
    assert result.decomposed_gap is None


def test_architecture_order_crossing_zero_stays_unresolved():
    result = classify_bounded_receipt(
        context_id="ctx-2",
        fitness_scale_id="seed_set",
        conflict_load=Interval(0.20, 0.30),
        shared_optimum_fitness=Interval(9.9, 10.1),
        differentiated_optimum_fitness=Interval(9.8, 10.2),
    )
    assert result.direct_state == "ARCHITECTURE_ORDER_UNRESOLVED"
    assert result.direct_gap.contains(0.0)


def test_bita_side_requires_positive_conflict_and_positive_direct_gap():
    result = classify_bounded_receipt(
        context_id="ctx-3",
        fitness_scale_id="seed_set",
        conflict_load=Interval(0.20, 0.30),
        shared_optimum_fitness=Interval(9.0, 9.1),
        differentiated_optimum_fitness=Interval(9.5, 9.6),
    )
    assert result.direct_state == "BITA_SIDE_IDENTIFIED"
    assert result.direct_gap.lower > 0


def test_optional_decomposition_reports_zero_compatible_bridge_residual():
    # Direct gap is [-0.22,-0.18].  sL-K is [-0.225,-0.175].
    result = classify_bounded_receipt(
        context_id="ctx-4",
        fitness_scale_id="seed_set",
        conflict_load=Interval(0.38, 0.42),
        shared_optimum_fitness=Interval(9.99, 10.01),
        differentiated_optimum_fitness=Interval(9.79, 9.81),
        decoupling=Interval(0.49, 0.51),
        architecture_cost=Interval(0.38, 0.42),
    )
    assert result.direct_state == "BALANCE_IDENTIFIED"
    assert result.bridge_zero_compatible is True
    assert result.bridge_residual.contains(0.0)


def test_incompatible_decomposition_is_not_silently_reconciled():
    result = classify_bounded_receipt(
        context_id="ctx-5",
        fitness_scale_id="seed_set",
        conflict_load=Interval(0.38, 0.42),
        shared_optimum_fitness=Interval(9.99, 10.01),
        differentiated_optimum_fitness=Interval(9.79, 9.81),
        decoupling=Interval(0.49, 0.51),
        architecture_cost=Interval(0.05, 0.07),
    )
    assert result.bridge_zero_compatible is False
    assert not result.bridge_residual.contains(0.0)


def test_bounded_receipt_requires_frozen_string_identifiers():
    kwargs = dict(
        conflict_load=Interval(0.2, 0.3),
        shared_optimum_fitness=Interval(9.9, 10.1),
        differentiated_optimum_fitness=Interval(9.4, 9.6),
    )
    for context_id, scale in ((None, "seed_set"), ("None", "seed_set"), ("ctx", "nan")):
        with pytest.raises(ValueError):
            classify_bounded_receipt(
                context_id=context_id,
                fitness_scale_id=scale,
                **kwargs,
            )

    normalized = classify_bounded_receipt(
        context_id="  ctx-6  ",
        fitness_scale_id=" seed_set ",
        **kwargs,
    )
    assert normalized.context_id == "ctx-6"
    assert normalized.fitness_scale_id == "seed_set"


def test_bounded_interval_rejects_nonfinite_and_reversed_bounds():
    with pytest.raises(ValueError):
        Interval(math.nan, 1.0)
    with pytest.raises(ValueError):
        Interval(0.0, math.inf)
    with pytest.raises(ValueError):
        Interval(2.0, 1.0)
    with pytest.raises(ValueError):
        Interval(10**10000, 10**10000)


def test_bounded_interval_normalizes_numeric_inputs_to_float():
    interval = Interval("0.2", "0.3")
    assert interval.lower == pytest.approx(0.2)
    assert interval.upper == pytest.approx(0.3)
    assert isinstance(interval.lower, float)
    assert isinstance(interval.upper, float)


def test_interval_membership_rejects_nonfinite_or_nonnumeric_queries():
    interval = Interval(0.0, 1.0)
    with pytest.raises(ValueError):
        interval.contains(math.nan)
    with pytest.raises(ValueError):
        interval.contains("not-a-number")
    with pytest.raises(ValueError):
        interval.contains(10**10000)

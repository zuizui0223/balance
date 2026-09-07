import pytest

from balance_domain.scope_depth import (
    compare_nested_scopes,
    envelope_reserve,
    fitness_depth,
    metric_scope_depth,
)


def test_scope_expansion_cannot_raise_envelope_reserve_or_fitness_depth():
    result = compare_nested_scopes(
        conflict_margin=0.8,
        old_reserves=[0.7, 1.1],
        added_reserves=[0.3, 2.0],
    )
    assert result.old_reserve == pytest.approx(0.7)
    assert result.new_reserve == pytest.approx(0.3)
    assert result.old_fitness_depth == pytest.approx(0.7)
    assert result.new_fitness_depth == pytest.approx(0.3)
    assert result.old_balance
    assert result.new_balance


def test_new_winning_alternative_can_destroy_balance_but_not_create_it():
    destroyed = compare_nested_scopes(
        conflict_margin=0.6,
        old_reserves=[0.4],
        added_reserves=[-0.2],
    )
    assert destroyed.old_balance
    assert not destroyed.new_balance

    still_not_balance = compare_nested_scopes(
        conflict_margin=0.6,
        old_reserves=[-0.1],
        added_reserves=[0.5],
    )
    assert not still_not_balance.old_balance
    assert not still_not_balance.new_balance


def test_dominated_addition_leaves_scope_depth_unchanged():
    result = compare_nested_scopes(
        conflict_margin=1.2,
        old_reserves=[0.55, 0.9],
        added_reserves=[0.8, 1.5],
    )
    assert result.new_reserve == pytest.approx(result.old_reserve)
    assert result.new_fitness_depth == pytest.approx(result.old_fitness_depth)


def test_metric_scope_depth_is_nonincreasing_when_boundary_set_expands():
    old_depth = metric_scope_depth([0.8, 0.6, 1.2])
    new_depth = metric_scope_depth([0.8, 0.6, 1.2, 0.35])
    assert new_depth <= old_depth
    assert new_depth == pytest.approx(0.35)


def test_helpers_fail_closed_on_empty_scope():
    with pytest.raises(ValueError):
        envelope_reserve([])
    with pytest.raises(ValueError):
        fitness_depth(1.0, [])
    with pytest.raises(ValueError):
        metric_scope_depth([])

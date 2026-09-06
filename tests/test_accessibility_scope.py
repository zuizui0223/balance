import pytest

from balance_domain.accessibility_scope import accessibility_scope_bounds


def test_robust_balance_requires_positive_reserve_even_under_possible_scope():
    result = accessibility_scope_bounds(
        conflict_load=0.8,
        reserve_definite=0.7,
        reserve_possible=0.3,
    )
    assert result.classification == "ROBUST_BALANCE"
    assert result.scope_fragility == pytest.approx(0.4)
    assert result.depth_lower == pytest.approx(0.3)
    assert result.depth_upper == pytest.approx(0.7)
    assert result.signed_margin_lower == pytest.approx(0.3)


def test_scope_unresolved_returns_signed_margin_not_balance_depth():
    result = accessibility_scope_bounds(
        conflict_load=0.8,
        reserve_definite=0.4,
        reserve_possible=-0.1,
    )
    assert result.classification == "ACCESSIBILITY_SCOPE_UNRESOLVED"
    assert result.scope_fragility == pytest.approx(0.5)
    assert result.signed_margin_lower == pytest.approx(-0.1)
    assert result.signed_margin_upper == pytest.approx(0.4)
    assert result.depth_lower is None
    assert result.depth_upper is None


def test_robust_non_balance_returns_no_depth():
    result = accessibility_scope_bounds(
        conflict_load=0.8,
        reserve_definite=-0.2,
        reserve_possible=-0.5,
    )
    assert result.classification == "ROBUST_NON_BALANCE"
    assert result.signed_margin_upper == pytest.approx(-0.2)
    assert result.depth_lower is None
    assert result.depth_upper is None


def test_no_positive_conflict_fails_before_architecture_scope():
    result = accessibility_scope_bounds(
        conflict_load=0.0,
        reserve_definite=0.5,
        reserve_possible=0.2,
    )
    assert result.classification == "NO_POSITIVE_CONFLICT"
    assert result.depth_lower is None
    assert result.depth_upper is None


def test_sch_facing_margin_can_make_depth_scope_invariant():
    result = accessibility_scope_bounds(
        conflict_load=0.1,
        reserve_definite=0.8,
        reserve_possible=0.3,
    )
    assert result.scope_fragility == pytest.approx(0.5)
    assert result.depth_lower == pytest.approx(0.1)
    assert result.depth_upper == pytest.approx(0.1)


def test_invalid_nested_reserve_order_fails_closed():
    with pytest.raises(ValueError):
        accessibility_scope_bounds(
            conflict_load=0.8,
            reserve_definite=0.2,
            reserve_possible=0.3,
        )

import pytest

from balance_domain.boundary import (
    analyze_two_margin_path,
    classify_two_margin_point,
    positive_support_monotone,
    two_margin_middle_position,
)


def test_boolean_margins_cannot_create_a_balance_point():
    with pytest.raises(ValueError, match="not boolean"):
        classify_two_margin_point(True, True)
    with pytest.raises(ValueError, match="not boolean"):
        classify_two_margin_point(1.0, True)
    with pytest.raises(ValueError, match="not boolean"):
        classify_two_margin_point(1.0, 1.0, tolerance=True)


def test_boolean_margins_cannot_create_a_middle_coordinate():
    with pytest.raises(ValueError, match="not boolean"):
        two_margin_middle_position(True, 1.0)
    with pytest.raises(ValueError, match="not boolean"):
        two_margin_middle_position(1.0, True)


def test_boolean_support_values_are_not_numeric_support_evidence():
    with pytest.raises(ValueError, match="not boolean"):
        positive_support_monotone([0.0, True, 1.0])
    with pytest.raises(ValueError, match="not boolean"):
        positive_support_monotone([0.0, 1.0], tolerance=False)


def test_boolean_path_coordinates_or_margins_fail_closed():
    with pytest.raises(ValueError, match="not boolean"):
        analyze_two_margin_path([0.0, True], [1.0, 1.0], [1.0, 1.0])
    with pytest.raises(ValueError, match="not boolean"):
        analyze_two_margin_path([0.0, 1.0], [1.0, True], [1.0, 1.0])
    with pytest.raises(ValueError, match="not boolean"):
        analyze_two_margin_path([0.0, 1.0], [1.0, 1.0], [1.0, True])

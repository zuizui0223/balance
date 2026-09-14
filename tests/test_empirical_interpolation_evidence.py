import pytest

from balance_domain.definition_concordance import (
    analyze_definitions,
    compare_definition_brackets,
    crossing_bracket,
)
from balance_domain.depth_path import deepest_middle_point


def test_deepest_point_rejects_boolean_path_evidence():
    valid = dict(
        environment=[0.0, 1.0, 2.0],
        conflict=[0.2, 0.5, 0.8],
        reserve=[0.8, 0.5, 0.2],
    )
    for field in valid:
        malformed = {name: list(values) for name, values in valid.items()}
        malformed[field][1] = True
        with pytest.raises(ValueError, match="boolean"):
            deepest_middle_point(**malformed)


def test_definition_crossing_rejects_boolean_numeric_evidence():
    contexts = ("A", "B")
    margins = {"A": -1.0, "B": 1.0}

    with pytest.raises(ValueError, match="boolean"):
        crossing_bracket("definition", contexts, {"A": True, "B": 1.0})
    with pytest.raises(ValueError, match="boolean"):
        crossing_bracket(
            "definition",
            contexts,
            margins,
            context_values={"A": True, "B": 1.0},
        )
    with pytest.raises(ValueError, match="boolean"):
        crossing_bracket("definition", contexts, margins, tolerance=True)


def test_definition_concordance_rejects_placeholder_labels():
    margins = {"A": -1.0, "B": 1.0}
    for bad in ("None", "null", "nan", "REQUIRED_BEFORE_USE"):
        with pytest.raises(ValueError, match="frozen"):
            crossing_bracket(bad, ("A", "B"), margins)
        with pytest.raises(ValueError, match="frozen"):
            crossing_bracket("definition", (bad, "B"), {bad: -1.0, "B": 1.0})


def test_numeric_concordance_tolerance_cannot_be_boolean():
    contexts = ("A", "B")
    context_values = {"A": 0.0, "B": 1.0}
    first = crossing_bracket(
        "first",
        contexts,
        {"A": -1.0, "B": 1.0},
        context_values=context_values,
    )
    second = crossing_bracket(
        "second",
        contexts,
        {"A": -2.0, "B": 2.0},
        context_values=context_values,
    )
    with pytest.raises(ValueError, match="boolean"):
        compare_definition_brackets((first, second), contexts, numeric_tolerance=True)


def test_valid_definition_analysis_remains_unchanged_in_kind():
    result = analyze_definitions(
        ("A", "B", "C"),
        {
            "first": {"A": -1.0, "B": 1.0, "C": 2.0},
            "second": {"A": -2.0, "B": 2.0, "C": 3.0},
        },
        context_values={"A": 0.0, "B": 1.0, "C": 2.0},
        numeric_tolerance=0.1,
    )
    assert result.classification == "SAME_NUMERIC_CRITICAL_CONTEXT_WITHIN_TOLERANCE"

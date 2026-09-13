import json
import math
from pathlib import Path

import pytest

from balance_domain.definition_concordance import (
    CrossingBracket,
    analyze_definitions,
    compare_definition_brackets,
    crossing_bracket,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "empirical" / "peucedanum" / "PEUCEDANUM_CRITICAL_DEFINITIONS_V1.json"


def _fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_peucedanum_three_definitions_share_hl_hc_coarse_bracket():
    data = _fixture()
    result = analyze_definitions(data["ordered_contexts"], data["definitions"])
    assert result.classification == "SAME_COARSE_CRITICAL_BRACKET"
    assert result.common_index_interval == (1, 2)
    assert result.common_contexts == ("HL", "HC")
    assert all(b.left_context == "HL" and b.right_context == "HC" for b in result.brackets)


def test_peucedanum_proxy_point_crossings_are_not_identical():
    data = _fixture()
    contexts = ["HL", "HC"]
    context_values = data["conditional_predator_egg_proxy"]
    definitions = {
        name: {c: margins[c] for c in contexts}
        for name, margins in data["definitions"].items()
    }
    result = analyze_definitions(
        contexts,
        definitions,
        context_values={"HL": context_values["HL"], "HC": context_values["HC"]},
        numeric_tolerance=0.1,
    )
    assert result.classification == "PARALLEL_NUMERIC_CRITICAL_CONTEXTS"
    points = {b.definition: b.numeric_critical_context for b in result.brackets}
    assert math.isclose(points["final_fruit_selection_gradient_beta"], 2.422539682539682)
    assert math.isclose(points["final_fruit_selection_differential_S"], 2.24)
    assert math.isclose(points["female_gain_exponent_minus_one"], 1.9507142857142856)


def test_ordered_labels_do_not_create_numeric_critical_point():
    data = _fixture()
    result = analyze_definitions(data["ordered_contexts"], data["definitions"])
    assert all(b.numeric_critical_context is None for b in result.brackets)


def test_multiple_crossings_fail_closed():
    with pytest.raises(ValueError):
        analyze_definitions(
            ["A", "B", "C", "D"],
            {
                "unstable": {"A": -1, "B": 1, "C": -1, "D": 1},
                "single": {"A": -1, "B": -1, "C": 1, "D": 1},
            },
        )


def test_extreme_finite_margins_do_not_overflow_crossing_fraction():
    bracket = crossing_bracket(
        "extreme",
        ["L", "R"],
        {"L": -1.0e308, "R": 1.0e308},
        context_values={"L": 0.0, "R": 10.0},
    )
    assert bracket.numeric_critical_context == pytest.approx(5.0)


def test_numeric_tolerance_requires_numeric_context_for_every_definition():
    with pytest.raises(ValueError, match="numeric critical context for every definition"):
        analyze_definitions(
            ["A", "B"],
            {
                "one": {"A": -1.0, "B": 1.0},
                "two": {"A": -2.0, "B": 1.0},
            },
            numeric_tolerance=0.1,
        )


def test_direct_bracket_comparison_rejects_context_provenance_mismatch():
    good = crossing_bracket(
        "good",
        ["A", "B"],
        {"A": -1.0, "B": 1.0},
    )
    forged = CrossingBracket(
        definition="forged",
        left_context="WRONG",
        right_context="B",
        left_index=0,
        right_index=1,
        left_margin=-1.0,
        right_margin=1.0,
        exact_context=False,
        numeric_critical_context=None,
        status="UNIQUE_ADJACENT_ZERO_CROSSING",
    )
    with pytest.raises(ValueError, match="left_context"):
        compare_definition_brackets((good, forged), ["A", "B"])


def test_numeric_gap_overflow_fails_closed_instead_of_classifying_parallel():
    left = CrossingBracket(
        definition="left",
        left_context="A",
        right_context="B",
        left_index=0,
        right_index=1,
        left_margin=-1.0,
        right_margin=1.0,
        exact_context=False,
        numeric_critical_context=-1.0e308,
        status="UNIQUE_ADJACENT_ZERO_CROSSING",
    )
    right = CrossingBracket(
        definition="right",
        left_context="A",
        right_context="B",
        left_index=0,
        right_index=1,
        left_margin=-1.0,
        right_margin=1.0,
        exact_context=False,
        numeric_critical_context=1.0e308,
        status="UNIQUE_ADJACENT_ZERO_CROSSING",
    )
    with pytest.raises(ValueError, match="max_pairwise_numeric_gap"):
        compare_definition_brackets((left, right), ["A", "B"], numeric_tolerance=1.0)

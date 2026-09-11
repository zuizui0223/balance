import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "assemble_balance_manuscript.py"


def _module():
    spec = importlib.util.spec_from_file_location("balance_manuscript", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_manuscript_contains_all_sections_in_order():
    text = _module().build_manuscript()
    headings = [
        "## Abstract",
        "## Introduction",
        "## Theory",
        "## Empirical synthesis methods",
        "## Results",
        "## Discussion",
    ]
    positions = [text.index(h) for h in headings]
    assert positions == sorted(positions)


def test_manuscript_preserves_core_sandwiched_regime_and_claim_ceiling():
    text = _module().build_manuscript()
    assert "L > 0" in text
    assert "Phi < 0" in text
    assert "W_D* - W_S* < 0" in text
    assert "direct-worldline reserve therefore remains empty" in text
    assert "does not identify direct BALANCE occupancy from unmatched systems" in text


def test_positive_selected_q1b_pool_is_explicitly_conditional_not_general_meta_analysis():
    text = _module().build_manuscript()
    assert "positive admission depended on the observed conflict pattern" in text
    assert "conditional on positive Q1B admission" in text
    assert "not an unbiased meta-analytic estimate" in text
    assert "not a meta-analysis of all design-eligible systems" in text
    assert "positive-selected Q1B pool" in text


def test_manuscript_keeps_focal_validation_last():
    text = _module().build_manuscript()
    assert "Direct focal worldline validation is intentionally retained as the final unresolved empirical layer" in text
    assert "Only then does a focal experiment have a well-defined role" in text
    assert "final-stage matched worldline test" in text


def test_manuscript_exposes_all_three_current_figures():
    text = _module().build_manuscript()
    assert "BALANCE_FIGURE1_THEORY_EMPIRICAL_SPINE_V1.svg" in text
    assert "BALANCE_FIGURE2_Q1B_QUANTITATIVE_V1.svg" in text
    assert "BALANCE_FIGURE3_REALITY_PATTERN_MAP_V1.svg" in text

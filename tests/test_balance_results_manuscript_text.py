from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "docs" / "BALANCE_RESULTS_MANUSCRIPT_TEXT_V1.md"


def _text():
    return RESULTS.read_text(encoding="utf-8")


def test_results_reports_q1b_recurrence_and_conditional_pool_without_general_mean_claim():
    text = _text()
    assert "three independent biological systems" in text
    assert "conditional summaries of effect magnitude and heterogeneity among admitted positives" in text
    assert "not an unbiased meta-analytic estimate across all design-eligible factorial systems" in text
    assert "all four conditional pooled confidence intervals included zero" in text
    assert "evidence that the conflict pattern recurs comes from recovery of the registered positive pattern in three independent biological clusters" in text
    assert "I2 = 62.7%" in text
    assert "I2 = 65.7%" in text


def test_results_reports_boundary_structure_and_broader_ledger():
    text = _text()
    assert "17 independent biological clusters" in text
    assert "Nine clusters expressed middle-regime signatures" in text
    assert "Seven were classified as conflict without splitting" in text
    assert "two boundary-crossing clusters" in text
    assert "five unresolved clusters" in text


def test_results_keeps_direct_balance_occupancy_unidentified():
    text = _text()
    assert "direct-worldline reserve therefore remains empty" in text
    assert "does not identify `W_S*`, `W_D*`, `rho = W_S* - W_D*`, `Phi`, `xi`, or `d_B`" in text
    assert "final-stage matched worldline test" in text

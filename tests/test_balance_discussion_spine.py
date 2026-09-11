from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISCUSSION = ROOT / "docs" / "BALANCE_DISCUSSION_SPINE_V1.md"


def _text():
    return DISCUSSION.read_text(encoding="utf-8")


def test_discussion_keeps_conflict_separate_from_balance_occupancy():
    text = _text()
    assert "Conflict is a prerequisite; persistence is the BALANCE phenomenon" in text
    assert "Q1B layer only establishes the prerequisite" in text
    assert "does not identify `W_S*`, `W_D*`, `rho = W_S* - W_D*`, `Phi`, `xi`, or `d_B`" in text


def test_discussion_places_focal_experiment_last():
    text = _text()
    assert "not a reason to move the empirical experiment to the front of the paper" in text
    assert "Only then does a focal experiment have a well-defined role" in text


def test_discussion_preserves_sch_balance_bita_sequence():
    text = _text()
    assert "SCH asks when one coordinate is pulled" in text
    assert "BALANCE asks when that conflict persists without immediate splitting" in text
    assert "BITA asks when differentiation or dimensional release becomes favourable" in text


def test_discussion_prohibits_overclaiming():
    text = _text()
    assert "natural prevalence from the screened literature counts" in text
    assert "positive-selected Q1B pool is an unbiased meta-analysis" in text
    assert "a universal non-zero Q1B mean effect at `k = 3`" in text
    assert "literature recurrence alone proves a focal natural system occupies BALANCE" in text

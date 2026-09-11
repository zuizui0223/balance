from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEORY = ROOT / "docs" / "BALANCE_THEORY_MANUSCRIPT_TEXT_V1.md"


def _text():
    return THEORY.read_text(encoding="utf-8")


def test_theory_defines_exact_sandwich_and_direct_worldline_routes():
    text = _text()
    assert "B = {L>0} ∩ {Phi<0}" in text
    assert "0 < L < K/s" in text
    assert "Delta_W < 0" in text
    assert "Delta_W = Phi = sL-K" in text


def test_theory_preserves_depth_and_deepest_point_results():
    text = _text()
    assert "xi = L/(L+rho)" in text
    assert "d_B = min(L,rho)" in text
    assert "L_deep = K/(1+s)" in text
    assert "xi_deep = 1/2" in text
    assert "W_B/W_S = 1/s" in text


def test_theory_preserves_path_and_hysteresis_results():
    text = _text()
    assert "BALANCE -> DIFFERENTIATION -> BALANCE" in text
    assert "-C_DS/T <= Phi <= C_SD/T" in text
    assert "(C_SD+C_DS)/T" in text
    assert "not itself identical to the static BALANCE core" in text


def test_theory_preserves_concordance_falsification_logic():
    text = _text()
    assert "delta_parallel = Delta_W-(sL-K)" in text
    assert "delta_parallel=0" in text
    assert "empirical falsification route" in text

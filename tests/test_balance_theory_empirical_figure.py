import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_balance_theory_empirical_figure.py"


def _module():
    spec = importlib.util.spec_from_file_location("balance_fig", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_flagship_figure_uses_frozen_counts_and_keeps_direct_gap_empty():
    svg = _module().build_svg()
    assert "strict positives = 3" in svg
    assert "design-matched negatives = 2" in svg
    assert "recurrence = 3 independent positives" in svg
    assert "pool = conditional positive-case summary" in svg
    assert "pattern-ledger clusters = 17" in svg
    assert "middle-regime signatures = 9" in svg
    assert "0 direct matched receipts" in svg
    assert "W*S, W*D, ρ, Φ, ξ, dB not identified" in svg


def test_flagship_figure_keeps_boundaries_outside_strict_q1b():
    svg = _module().build_svg()
    assert "estimand boundaries = 2" in svg
    assert "attribution failures = 1" in svg
    assert "rather than inflate k" in svg
    assert "Q1B pool ≠ design-wide mean or BALANCE occupancy" in svg


def test_flagship_figure_freezes_moderator_gate():
    svg = _module().build_svg()
    assert "moderator meta-regression prohibited until k≥5" in svg
    assert "conditional positive-case summary: k=3" in svg

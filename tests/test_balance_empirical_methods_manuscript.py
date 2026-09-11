from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METHODS = ROOT / "docs" / "BALANCE_EMPIRICAL_METHODS_MANUSCRIPT_TEXT_V1.md"


def _text():
    return METHODS.read_text(encoding="utf-8")


def test_methods_places_pattern_recovery_before_direct_validation():
    text = _text()
    assert "mathematical mechanism" in text
    assert "source-adjudicated pattern ledger" in text
    assert "residual direct-identification gap" in text
    assert "reserved for this final identification problem" in text


def test_methods_uses_biological_cluster_as_replication_unit():
    text = _text()
    assert "independent biological cluster" in text
    assert "not the publication, population, site, year, treatment cell, or measured trait" in text
    assert "multiple traits from one cluster could not inflate the independent-cluster count" in text


def test_methods_preserves_q1b_effect_ready_contract():
    text = _text()
    for phrase in [
        "pollinator and antagonist roles were biologically identified",
        "same defined trait coordinate",
        "common reproductive-fitness interpretation",
        "joint uncertainty",
        "We did not cherry-pick",
    ]:
        assert phrase in text


def test_methods_reports_first_pool_and_moderator_gate():
    text = _text()
    assert "DerSimonian–Laird random-effects model" in text
    assert "modified Knapp–Hartung interval with `df=2`" in text
    assert "`k=3`" in text
    assert "At `k=3` or `k=4`, moderators are descriptive only" in text
    assert "only at `k>=5`" in text


def test_methods_explicitly_rejects_prevalence_and_direct_worldline_backfill():
    text = _text()
    assert "rather than an estimate of natural prevalence" in text
    assert "does not identify direct BALANCE occupancy from unmatched systems" in text
    assert "did not estimate `W_S*`, `W_D*`, `rho`, `Phi`, `xi`, or `d_B`" in text

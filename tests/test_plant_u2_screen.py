from pathlib import Path

from balance_domain.plant_u2_screen import (
    build_u2_conflict_screen_readout,
    load_u2_conflict_screen,
)


ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv"


def test_u2_conflict_screen_contains_all_review_groups():
    rows = load_u2_conflict_screen(SCREEN)
    assert len(rows) == 22
    assert len({r["dependency_group"] for r in rows}) == 22


def test_u2_strict_screen_recovers_direct_conflict_without_promoting_all_review_cases():
    readout = build_u2_conflict_screen_readout(SCREEN)
    assert readout["n_positive_conflict"] == 8
    assert readout["n_no_demonstrated_conflict"] == 3
    assert readout["n_unresolved_candidate"] == 11
    assert readout["screen_decision_counts"] == {
        "FAIL_CONFLICT_GATE": 3,
        "HOLD_FOR_FULL_TEXT": 11,
        "PASS_CONFLICT_GATE": 8,
    }


def test_pontederia_cordata_is_retained_as_explicit_null():
    rows = load_u2_conflict_screen(SCREEN)
    row = next(r for r in rows if r["dependency_group"] == "Pontederia_cordata")
    assert row["conflict_status"] == "NO_DEMONSTRATED_CONFLICT"
    assert row["reason_code"] == "EXPLICIT_INTERFERENCE_NULL"


def test_mimulus_is_direct_positive_conflict():
    rows = load_u2_conflict_screen(SCREEN)
    row = next(r for r in rows if r["dependency_group"] == "Mimulus_aurantiacus")
    assert row["conflict_status"] == "POSITIVE"
    assert row["screen_decision"] == "PASS_CONFLICT_GATE"


def test_architecture_only_historical_heteranthery_is_not_promoted():
    rows = load_u2_conflict_screen(SCREEN)
    for dep in ("Solanum_rostratum_historical", "Chamaecrista_fasciculata_historical"):
        row = next(r for r in rows if r["dependency_group"] == dep)
        assert row["conflict_status"] == "UNRESOLVED_CANDIDATE"
        assert row["screen_decision"] == "HOLD_FOR_FULL_TEXT"

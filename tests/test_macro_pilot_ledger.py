from collections import Counter
from pathlib import Path

from balance_domain.macro_ledger import build_macro_readout, load_macro_ledger


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data" / "BALANCE_MACRO_PILOT_LEDGER_V1.csv"


def test_macro_pilot_ledger_satisfies_schema_and_stays_screening_only():
    rows = load_macro_ledger(PILOT)
    assert len(rows) == 55
    assert all(r["adjudication_status"] == "SCREENED" for r in rows)
    assert all(r["primary_model_eligible"] == "false" for r in rows)


def test_macro_pilot_has_all_three_registered_strata():
    rows = load_macro_ledger(PILOT)
    domains = {r["domain"] for r in rows}
    assert domains == {
        "plant_reproductive",
        "animal_morphology",
        "molecular_gene",
    }


def test_macro_pilot_contains_positive_and_negative_conflict_screens():
    readout = build_macro_readout(PILOT)
    conflict = readout["conflict_status_counts"]
    assert conflict["POSITIVE"] == 32
    assert conflict["NO_DEMONSTRATED_CONFLICT"] == 11
    assert conflict["ALIGNED_NO_CONFLICT"] == 1
    assert conflict["UNRESOLVED"] == 11


def test_macro_pilot_preserves_both_structural_outcomes():
    rows = load_macro_ledger(PILOT)
    logical_candidates = [
        r
        for r in rows
        if r["conflict_status"] == "POSITIVE"
        and r["structural_differentiation"] in {"true", "false"}
    ]
    assert len(logical_candidates) == 31
    outcomes = {r["structural_differentiation"] for r in logical_candidates}
    assert outcomes == {"true", "false"}


def test_coverage_repair_breaks_initial_domain_outcome_bottleneck():
    rows = load_macro_ledger(PILOT)
    logical_candidates = [
        r
        for r in rows
        if r["conflict_status"] == "POSITIVE"
        and r["structural_differentiation"] in {"true", "false"}
    ]
    structural_by_domain = Counter(
        r["domain"]
        for r in logical_candidates
        if r["structural_differentiation"] == "true"
    )
    assert structural_by_domain == {
        "animal_morphology": 5,
        "molecular_gene": 4,
        "plant_reproductive": 5,
    }

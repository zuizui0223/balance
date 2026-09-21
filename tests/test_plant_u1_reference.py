from pathlib import Path

from balance_domain.plant_u1_reference import (
    build_u1_reference_readout,
    load_u1_reference_coverage,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U1_REFERENCE_COVERAGE_V1.csv"


def test_u1_reference_coverage_validates():
    rows = load_u1_reference_coverage(LEDGER)
    assert len(rows) == 7


def test_no_article_only_candidate_can_close_full47():
    readout = build_u1_reference_readout(LEDGER)
    assert readout["n_canonical_supplement_only_taxa"] == 0
    assert readout["full47_supplement_gap_closed"] is False
    assert readout["n_pending_supplement_confirmation"] == 5


def test_leading_nonnetwork_candidates_are_explicit_but_not_promoted():
    readout = build_u1_reference_readout(LEDGER)
    assert readout["leading_nonnetwork_candidates"] == [
        "Alstroemeria exerens",
        "Eichhornia crassipes",
        "Nemophila menziesii",
    ]

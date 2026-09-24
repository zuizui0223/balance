from pathlib import Path
from balance_domain.plant_u1_reference import build_u1_reference_readout, load_u1_reference_coverage

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U1_REFERENCE_COVERAGE_V1.csv"

def test_u1_reference_coverage_validates():
    assert len(load_u1_reference_coverage(LEDGER)) == 9

def test_direct_figshare_reconciliation_closes_full47_gap():
    out = build_u1_reference_readout(LEDGER)
    assert out["n_canonical_supplement_only_taxa"] == 3
    assert out["canonical_supplement_only_taxa"] == ["Eichhornia crassipes","Nemophila menziesii","Ruellia nudiflora"]
    assert out["n_pending_supplement_confirmation"] == 0
    assert out["full47_supplement_gap_closed"] is True

def test_false_candidates_are_retained_as_direct_exclusions():
    out = build_u1_reference_readout(LEDGER)
    assert out["n_direct_reconciliation_excluded"] == 4
    assert out["direct_reconciliation_excluded_taxa"] == ["Alstroemeria exerens","Cucurbita pepo ssp. texana","Mimulus guttatus","Mimulus luteus"]
    assert out["leading_nonnetwork_candidates"] == []

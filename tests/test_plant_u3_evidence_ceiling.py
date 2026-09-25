from pathlib import Path

from balance_domain.plant_u3_evidence_ceiling import (
    build_u3_evidence_ceiling_readout,
    load_u3_evidence_ceilings,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U3_EVIDENCE_CEILING_V1.csv"


def test_u3_public_evidence_ceiling_has_four_frozen_unresolved_targets():
    rows = load_u3_evidence_ceilings(LEDGER)
    assert len(rows) == 4
    assert all(r["qualifying_direct_evidence"] is False for r in rows)
    assert all(r["status"] == "PUBLIC_RETRIEVAL_CEILING_FROZEN_UNRESOLVED" for r in rows)


def test_u3_public_retrieval_is_no_longer_an_open_development_gate():
    out = build_u3_evidence_ceiling_readout(LEDGER)
    assert out["public_retrieval_ceiling_frozen"] is True
    assert out["retrieval_open"] is False
    assert out["n_frozen_unresolved"] == 4
    assert out["taxa_requiring_new_direct_or_empirical_evidence"] == [
        "Monochoria australasica",
        "Monochoria cyanea",
        "Osbeckia chinensis",
        "Senna covesii",
    ]


def test_ceiling_is_not_misread_as_biological_absence():
    out = build_u3_evidence_ceiling_readout(LEDGER)
    assert "not_biological_absence" in out["claim_ceiling"]

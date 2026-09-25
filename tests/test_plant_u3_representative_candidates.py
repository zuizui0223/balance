from pathlib import Path

import csv
import pytest

from balance_domain.plant_u3_representative_candidates import (
    FIELDS,
    build_u3_representative_candidate_readout,
    load_u3_representative_candidate_audit,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U3_REPRESENTATIVE_CANDIDATE_AUDIT_V1.csv"


def test_current_candidate_audit_keeps_all_three_families_open():
    rows = load_u3_representative_candidate_audit(LEDGER)
    out = build_u3_representative_candidate_readout(LEDGER)
    assert len(rows) == 5
    assert out["selection_status_counts"] == {"OPEN": 2, "REJECTED": 3}
    assert out["open_families"] == ["Bixaceae", "Malvaceae", "Scrophulariaceae"]
    assert out["representative_identity_closed"] is False


def test_sparrmannia_is_not_promoted_from_sterile_vs_fertile_differentiation():
    rows = load_u3_representative_candidate_audit(LEDGER)
    row = next(r for r in rows if r["candidate_taxon"] == "Sparrmannia africana")
    assert row["taxonomy_status"] == "PASS"
    assert row["heteranthery_evidence_status"] == "CONFLICT"
    assert row["selection_status"] == "OPEN"
    assert "STERILE_OUTER_SET" in row["blocker"]


def test_cochlospermum_is_pre2010_supported_but_identity_stays_open():
    rows = load_u3_representative_candidate_audit(LEDGER)
    row = next(r for r in rows if r["candidate_taxon"] == "Cochlospermum vitifolium")
    assert row["taxonomy_status"] == "PASS"
    assert row["pre2010_evidence_status"] == "PASS"
    assert row["heteranthery_evidence_status"] == "PARTIAL"
    assert row["table_s1_linkage_status"] == "UNRESOLVED"
    assert row["selection_status"] == "OPEN"


def test_historical_scrophulariaceae_candidates_fail_apg3_guard():
    rows = load_u3_representative_candidate_audit(LEDGER)
    by_taxon = {r["candidate_taxon"]: r for r in rows}
    assert by_taxon["Agalinis spp."]["selection_status"] == "REJECTED"
    assert by_taxon["Pedicularis spp."]["selection_status"] == "REJECTED"
    assert by_taxon["Torenia spp."]["selection_status"] == "REJECTED"


def test_selected_candidate_requires_exact_or_independent_pre2010_evidence(tmp_path):
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    target = next(r for r in rows if r["candidate_taxon"] == "Cochlospermum vitifolium")
    target["selection_status"] = "SELECTED"
    target["blocker"] = "NONE"
    path = tmp_path / "audit.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="SELECTED requires exact Table S1 linkage"):
        load_u3_representative_candidate_audit(path)

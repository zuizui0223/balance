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
    assert len(rows) == 8
    assert out["selection_status_counts"] == {"OPEN": 4, "REJECTED": 4}
    assert out["open_families"] == ["Bixaceae", "Malvaceae", "Scrophulariaceae"]
    assert out["representative_identity_closed"] is False


def test_review_unique_guard_applies_only_to_malvaceae():
    rows = load_u3_representative_candidate_audit(LEDGER)
    by_family = {}
    for row in rows:
        by_family.setdefault(row["family"], set()).add(row["review_uniqueness_status"])
    assert by_family["Malvaceae"] == {"SINGLE_SPECIES_REPORTED"}
    assert by_family["Bixaceae"] == {"MULTIPLE_OR_UNSPECIFIED"}
    assert by_family["Scrophulariaceae"] == {"MULTIPLE_OR_UNSPECIFIED"}


def test_strongest_species_level_open_candidates_are_amoreuxia_and_diascia():
    out = build_u3_representative_candidate_readout(LEDGER)
    assert out["strongest_open_candidates"]["Bixaceae"] == ["Amoreuxia palmatifida"]
    assert out["strongest_open_candidates"]["Scrophulariaceae"] == ["Diascia anastrepta"]
    assert out["strongest_open_candidates"]["Malvaceae"] == []


def test_sparrmannia_is_explicitly_rejected_as_pollen_mimic_staminode_false_positive():
    rows = load_u3_representative_candidate_audit(LEDGER)
    row = next(r for r in rows if r["candidate_taxon"] == "Sparrmannia africana")
    assert row["heteranthery_evidence_status"] == "NEGATIVE"
    assert row["selection_status"] == "REJECTED"
    assert "NO_TWO_FERTILE_STAMEN_TYPES" in row["blocker"]


def test_pseudocorchorus_is_strong_lineage_clue_but_not_species_resolution():
    rows = load_u3_representative_candidate_audit(LEDGER)
    row = next(r for r in rows if r["candidate_taxon"] == "Pseudocorchorus spp.")
    assert row["taxonomy_status"] == "PASS"
    assert row["heteranthery_evidence_status"] == "PARTIAL"
    assert row["pre2010_evidence_status"] == "PASS"
    assert row["review_uniqueness_status"] == "SINGLE_SPECIES_REPORTED"
    assert row["selection_status"] == "OPEN"
    assert "EXACT_SPECIES" in row["blocker"]


def test_amoreuxia_has_pre2010_two_stamen_set_evidence_but_not_identity():
    rows = load_u3_representative_candidate_audit(LEDGER)
    row = next(r for r in rows if r["candidate_taxon"] == "Amoreuxia palmatifida")
    assert row["taxonomy_status"] == "PASS"
    assert row["heteranthery_evidence_status"] == "PASS"
    assert row["pre2010_evidence_status"] == "PASS"
    assert row["table_s1_linkage_status"] == "UNRESOLVED"
    assert row["selection_status"] == "OPEN"


def test_diascia_has_direct_pre2010_heteranthery_but_not_review_identity():
    rows = load_u3_representative_candidate_audit(LEDGER)
    row = next(r for r in rows if r["candidate_taxon"] == "Diascia anastrepta")
    assert row["taxonomy_status"] == "PASS"
    assert row["heteranthery_evidence_status"] == "PASS"
    assert row["pre2010_evidence_status"] == "PASS"
    assert row["selection_status"] == "OPEN"
    assert "Manning_Brothers_1986" in row["source_id"]


def test_nonunique_family_cannot_select_strong_candidate_without_table_link(tmp_path):
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    target = next(r for r in rows if r["candidate_taxon"] == "Diascia anastrepta")
    target["selection_status"] = "SELECTED"
    target["blocker"] = "NONE"
    path = tmp_path / "audit.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="review-unique species"):
        load_u3_representative_candidate_audit(path)


def test_historical_scrophulariaceae_false_candidates_remain_rejected():
    rows = load_u3_representative_candidate_audit(LEDGER)
    by_taxon = {r["candidate_taxon"]: r for r in rows}
    assert by_taxon["Agalinis spp."]["selection_status"] == "REJECTED"
    assert by_taxon["Pedicularis spp."]["selection_status"] == "REJECTED"
    assert by_taxon["Torenia spp."]["selection_status"] == "REJECTED"

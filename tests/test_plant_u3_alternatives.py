from pathlib import Path

import csv
import pytest

from balance_domain.plant_u3_alternatives import (
    FIELDS,
    build_u3_control_alternatives_readout,
    load_u3_control_alternatives,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
ALTS = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ALTERNATIVES_V1.csv"


def test_real_u3_alternative_registry_keeps_search_open():
    rows = load_u3_control_alternatives(ALTS, CASES, U3)
    out = build_u3_control_alternatives_readout(ALTS, CASES, U3)
    assert len(rows) == 15
    assert out["status_counts"] == {"OPEN": 9, "REJECTED": 6}
    assert out["n_screened"] == 0
    assert out["candidate_search_closed"] is False
    assert set(out["open_case_taxa"]) == {
        "Monochoria korsakowii",
        "Monochoria vaginalis",
        "Senna alata",
        "Senna bicapsularis",
    }


def test_closest_eligible_search_is_separate_from_phylogenetic_proximity():
    rows = load_u3_control_alternatives(ALTS, CASES, U3)
    armata = next(r for r in rows if r["candidate_control"] == "Senna armata")
    assert armata["phylogenetic_proximity_status"] == "PASS"
    assert armata["closest_eligible_search_status"] == "OPEN"
    assert armata["selection_status"] == "OPEN"


def test_monochoria_cyanea_is_explicitly_in_closest_control_search():
    rows = load_u3_control_alternatives(ALTS, CASES, U3)
    cyanea = [r for r in rows if r["candidate_control"] == "Monochoria cyanea"]
    assert {r["case_taxon"] for r in cyanea} == {
        "Monochoria korsakowii",
        "Monochoria vaginalis",
    }
    assert all(r["heteranthery_absence_status"] == "PASS" for r in cyanea)
    assert all(r["animal_pollination_status"] == "OPEN" for r in cyanea)
    assert all(r["phylogenetic_proximity_status"] == "OPEN" for r in cyanea)
    assert all(r["closest_eligible_search_status"] == "OPEN" for r in cyanea)
    assert all(r["selection_status"] == "OPEN" for r in cyanea)


def test_same_clade_senna_alata_candidates_block_clade_jump():
    rows = load_u3_control_alternatives(ALTS, CASES, U3)
    for taxon in ("Senna martiana", "Senna pleurocarpa"):
        row = next(r for r in rows if r["candidate_control"] == taxon)
        assert row["case_taxon"] == "Senna alata"
        assert row["phylogenetic_proximity_status"] == "PASS"
        assert row["heteranthery_absence_status"] == "OPEN"
        assert row["closest_eligible_search_status"] == "OPEN"
        assert row["selection_status"] == "OPEN"

    atomaria = next(r for r in rows if r["candidate_control"] == "Senna atomaria")
    assert atomaria["heteranthery_absence_status"] == "PASS"
    assert atomaria["phylogenetic_proximity_status"] == "OPEN"
    assert atomaria["selection_status"] == "OPEN"


def test_rejected_senna_surattensis_cannot_reenter_as_open():
    rows = load_u3_control_alternatives(ALTS, CASES, U3)
    surattensis = [r for r in rows if r["candidate_control"] == "Senna surattensis"]
    assert len(surattensis) == 2
    assert all(r["heteranthery_absence_status"] == "FAIL" for r in surattensis)
    assert all(r["selection_status"] == "REJECTED" for r in surattensis)


def test_senna_rugosa_is_rejected_after_primary_morphology_audit():
    rows = load_u3_control_alternatives(ALTS, CASES, U3)
    rugosa = [r for r in rows if r["candidate_control"] == "Senna rugosa"]
    assert len(rugosa) == 2
    assert all(r["heteranthery_absence_status"] == "FAIL" for r in rugosa)
    assert all(r["selection_status"] == "REJECTED" for r in rugosa)
    assert all("Irwin_Barneby_1982" in r["source_id"] for r in rugosa)


def test_close_senna_candidates_are_rejected_when_heteranthery_persists():
    rows = load_u3_control_alternatives(ALTS, CASES, U3)
    siamea = next(r for r in rows if r["candidate_control"] == "Senna siamea")
    assert siamea["case_taxon"] == "Senna alata"
    assert siamea["phylogenetic_proximity_status"] == "PASS"
    assert siamea["heteranthery_absence_status"] == "FAIL"
    assert siamea["selection_status"] == "REJECTED"

    corymbosa = next(r for r in rows if r["candidate_control"] == "Senna corymbosa")
    assert corymbosa["case_taxon"] == "Senna bicapsularis"
    assert corymbosa["phylogenetic_proximity_status"] == "PASS"
    assert corymbosa["closest_eligible_search_status"] == "PASS"
    assert corymbosa["heteranthery_absence_status"] == "FAIL"
    assert corymbosa["selection_status"] == "REJECTED"


def test_vii_b_contains_biologically_eligible_candidate_but_tiebreak_stays_open():
    rows = load_u3_control_alternatives(ALTS, CASES, U3)
    covesii = next(r for r in rows if r["candidate_control"] == "Senna covesii")
    assert covesii["case_taxon"] == "Senna bicapsularis"
    assert covesii["heteranthery_absence_status"] == "PASS"
    assert covesii["animal_pollination_status"] == "PASS"
    assert covesii["phylogenetic_proximity_status"] == "PASS"
    assert covesii["closest_eligible_search_status"] == "OPEN"
    assert covesii["selection_status"] == "OPEN"

    out = build_u3_control_alternatives_readout(ALTS, CASES, U3)
    assert out["n_biological_gates_pass_closest_search_open"] == 1
    assert out["biological_pass_but_unselected_candidates"] == ["Senna covesii"]


def _read_rows():
    with ALTS.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_open_candidate_cannot_hide_failed_gate(tmp_path):
    rows = _read_rows()
    row = next(r for r in rows if r["selection_status"] == "OPEN")
    row["heteranthery_absence_status"] = "FAIL"
    path = tmp_path / "alts.csv"
    _write(path, rows)
    with pytest.raises(ValueError, match="OPEN candidate cannot contain a FAIL gate"):
        load_u3_control_alternatives(path, CASES, U3)


def test_screened_candidate_requires_all_four_gates_pass(tmp_path):
    rows = _read_rows()
    row = next(r for r in rows if r["selection_status"] == "OPEN")
    row["selection_status"] = "SCREENED"
    row["blocker"] = ""
    path = tmp_path / "alts.csv"
    _write(path, rows)
    with pytest.raises(ValueError, match="SCREENED candidate requires all gates PASS"):
        load_u3_control_alternatives(path, CASES, U3)

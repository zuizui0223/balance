from pathlib import Path

import csv
import pytest

from balance_domain.monochoria_common_marker import (
    CANDIDATE_TAXA,
    FIELDS,
    choose_candidate,
    load_accession_ledger,
    p_distance,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U3_MONOCHORIA_COMMON_MARKER_V1.csv"


def test_real_common_marker_accession_ledger_validates():
    rows = load_accession_ledger(LEDGER)
    by_taxon = {r["taxon"]: r for r in rows}
    assert set(CANDIDATE_TAXA) <= set(by_taxon)
    assert by_taxon["Pontederia australasica"]["record_type"] == "COMPLETE_PLASTOME"
    assert by_taxon["Pontederia australasica"]["rbcl_accession"] == "NC_063307.1"
    assert by_taxon["Pontederia cyanea"]["ndhf_accession"] == "U41613.1"
    assert by_taxon["Pontederia cyanea"]["rbcl_accession"] == "U41588.1"


def test_p_distance_masks_gaps_and_ambiguity():
    out = p_distance("ACGT-NACGT", "ACGAANAC-T")
    assert out["comparable_sites"] == 7
    assert out["differences"] == 1
    assert out["p_distance"] == pytest.approx(1 / 7)


def test_candidate_choice_reports_lower_distance_without_promoting_control():
    distances = {
        "Pontederia australasica || Pontederia korsakowii": {
            "comparable_sites": 1000,
            "differences": 12,
            "p_distance": 0.012,
        },
        "Pontederia cyanea || Pontederia korsakowii": {
            "comparable_sites": 1000,
            "differences": 8,
            "p_distance": 0.008,
        },
    }
    out = choose_candidate(distances, "Pontederia korsakowii")
    assert out["closest_candidate_by_p_distance"] == "Pontederia cyanea"
    assert out["distance_outcome"] == "LOWER_COMMON_MARKER_P_DISTANCE"
    assert "not_control_adjudication" in out["claim_ceiling"]


def test_candidate_choice_can_fail_closed_on_tie():
    distances = {
        "Pontederia australasica || Pontederia vaginalis": {
            "comparable_sites": 1000,
            "differences": 8,
            "p_distance": 0.008,
        },
        "Pontederia cyanea || Pontederia vaginalis": {
            "comparable_sites": 1000,
            "differences": 8,
            "p_distance": 0.008,
        },
    }
    out = choose_candidate(distances, "Pontederia vaginalis")
    assert out["closest_candidate_by_p_distance"] is None
    assert out["distance_outcome"] == "TIE"


def test_complete_plastome_row_cannot_mix_accessions(tmp_path):
    rows = load_accession_ledger(LEDGER)
    rows[0]["rbcl_accession"] = "OTHER"
    path = tmp_path / "ledger.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="one genome accession"):
        load_accession_ledger(path)

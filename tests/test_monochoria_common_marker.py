from pathlib import Path

import csv
import json
import pytest

from balance_domain.monochoria_common_marker import (
    CANDIDATE_TAXA,
    FIELDS,
    compare_candidates_on_common_sites,
    load_accession_ledger,
    p_distance,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U3_MONOCHORIA_COMMON_MARKER_V1.csv"
RESULT = ROOT / "data" / "BALANCE_PLANT_U3_MONOCHORIA_COMMON_MARKER_RESULT_V1.json"


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


def test_candidate_comparison_uses_one_joint_site_mask():
    aligned = {
        "Pontederia korsakowii": "ACGTACGT--AA",
        "Pontederia australasica": "ACGAACGTGGAA",
        "Pontederia cyanea": "ACGTTCGT--AA",
    }
    out = compare_candidates_on_common_sites(aligned, "Pontederia korsakowii")
    # Sites with a gap in cyanea are excluded for *both* candidates.
    assert out["jointly_comparable_sites"] == 10
    assert out["candidate_distances"]["Pontederia australasica"]["comparable_sites"] == 10
    assert out["candidate_distances"]["Pontederia cyanea"]["comparable_sites"] == 10
    assert out["candidate_distances"]["Pontederia australasica"]["differences"] == 1
    assert out["candidate_distances"]["Pontederia cyanea"]["differences"] == 1
    assert out["distance_outcome"] == "TIE"
    assert out["closest_candidate_by_p_distance"] is None


def test_candidate_comparison_reports_lower_distance_on_same_sites():
    aligned = {
        "Pontederia korsakowii": "ACGTACGT",
        "Pontederia australasica": "ACGAACGT",
        "Pontederia cyanea": "ACGGTCGT",
    }
    out = compare_candidates_on_common_sites(aligned, "Pontederia korsakowii")
    assert out["jointly_comparable_sites"] == 8
    assert out["candidate_distances"]["Pontederia australasica"]["differences"] == 1
    assert out["candidate_distances"]["Pontederia cyanea"]["differences"] == 2
    assert out["closest_candidate_by_p_distance"] == "Pontederia australasica"
    assert out["distance_outcome"] == "LOWER_COMMON_SITE_P_DISTANCE"
    assert "not_control_adjudication" in out["claim_ceiling"]


def test_identical_candidates_on_joint_sites_fail_closed_as_tie():
    aligned = {
        "Pontederia vaginalis": "ACGTACGT",
        "Pontederia australasica": "ACGAACGT",
        "Pontederia cyanea": "ACGAACGT",
    }
    out = compare_candidates_on_common_sites(aligned, "Pontederia vaginalis")
    assert out["candidate_pair_differences_on_joint_sites"] == 0
    assert out["candidate_distances"]["Pontederia australasica"]["differences"] == 1
    assert out["candidate_distances"]["Pontederia cyanea"]["differences"] == 1
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


def test_frozen_real_data_receipt_is_nonidentifying_for_both_cases():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["workflow_run_id"] == 35972984652
    assert result["workflow_run_number"] == 5
    assert result["source_commit"] == "926493b35a05ca14942a42b21ad182eb155d7f9d"
    assert result["comparison_method"].startswith("MAFFT per marker")

    kors = result["case_comparisons"]["Pontederia korsakowii"]
    assert kors["jointly_comparable_sites"] == 1825
    assert kors["candidates"]["Pontederia australasica"]["differences"] == 36
    assert kors["candidates"]["Pontederia cyanea"]["differences"] == 36
    assert kors["candidate_pair_differences_on_joint_sites"] == 0
    assert kors["outcome"] == "TIE"
    assert kors["closest_candidate"] is None

    vag = result["case_comparisons"]["Pontederia vaginalis"]
    assert vag["jointly_comparable_sites"] == 1786
    assert vag["candidates"]["Pontederia australasica"]["differences"] == 30
    assert vag["candidates"]["Pontederia cyanea"]["differences"] == 30
    assert vag["candidate_pair_differences_on_joint_sites"] == 0
    assert vag["outcome"] == "TIE"
    assert vag["closest_candidate"] is None

    pair = result["candidate_pair_overlap"]
    assert pair["comparable_sites"] == 1833
    assert pair["differences"] == 0
    assert pair["p_distance"] == 0.0
    assert "identification_limit" in result["claim_ceiling"]

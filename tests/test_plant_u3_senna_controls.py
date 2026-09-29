from pathlib import Path

from balance_domain.plant_u3_senna_controls import (
    build_u3_senna_control_search_readout,
    load_u3_senna_control_search,
)


ROOT = Path(__file__).resolve().parents[1]
SEARCH = ROOT / "data" / "BALANCE_PLANT_U3_SENNA_CONTROL_SEARCH_V1.csv"


def test_senna_control_search_validates():
    rows = load_u3_senna_control_search(SEARCH)
    assert len(rows) == 10
    assert {r["case_taxon"] for r in rows} == {"Senna alata", "Senna bicapsularis"}


def test_close_relatives_are_not_kept_when_heterantherous():
    rows = load_u3_senna_control_search(SEARCH)
    excluded = [
        r for r in rows if r["candidate_status"] == "EXCLUDED_HETERANTHEROUS"
    ]
    assert len(excluded) == 4
    assert all(r["heteranthery_absence_status"] == "FAIL" for r in excluded)


def test_no_replacement_control_is_promoted_yet():
    readout = build_u3_senna_control_search_readout(SEARCH)
    assert readout["n_eligible_not_selected"] == 0
    assert readout["open_homantherous_candidates"]["Senna alata"] == [
        "Senna pumilio",
        "Senna racemosa",
        "Senna villosa",
    ]
    assert readout["open_homantherous_candidates"]["Senna bicapsularis"] == [
        "Senna pumilio",
        "Senna racemosa",
        "Senna villosa",
    ]


def test_bicapsularis_sister_control_is_excluded_for_real_heteranthery():
    rows = load_u3_senna_control_search(SEARCH)
    row = next(
        r for r in rows
        if r["case_taxon"] == "Senna bicapsularis"
        and r["candidate_control"] == "Senna corymbosa"
    )
    assert row["phylogenetic_proximity_status"] == "SISTER_RELATIVE"
    assert row["candidate_status"] == "EXCLUDED_HETERANTHEROUS"

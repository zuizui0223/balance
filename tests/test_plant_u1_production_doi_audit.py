from pathlib import Path

import pytest

from balance_domain.plant_u1_production_doi_audit import (
    load_inventory,
    normalize_title,
    score_crossref_item,
    title_similarity,
)


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "data" / "BALANCE_PLANT_U1_PRODUCTION_SOURCE_INVENTORY_V1.csv"


def test_inventory_covers_all_27_post_first20_taxa_with_30_study_occurrences():
    rows = load_inventory(INVENTORY)
    assert len(rows) == 30
    assert len({r["universe_record_id"] for r in rows}) == 27
    assert {r["universe_record_id"] for r in rows} == {
        f"U1_{i:03d}" for i in range(21, 48)
    }


def test_title_normalization_ignores_case_and_punctuation():
    assert normalize_title("Florivory and pollinator visitation: A cautionary tale") == (
        "florivory and pollinator visitation a cautionary tale"
    )
    assert title_similarity(
        "DOES DOSE-DEPENDENT PETAL DAMAGE AFFECT POLLEN LIMITATION IN AN ANNUAL PLANT?",
        "Does dose-dependent petal damage affect pollen limitation in an annual plant?",
    ) == 1.0


def test_crossref_candidate_requires_high_title_match_and_exact_year():
    row = {
        "title": "FLORIVORY AND POLLINATOR VISITATION: A CAUTIONARY TALE",
        "publication_year": "2016",
    }
    item = {
        "DOI": "10.1093/aobpla/plw036",
        "title": ["Florivory and pollinator visitation: a cautionary tale"],
        "issued": {"date-parts": [[2016, 1, 1]]},
    }
    score = score_crossref_item(row, item)
    assert score["accepted"] is True
    assert score["doi"] == "10.1093/aobpla/plw036"


def test_wrong_year_fails_closed_even_with_exact_title():
    row = {"title": "Example title", "publication_year": "2016"}
    item = {
        "DOI": "10.1000/example",
        "title": ["Example title"],
        "issued": {"date-parts": [[2015]]},
    }
    assert score_crossref_item(row, item)["accepted"] is False

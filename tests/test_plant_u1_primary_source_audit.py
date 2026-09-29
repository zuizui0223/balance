from balance_domain.plant_u1_primary_source_audit import (
    choose_crossref_candidate,
    classify_crossref_match,
    normalize_title,
    parse_study_list,
    title_similarity,
)


def test_title_normalization_and_similarity_tolerate_case_punctuation():
    a = "Effects of Herbivory and Inflorescence Size on Insect Visitation"
    b = "EFFECTS OF HERBIVORY & INFLORESCENCE SIZE ON INSECT VISITATION."
    assert normalize_title(a)
    assert title_similarity(a, b) > 0.95


def test_crossref_match_fails_closed_on_weak_title():
    assert classify_crossref_match(0.95, 0) == "RESOLVED"
    assert classify_crossref_match(0.85, 0) == "REVIEW"
    assert classify_crossref_match(0.70, 0) == "NOT_RESOLVED"
    assert classify_crossref_match(0.95, 5) == "NOT_RESOLVED"


def test_choose_crossref_candidate_prefers_exact_title_and_year():
    items = [
        {
            "DOI": "10.1/wrong",
            "title": ["A loosely related paper"],
            "score": 99,
            "published-print": {"date-parts": [[2010]]},
        },
        {
            "DOI": "10.1/right",
            "title": ["Effects of herbivory on pollinator visitation"],
            "score": 80,
            "published-print": {"date-parts": [[2010]]},
        },
    ]
    out = choose_crossref_candidate(
        "Effects of herbivory on pollinator visitation",
        2010,
        items,
    )
    assert out["status"] == "RESOLVED"
    assert out["doi"] == "10.1/right"


def test_parse_study_list_requires_identity_columns():
    data = (
        "article id,author,title,journal,publication year\n"
        "464,A B,Example title,Example Journal,2010\n"
    ).encode()
    out = parse_study_list(data)
    assert out["464"]["title"] == "Example title"
    assert out["464"]["publication_year"] == "2010"

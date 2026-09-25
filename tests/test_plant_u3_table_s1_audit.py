from balance_domain.plant_u3_table_s1_audit import (
    discover_supplement_hrefs,
    extract_family_contexts,
    extract_scientific_names,
    parse_wayback_cdx,
)


def test_discovers_table_s1_href_from_article_html():
    html = """
    <a href="/action/downloadSupplement?doi=x&amp;file=NPH_3430_sm_TableS1.doc">
      Table S1
    </a>
    """
    assert discover_supplement_hrefs(html) == [
        "https://nph.onlinelibrary.wiley.com/action/downloadSupplement?"
        "doi=x&file=NPH_3430_sm_TableS1.doc"
    ]


def test_extract_scientific_names_is_conservative():
    text = "Malvaceae Examplea alpha and Bixaceae Exampleb beta var. gamma."
    assert extract_scientific_names(text) == [
        "Examplea alpha",
        "Exampleb beta gamma",
    ]


def test_family_contexts_fail_closed_when_family_absent():
    text = "Malvaceae Examplea alpha. Some spacer. Bixaceae Exampleb beta."
    out = extract_family_contexts(text, radius=80)
    assert out["Malvaceae"]["found"] is True
    assert "Examplea alpha" in out["Malvaceae"]["scientific_name_candidates"]
    assert out["Bixaceae"]["found"] is True
    assert out["Scrophulariaceae"]["found"] is False
    assert out["Scrophulariaceae"]["scientific_name_candidates"] == []


def test_parse_wayback_cdx_deduplicates_snapshots_and_ignores_malformed_rows():
    payload = b'''[
      ["timestamp","original","mimetype","statuscode","digest","length"],
      ["20110101000000","https://example.org/TableS1.doc","application/msword","200","ABC","1234"],
      ["20110101000000","https://example.org/TableS1.doc","application/msword","200","ABC","1234"],
      ["bad"]
    ]'''
    out = parse_wayback_cdx(payload)
    assert out == [
        {
            "timestamp": "20110101000000",
            "original": "https://example.org/TableS1.doc",
            "mimetype": "application/msword",
            "statuscode": "200",
            "digest": "ABC",
            "length": "1234",
        }
    ]

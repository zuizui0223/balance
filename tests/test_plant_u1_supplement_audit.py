import io
import zipfile

from balance_domain.plant_u1_supplement_audit import (
    discover_figshare_files,
    discover_relevant_links,
    extract_scientific_names,
    summarize_csv_bytes,
    summarize_docx_bytes,
)


def test_discover_relevant_links_keeps_supplements_and_files_only():
    html = """
    <a href="/articles/9049/supp-1/">Supplement 1</a>
    <a href="https://example.org/peerj-9049-supp-2.csv">Supplement 2</a>
    <a href="/articles/9049/">Article</a>
    <a href="https://figshare.com/articles/dataset/example/123">Figshare</a>
    """
    out = discover_relevant_links(html, "https://peerj.com/articles/9049/")
    assert out == [
        "https://peerj.com/articles/9049/supp-1/",
        "https://example.org/peerj-9049-supp-2.csv",
        "https://figshare.com/articles/dataset/example/123",
    ]


def test_discover_figshare_files_extracts_named_downloads_deterministically():
    payload = {
        "title": "example",
        "files": [
            {"name": "supp-2.csv", "download_url": "https://files.example/b"},
            {"name": "supp-1.docx", "download_url": "https://files.example/a"},
            {"name": "", "download_url": "https://files.example/ignored"},
            {"name": "duplicate.csv", "download_url": "https://files.example/b"},
        ],
    }
    assert discover_figshare_files(payload) == [
        {"name": "supp-1.docx", "download_url": "https://files.example/a"},
        {"name": "supp-2.csv", "download_url": "https://files.example/b"},
    ]


def test_extract_scientific_names_is_conservative_and_counts_duplicates():
    text = (
        "Nemophila menziesii and Eichhornia crassipes were listed. "
        "Nemophila menziesii was repeated. Cucurbita pepo ssp. texana was tested."
    )
    assert extract_scientific_names(text) == {
        "Cucurbita pepo texana": 1,
        "Eichhornia crassipes": 1,
        "Nemophila menziesii": 2,
    }


def test_summarize_csv_bytes_reports_shape_columns_and_taxa():
    data = (
        "study,plant,outcome\n"
        "A,Nemophila menziesii,seed set\n"
        "B,Eichhornia crassipes,fruit set\n"
    ).encode()
    out = summarize_csv_bytes(data)
    assert out["kind"] == "delimited_text"
    assert out["data_row_count"] == 2
    assert out["columns"] == ["study", "plant", "outcome"]
    assert out["scientific_name_candidates"] == {
        "Eichhornia crassipes": 1,
        "Nemophila menziesii": 1,
    }


def test_summarize_docx_bytes_reads_document_xml_without_python_docx():
    xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:body><w:p><w:r><w:t>Alstroemeria exerens</w:t></w:r></w:p></w:body>
    </w:document>
    """.encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", xml)
    out = summarize_docx_bytes(buf.getvalue())
    assert out["kind"] == "docx"
    assert out["scientific_name_candidates"] == {"Alstroemeria exerens": 1}

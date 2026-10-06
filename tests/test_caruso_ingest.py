import pytest

from balance_domain.caruso_ingest import (
    EXPECTED_RECORD_COUNT,
    build_dictionary_inventory,
    build_inventory,
    detect_data_sheet,
)


def _sheets(n=EXPECTED_RECORD_COUNT):
    header = ["Article", "Species", "Trait", "Fitness", "Beta", "SE"]
    data = [["Caruso source inventory"], header]
    for i in range(n):
        data.append([
            f"Article_{i // 5}",
            f"Species_{i // 10}",
            f"Trait_{i % 7}",
            "female_fitness",
            (-1) ** i * (i + 1) / 1000,
            0.1,
        ])
    dictionary = [
        ["Column", "Description"],
        ["Article", "original article identifier"],
        ["Beta", "signed directional selection gradient"],
        ["SE", "reported standard error"],
    ]
    return {
        "Selection database": data,
        "Column information": dictionary,
    }


def test_caruso_stage_a_detects_unique_755_record_data_sheet():
    sheets = _sheets()
    detected = detect_data_sheet(sheets)
    assert detected["sheet_name"] == "Selection database"
    assert detected["header_index"] == 1
    assert len(detected["records"]) == 755

    fields, rows, detected_again = build_inventory(sheets)
    assert fields == [
        "source_row_number",
        "Article",
        "Species",
        "Trait",
        "Fitness",
        "Beta",
        "SE",
    ]
    assert len(rows) == 755
    assert rows[0]["source_row_number"] == "3"
    assert rows[0]["Beta"] == "0.001"
    assert rows[1]["Beta"] == "-0.002"
    assert detected_again["sheet_name"] == "Selection database"


def test_caruso_dictionary_is_preserved_as_positioned_text_inventory():
    sheets = _sheets()
    _, _, detected = build_inventory(sheets)
    fields, rows, name = build_dictionary_inventory(
        sheets,
        data_sheet_name=detected["sheet_name"],
    )
    assert name == "Column information"
    assert fields == ["source_row_number", "column_1", "column_2"]
    assert rows[0] == {
        "source_row_number": "1",
        "column_1": "Column",
        "column_2": "Description",
    }
    assert rows[-1]["column_1"] == "SE"


def test_caruso_ingest_fails_closed_on_wrong_record_count():
    with pytest.raises(ValueError, match="exactly one sheet/header yielding 755"):
        detect_data_sheet(_sheets(n=754))


def test_caruso_ingest_fails_closed_on_ambiguous_data_sheet():
    sheets = _sheets()
    sheets["Unexpected duplicate inventory"] = [
        list(row) for row in sheets["Selection database"]
    ]
    with pytest.raises(ValueError, match="candidates=2"):
        detect_data_sheet(sheets)


def test_caruso_inventory_rejects_blank_internal_header():
    sheets = _sheets()
    sheets["Selection database"][1][2] = ""
    with pytest.raises(ValueError):
        build_inventory(sheets)

import csv
import json

import pytest

from balance_domain.peucedanum_ingest import (
    build_source_inventory_receipt,
    inventory_tables,
    normalize_from_mapping,
    read_tabular_source,
)


def _tables():
    return {
        ("raw.csv", "__CSV__"): [
            ["Year", "Plot", "Plant", "DOY", "Perfect", "Male", "Intact", "PredRate"],
            [2021, "HL", "P1", 210, 20, 30, 8, 0.4],
            [2022, "HC", "P2", 215, 40, 10, 18, 0.1],
        ]
    }


def _mapping(status="SOURCE_VERIFIED_MAPPING"):
    return {
        "schema_version": "BALANCE_PEUCEDANUM_RAW_SEMANTIC_MAPPING_V1",
        "status": status,
        "registered_sources": [
            {
                "source_doi": "10.14943/hu95572",
                "sheet_mappings": [
                    {
                        "dataset_id": "peucedanum_2025_demo",
                        "source_file": "raw.csv",
                        "source_sheet": "__CSV__",
                        "header_row": 1,
                        "columns": {
                            "year": "Year",
                            "population_id": "Plot",
                            "plant_id": "Plant",
                            "flowering_day": "DOY",
                            "perfect_flower_count": "Perfect",
                            "male_flower_count": "Male",
                            "intact_fruit_count": "Intact",
                            "seed_predation_rate": "PredRate",
                        },
                    }
                ],
            }
        ],
    }


def test_inventory_reports_structure_without_guessing_header_semantics():
    inventory = inventory_tables(_tables())
    assert inventory == [
        {
            "source_file": "raw.csv",
            "source_sheet": "__CSV__",
            "row_count": 3,
            "column_count": 8,
            "nonempty_row_count": 3,
        }
    ]


def test_source_verified_mapping_normalizes_only_explicit_columns():
    rows = normalize_from_mapping(_tables(), _mapping())
    assert len(rows) == 2
    assert rows[0]["dataset_id"] == "peucedanum_2025_demo"
    assert rows[0]["source_doi"] == "10.14943/hu95572"
    assert rows[0]["source_row_number"] == "2"
    assert rows[0]["population_id"] == "HL"
    assert rows[0]["male_fraction"] == "0.6"
    assert rows[0]["total_flower_count"] == "50"
    assert rows[0]["final_fruit_set_rate"] == "0.4"

    assert rows[1]["population_id"] == "HC"
    assert rows[1]["male_fraction"] == "0.2"
    assert rows[1]["final_fruit_set_rate"] == "0.45"


def test_unverified_mapping_template_cannot_normalize():
    with pytest.raises(ValueError, match="SOURCE_VERIFIED_MAPPING"):
        normalize_from_mapping(_tables(), _mapping("TEMPLATE_NOT_SOURCE_VERIFIED"))


def test_mapping_does_not_guess_missing_required_semantics():
    mapping = _mapping()
    del mapping["registered_sources"][0]["sheet_mappings"][0]["columns"]["plant_id"]
    with pytest.raises(ValueError, match="lacks required normalized fields"):
        normalize_from_mapping(_tables(), mapping)


def test_mapping_fails_closed_on_unknown_source_column():
    mapping = _mapping()
    mapping["registered_sources"][0]["sheet_mappings"][0]["columns"][
        "flowering_day"
    ] = "Flowering day maybe"
    with pytest.raises(ValueError, match="not found"):
        normalize_from_mapping(_tables(), mapping)


def test_mapping_can_use_explicit_constants_for_sheet_level_semantics():
    tables = {
        ("plot_hl.csv", "__CSV__"): [
            ["Plant", "DOY", "Perfect", "Male"],
            ["P1", 210, 20, 30],
        ]
    }
    mapping = {
        "schema_version": "BALANCE_PEUCEDANUM_RAW_SEMANTIC_MAPPING_V1",
        "status": "SOURCE_VERIFIED_MAPPING",
        "registered_sources": [
            {
                "source_doi": "10.14943/hu95572",
                "sheet_mappings": [
                    {
                        "dataset_id": "plot_hl_2021",
                        "source_file": "plot_hl.csv",
                        "source_sheet": "__CSV__",
                        "header_row": 1,
                        "constants": {
                            "year": 2021,
                            "population_id": "HL",
                        },
                        "columns": {
                            "plant_id": "Plant",
                            "flowering_day": "DOY",
                            "perfect_flower_count": "Perfect",
                            "male_flower_count": "Male",
                        },
                    }
                ],
            }
        ],
    }
    rows = normalize_from_mapping(tables, mapping)
    assert rows[0]["year"] == "2021"
    assert rows[0]["population_id"] == "HL"


def test_duplicate_mapped_header_is_rejected():
    tables = {
        ("raw.csv", "__CSV__"): [
            ["Year", "Plot", "Plant", "DOY", "Perfect", "Perfect"],
            [2021, "HL", "P1", 210, 20, 30],
        ]
    }
    mapping = _mapping()
    with pytest.raises(ValueError, match="header columns must be unique"):
        normalize_from_mapping(tables, mapping)


def test_csv_reader_preserves_exact_file_identity_and_tables(tmp_path):
    source = tmp_path / "demo.csv"
    source.write_text(
        "Year,Plot,Plant,DOY,Perfect,Male\n"
        "2021,HL,P1,210,20,30\n",
        encoding="utf-8",
    )
    raw, tables = read_tabular_source(source)
    assert raw == source.read_bytes()
    assert tables["__CSV__"][1] == ["2021", "HL", "P1", "210", "20", "30"]

    receipt = build_source_inventory_receipt([source])
    assert receipt["status"] == (
        "SOURCE_BYTES_INVENTORIED_SEMANTIC_MAPPING_NOT_APPLIED"
    )
    assert receipt["files"]["demo.csv"]["source_bytes"] == len(raw)
    assert receipt["semantic_mapping_applied"] is False


def test_boolean_core_measurement_from_source_fails_closed():
    tables = _tables()
    tables[("raw.csv", "__CSV__")][1][4] = True
    with pytest.raises(ValueError, match="not numeric"):
        normalize_from_mapping(tables, _mapping())


def test_large_finite_mapped_flower_counts_do_not_overflow_derived_fields():
    tables = {
        ("raw.csv", "__CSV__"): [
            ["Year", "Plot", "Plant", "DOY", "Perfect", "Male"],
            [2021, "HL", "P1", 210, "1e308", "1e308"],
        ]
    }
    mapping = {
        "schema_version": "BALANCE_PEUCEDANUM_RAW_SEMANTIC_MAPPING_V1",
        "status": "SOURCE_VERIFIED_MAPPING",
        "registered_sources": [
            {
                "source_doi": "10.14943/hu95572",
                "sheet_mappings": [
                    {
                        "dataset_id": "large_counts",
                        "source_file": "raw.csv",
                        "source_sheet": "__CSV__",
                        "header_row": 1,
                        "columns": {
                            "year": "Year",
                            "population_id": "Plot",
                            "plant_id": "Plant",
                            "flowering_day": "DOY",
                            "perfect_flower_count": "Perfect",
                            "male_flower_count": "Male",
                        },
                    }
                ],
            }
        ],
    }
    rows = normalize_from_mapping(tables, mapping)
    assert float(rows[0]["male_fraction"]) == pytest.approx(0.5)
    assert rows[0]["total_flower_count"].lower().startswith("2e+308")

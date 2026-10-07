import csv
import hashlib
import io
import json
import zipfile

import pytest

from balance_domain.peucedanum_ingest import (
    build_source_inventory_receipt,
    inventory_tables,
    normalize_from_mapping,
    normalize_peucedanum_sources,
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



def test_mapping_constants_cannot_override_source_provenance():
    mapping = _mapping()
    mapping["registered_sources"][0]["sheet_mappings"][0]["constants"] = {
        "source_doi": "10.0000/fake"
    }
    with pytest.raises(ValueError, match="provenance normalized fields"):
        normalize_from_mapping(_tables(), mapping)


def test_unsupported_source_format_fails_closed(tmp_path):
    source = tmp_path / "raw.json"
    source.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="accepts only"):
        read_tabular_source(source)



def test_registered_expected_source_basename_is_enforced():
    mapping = _mapping()
    source = mapping["registered_sources"][0]
    source["expected_file"] = "Kudo&Shibata_Ecol&Evol_DataSet.xlsx"
    with pytest.raises(ValueError, match="not registered"):
        normalize_from_mapping(_tables(), mapping)



def test_zip_inventory_binds_outer_and_member_hashes_and_exposes_tabular_member(tmp_path):
    archive = tmp_path / "jec70130-sup-0001-supinfo.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(
            "data/raw.csv",
            "Year,Plot,Plant,DOY,Perfect,Male\n2021,HL,P1,210,20,30\n",
        )
        zf.writestr("code/reproduce.R", "print('source code')\n")

    receipt = build_source_inventory_receipt([archive])
    file_info = receipt["files"][archive.name]
    assert file_info["format"] == "zip"
    assert file_info["member_count"] == 2
    assert [member["member"] for member in file_info["members"]] == [
        "code/reproduce.R",
        "data/raw.csv",
    ]
    assert receipt["tables"] == [
        {
            "source_file": f"{archive.name}::data/raw.csv",
            "source_sheet": "__CSV__",
            "row_count": 2,
            "column_count": 6,
            "nonempty_row_count": 2,
        }
    ]


def test_zip_tabular_member_can_be_mapped_explicitly(tmp_path):
    archive = tmp_path / "source.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(
            "tables/raw.csv",
            "Year,Plot,Plant,DOY,Perfect,Male\n2021,HL,P1,210,20,30\n",
        )

    from balance_domain.peucedanum_ingest import load_sources

    _, tables = load_sources([archive])
    mapping = {
        "schema_version": "BALANCE_PEUCEDANUM_RAW_SEMANTIC_MAPPING_V1",
        "status": "SOURCE_VERIFIED_MAPPING",
        "registered_sources": [
            {
                "source_doi": "10.14943/hu95572",
                "expected_file": "source.zip",
                "sheet_mappings": [
                    {
                        "dataset_id": "zip_demo",
                        "source_file": "source.zip::tables/raw.csv",
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
    assert rows[0]["source_file"] == "source.zip::tables/raw.csv"
    assert rows[0]["male_fraction"] == "0.6"


@pytest.mark.parametrize("member", ["../raw.csv", "/raw.csv", "..\\raw.csv"])
def test_zip_unsafe_member_paths_fail_closed(tmp_path, member):
    archive = tmp_path / "source.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(member, "x,y\n1,2\n")

    with pytest.raises(ValueError, match="unsafe member path"):
        build_source_inventory_receipt([archive])



def _write_verified_csv_mapping(path, source):
    mapping = _mapping()
    source_entry = mapping["registered_sources"][0]
    source_entry["expected_file"] = source.name
    source_entry["expected_file_sha256s"] = {
        source.name: hashlib.sha256(source.read_bytes()).hexdigest()
    }
    source_entry["sheet_mappings"][0]["source_file"] = source.name
    path.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    return mapping


def test_production_normalization_binds_verified_mapping_to_exact_source_bytes(tmp_path):
    source = tmp_path / "raw.csv"
    source.write_text(
        "Year,Plot,Plant,DOY,Perfect,Male,Intact,PredRate\n"
        "2021,HL,P1,210,20,30,8,0.4\n",
        encoding="utf-8",
    )
    mapping_path = tmp_path / "mapping.json"
    _write_verified_csv_mapping(mapping_path, source)

    out_dir = tmp_path / "normalized"
    receipt = normalize_peucedanum_sources([source], mapping_path, out_dir)

    assert receipt["source_hash_binding_verified"] is True
    assert receipt["source_files"][source.name]["source_sha256"] == (
        hashlib.sha256(source.read_bytes()).hexdigest()
    )
    assert (out_dir / "BALANCE_PEUCEDANUM_NORMALIZED_ROWS_V1.csv").exists()
    assert (out_dir / "BALANCE_PEUCEDANUM_NORMALIZATION_RECEIPT_V1.json").exists()


def test_production_normalization_rejects_same_named_source_with_changed_bytes(tmp_path):
    source = tmp_path / "raw.csv"
    source.write_text(
        "Year,Plot,Plant,DOY,Perfect,Male,Intact,PredRate\n"
        "2021,HL,P1,210,20,30,8,0.4\n",
        encoding="utf-8",
    )
    mapping_path = tmp_path / "mapping.json"
    _write_verified_csv_mapping(mapping_path, source)

    # Keep the same basename/header while changing the bytes after human verification.
    source.write_text(
        "Year,Plot,Plant,DOY,Perfect,Male,Intact,PredRate\n"
        "2021,HL,P1,210,20,31,8,0.4\n",
        encoding="utf-8",
    )
    out_dir = tmp_path / "normalized"
    with pytest.raises(ValueError, match="source SHA256 mismatch"):
        normalize_peucedanum_sources([source], mapping_path, out_dir)
    assert not out_dir.exists()


def test_production_normalization_rejects_verified_mapping_without_source_hash(tmp_path):
    source = tmp_path / "raw.csv"
    source.write_text(
        "Year,Plot,Plant,DOY,Perfect,Male,Intact,PredRate\n"
        "2021,HL,P1,210,20,30,8,0.4\n",
        encoding="utf-8",
    )
    mapping = _mapping()
    mapping["registered_sources"][0]["expected_file"] = source.name
    mapping["registered_sources"][0]["sheet_mappings"][0]["source_file"] = source.name
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="requires expected_file_sha256s"):
        normalize_peucedanum_sources([source], mapping_path, tmp_path / "normalized")

import csv
import hashlib
import json
from pathlib import Path

import pytest

from balance_domain.peucedanum_ingest import NORMALIZED_FIELDS
from balance_domain.peucedanum_r1_support import (
    audit_normalized_csv,
    build_r1_row_support_audit,
)
from scripts.audit_peucedanum_r1_support import (
    build_receipt,
    validate_against_expectations,
)


ROOT = Path(__file__).resolve().parents[1]


def _row(n, year, plot, plant, *, initial="2", final="1", height="10"):
    row = {name: "" for name in NORMALIZED_FIELDS}
    row.update({
        "dataset_id": "source_2025",
        "source_doi": "10.14943/hu95572",
        "source_file": "verified.zip::All_Plots_Data.csv",
        "source_sheet": "__CSV__",
        "source_row_number": str(n),
        "year": year,
        "population_id": plot,
        "plant_id": plant,
        "perfect_flower_count": "4",
        "male_flower_count": "3",
        "initial_fruit_count": initial,
        "intact_fruit_count": final,
        "flower_stem_height": height,
        "total_flower_count": "7",
        "male_fraction": "0.42857142857",
    })
    return row


def test_r1_support_is_not_a_unique_plant_id_deduplication():
    rows = [
        _row(2, "2020", "HA", "id_1"),
        _row(3, "2020", "HA", "id_1", final=""),
        _row(4, "2021", "HD", "id_2", height=""),
        _row(5, "2021", "HD", "id_3", initial="", final=""),
    ]
    result = build_r1_row_support_audit(rows)
    assert result["source_rows"] == 4
    assert result["observed_plot_year_cells"] == 2
    assert result["source_fit_plot_year_cells"] == 1
    assert result["observed_cells_without_source_fit_candidates"] == [
        {"year": "2021", "population_id": "HD", "source_rows": 2}
    ]
    assert result["missing_counts"]["intact_fruit_count"] == 2
    assert result["missing_counts"]["initial_fruit_count"] == 1
    assert result["missing_counts"]["flower_stem_height"] == 1
    assert result["pre_height_fruit_complete_rows"] == 2
    assert result["differential_candidate_rows"] == 1
    assert result["gradient_candidate_rows"] == 1
    assert result["reused_year_plot_plant_id_keys"] == [{
        "year": "2020",
        "population_id": "HA",
        "plant_id": "id_1",
        "source_row_numbers": ["2", "3"],
    }]
    assert result["reused_biological_id_keys_are_not_automatically_deduplicated"] is True
    assert "not_reproduction" in result["claim_ceiling"]


def test_r1_support_rejects_duplicate_source_provenance():
    with pytest.raises(ValueError, match="duplicate source-row provenance"):
        build_r1_row_support_audit([
            _row(2, "2020", "HA", "id_1"),
            _row(2, "2020", "HA", "id_2"),
        ])


def test_r1_support_requires_canonical_normalized_csv_columns(tmp_path):
    path = tmp_path / "rows.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["year", "plot"])
        writer.writeheader()
        writer.writerow({"year": "2020", "plot": "HA"})
    with pytest.raises(ValueError, match="canonical schema"):
        audit_normalized_csv(path)


def test_2025_r1_support_expected_observation_grain_is_frozen():
    path = ROOT / "empirical/peucedanum/PEUCEDANUM_2025_R1_ROW_SUPPORT_EXPECTATIONS_V1.json"
    expected = json.loads(path.read_text(encoding="utf-8"))
    assert expected["source_rows"] == 685
    assert expected["observed_plot_year_cells"] == 19
    assert expected["source_fit_plot_year_cells"] == 18
    assert expected["observed_cells_without_source_fit_candidates"] == [
        {"year": "2021", "population_id": "HA", "source_rows": 50}
    ]
    assert expected["pre_height_fruit_complete_rows"] == 620
    assert expected["differential_candidate_rows"] == 608
    assert expected["gradient_candidate_rows"] == 608
    assert expected["candidate_rows_by_plot"]["HD"] == {
        "source_rows": 139,
        "pre_height_fruit_complete_rows": 139,
        "differential_candidate_rows": 127,
        "gradient_candidate_rows": 127,
    }
    assert expected["special_missing_cells"] == [
        {"year": "2020", "population_id": "HA", "missing_intact_fruit_count": 1},
        {"year": "2021", "population_id": "HA", "missing_intact_fruit_count": 50},
        {"year": "2022", "population_id": "HC", "missing_intact_fruit_count": 7},
        {"year": "2022", "population_id": "HL", "missing_intact_fruit_count": 7},
    ]
    assert expected["special_missing_height_cells"] == [
        {"year": "2022", "population_id": "HD", "missing_flower_stem_height": 12}
    ]
    assert len(expected["reused_year_plot_plant_id_keys"]) == 2


def test_exact_expectations_reject_drift():
    audit = build_r1_row_support_audit([
        _row(2, "2020", "HA", "id_1"),
        _row(3, "2020", "HA", "id_2", final=""),
    ])
    expected = {
        **audit,
        "schema_version": "BALANCE_PEUCEDANUM_2025_R1_ROW_SUPPORT_EXPECTATIONS_V1",
        "special_missing_cells": [
            {"year": "2020", "population_id": "HA", "missing_intact_fruit_count": 1}
        ],
        "special_missing_height_cells": [],
    }
    validate_against_expectations(audit, expected)
    expected["source_rows"] = 3
    with pytest.raises(ValueError, match="source_rows"):
        validate_against_expectations(audit, expected)



def test_r1_audit_rejects_changed_source_values_with_unchanged_missingness(tmp_path):
    rows_path = tmp_path / "normalized.csv"
    row = _row(2, "2020", "HA", "id_1")
    with rows_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=NORMALIZED_FIELDS)
        writer.writeheader()
        writer.writerow(row)

    nr_path = tmp_path / "normalization.json"
    nr = {
        "status": "SOURCE_VERIFIED_MAPPING_APPLIED",
        "normalized_rows": 1,
        "source_files": {
            "Kudo$Shibata_JEcol_Data.zip": {
                "source_sha256": "a" * 64,
            }
        },
    }
    nr_path.write_text(json.dumps(nr, sort_keys=True) + "\n", encoding="utf-8")

    expectations = {
        **build_r1_row_support_audit([row]),
        "schema_version": "BALANCE_PEUCEDANUM_2025_R1_ROW_SUPPORT_EXPECTATIONS_V1",
        "source_archive_sha256": "a" * 64,
        "normalized_csv_sha256": hashlib.sha256(rows_path.read_bytes()).hexdigest(),
        "normalization_receipt_sha256": hashlib.sha256(nr_path.read_bytes()).hexdigest(),
        "special_missing_cells": [],
        "special_missing_height_cells": [],
    }
    expected_path = tmp_path / "expectations.json"
    expected_path.write_text(
        json.dumps(expectations, sort_keys=True) + "\n", encoding="utf-8"
    )

    assert build_receipt(rows_path, nr_path, expected_path)["source_rows"] == 1

    # Changed biology with identical source-row/missingness statistics fails closed.
    row["male_flower_count"] = "4"
    with rows_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=NORMALIZED_FIELDS)
        writer.writeheader()
        writer.writerow(row)
    with pytest.raises(ValueError, match="normalized CSV SHA256"):
        build_receipt(rows_path, nr_path, expected_path)

    # Even metadata/provenance changes with unmodified normalized rows fail closed.
    row["male_flower_count"] = "3"
    with rows_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=NORMALIZED_FIELDS)
        writer.writeheader()
        writer.writerow(row)
    nr["unregistered_mapping_change"] = True
    nr_path.write_text(json.dumps(nr, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="normalization receipt SHA256"):
        build_receipt(rows_path, nr_path, expected_path)



def test_global_height_exclusion_applies_to_differential_as_well_as_gradient():
    rows = [
        _row(2, "2023", "HD", "id_a", height=""),
        _row(3, "2023", "HD", "id_b"),
    ]
    out = build_r1_row_support_audit(rows)
    assert out["pre_height_fruit_complete_rows"] == 2
    assert out["differential_candidate_rows"] == 1
    assert out["gradient_candidate_rows"] == 1
    assert out["candidate_rows_by_plot"]["HD"]["pre_height_fruit_complete_rows"] == 2
    assert out["candidate_rows_by_plot"]["HD"]["differential_candidate_rows"] == 1



def test_height_missingness_cell_cannot_drift_after_source_freeze():
    audit = build_r1_row_support_audit([
        _row(2, "2022", "HD", "id_1", height=""),
        _row(3, "2022", "HD", "id_2"),
    ])
    expected = {
        **audit,
        "schema_version": "BALANCE_PEUCEDANUM_2025_R1_ROW_SUPPORT_EXPECTATIONS_V1",
        "special_missing_cells": [],
        "special_missing_height_cells": [
            {"year": "2022", "population_id": "HD", "missing_flower_stem_height": 1}
        ],
    }
    validate_against_expectations(audit, expected)
    expected["special_missing_height_cells"][0]["missing_flower_stem_height"] = 0
    with pytest.raises(ValueError, match="special_missing_height_cells"):
        validate_against_expectations(audit, expected)

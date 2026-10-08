import csv
import json
from pathlib import Path

import pytest

from balance_domain.peucedanum_ingest import NORMALIZED_FIELDS
from balance_domain.peucedanum_r1_support import (
    audit_normalized_csv,
    build_r1_row_support_audit,
)
from scripts.audit_peucedanum_r1_support import validate_against_expectations


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
    assert result["missing_counts"]["intact_fruit_count"] == 2
    assert result["missing_counts"]["initial_fruit_count"] == 1
    assert result["missing_counts"]["flower_stem_height"] == 1
    assert result["differential_candidate_rows"] == 2
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
    assert expected["differential_candidate_rows"] == 620
    assert expected["gradient_candidate_rows"] == 608
    assert expected["candidate_rows_by_plot"]["HD"] == {
        "source_rows": 139,
        "differential_candidate_rows": 139,
        "gradient_candidate_rows": 127,
    }
    assert expected["special_missing_cells"] == [
        {"year": "2020", "population_id": "HA", "missing_intact_fruit_count": 1},
        {"year": "2021", "population_id": "HA", "missing_intact_fruit_count": 50},
        {"year": "2022", "population_id": "HC", "missing_intact_fruit_count": 7},
        {"year": "2022", "population_id": "HL", "missing_intact_fruit_count": 7},
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
    }
    validate_against_expectations(audit, expected)
    expected["source_rows"] = 3
    with pytest.raises(ValueError, match="source_rows"):
        validate_against_expectations(audit, expected)

"""R1 adjudication tests are synthetic; these are not empirical model fits."""
import csv
import json
from pathlib import Path

import pytest

from scripts.adjudicate_peucedanum_r1 import (
    EXPECTED_FIELDS,
    adjudicate,
    read_reproduction,
    run,
)

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = json.loads((ROOT /
    "empirical/peucedanum/PEUCEDANUM_2025_PUBLISHED_SUMMARY_RECEIPT_V1.json"
).read_text(encoding="utf-8"))
SUPPORT = json.loads((ROOT /
    "empirical/peucedanum/PEUCEDANUM_2025_R1_ROW_SUPPORT_EXPECTATIONS_V1.json"
).read_text(encoding="utf-8"))


def fixture_rows():
    rows = []
    for p in PUBLISHED["ordered_contexts"]:
        s = PUBLISHED["final_fruit_set_rate"]["linear_selection_differential_S"][p]
        beta = PUBLISHED["final_fruit_set_rate"]["linear_selection_gradient_beta"][p]
        gain = PUBLISHED["female_gain_exponent_b"][p]
        n = SUPPORT["candidate_rows_by_plot"][p]["differential_candidate_rows"]
        row = {
            "Plot": p,
            "S": str(s["estimate"]),
            "S_se": str(s["se"]),
            "S_fitted_n": str(n),
            "beta": str(beta["estimate"]),
            "beta_se": str(beta["se"]),
            "beta_fitted_n": str(n),
            "female_gain_b": str(gain["estimate"]),
            "female_gain_b_se": str(gain["se"]),
            "female_gain_fitted_n": str(n),
            "published_S": str(s["estimate"]),
            "published_beta": str(beta["estimate"]),
            "published_b": str(gain["estimate"]),
            "S_round3_match": "TRUE",
            "beta_round3_match": "TRUE",
            "b_round2_match": "TRUE",
        }
        rows.append(row)
    assert tuple(rows[0]) == EXPECTED_FIELDS
    return rows


def test_r1_exact_published_precision_is_only_numeric_concordance():
    result = adjudicate(fixture_rows(), PUBLISHED, SUPPORT)
    assert result["status"] == "NUMERICALLY_CONCORDANT_PENDING_SOURCE_MODEL_VERIFICATION"
    assert result["matched_point_estimates"] == 15
    assert result["matched_standard_errors"] == 15
    assert result["fitted_counts"]["HD"]["linear_selection_gradient_beta"] == 127
    assert "not_causal" in result["claim_ceiling"]


def test_r1_13_of_15_near_miss_stays_not_reproduced():
    rows = fixture_rows()
    rows[0]["S"] = "-0.02801687695"
    rows[0]["S_round3_match"] = "FALSE"
    rows[3]["beta"] = "0.008501698124"
    rows[3]["beta_round3_match"] = "FALSE"
    rows[2]["S_se"] = "0.008846196217"
    result = adjudicate(rows, PUBLISHED, SUPPORT)
    assert result["status"] == "R1_NOT_FULLY_REPRODUCED"
    assert result["matched_point_estimates"] == 13
    assert result["matched_standard_errors"] == 14
    mismatches = {
        (x["plot"], x["metric"])
        for x in result["comparisons"]
        if not x["point_matches_published_precision"]
    }
    assert mismatches == {
        ("HA", "linear_selection_differential_S"),
        ("KD", "linear_selection_gradient_beta"),
    }


def test_r1_rejects_dropped_and_duplicated_plots():
    rows = fixture_rows()
    with pytest.raises(ValueError, match="missing, extra, duplicated"):
        adjudicate(rows[:-1], PUBLISHED, SUPPORT)
    rows[1]["Plot"] = "HA"
    with pytest.raises(ValueError, match="missing, extra, duplicated"):
        adjudicate(rows, PUBLISHED, SUPPORT)


def test_r1_fitted_counts_fail_closed():
    rows = fixture_rows()
    rows[-1]["beta_fitted_n"] = "139"
    with pytest.raises(ValueError, match="fitted N differs"):
        adjudicate(rows, PUBLISHED, SUPPORT)


def test_r1_does_not_trust_self_reported_match_flags_or_embedded_targets():
    rows = fixture_rows()
    rows[0]["S"] = "-0.028"
    with pytest.raises(ValueError, match="disagrees with numeric"):
        adjudicate(rows, PUBLISHED, SUPPORT)
    rows = fixture_rows()
    rows[1]["published_b"] = "99.99"
    with pytest.raises(ValueError, match="embedded target differs"):
        adjudicate(rows, PUBLISHED, SUPPORT)


def test_r1_rejects_nonfinite_values_and_incorrect_source_receipt():
    rows = fixture_rows()
    rows[2]["beta_se"] = "NaN"
    with pytest.raises(ValueError, match="must be finite"):
        adjudicate(rows, PUBLISHED, SUPPORT)
    altered = dict(SUPPORT, source_archive_sha256="invalid")
    with pytest.raises(ValueError, match="archive mismatch"):
        adjudicate(fixture_rows(), PUBLISHED, altered)


def test_r1_csv_schema_and_source_bytes_prevent_unverified_execution(tmp_path):
    csv_path = tmp_path / "fit.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPECTED_FIELDS)
        writer.writeheader()
        writer.writerows(fixture_rows())
    assert len(read_reproduction(csv_path)) == 5
    source_path = tmp_path / "unverified.zip"
    source_path.write_bytes(b"not the source archive")
    with pytest.raises(ValueError, match="unverified source archive"):
        run(csv_path, source_path, source_path, source_path,
            ROOT / "empirical/peucedanum/PEUCEDANUM_2025_PUBLISHED_SUMMARY_RECEIPT_V1.json",
            ROOT / "empirical/peucedanum/PEUCEDANUM_2025_R1_ROW_SUPPORT_EXPECTATIONS_V1.json",
            tmp_path / "out.json")

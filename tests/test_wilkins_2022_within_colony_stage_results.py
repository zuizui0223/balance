"""Regress actual externally re-executed Wilkins colony/stigma source results.

Scientific ceiling: a source-backed post-open study sensitivity, not a new
pre-registered V4 result or a pollen-genetic paternity measurement.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT / "results" / "wilkins_2022" /
    "WITHIN_COLONY_STIGMA_STAGES_20261122.json"
)


def read_report():
    return json.loads(OUTPUT.read_text(encoding="utf-8"))


def test_real_workflow_source_and_artifact_are_pinned():
    result = read_report()
    assert result["status"] == (
        "ACTUAL_AUTHENTICATED_SOURCE_EXPLORATORY_POSTOPEN_SENSITIVITY"
    )
    assert result["source"]["article_doi"] == "10.1007/s00442-022-05246-0"
    assert result["source"]["raw_csv_sha256"] == (
        "0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62"
    )
    assert result["source"]["n_complete_bee_trials"] == 59
    assert result["source"]["n_colonies"] == 3
    assert result["provenance"]["workflow_id"] == 45017036647
    assert result["provenance"]["original_executed_head"] == (
        "a62e9c947c445c5e94e69b542660eb87195a7d8a"
    )
    assert result["provenance"]["workflow_artifact_id"] == 14752457051
    assert result["provenance"]["workflow_artifact_zip_sha256"] == (
        "b1a8a1f3120650ecfa9fcf86ef5224ad5f31367bf17ce5312724f62586fcc541"
    )
    assert result["provenance"]["original_2022_typeII_tests_reproduced"] == 37


def test_all_colony_slope_point_estimates_are_positive_but_imprecise():
    r = read_report()["within_colony_headwidth_results"]
    assert [x["colony"] for x in r] == ["Blue", "Orange", "Red"]
    assert [x["n_bees"] for x in r] == [14, 18, 27]
    assert [x["joined"] for x in r] == [9, 9, 13]
    assert [x["free"] for x in r] == [5, 9, 14]
    assert [x["observed_bees_in_overlap"] for x in r] == [9, 15, 25]
    for item, beta in zip(r, (6.34068830, 1.64309292, 1.85273939)):
        assert item["slope_free_minus_joined_per_mm"] == pytest.approx(beta)
        assert item["slope_free_minus_joined_per_mm"] > 0
        low, upper = item["descriptive_ols_95pct_interval"]
        assert low < 0 < upper
        assert item["within_treatment_headwidth_support_overlap"] is True


def test_separate_stage_outcomes_and_visit_time_sensitivity():
    rows = read_report()["pollen_stage_endpoint_sensitivity"]
    assert len(rows) == 6
    by = {
        (x["endpoint"], x["specification"]): x
        for x in rows
    }
    assert len(by) == 6
    expected = {
        ("log_body_basket", "with_postvisit_time"): (
            3.17546609, 0.95490686, 5.39602532, 0.0059290062
        ),
        ("log_body_basket", "without_postvisit_time"): (
            2.96504930, 0.76231320, 5.16778540, 0.0092891907
        ),
        ("log_stigma_body", "with_postvisit_time"): (
            -2.78571840, -8.51882097, 2.94738417, 0.33405905
        ),
        ("log_stigma_body", "without_postvisit_time"): (
            -2.68579253, -8.11164108, 2.74005603, 0.32529766
        ),
        ("log_stigma_count", "with_postvisit_time"): (
            -1.18324380, -5.93346082, 3.56697322, 0.61929578
        ),
        ("log_stigma_count", "without_postvisit_time"): (
            -1.33275174, -5.95722931, 3.29172583, 0.56568103
        )
    }
    assert set(by) == set(expected)
    for key, (b, low, high, p) in expected.items():
        row = by[key]
        assert row["n_bees"] == 59
        assert row["beta_free_minus_joined_size_per_mm"] == pytest.approx(b)
        assert row["bee_row_hc3_approximate_95pct_interval"] == pytest.approx(
            [low, high]
        )
        assert row["bee_row_hc3_approximate_p"] == pytest.approx(p)
    for spec in ("with_postvisit_time", "without_postvisit_time"):
        assert by[("log_body_basket", spec)][
            "bee_row_hc3_approximate_95pct_interval"][0] > 0
        for endpoint in ("log_stigma_body", "log_stigma_count"):
            low, hi = by[(endpoint, spec)][
                "bee_row_hc3_approximate_95pct_interval"]
            assert low < 0 < hi


def test_scientific_ceiling_for_postopen_stage_claims():
    r = read_report()
    scope = r["model_scope"]
    assert scope["HC3_not_colony_robust"] is True
    assert scope["not_cross_endpoint_effect_difference_test"] is True
    assert scope["post_treatment_covariate_caveat"] is True
    assert scope["trial_assignments_alternated_not_proven_randomized"] is True
    assert scope["sexually_viable_donor_paternity_not_measured"] is True
    assert scope["source_plant_cluster_not_identified"] is True
    assert scope["not_frozen_BALANCE_V4_or_Phi"] is True

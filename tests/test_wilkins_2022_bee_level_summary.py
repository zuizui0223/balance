"""Provenance-locked observed bee-level post-open robustness receipt.

These values must come from the authenticated 2022 source workflow, not be
introduced as a new model selection or independent biological replication.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT / "results" / "wilkins_2022" /
    "BEE_LEVEL_ROBUSTNESS_SUMMARY_20261122.json"
)


def readout():
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def test_actual_action_provenance_is_not_called_new_evolutionary_fitness():
    x = readout()
    assert x["status"] == (
        "ACTUAL_VERIFIED_SOURCE_POSTOPEN_EXPLORATORY_BEE_LEVEL_SENSITIVITY"
    )
    assert x["source"]["sha256"] == (
        "0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62"
    )
    assert x["scope"]["no_independent_genetic_paternity"] is True
    assert x["scope"]["not_new_BALANCE_V4_architecture_outcome"] is True
    assert x["scope"]["plant_source_clusters_unknown"] is True
    assert "NOT 3-colony-robust" in x["scope"]["covariance"]
    assert x["reproducibility"]["workflow_run_id"] == 45013279220
    assert x["reproducibility"]["verified_head_commit"] == (
        "4bded595c93d54de1914c766a713b51676b0a1e0"
    )
    assert x["reproducibility"]["artifact_zip_sha256"] == (
        "bceafeb74283bee7eabdc0315768b9f694ab25b19bf768b1a53cbcfa78fe87a8"
    )


def test_two_locked_models_and_each_actual_sign_preserving_deletion():
    models = {x["model"]: x for x in readout()["results"]}
    assert set(models) == {"full_three_way", "reduced_two_way"}
    expected = {
        "full_three_way": (
            3.52554343, 1.47539422, 0.020760817,
            (0.56062775, 6.49045912),
            (1.85597511, 4.31832139),
        ),
        "reduced_two_way": (
            3.17546609, 1.10660193, 0.0059290062,
            (0.95490686, 5.39602532),
            (2.76152657, 3.44974395),
        ),
    }
    for name, row in models.items():
        beta, se, p, ci, colonies = expected[name]
        assert row["n_bees"] == 59
        assert row["beta_free_minus_joined_per_mm"] == pytest.approx(beta)
        assert row["hc3_se"] == pytest.approx(se)
        assert row["p_approximate_bee_row_hc3"] == pytest.approx(p)
        assert row["hc3_approximate_95pct_interval"] == pytest.approx(ci)
        assert row["leave_one_colony_beta_range"] == pytest.approx(colonies)
        assert row["leave_one_bee_same_sign_count"] == row["leave_one_bee_total"] == 59
        assert row["leave_one_colony_same_sign_count"] == row["leave_one_colony_total"] == 3
        assert row["leave_one_colony_beta_range"][0] > 0
        assert ci[0] > 0


def test_saved_raw_result_is_diagnostic_not_preregistered_directional_v4():
    x = readout()
    assert "postopen" in x["status"].lower()
    assert x["source"]["colony_count"] == 3
    assert x["response"] == "log(BodyPollen/CorbiculaPollen)"
    assert x["reproducibility"]["original_five_model_source_chisq_replay_max_abs_error"] < 0.002
    assert "not-architecture-evolution-or-donor-paternity-or-fitness" in x[
        "claim_ceiling"
    ]

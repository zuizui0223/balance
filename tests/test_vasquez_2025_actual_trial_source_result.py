"""Pin genuine original 15-trial source-throughput reanalysis, not source means product.

This is actual Zenodo data.csv (60 nested recipient rows) measured in a
source-only GitHub Action and recorded without redistributing original rows.
"""
from pathlib import Path
import json

import pytest

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"results"/"vasquez_2025"/"ACTUAL_TRIAL_PTE_AND_PRODUCED_DELIVERY_20261122.json"


def source():
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_genuine_zenodo_trial_level_source_identity_and_hierarchy():
    x=source()
    assert x["status"]=="ORIGINAL_ZENODO_60_RECIPIENT_ROWS_AGGREGATED_TO_15_AUTHENTIC_TRIALS"
    assert x["source_hash"]=="484ed52ac611dbc6dc1831320a6c54d314492e9830823edd8934690c35205b79"
    assert x["total_donor_trials"]==15
    assert x["nested_stigma_rows"]==60
    assert x["independent_original_research_programmes"]==1
    assert x["raw_trial_rows_in_repo"]==0
    assert x["provenance"]["workflow_run_id"]==45030158810
    assert x["provenance"]["original_run_head"]=="f2fc10583e3023f9d811ed6d655034a6378fdeee"
    assert x["provenance"]["artifact_id"]==14756788770


def test_actual_h_over_a_h_over_b_and_b_over_a_are_distinct():
    x=source()
    actual={
        "S.rostratum":(6,13.5470068718319,.8610764890798217,.06495702836418192),
        "S.dulcamara":(9,37.76799408538001,1.0006996406397812,.3137500727232434)
    }
    for species,(n,rel,pte,full) in actual.items():
        row=x["species"][species]
        assert row["n_donor_bee_trials"]==row["n_donor_bees"]==n
        mean=row["mean_per_trial"]
        assert mean["fraction_released_pct_of_measured_source"]==pytest.approx(rel)
        assert mean["pollen_transfer_efficiency_pct_of_removed"]==pytest.approx(pte)
        assert mean["source_to_four_stigmas_pct_of_production"]==pytest.approx(full)
        assert "n_donor_bee_trials" in row
        # Source species means produce materially different estimates if
        # naively multiplied; covariance between within-trial variables matters.
        assert abs(full-rel*pte/100)>.03
    assert x["species"]["S.dulcamara"]["hive_counts"]=={"B1":5,"B2":4}
    assert x["species"]["S.rostratum"]["hive_counts"]=={"B1":5,"B2":1}


def test_actual_predefined_trial_bootstrap_intervals_and_ceiling():
    x=source()
    expected={
        "fraction_released_pct_of_measured_source":
            (24.22098721354811,(11.353309437965336,37.142196066434686)),
        "pollen_transfer_efficiency_pct_of_removed":
            (.13962315155995952,(-.7781930252539648,.9185107046616129)),
        "source_to_four_stigmas_pct_of_production":
            (.24879304435906147,(.12359794566221402,.4129667851068951))
    }
    for field,(diff,interval) in expected.items():
        row=x["predefined_trial_level_species_mean_differences"][field]
        assert row["dulcamara_minus_rostratum_pct_points"]==pytest.approx(diff)
        assert row["descriptive_95pct_trial_bootstrap_interval"]==pytest.approx(interval)
        assert row["bootstrap_replicates"]==20000
        assert row["not_random_assignment_or_colony_robust_confidence"] is True
    limits=x["statistical_limits"]
    assert limits["no_inferential_species_causality"] is True
    assert limits["no_colony_robust_population_generalization"] is True
    assert limits["no_ground_corbicula_terminal_body_source_rows"] is True
    assert limits["no_genetic_paternity"] is True

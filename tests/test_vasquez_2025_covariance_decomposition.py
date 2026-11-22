"""Regression guards for the post-open paired release/PTE covariance audit.

All in-memory paired-donor examples in this file are synthetic TEST FIXTURES.
Original empirical results are source-locked separately in the
15-donor original source receipt and executed GitHub Actions workflow.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.decompose_vasquez_2025_release_transfer import (
    _components,
    _pearson,
    _percentile,
    _spearman,
    _symmetric_decomposition,
    analyze_paired_trials,
)
from scripts.audit_vasquez_2025_trial_structure import RAW_SHA256

ROOT=Path(__file__).resolve().parents[1]
RESULT=(ROOT/"results"/"vasquez_2025"/
        "ACTUAL_TRIAL_PTE_AND_PRODUCED_DELIVERY_20261122.json")


def source_numeric_original():
    return json.loads(RESULT.read_text(encoding="utf-8"))


def make_synthetic_source():
    rows=[]
    for species,n,offset in (
        ("S.rostratum",6,0),
        ("S.dulcamara",9,1),
    ):
        for i in range(n):
            rfrac=.08+.03*i+.025*offset
            tfrac=.023-.002*i+.003*offset
            b=100000*rfrac
            h=b*tfrac
            rows.append({
                "source_species":species,
                "source_hive":"B1" if i%2==0 else "B2",
                "source_bee_id":f"{species}-{i}",
                "fraction_released_pct_of_measured_source":100*rfrac,
                "pollen_transfer_efficiency_pct_of_removed":100*tfrac,
                "source_to_four_stigmas_pct_of_production":100*rfrac*tfrac,
                "measured_released_grains":b,
                "measured_recipient_stigma_grains":h,
            })
    return {
        "source":{
            "raw_csv_sha256":RAW_SHA256,
            "n_donor_trials":15,
            "n_original_recipient_measurements":60,
        },
        "trials":rows,
    }


def test_source_mean_product_is_not_trial_mean_product():
    # This is an independent arithmetic check using prior authentic
    # source-trial aggregate estimates, no synthetic field measurements.
    source=source_numeric_original()
    expected={
        "S.rostratum":(-0.051693062783190386,0.1166500911473723),
        "S.dulcamara":(-0.0641941083660082,0.3779441810892516),
    }
    for sp,(cov_pp,naive_product_pp) in expected.items():
        a=source["species"][sp]["mean_per_trial"]
        r=a["fraction_released_pct_of_measured_source"]/100
        t=a["pollen_transfer_efficiency_pct_of_removed"]/100
        y=a["source_to_four_stigmas_pct_of_production"]/100
        assert (y-r*t)*100==pytest.approx(cov_pp)
        assert (r*t)*100==pytest.approx(naive_product_pp)
        assert y<r*t
    assert source["total_donor_trials"]==15


def test_descriptive_decomposition_identity_on_paired_synthetic_donors():
    dummy=make_synthetic_source()
    group={
        sp:[
            {
                "release_fraction":x["fraction_released_pct_of_measured_source"]/100,
                "transfer_conditional_fraction":x[
                    "pollen_transfer_efficiency_pct_of_removed"
                ]/100,
                "source_to_stigma_fraction":x[
                    "source_to_four_stigmas_pct_of_production"
                ]/100,
            }
            for x in dummy["trials"] if x["source_species"]==sp
        ]
        for sp in ("S.rostratum","S.dulcamara")
    }
    r=_symmetric_decomposition(group)
    assert r["decomposition_error_pp"]==pytest.approx(0,abs=1e-12)
    assert sum(
        r[k] for k in (
            "release_component_percentage_points",
            "conditional_transfer_component_percentage_points",
            "paired_covariance_component_percentage_points"
        )
    )==pytest.approx(
        r["actual_dulcamara_minus_rostratum_source_throughput_pp"]
    )
    assert all(
        _components(x)["paired_release_transfer_population_covariance"]<0
        for x in group.values()
    )


def test_synthetic_bootstrap_preserves_donor_pairs_and_source_denominator_caveat():
    data=make_synthetic_source()
    a=analyze_paired_trials(data,bootstrap_count=120)
    b=analyze_paired_trials(data,bootstrap_count=120)
    assert a==b
    assert a["n_original_donor_trials"]==15
    assert a["n_recipient_rows_nested"]==60
    assert a["raw_donor_row_values_exported"] is False
    assert a["fixed_bootstrap_seed"]==20261122
    assert a["strict_interpretation"][
        "negative_covariance_is_NOT_evidence_of_causal_pollen_release_transfer_tradeoff"
    ] is True
    for sp in ("S.rostratum","S.dulcamara"):
        v=a["species"][sp]
        assert v["paired_covariance_pct_points"]<0
        assert v["n_single_donor_deletions"]==v["n_donor_bee_trials"]
        assert v["covariance_sign_preserving_single_donor_deletions"]==v[
            "n_donor_bee_trials"
        ]
        assert v["no_correlation_p_values"] is True
    for row in a["paired_trial_bootstrap_descriptive"].values():
        assert row["bootstrap_resamples"]==120
        assert row["not_hive_or_plant_cluster_robust"] is True


def test_a_spurious_correlation_warning_is_explicit_and_no_p_value_in_the_output():
    a=analyze_paired_trials(make_synthetic_source(),bootstrap_count=100)
    assert a["strict_interpretation"][
        "ratio_shared_denominator_B_induces_spurious_correlation_risk"
    ] is True
    assert all(v["no_correlation_p_values"] is True for v in a["species"].values())
    assert "paternity" in json.dumps(a)


def test_wrong_original_receipt_or_observation_count_fails_closed():
    dummy=make_synthetic_source()
    dummy["source"]["raw_csv_sha256"]="not original data"
    with pytest.raises(ValueError,match="source-verified"):
        analyze_paired_trials(dummy,bootstrap_count=100)
    dummy=make_synthetic_source()
    dummy["trials"].pop()
    with pytest.raises(ValueError,match="15 independent"):
        analyze_paired_trials(dummy,bootstrap_count=100)


def test_percentiles_and_rank_correlations_work_with_ties():
    assert _percentile([1,2,3],0)==pytest.approx(1)
    assert _percentile([1,2,3],1)==pytest.approx(3)
    assert _percentile([1,2,3],.5)==pytest.approx(2)
    assert _pearson([1,2,3],[3,2,1])==pytest.approx(-1)
    assert _spearman([1,2,3],[3,2,1])==pytest.approx(-1)
    assert _spearman([1,2,2,3],[4,2,2,1])==pytest.approx(-1)

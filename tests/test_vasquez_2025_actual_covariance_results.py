"""Pin actual authentic trial-level release/PTE decomposition results.

Post-open arithmetic/ratio covariance is descriptive and must not be promoted
to a new independent field experiment or a causal morphological mechanism.
"""
import json
from pathlib import Path

import pytest


ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"vasquez_2025"/"PAIRED_RELEASE_TRANSFER_COVARIANCE_20261122.json"


def original():
    return json.loads(OUT.read_text(encoding="utf-8"))


def test_actual_source_and_no_fitness_promotion():
    r=original()
    assert r["status"]=="POSTOPEN_AUTHENTIC_ORIGINAL_15_TRIAL_ARITHMETIC_DECOMPOSITION_NOT_CAUSAL"
    assert r["n_original_donor_trials"]==15
    assert r["n_recipient_rows_nested"]==60
    assert r["source_sha256"]=="484ed52ac611dbc6dc1831320a6c54d314492e9830823edd8934690c35205b79"
    assert r["fixed_bootstrap_seed"]==20261122
    assert r["raw_donor_row_values_exported"] is False
    assert r["provenance"]["workflow_run_id"]==45031783505
    assert r["provenance"]["artifact_id"]==14758620232
    assert r["provenance"]["zip_sha256"]=="b22cf7db0312d6ed4435fd1fdea98aa5bf400f1d58f74a0814c3099a12db8783"
    scope=r["strict_interpretation"]
    assert all(scope.values())
    assert scope["negative_covariance_is_NOT_evidence_of_causal_pollen_release_transfer_tradeoff"] is True
    assert scope["no_frozen_BALANCE_U2_U6_V4_update"] is True


def test_negative_paired_covariance_is_actual_but_absolute_grain_relations_diverge():
    r=original()
    s=r["species"]
    assert set(s)=={"S.rostratum","S.dulcamara"}
    ro=s["S.rostratum"]
    du=s["S.dulcamara"]
    for sp,x,n,cov,lo,hi in [
        ("S.rostratum",ro,6,-.051693062783190406,-.0954491404172211,-.003533934133910532),
        ("S.dulcamara",du,9,-.0641941083660082,-.1356806351914839,.014374684654739484)
    ]:
        assert x["n_donor_bee_trials"]==n
        assert x["paired_covariance_pct_points"]==pytest.approx(cov)
        assert x["paired_covariance_pct_points"]<0
        assert x["covariance_sign_preserving_single_donor_deletions"]==n
        assert x["n_single_donor_deletions"]==n
        assert x["product_of_separate_group_means_pct"] > x[
            "group_mean_full_source_transfer_pct"]
        boot=r["paired_trial_bootstrap_descriptive"][
            "cov_rostratum_pp" if sp=="S.rostratum" else "cov_dulcamara_pp"]
        assert boot["trial_bootstrap_95pct_interval"]==pytest.approx([lo,hi])
        assert boot["not_hive_or_plant_cluster_robust"] is True
    assert ro["release_pct_vs_conditional_PTE_spearman"]==pytest.approx(-.8857142857142857)
    assert du["release_pct_vs_conditional_PTE_spearman"]==pytest.approx(-.55)
    assert ro["absolute_released_grains_vs_absolute_stigmatic_grains_spearman"]==pytest.approx(-.8857142857142857)
    assert du["absolute_released_grains_vs_absolute_stigmatic_grains_spearman"]==pytest.approx(.65)
    assert ro["absolute_released_grains_vs_absolute_stigmatic_grains_spearman"]<0
    assert du["absolute_released_grains_vs_absolute_stigmatic_grains_spearman"]>0


def test_exact_arithmetic_difference_and_bootstrap_component_limits():
    r=original()
    out=r["symmetric_between_species_arithmetic_decomposition"]
    expected={
        "release_component_percentage_points":.22547027916213794,
        "conditional_transfer_component_percentage_points":.03582381077974134,
        "paired_covariance_component_percentage_points":-.012501045582817788,
        "actual_dulcamara_minus_rostratum_source_throughput_pp":.2487930443590615
    }
    for key,value in expected.items():
        assert out[key]==pytest.approx(value)
    assert out["decomposition_error_pp"]==pytest.approx(0,abs=1e-12)
    assert sum(out[k] for k in list(expected)[:3])==pytest.approx(
        out["actual_dulcamara_minus_rostratum_source_throughput_pp"]
    )
    expected_ci={
        "release_component_percentage_points":(.0921244261352006,.42574316424921427),
        "conditional_transfer_component_percentage_points":(-.19879611193832597,.23636485192509607),
        "paired_covariance_component_percentage_points":(-.10896404705985765,.07857225219766545),
        "actual_dulcamara_minus_rostratum_source_throughput_pp":(.12599529279023952,.4117856227627733)
    }
    for key,ci in expected_ci.items():
        line=r["paired_trial_bootstrap_descriptive"][key]
        assert line["trial_bootstrap_95pct_interval"]==pytest.approx(ci)
        assert line["bootstrap_resamples"]==20000
    assert expected_ci["release_component_percentage_points"][0]>0
    assert (expected_ci["paired_covariance_component_percentage_points"][0] < 0
            < expected_ci["paired_covariance_component_percentage_points"][1])

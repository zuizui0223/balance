"""Original-source R nested covariance result, not a source data reanalysis fixture."""
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/"data/DALECHAMPIA_2015_NESTED_BLOSSOM_SOURCE_VERIFIED_V1.json"


def test_exact_source_support_and_dominant_within_blossom_variation():
    d=json.loads(FREEZE.read_text(encoding="utf-8"))
    assert d["status"]=="ORIGINAL_DRYAD_NESTED_COVARIANCE_STRONGLY_SUPPORTED_NOT_CAUSAL"
    s=d["same_raw_source_and_fixed_effects"]
    assert (s["numeric_ge20mg_seed_masses"],s["blossoms"],s["mothers"])==(1103,132,36)
    assert s["seed_morphological_abortion_independently_observed"] is False
    x=d["random_intercept_comparison"]
    assert x["maternal_only"]["ML_AIC"]==pytest.approx(6152.411839)
    assert x["maternal_plus_blossom"]["ML_AIC"]==pytest.approx(5135.56109)
    assert x["nested_minus_maternal_only_AIC"]==pytest.approx(-1016.85075)
    assert x["maternal_plus_blossom"]["same_blossom_seed_icc"]==pytest.approx(0.886298)
    assert x["maternal_plus_blossom"]["different_blossoms_same_mother_seed_icc"]==pytest.approx(0.453457)
    assert x["maternal_plus_blossom"]["blossom_variance"]>0


def test_source_treatment_standard_errors_triple_when_blossoms_are_modelled():
    d=json.loads(FREEZE.read_text(encoding="utf-8"))
    q=d["reml_treatment_effects"]
    assert len(q)==3
    assert all(3.0<=x["SE_inflation_factor"]<=3.2 for x in q)
    assert all(x["includes_zero"] is True for x in q)
    assert q[0]["nested_asymptotic_normal_95_mg"]==pytest.approx([-3.772445,0.113812])
    assert q[1]["nested_asymptotic_normal_95_mg"]==pytest.approx([-3.079623,0.84067])


def test_original_nlme_reproduction_hold_remains_distinct_from_new_covariance():
    d=json.loads(FREEZE.read_text(encoding="utf-8"))
    l=d["interpretation_limits"]
    assert l["alternative_random_effect_specification_is_posthoc"] is True
    assert l["original_published_R_code_recovered"] is False
    assert l["original_published_mixed_model_AIC_reproduced"] is False
    assert l["carbon_assimilation_in_seed_traced"] is False
    assert l["structural_BALANCE_occupancy_identified"] is False
    assert l["additional_independent_biological_clusters"]==0
    assert len(d["generated_source_readout_sha256"])==64
    assert d["github_artifact_id"]==12055246869

"""Ground actual paired-stigma/bee pollen tests in the archived source log.

The joint test is on the original 59 bee observations, not on pooled pollen
grains and not on independently repeated evolutionary changes.
"""
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"results"/"wilkins_2022"/"PAIRED_DESTINATION_CONTRASTS_20261122.json"


def load():
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_genuine_exploratory_source_provenance_and_uncertainty_ceiling():
    x=load()
    assert x["status"]=="ACTUAL_ORIGINAL_SOURCE_POSTOPEN_PAIRED_BEE_COVARIANCE_TEST_NOT_CONFIRMATORY"
    assert x["source"]["original_csv_sha256"]=="0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62"
    assert x["source"]["analysis_bees"]==59
    assert x["source"]["original_bee_colonies"]==3
    assert x["design"]["new_frozen_V4_outcome_rows"]==0
    assert x["design"]["genetically_verified_donor_paternity_unmeasured"] is True
    assert x["design"]["postopen_multiple_outcomes_no_multiplicity_adjustment"] is True
    assert x["provenance"]["original_verified_run_id"]==45017971832
    assert x["provenance"]["artifact_id"]==14752347567
    assert x["provenance"]["artifact_sha256"]=="3ea5ea51fdca69e8c808c449f31e4a2624fb53b466d2bd83e52d4dc467e9a690"
    assert x["provenance"]["archived_typeII_replayed"]==37


def test_four_direct_stage_contrasts_with_same_bee_covariance():
    x=load()
    grouped={}
    for row in x["stage_results"]:
        grouped[(row["specification"],row["contrast"])]=row
        assert row["n_bees"]==59
    assert len(grouped)==8
    expected={
      ("with_postvisit_time","body_vs_basket"):(3.17546609,[0.95490686,5.39602532],0.0059290062),
      ("with_postvisit_time","stigma_vs_body"):(-2.78571840,[-8.51882097,2.94738417],0.33405905),
      ("with_postvisit_time","stigma_vs_basket"):(0.38974769,[-4.25952497,5.03902035],0.86706527),
      ("with_postvisit_time","difference_body_vs_basket_minus_stigma_vs_basket"):(2.78571840,[-2.94738417,8.51882097],0.33405905),
      ("without_postvisit_time","body_vs_basket"):(2.96504930,[0.76231320,5.16778540],0.0092891907),
      ("without_postvisit_time","stigma_vs_body"):(-2.68579253,[-8.11164108,2.74005603],0.32529766),
      ("without_postvisit_time","stigma_vs_basket"):(0.27925677,[-4.23137684,4.78989039],0.90164469),
      ("without_postvisit_time","difference_body_vs_basket_minus_stigma_vs_basket"):(2.68579253,[-2.74005603,8.11164108],0.32529766),
    }
    assert set(expected)==set(grouped)
    for key,(beta,interval,p) in expected.items():
        row=grouped[key]
        assert row["beta_free_minus_joined_headwidth_per_mm"]==pytest.approx(beta)
        assert row["approximate_bee_row_hc3_95ci"]==pytest.approx(interval)
        assert row["approximate_bee_row_hc3_p"]==pytest.approx(p)
    for spec in ("with_postvisit_time","without_postvisit_time"):
        b=grouped[(spec,"body_vs_basket")]["beta_free_minus_joined_headwidth_per_mm"]
        s=grouped[(spec,"stigma_vs_body")]["beta_free_minus_joined_headwidth_per_mm"]
        t=grouped[(spec,"stigma_vs_basket")]["beta_free_minus_joined_headwidth_per_mm"]
        delta=grouped[(spec,"difference_body_vs_basket_minus_stigma_vs_basket")]
        assert b+s==pytest.approx(t,abs=1e-7)
        assert b-t==pytest.approx(delta["beta_free_minus_joined_headwidth_per_mm"],abs=1e-7)
        low,high=delta["approximate_bee_row_hc3_95ci"]
        assert low<0<high
        assert delta["approximate_bee_row_hc3_p"]>0.3


def test_omnibus_positive_but_direct_stage_difference_unidentified():
    vals={v["specification"]:v for v in load()["omnibus_results"]}
    assert set(vals)=={"with_postvisit_time","without_postvisit_time"}
    assert vals["with_postvisit_time"]["wald_2df"]==pytest.approx(9.44353826)
    assert vals["with_postvisit_time"]["asymptotic_bee_row_hc3_2df_p"]==pytest.approx(0.0088994204)
    assert vals["without_postvisit_time"]["wald_2df"]==pytest.approx(7.80354547)
    assert vals["without_postvisit_time"]["asymptotic_bee_row_hc3_2df_p"]==pytest.approx(0.02020606)

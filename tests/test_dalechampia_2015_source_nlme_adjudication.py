"""Synthetic contracts for archival R nlme Table-2 adjudication.

Test fixtures are algebraic stand-ins, NOT Pélabon et al. 2015 observations.
"""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts.adjudicate_dalechampia_2015_nlme import (
    MODELS, VARIANT, _rows, adjudicate_published_nlme,
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/DALECHAMPIA_2015_PUBLISHED_NLME_REPLAY_CONTRACT_V1.json"


def _fixture(*, delta=0.0):
    x=json.loads(SOURCE.read_text(encoding="utf-8"))
    files={"Pelabon et al FE file 1.txt":b"synthetic seed bytes",
           "Pelabon et al FE file 2.txt":b"synthetic gas bytes"}
    x["original_file_sha256"]={
        name:hashlib.sha256(b).hexdigest() for name,b in files.items()
    }
    paper=x["source_table2_ml_aic"]
    rows=[]
    for m in (*MODELS,VARIANT):
        rows.append({
            "model_id":m,"n_obs":"1103","n_mothers":"36",
            "ml_aic":str(paper[m]+delta if m in MODELS
                         else x["source_residual_variance_sensitivity"]
                             ["treatment_specific_residual_varident_aic_ml_reported"]+delta),
            "ml_loglik":"-3000.0","ml_bic":"6050.0","ml_residual_sd":"3.1",
        })
    coefficients=[
        {"model_id":"ped_treat","term":name,
         "ml_point":str(v.get("estimate_mg",v.get("estimate_mg_per_mm"))),
         "reml_point":str(v.get("estimate_mg",v.get("estimate_mg_per_mm"))),
         "reml_se":str(v.get("reported_se_mg",v.get("reported_se_mg_per_mm")))}
        for name,v in x["printed_source_remL_fixed_effects_references"]["ped_treat"].items()
    ]
    return x,rows,coefficients,files


def test_synthetic_exact_table2_match_never_promotes_biology():
    x,rows,coeffs,files=_fixture()
    r=adjudicate_published_nlme(x,rows,coeffs,files)
    assert r["status"]=="TABLE2_ALL_SIX_MODELS_MATCH_SOURCE_AIC"
    assert r["all_six_within_registered_AIC_tolerance"] is True
    assert len(r["published_table2"])==6
    assert r["primary_aic_delta"]==0
    assert r["ecological_claim_ceiling"]["publication_error_proven"] is False
    assert r["ecological_claim_ceiling"]["structural_BALANCE_occupancy_identified"] is False
    assert r["modern_R_nlme_is_historical_R_2_15_2_exact_recreation"] is False


def test_synthetic_uniform_AIC_gap_is_nonconfirmatory_HOLD():
    x,rows,coeffs,files=_fixture(delta=149)
    r=adjudicate_published_nlme(x,rows,coeffs,files)
    assert r["status"]=="PUBLISHED_TABLE2_NLME_NUMERICAL_REPRODUCTION_HOLD"
    assert r["primary_aic_delta"]==149.0
    assert all(v["R_minus_published_AIC"]==149 for v in r["published_table2"])
    assert r["ecological_claim_ceiling"]["publication_error_proven"] is False


def test_single_source_model_drift_does_not_get_ignored():
    x,rows,coeffs,files=_fixture()
    rows[2]["ml_aic"]=str(float(rows[2]["ml_aic"])+2.5)
    r=adjudicate_published_nlme(x,rows,coeffs,files)
    assert r["all_six_within_registered_AIC_tolerance"] is False
    assert r["status"]=="PUBLISHED_TABLE2_NLME_NUMERICAL_REPRODUCTION_HOLD"
    assert sum(not d["matches_source_within_registered_tolerance"]
               for d in r["published_table2"])==1


def test_missing_or_duplicate_registered_source_model_rejected():
    x,rows,coeffs,files=_fixture()
    with pytest.raises(ValueError,match="missing candidate"):
        adjudicate_published_nlme(x,rows[:-1],coeffs,files)
    with pytest.raises(ValueError,match="unexpected/duplicate"):
        adjudicate_published_nlme(x,rows+[rows[0]],coeffs,files)


def test_source_hash_and_biological_support_fail_closed():
    x,rows,coeffs,files=_fixture()
    with pytest.raises(ValueError,match="SHA256"):
        adjudicate_published_nlme(x,rows,coeffs,{**files,"Pelabon et al FE file 1.txt":b"altered"})
    changed=copy.deepcopy(rows)
    changed[0]["n_obs"]="1104"
    with pytest.raises(ValueError,match="n/maternal unit"):
        adjudicate_published_nlme(x,changed,coeffs,files)
    with pytest.raises(ValueError,match="both exact"):
        adjudicate_published_nlme(x,rows,coeffs,{"wrong filename":b"bytes"})


def test_missing_fixed_effect_reference_is_not_imputed():
    x,rows,coeffs,files=_fixture()
    with pytest.raises(ValueError,match="REML fixed term"):
        adjudicate_published_nlme(x,rows,coeffs[:-1],files)


def test_published_AIC_frozen_and_retrospective_not_prereg_ecology():
    x=json.loads(SOURCE.read_text(encoding="utf-8"))
    assert len(x["source_table2_ml_aic"])==6
    assert x["source_table2_ml_aic"]["ped_treat"]==6005.72
    assert x["source_table2_ml_aic"]["ped_seedset_treat"]==6006.35
    assert x["source_residual_variance_sensitivity"]["treatment_specific_residual_varident_aic_ml_reported"]==5987.3
    assert x["replay_rules"]["source_AIC_abs_tolerance"]==1.0
    assert x["original_R_code_available"] is False
    assert x["evidence_limits"]["new_biological_clusters"]==0


def test_exact_csv_reader_requires_fields_and_rows(tmp_path):
    p=tmp_path/"bad.csv";p.write_text("model_id,ml_aic\nped_treat,6005.72\n",encoding="utf-8")
    with pytest.raises(ValueError,match="missing required"):
        _rows(p,{"model_id","n_obs","ml_aic"})
    p.write_text("model_id,n_obs,ml_aic\n",encoding="utf-8")
    with pytest.raises(ValueError,match="empty"):
        _rows(p,{"model_id","n_obs","ml_aic"})

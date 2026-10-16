"""Independent source-covariance controls; fixtures here are not field data."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts.adjudicate_dalechampia_nested_nlme import adjudicate_nested_covariance


ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/"data/DALECHAMPIA_2015_NESTED_BLOSSOM_COVARIANCE_CONTRACT_V1.json"


def fake(advantage=-30):
    c=json.loads(FREEZE.read_text(encoding="utf-8"))
    files={name:(name+" synthetic").encode() for name in c["source_files_sha256"]}
    c["source_files_sha256"]={n:hashlib.sha256(b).hexdigest() for n,b in files.items()}
    rows=[]
    for name,nested in (("maternal_only",False),("maternal_plus_blossom",True)):
        var_m,var_b,var_e=(19.,0.,14.) if not nested else (15.,12.,4.)
        total=var_m+var_b+var_e
        rows.append({
            "model_id":name,"n_seeds":"1103","n_blossoms":"132","n_mothers":"36",
            "ml_aic":str(6152.411839+(advantage if nested else 0)),
            "ml_loglik":"-3000","mother_variance":str(var_m),
            "blossom_variance":str(var_b),"residual_variance":str(var_e),
            "implied_same_blossom_seed_correlation":str((var_m+var_b)/total),
            "implied_same_mother_different_blossom_seed_correlation":str(var_m/total),
        })
    coeff=[]
    for name,nested in (("maternal_only",False),("maternal_plus_blossom",True)):
        for idx,term in enumerate(("treatcodebag","treatcodecut","treatcodecutcont","ped")):
            orig_se=(.318239,.322560,.321516,1.01)[idx]
            se=orig_se*(3 if nested else 1)
            coeff.append({
                "model_id":name,"term":term,"reml_beta":str(-1.8 if idx==0 else .3),
                "reml_se":str(se),"normal_wald95_lo":str(-1.8-1.96*se),
                "normal_wald95_hi":str(-1.8+1.96*se),
            })
    return c,rows,coeff,files


def test_nested_bl0ssom_source_improvement_only_a_covariance_result():
    c,r,b,f=fake()
    v=adjudicate_nested_covariance(c,r,b,f)
    assert v["status"]=="NESTED_BLOSSOM_COVARIANCE_FITS_BETTER_IN_SOURCE"
    assert v["n_blossoms"]==132
    assert v["record_count"]==1103
    assert v["n_mothers"]==36
    assert v["nested_minus_maternal_only_AIC"]==-30
    assert v["implied_same_blossom_seed_correlation"]==pytest.approx(27/31)
    assert v["source_REML_treatment_effects"][0]["nested_to_maternal_only_SE_ratio"]==3
    assert v["structural_BALANCE_occupancy_identified"] is False
    assert v["causal_bract_photosynthesis_identified"] is False
    assert v["published_2015_nlme_model_reproduced"] is False


def test_source_covariance_advantage_can_be_unresolved():
    c,r,b,f=fake(advantage=-1)
    d=adjudicate_nested_covariance(c,r,b,f)
    assert d["status"]=="NESTED_BLOSSOM_COVARIANCE_ADVANTAGE_UNRESOLVED"


def test_missing_hash_and_unmatched_model_support_fail_closed():
    c,r,b,f=fake()
    wrong=dict(f)
    first=next(iter(wrong))
    wrong[first]=b"altered"
    with pytest.raises(ValueError,match="original archived Dryad"):
        adjudicate_nested_covariance(c,r,b,wrong)
    bad=copy.deepcopy(r)
    bad[1]["n_blossoms"]="131"
    with pytest.raises(ValueError,match="biological source unit"):
        adjudicate_nested_covariance(c,bad,b,f)
    with pytest.raises(ValueError,match="two same-source"):
        adjudicate_nested_covariance(c,r[:1],b,f)


def test_model_covariance_positive_and_effects_required():
    c,r,b,f=fake()
    bad=copy.deepcopy(r)
    bad[1]["blossom_variance"]="-2"
    with pytest.raises(ValueError,match="variance"):
        adjudicate_nested_covariance(c,bad,b,f)
    with pytest.raises(ValueError,match="fixed-effect contrasts missing"):
        adjudicate_nested_covariance(c,r,b[:-1],f)


def test_maternal_only_source_match_required():
    c,r,b,f=fake()
    bad=copy.deepcopy(r)
    bad[0]["ml_aic"]="6005.72"
    with pytest.raises(ValueError,match="not reproduced"):
        adjudicate_nested_covariance(c,bad,b,f)
    bb=copy.deepcopy(b)
    bb[0]["reml_se"]="1.0"
    with pytest.raises(ValueError,match="SE changed"):
        adjudicate_nested_covariance(c,r,bb,f)


def test_contract_contains_no_source_unseen_structural_result():
    d=json.loads(FREEZE.read_text(encoding="utf-8"))
    assert d["fixed_observations"]["experimental_treatment_unit"]=="blossom"
    assert d["fixed_observations"]["numeric_ge20mg_seed_masses"]==1103
    assert d["scientific_ceiling"]["historical_published_nlme_reproduced"] is False
    assert d["scientific_ceiling"]["structural_BALANCE_occupancy_identified"] is False

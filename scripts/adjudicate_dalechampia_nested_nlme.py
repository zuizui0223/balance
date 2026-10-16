#!/usr/bin/env python3
"""Adjudicate original-Dryad maternal vs nested-blossom nlme covariance.

This posthoc source sensitivity uses identical seed rows/fixed effects in both
models. It detects whether seeds share a blossom-level residual correlation,
without treating a different covariance model as an exact reproduction of
Pélabon et al. (2015) or an architecture differentiation experiment.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

SCHEMA="DALECHAMPIA_2015_NESTED_BLOSSOM_COVARIANCE_READOUT_V1"
IDS=("maternal_only","maternal_plus_blossom")
ARMS=("treatcodebag","treatcodecut","treatcodecutcont")


def _finite(value, name) -> float:
    if isinstance(value,bool):
        raise ValueError(f"{name} cannot be boolean")
    try:
        x=float(value)
    except (ValueError,TypeError,OverflowError) as exc:
        raise ValueError(f"{name} not numeric") from exc
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite")
    return x


def _read(path:Path, fields:set[str]) -> list[dict[str,str]]:
    with path.open("r",encoding="utf-8",newline="") as src:
        reader=csv.DictReader(src)
        if not set(reader.fieldnames or ()).issuperset(fields):
            raise ValueError("R covariance CSV missing model fields")
        rows=list(reader)
    if not rows:
        raise ValueError("R covariance CSV empty")
    return rows


def adjudicate_nested_covariance(
    freeze:dict, model_rows:list[dict], effect_rows:list[dict],
    originals:dict[str,bytes],
) -> dict:
    if (not isinstance(freeze,dict) or
            freeze.get("schema_version")!="DALECHAMPIA_2015_NESTED_BLOSSOM_COVARIANCE_CONTRACT_V1"
            or freeze.get("status")!="POSTHOC_EXPERIMENTAL_UNIT_SENSITIVITY_NO_NEW_FIELD_DATA"):
        raise ValueError("registered nesting sensitivity contract is not valid")
    sha=freeze["source_files_sha256"]
    if set(originals)!=set(sha) or any(
        type(originals[n]) is not bytes or hashlib.sha256(originals[n]).hexdigest()!=sha[n]
        for n in sha
    ):
        raise ValueError("exact original archived Dryad files missing or altered")
    fixed=freeze["fixed_observations"]
    if fixed["experimental_treatment_unit"]!="blossom" or fixed["measured_unit"]!="seed":
        raise ValueError("experimental-unit identity has changed")
    model_map={}
    for row in model_rows:
        key=row.get("model_id")
        if key not in IDS or key in model_map:
            raise ValueError("unknown or duplicate registered covariance model")
        for col,value in (
            ("n_seeds",1103),("n_blossoms",132),("n_mothers",36)
        ):
            if _finite(row.get(col),f"{key}.{col}") != value:
                raise ValueError(f"{key} original biological source unit count drifted")
        model_map[key]={
            k:_finite(row.get(k),f"{key}.{k}")
            for k in (
                "ml_aic","ml_loglik","mother_variance","blossom_variance",
                "residual_variance","implied_same_blossom_seed_correlation",
                "implied_same_mother_different_blossom_seed_correlation",
            )
        }
    if set(model_map)!=set(IDS):
        raise ValueError("two same-source variance models required")
    maternal,nested=(model_map[k] for k in IDS)
    if not all(m["residual_variance"]>0 and m["mother_variance"]>=0
               for m in (maternal,nested)):
        raise ValueError("nonphysical source covariance estimates")
    if maternal["blossom_variance"]!=0 or nested["blossom_variance"]<0:
        raise ValueError("random blossom variance defined incorrectly")
    if not (0<=maternal["implied_same_blossom_seed_correlation"]<1
            and 0<=nested["implied_same_mother_different_blossom_seed_correlation"]<1
            and 0<=nested["implied_same_blossom_seed_correlation"]<1):
        raise ValueError("source seed-level ICC out of range")
    registered=freeze["registered_R_nlme_models"]["maternal_only"]
    abs_tol=_finite(freeze["source_matching"]["maternal_only_AIC_difference_limit"],"AIC tolerance")
    if not 0<abs_tol<1 or abs(maternal["ml_aic"]-
                _finite(registered["previous_source_verified_AIC_ML"],"source AIC")) > abs_tol:
        raise ValueError("source maternal-only ML AIC is not reproduced across R runs")
    if not freeze["scientific_ceiling"].get("structural_BALANCE_occupancy_identified") is False:
        raise ValueError("source covariance cannot promote structural BALANCE")

    effect_map={}
    for row in effect_rows:
        key=(row.get("model_id"),row.get("term"))
        if key in effect_map or key[0] not in IDS or key[1] not in (*ARMS,"ped"):
            raise ValueError("unknown or duplicate treatment fixed effect")
        effect_map[key]={
            "reml_beta":_finite(row.get("reml_beta"),"REML beta"),
            "reml_se":_finite(row.get("reml_se"),"REML SE"),
            "normal_wald95_interval":[
                _finite(row.get("normal_wald95_lo"),"Wald low"),
                _finite(row.get("normal_wald95_hi"),"Wald high"),
            ],
        }
    if set(effect_map)!={(m,t) for m in IDS for t in (*ARMS,"ped")}:
        raise ValueError("registered fixed-effect contrasts missing")
    comparisons=[]
    for term in ARMS:
        old=effect_map[("maternal_only",term)]
        new=effect_map[("maternal_plus_blossom",term)]
        if old["reml_se"]<=0 or new["reml_se"]<=0:
            raise ValueError("source treatment SE nonpositive")
        frozen_se=_finite(registered["previous_source_verified_REML_treatment_SE_mg"][term.removeprefix("treatcode")],"frozen source SE")
        if abs(old["reml_se"]-frozen_se)>0.002:
            raise ValueError("source maternal model REML SE changed")
        comparisons.append({
            "term":term,
            "maternal_only_reml_beta":round(old["reml_beta"],6),
            "nested_blossom_reml_beta":round(new["reml_beta"],6),
            "maternal_only_reml_SE":round(old["reml_se"],6),
            "nested_blossom_reml_SE":round(new["reml_se"],6),
            "nested_to_maternal_only_SE_ratio":round(new["reml_se"]/old["reml_se"],4),
            "nested_blossom_normal_wald95": [
                round(v,6) for v in new["normal_wald95_interval"]
            ],
            "nested_blossom_interval_includes_zero":
                new["normal_wald95_interval"][0]<=0<=new["normal_wald95_interval"][1],
        })

    diff=nested["ml_aic"]-maternal["ml_aic"]
    # An AIC difference compares conditional covariance modeling, not
    # architecture S-vs-D or alternative life-history fitness pathways.
    status=("NESTED_BLOSSOM_COVARIANCE_FITS_BETTER_IN_SOURCE"
            if diff< -2 else "NESTED_BLOSSOM_COVARIANCE_ADVANTAGE_UNRESOLVED")
    return {
        "schema_version":SCHEMA,
        "status":status,
        "source_doi":freeze["source_doi"],
        "source_sha256":sha,
        "record_count":1103,
        "n_blossoms":132,
        "n_mothers":36,
        "maternal_only_AIC":round(maternal["ml_aic"],6),
        "maternal_and_blossom_AIC":round(nested["ml_aic"],6),
        "nested_minus_maternal_only_AIC":round(diff,6),
        "nested_variance_components": {
            "mother":round(nested["mother_variance"],6),
            "blossom":round(nested["blossom_variance"],6),
            "residual":round(nested["residual_variance"],6),
        },
        "implied_same_blossom_seed_correlation":round(
            nested["implied_same_blossom_seed_correlation"],6),
        "implied_same_mother_different_blossom_seed_correlation":round(
            nested["implied_same_mother_different_blossom_seed_correlation"],6),
        "source_REML_treatment_effects":comparisons,
        "experimental_assignment_unit":"blossom",
        "statistical_comparison":"posthoc_same_rows_same_fixed_effects_nested_random_blossom_intercept",
        "published_2015_nlme_model_reproduced":False,
        "source_2015_original_author_code_recovered":False,
        "causal_bract_photosynthesis_identified":False,
        "structural_BALANCE_occupancy_identified":False,
        "additional_independent_biological_clusters":0,
        "claim_ceiling":"nested_seed_dependence_diagnostic_not_causal_biology_or_source_error",
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract",type=Path,required=True)
    parser.add_argument("--models-csv",type=Path,required=True)
    parser.add_argument("--effects-csv",type=Path,required=True)
    parser.add_argument("--seed-file",type=Path,required=True)
    parser.add_argument("--gas-file",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():
        raise ValueError("refuse to overwrite verified source covariance readout")
    frozen=json.loads(args.contract.read_text(encoding="utf-8"))
    sources={
        "Pelabon et al FE file 1.txt":args.seed_file.read_bytes(),
        "Pelabon et al FE file 2.txt":args.gas_file.read_bytes(),
    }
    out=adjudicate_nested_covariance(frozen,
        _read(args.models_csv,{
            "model_id","n_seeds","n_blossoms","n_mothers","ml_aic",
            "ml_loglik","mother_variance","blossom_variance","residual_variance",
            "implied_same_blossom_seed_correlation",
            "implied_same_mother_different_blossom_seed_correlation"}),
        _read(args.effects_csv,{
            "model_id","term","reml_beta","reml_se",
            "normal_wald95_lo","normal_wald95_hi"}),
        sources)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open("x",encoding="utf-8") as target:
        json.dump(out,target,sort_keys=True,indent=2)
        target.write("\n")
    print(json.dumps({
        "status":out["status"],
        "nested_minus_maternal_only_AIC":out["nested_minus_maternal_only_AIC"],
        "implied_same_blossom_seed_correlation":
            out["implied_same_blossom_seed_correlation"],
        "structural_BALANCE_occupancy_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""Adjudicate original Dalechampia Table 2 against an independent R nlme replay.

Retrospective source-recovery question, not a new plant experiment. A mismatch
is a reproducibility HOLD until R 2.15.2 processing details, original exclusions
and model covariance specification can be independently checked. Not evidence
of scientific misconduct or a false published ecological conclusion.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "DALECHAMPIA_2015_PUBLISHED_NLME_REPLAY_READOUT_V1"
MODELS = (
    "ped_seedset_treat", "ped_treat", "ped_seedset",
    "seedset_only", "ped_only", "intercept",
)
VARIANT = "ped_treat__heterogeneous_residual"


def _rows(path: Path, names: set[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        reader=csv.DictReader(file)
        if not set(reader.fieldnames or ()).issuperset(names):
            raise ValueError("R nlme CSV missing required output fields")
        values=list(reader)
    if not values:
        raise ValueError("R nlme emitted empty model statistics")
    return values


def _finite(x, name) -> float:
    if isinstance(x, bool):
        raise ValueError(f"{name} cannot be boolean")
    try:
        n=float(x)
    except (ValueError, OverflowError, TypeError) as exc:
        raise ValueError(f"{name} nonnumeric") from exc
    if not math.isfinite(n):
        raise ValueError(f"{name} must be finite")
    return n


def adjudicate_published_nlme(
    frozen: dict, model_rows: list[dict[str, str]],
    fixed_rows: list[dict[str, str]], original_file_bytes: dict[str, bytes],
) -> dict:
    if not isinstance(frozen, dict) or frozen.get("schema_version") != "DALECHAMPIA_2015_PUBLISHED_NLME_REPLAY_CONTRACT_V1":
        raise ValueError("original 2015 source nlme contract mismatch")
    if frozen.get("status") != "RETROSPECTIVE_SOURCE_REGISTERED_BEFORE_R_NLME_RUN":
        raise ValueError("source nlme reconstruction not registered")
    if frozen.get("replay_rules", {}).get("model_family") != "nlme::lme Gaussian LMM random=~1|FemaleID":
        raise ValueError("model family cannot be silently switched")
    source_files = frozen["original_file_sha256"]
    if set(original_file_bytes) != set(source_files):
        raise ValueError("both exact original Dryad file identities required")
    for name, expected_sha in source_files.items():
        if type(original_file_bytes[name]) is not bytes or hashlib.sha256(original_file_bytes[name]).hexdigest() != expected_sha:
            raise ValueError("original Dryad source SHA256 mismatch")

    models={}
    for row in model_rows:
        name=row.get("model_id")
        if name not in (*MODELS, VARIANT) or name in models:
            raise ValueError("unexpected/duplicate R nlme model")
        n=int(row["n_obs"])
        m=int(row["n_mothers"])
        if n!=1103 or m!=36:
            raise ValueError("R source analysis n/maternal unit drift")
        models[name]={
            "ml_aic":_finite(row["ml_aic"], f"{name}.AIC"),
            "ml_loglik":_finite(row["ml_loglik"], f"{name}.loglik"),
            "ml_bic":_finite(row["ml_bic"], f"{name}.BIC"),
            "ml_residual_sd":_finite(row["ml_residual_sd"], f"{name}.sigma"),
            "n_seed_rows":n, "n_mothers":m,
        }
    if set(models)!=set((*MODELS, VARIANT)):
        raise ValueError("missing candidate models or varIdent sensitivity")

    terms={}
    for row in fixed_rows:
        name=row.get("model_id")
        if name not in MODELS:
            raise ValueError("unexpected fixed-effect model label")
        term=row.get("term")
        if not term or (name,term) in terms:
            raise ValueError("duplicate / empty fixed-effect term")
        terms[(name,term)]={
            "ml_beta":_finite(row["ml_point"],"beta ML"),
            "reml_beta":_finite(row["reml_point"],"beta REML"),
            "reml_se":_finite(row["reml_se"],"SE REML"),
        }

    tolerance=_finite(frozen["replay_rules"]["source_AIC_abs_tolerance"],"AIC tolerance")
    if tolerance<=0 or tolerance>2.0:
        raise ValueError("original source AIC comparison tolerance invalid")
    table=frozen["source_table2_ml_aic"]
    if set(table)!=set(MODELS):
        raise ValueError("published Table 2 is incomplete")
    measured=[]
    for model in MODELS:
        published=_finite(table[model],f"{model}.publishedAIC")
        replay=models[model]["ml_aic"]
        delta=replay-published
        measured.append({
            "model_id":model,
            "published_2015_AIC_ML":published,
            "independent_R_nlme_AIC_ML":round(replay,6),
            "R_minus_published_AIC":round(delta,6),
            "matches_source_within_registered_tolerance":abs(delta)<=tolerance,
            "analysis_seed_rows":1103,
            "biological_unit_random_effect":"maternal_plant",
        })
    # Table 2 is a fixed candidate set, irrespective of which model agrees best.
    matches=all(x["matches_source_within_registered_tolerance"] for x in measured)
    selected=[x for x in measured if x["model_id"]=="ped_treat"][0]
    expected_betas=frozen["printed_source_remL_fixed_effects_references"]["ped_treat"]
    beta_comparison=[]
    for term, published in expected_betas.items():
        actual=terms.get(("ped_treat",term))
        if actual is None:
            raise ValueError(f"registered REML fixed term unavailable: {term}")
        beta_comparison.append({
            "term":term,
            "published_reml_coefficient":_finite(
                published.get("estimate_mg",published.get("estimate_mg_per_mm")),
                f"published beta {term}"),
            "independent_R_reml_coefficient":round(actual["reml_beta"],6),
            "published_SE":_finite(
                published.get("reported_se_mg",published.get("reported_se_mg_per_mm")),
                f"published SE {term}"),
            "independent_R_reml_SE":round(actual["reml_se"],6),
        })
    source_variance=frozen["source_residual_variance_sensitivity"]
    source_var_aic=_finite(source_variance["treatment_specific_residual_varident_aic_ml_reported"],"published treatment heterogeneity AIC")
    source_common_aic=_finite(source_variance["shared_residual_aic_ml_reported"],"published common variance AIC")
    var_aic=models[VARIANT]["ml_aic"]
    result={
        "schema_version":SCHEMA,
        "status":("TABLE2_ALL_SIX_MODELS_MATCH_SOURCE_AIC"
                  if matches else "PUBLISHED_TABLE2_NLME_NUMERICAL_REPRODUCTION_HOLD"),
        "source_article_doi":frozen["article_doi"],
        "source_data_doi":frozen["data_doi"],
        "original_R_version_reported":frozen["original_R_version_reported"],
        "modern_R_nlme_is_historical_R_2_15_2_exact_recreation":False,
        "source_original_R_script_recovered":False,
        "replay_method":"nlme::lme random maternal intercept, source numeric >=20mg subset; ML AIC, REML beta",
        "published_table2":measured,
        "all_six_within_registered_AIC_tolerance":matches,
        "primary_aic_delta":selected["R_minus_published_AIC"],
        "primary_reml_fixed_effects":beta_comparison,
        "varIdent_residual_sensitivity":{
            "published_treatment_heterogeneous_residual_AIC":source_var_aic,
            "replay_treatment_heterogeneous_residual_AIC":round(var_aic,6),
            "replay_minus_published_AIC":round(var_aic-source_var_aic,6),
            "published_heterogeneous_minus_common_residual_AIC":round(source_var_aic-source_common_aic,6),
            "replay_heterogeneous_minus_common_residual_AIC":round(var_aic-models["ped_treat"]["ml_aic"],6),
            "not_one_of_six_table2_candidates":True,
        },
        "all_source_files_sha256":{
            name:hashlib.sha256(content).hexdigest() for name,content in sorted(original_file_bytes.items())
        },
        "original_source_seed_count_included":1103,
        "original_source_maternal_groups":36,
        "provenance_conclusion":"independent reconstruction with modern R nlme; source R script, historical package and optional exclusions unresolved",
        "ecological_claim_ceiling":{
            "publication_error_proven":False,
            "causal_bract_carbon_isolated":False,
            "seed_to_mature_organism_fitness_identified":False,
            "structural_BALANCE_occupancy_identified":False,
            "additional_independent_biological_clusters":0,
        },
    }
    return result


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract",type=Path,required=True)
    parser.add_argument("--models-csv",type=Path,required=True)
    parser.add_argument("--effects-csv",type=Path,required=True)
    parser.add_argument("--seed-file",type=Path,required=True)
    parser.add_argument("--gas-file",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():
        raise ValueError("do not overwrite published-source adjudication receipt")
    frozen=json.loads(args.contract.read_text(encoding="utf-8"))
    files={
        "Pelabon et al FE file 1.txt":args.seed_file.read_bytes(),
        "Pelabon et al FE file 2.txt":args.gas_file.read_bytes(),
    }
    data=adjudicate_published_nlme(
        frozen,
        _rows(args.models_csv,{"model_id","n_obs","n_mothers","ml_aic","ml_loglik","ml_bic","ml_residual_sd"}),
        _rows(args.effects_csv,{"model_id","term","ml_point","reml_point","reml_se"}),
        files,
    )
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open("x",encoding="utf-8") as target:
        json.dump(data,target,indent=2,sort_keys=True)
        target.write("\n")
    print(json.dumps({
        "status":data["status"],
        "primary_aic_delta":data["primary_aic_delta"],
        "all_six_within_registered_AIC_tolerance":data["all_six_within_registered_AIC_tolerance"],
        "structural_BALANCE_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

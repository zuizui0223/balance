#!/usr/bin/env python3
"""Frozen-source, one-program, four-species observational prediction calibration.

Null simulations are conditional reference calculations, NOT randomization
p-values or causal tests. 24 gardens are the independent resampling blocks.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "scripts/analyze_zurich_four_species.py"
SOURCE_SHA256 = "b1ea0dc54d0c6e33bfacb44d7285377ec3e113807cc945fc2dfbfcc9"
SPECIES = ["Carrot", "Radish", "Sainfoin", "Comfrey"]
GROUPS = ["apis", "other_bee", "other_nonbee", "robber"]


def upstream():
    spec = importlib.util.spec_from_file_location("zurich_original_study", UPSTREAM)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_sites(source: Path):
    mod = upstream()
    z = mod.check_source(Path(source))
    survey, captures = mod.source_frame(z)
    outcomes = mod.site_outcomes(z)
    sites, quality = mod.assembled(survey, captures, outcomes)
    if len(sites) != 96 or len(survey) != 670 or len(captures) != 5794:
        raise ValueError("Original source denominators do not match 96/670/5794")
    if quality["unmatched_individual_visits"] != 27:
        raise ValueError("Original unsurveyed visitor count changed")
    return sites


def make_designs(sites):
    import numpy as np
    keys = [(row["garden"], row["species"]) for row in sites]
    if len(set(keys)) != len(keys):
        raise ValueError("Garden/species duplicate observations")
    if len(sites) != 96:
        raise ValueError("Require exactly 96 garden-by-species rows")
    shared = sorted({g for g, _ in keys})
    if len(shared) != 24 or any({g for g,sp in keys if sp == s} != set(shared) for s in SPECIES):
        raise ValueError("Four species do not have identical 24 garden identities")
    out = {}
    for sp in SPECIES:
        sub = sorted((r for r in sites if r["species"] == sp), key=lambda x:x["garden"])
        visits = np.array([r["n_visits"] for r in sub], dtype=float)
        y = np.array([r["response"] for r in sub], dtype=float)
        rate = np.array([r["rate"] for r in sub], dtype=float)
        counts = np.array([[r["counts"][g] for g in GROUPS] for r in sub], dtype=float)
        if any(not np.isfinite(q).all() for q in (visits,y,rate,counts)):
            raise ValueError("Nonfinite original observation")
        if (counts < 0).any() or not np.allclose(visits, counts.sum(axis=1)) or (rate < 0).any():
            raise ValueError("Invalid original visitor counts, totals or rates")
        active = [j for j in range(4) if counts[:,j].sum() > 0]
        if len(active) < 2:
            raise ValueError("Composition model without two visitor guilds")
        reference = max(active, key=lambda j:counts[:,j].sum())
        extra = [j for j in active if j != reference]
        X0 = np.column_stack([np.ones(24), np.log1p(rate)])
        fractions = np.divide(counts[:,extra], visits[:,None],
                              out=np.zeros((24,len(extra))), where=visits[:,None]>0)
        X1 = np.column_stack([X0, fractions])
        out[sp] = {"y":y,"X0":X0,"X1":X1,"gardens":shared,
                   "reference_guild":GROUPS[reference],"extra_guilds":[GROUPS[j] for j in extra]}
    return out


def loo_operator(X):
    """Linear operator mapping observations to true OLS leave-one-out residuals."""
    import numpy as np
    X = np.asarray(X, dtype=float)
    if len(X.shape)!=2 or len(X)<=X.shape[1]+1 or not np.isfinite(X).all():
        raise ValueError("Invalid/full-rank design expected")
    if np.linalg.matrix_rank(X) != X.shape[1]:
        raise ValueError("Model design is rank deficient")
    H=X @ np.linalg.solve(X.T@X,X.T)
    leverage=np.diag(H)
    if (leverage>=1-1e-10).any():
        raise ValueError("Leave-one-garden-out model not estimable")
    return (np.eye(len(X))-H)/(1-leverage)[:,None]


def audit(source:Path,draws:int=20000,seed:int=987654):
    import numpy as np
    if draws < 100 or draws > 100000:
        raise ValueError("Null reference draw count must be within 100..100000")
    sites=load_sites(Path(source))
    model=make_designs(sites)
    rng=np.random.default_rng(seed)
    n=24
    perm_indices=np.vstack([rng.permutation(n) for _ in range(draws)])
    wild_signs=rng.choice([-1.,1.],size=(draws,n))
    boots=rng.integers(0,n,size=(draws,n))
    null_residual=np.empty((draws,len(SPECIES)),float)
    null_wild=np.empty((draws,len(SPECIES)),float)
    info={}
    for j,sp in enumerate(SPECIES):
        z=model[sp];y=z["y"]
        X0,X1=z["X0"],z["X1"]
        A0,A1=loo_operator(X0),loo_operator(X1)
        err0,err1=A0@y,A1@y
        rm0=np.sqrt(np.mean(err0**2));rm1=np.sqrt(np.mean(err1**2))
        if rm0<=0 or not np.isfinite(rm0+rm1):
            raise ValueError("Zero or invalid baseline prediction error")
        gain=1-rm1/rm0
        beta=np.linalg.lstsq(X0,y,rcond=None)[0]
        fitted=X0@beta;resid=y-fitted
        simulated_permutation=fitted[None,:]+resid[perm_indices]
        simulated_wild=fitted[None,:]+resid[None,:]*wild_signs
        for dest,sim in ((null_residual,simulated_permutation),(null_wild,simulated_wild)):
            err_base=sim@A0.T;err_comp=sim@A1.T
            msebase=np.mean(err_base**2,axis=1)
            msecomp=np.mean(err_comp**2,axis=1)
            dest[:,j]=1-np.sqrt(msecomp/msebase)
        bs0=np.sqrt(np.mean(err0[boots]**2,axis=1))
        bs1=np.sqrt(np.mean(err1[boots]**2,axis=1))
        # Only paired resampling of *already held-out losses*, not full refit uncertainty.
        resampled=1-bs1/bs0
        ci=np.quantile(resampled,[.025,.975])
        influence=(err0**2-err1**2)
        topidx=int(np.argmax(influence))
        info[sp]={
            "n_gardens":n,"response":"Carrot log1p seeds; other three arcsin-sqrt fruit/seed fractions",
            "reference_guild":z["reference_guild"],"additional_guilds":z["extra_guilds"],
            "rmse_total":float(rm0),"rmse_total_plus_composition":float(rm1),
            "gain_fraction":float(gain),
            "gardens_with_lower_loss":int(np.sum(err1**2<err0**2)),
            "paired_bootstrap_ci95":list(map(float,ci)),
            "paired_bootstrap_probability_positive":float(np.mean(resampled>0)),
            "top_positive_garden":int(z["gardens"][topidx]),
            "top_positive_sqerror_gain":float(influence[topidx]),
            "net_sqerror_gain":float(influence.sum()),
        }
    topperm=null_residual.max(axis=1)
    topwild=null_wild.max(axis=1)
    for j,sp in enumerate(SPECIES):
        gain=info[sp]["gain_fraction"]
        info[sp].update({
            "residual_permutation_p_raw":float((1+np.sum(null_residual[:,j]>=gain))/(draws+1)),
            "residual_permutation_p_fwer":float((1+np.sum(topperm>=gain))/(draws+1)),
            "wild_signflip_p_raw":float((1+np.sum(null_wild[:,j]>=gain))/(draws+1)),
            "wild_signflip_p_fwer":float((1+np.sum(topwild>=gain))/(draws+1)),
        })
    return {
        "schema":"BALANCE_ZURICH_COMPOSITION_NULL_CALIBRATION_V1",
        "source_sha256":SOURCE_SHA256,"original_source_doi":"10.16904/envidat.676",
        "independent_research_programmes":1,"n_gardens":24,"species_order":SPECIES,
        "draws":draws,"seed":seed,"species":info,
        "method":"True garden-leave-one-out OLS; fixed-geometry residual-permutation, shared-garden wild sign-flip, four-species max statistic, paired resampling of held-out losses",
        "independence_note":"All four phytometers in a garden share one sampling environment; 24 resampling blocks, not 96 independent environments",
        "not_a_randomized_p_value":True,
        "residual_exchangeability_unverified":True,
        "paired_bootstrap_not_full_refit_uncertainty":True,
        "source_based_inference_not_a_direct_BALANCE_architecture_test":True,
        "causal_intervention_test":False,"frozen_V4_modified":False,
        "no_new_direct_Ws_Wd_Phi":True,
        "claim_ceiling":"Null-reference and prediction-stability diagnostics only; no architecture selection, structural fitness, causal visitor guild effect or unbiased generality prevalence"
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    p.add_argument('--draws',type=int,default=20000)
    p.add_argument('--seed',type=int,default=987654)
    a=p.parse_args()
    out=audit(a.source,draws=a.draws,seed=a.seed)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    if a.out.exists():raise FileExistsError('Cannot overwrite frozen analysis output')
    a.out.write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({sp:{k:round(v[k],5) for k in ('gain_fraction','residual_permutation_p_fwer','wild_signflip_p_fwer')}
           for sp,v in out['species'].items()},indent=2))

if __name__=='__main__':main()

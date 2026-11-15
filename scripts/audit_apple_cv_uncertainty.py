#!/usr/bin/env python3
"""Group-blocked prediction error uncertainty for the independent apple study.

This is a site-resampling diagnostic for already computed out-of-orchard losses,
not a causal estimate, full model-refit CI or replication across plant species.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
UPSTREAM=ROOT/'scripts/audit_wisconsin_apple_independent.py'

def upstream():
    spec=importlib.util.spec_from_file_location('original_apple_audit',UPSTREAM)
    z=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)
    return z


def heldout_orchard_mse(rows,predictors):
    import numpy as np
    f={
        'year':lambda r:float(r['year']==2013),
        'frost':lambda r:float(r['frost']),
        'total':lambda r:float(np.log1p(r['total'])),
        'share':lambda r:float(r['share']),
        'rich':lambda r:float(np.log1p(r['rich'])),
        'management':lambda r:float(r['organic']),
    }
    if not rows or len({(r['orchard'],r['year']) for r in rows})!=len(rows):
        raise ValueError('Orchard-year duplicate or empty input')
    if any(p not in f for p in predictors):raise ValueError('Unknown predictor')
    ordered=sorted(rows,key=lambda r:(r['orchard'],r['year']))
    y=np.array([np.arcsin(np.sqrt(r['fruit'])) for r in ordered])
    groups=np.array([r['orchard'] for r in ordered])
    X=np.array([[1.0]+[f[k](r) for k in predictors] for r in ordered])
    if not np.isfinite(X).all() or not np.isfinite(y).all():raise ValueError('Nonfinite orchard input')
    if np.linalg.matrix_rank(X)!=X.shape[1]:raise ValueError('Full design rank failure')
    result={}
    for g in sorted(set(groups)):
        train=groups!=g;test=groups==g
        if np.linalg.matrix_rank(X[train])!=X.shape[1]:
            raise ValueError('Held-out orchard design rank failure')
        b=np.linalg.lstsq(X[train],y[train],rcond=None)[0]
        result[int(g)]=float(np.mean((y[test]-X[test]@b)**2))
    return result


def audit(source:Path,draws:int=20000,seed:int=20261115):
    import numpy as np
    if draws<100 or draws>100000:raise ValueError('Draws must be within 100..100000')
    src=upstream();original,sha=src.read_original(source)
    usable=src.complete(original)
    if len(usable)!=36 or len({r['orchard'] for r in usable})!=21:
        raise ValueError('Expected 36 observed orchard-years within 21 independent orchards')
    model_scope={
        'main_year_and_frost_adjusted':(usable,('year','frost','total'),('year','frost','total','share','rich')),
        'year_only_no_frost':(usable,('year','total'),('year','total','share','rich')),
        'year_2012_frost_adjusted':([r for r in usable if r['year']==2012],('frost','total'),('frost','total','share','rich')),
        'year_2013_only':([r for r in usable if r['year']==2013],('total',),('total','share','rich')),
    }
    rng=np.random.default_rng(seed)
    reports={}
    for name,(rows,bcols,ecols) in model_scope.items():
        a=heldout_orchard_mse(rows,bcols);b=heldout_orchard_mse(rows,ecols)
        orch=sorted(a)
        if sorted(b)!=orch:raise ValueError('Base/full orchard denominators differ')
        e0=np.array([a[g] for g in orch]);e1=np.array([b[g] for g in orch])
        rm0=np.sqrt(np.mean(e0));rm1=np.sqrt(np.mean(e1))
        gain=1-rm1/rm0
        ix=rng.integers(0,len(orch),size=(draws,len(orch)))
        draws_gain=1-np.sqrt(np.mean(e1[ix],axis=1)/np.mean(e0[ix],axis=1))
        diff=e0-e1;idx=int(np.argmax(diff))
        reports[name]={
            'n_orchards':len(orch),'n_orchard_years':len(rows),
            'baseline_predictors':bcols,'extension_predictors':ecols,
            'baseline_rmse_orchard_equal':float(rm0),
            'extension_rmse_orchard_equal':float(rm1),
            'gain_fraction':float(gain),
            'orchards_with_lower_loss':int(np.sum(e1<e0)),
            'paired_bootstrap_ci95':list(map(float,np.quantile(draws_gain,[.025,.975]))),
            'paired_bootstrap_probability_positive':float(np.mean(draws_gain>0)),
            'largest_positive_orchard':int(orch[idx]),
            'largest_positive_loss_change':float(diff[idx]),
            'net_orchard_loss_change':float(diff.sum()),
        }
    return {'schema':'BALANCE_APPLE_GROUP_CV_UNCERTAINTY_V1',
            'original_source_doi':src.DOC_DOI, 'source_md5':src.EXPECTED_MD5,
            'source_sha256':sha,'n_orchard_years_original':47,
            'n_orchard_years_usable':36,'n_independent_orchards':21,
            'untouched_original_2011_missing_year':11,
            'independent_research_programmes':1,'independent_plant_species':1,
            'draws':draws,'seed':seed,'comparisons':reports,
            'main_year_and_frost_adjusted':reports['main_year_and_frost_adjusted'],
            'paired_bootstrap_not_full_model_refit':True,
            'year_and_frost_associations_not_randomized':True,
            'bee_abundance_not_per_flower_visitation':True,
            'frozen_V4_modified':False,
            'no_direct_BALANCE_architecture_worldline':True,
            'claim_ceiling':'Exploratory error stability of original out-of-orchard predictions; not direct structural architecture selection or cross-species effect-size meta-analysis'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--draws',type=int,default=20000)
    p.add_argument('--seed',type=int,default=20261115)
    z=p.parse_args(); result=audit(z.source,z.draws,z.seed)
    z.out.parent.mkdir(parents=True,exist_ok=True)
    if z.out.exists():raise FileExistsError('Cannot overwrite existing analysis receipt')
    z.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k: {'n_orchards':v['n_orchards'],
               'gain_percent':round(100*v['gain_fraction'],3),
               'loss_bootstrap_ci95':v['paired_bootstrap_ci95']}
               for k,v in result['comparisons'].items()},indent=2))

if __name__=='__main__':main()

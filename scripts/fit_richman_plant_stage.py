#!/usr/bin/env python3
"""Authenticated original Richman plant-linked stage contrasts; post-open descriptive bootstrap."""
from __future__ import annotations
import argparse, collections, hashlib, json, math, pathlib, sys
import numpy as np
from openpyxl import load_workbook
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.recover_richman_direct_mirror import NAME, MD5, SIZE
SHA='c3b8dd209039ab1beca1a098e60906eb4be1fc3b9b57dff9daff66a72fec8a84'
ARMS=('C','P','S')
CONTRASTS=(('P','C'),('S','P'),('S','C'))
POLLEN_HEADER=('date','week','treatment','plant','plant_id','grains','open.flow')
FRUIT_HEADER=('treatment','plant','successful_fruits','DF','total_successful','aborts','deh, drop, hyl','total_fruit','prop_fruit_set','total_seeds_plant','seeds_fruit_plant','browse','height')
def number(v):
    if v is None or (isinstance(v,str) and v.strip().lower() in ('','na','nan','n/a')):return None
    if isinstance(v,bool):raise ValueError('unexpected boolean numeric')
    x=float(v)
    if not math.isfinite(x) or x<0:raise ValueError('invalid nonnegative numeric')
    return x
def key(row):
    a=row['treatment'];p=number(row['plant'])
    if a not in ARMS or p is None or int(p)!=p or not 1<=p<=40:raise ValueError('invalid plant key')
    return a,int(p)
def safe_ratio(a,b):
    return a/b if a is not None and b is not None and b>0 else None
def add(a,b):return a+b if a is not None and b is not None else None
def load_original(path):
    b=path.read_bytes()
    if len(b)!=SIZE or hashlib.md5(b).hexdigest()!=MD5 or hashlib.sha256(b).hexdigest()!=SHA:raise ValueError('pinned source bytes mismatch')
    w=load_workbook(path,read_only=True,data_only=True)
    def rows(sheet,header):
        rr=list(w[sheet].values)
        if tuple(rr[0])!=header:raise ValueError('sheet header mismatch '+sheet)
        return [dict(zip(header,r)) for r in rr[1:] if any(v is not None for v in r)]
    pollen=rows('pollen receipt',POLLEN_HEADER);fruit=rows('fruit and seed success',FRUIT_HEADER)
    visit_n=sum(any(v is not None for v in r) for r in list(w['hummingbird visitation'].values)[1:])
    meta=[list(r) for r in w['metadata'].values]
    w.close()
    if (len(pollen),len(fruit),visit_n)!=(435,120,30):raise ValueError('source row count mismatch')
    return pollen,fruit,meta
def assemble(pollen,fruit):
    plants={}; samples=collections.defaultdict(list); pid_to_key={}; key_to_pid={}
    for r in fruit:
        k=key(r)
        if k in plants:raise ValueError('duplicate fruit plant')
        p={f:number(r[f]) for f in FRUIT_HEADER[2:]}
        if p['prop_fruit_set'] is not None and p['prop_fruit_set']>1:raise ValueError('fruit proportion >1')
        a,b,c,d,e,f=[p[x] for x in ('successful_fruits','DF','total_successful','aborts','deh, drop, hyl','total_fruit')]
        p['success_over_total_fruit']=safe_ratio(c,f)
        p['total_fruit_over_fruit_plus_aborts']=safe_ratio(f,add(f,d))
        p['success_over_fruit_plus_aborts']=safe_ratio(c,add(f,d))
        p['success_over_success_plus_aborts']=safe_ratio(c,add(c,d))
        p['collected_success_over_fruit']=safe_ratio(a,f)
        p['success_identity_expected']=add(a,b)
        p['total_identity_expected']=add(c,e)
        plants[k]=p
    if set(plants)!={(a,p) for a in ARMS for p in range(1,41)}:raise ValueError('fruit allocation incomplete')
    for r in pollen:
        k=key(r);pid=number(r['plant_id']);week=number(r['week'])
        if pid is None or int(pid)!=pid or not 1<=pid<=120 or week is None or int(week)!=week or not 1<=week<=6:raise ValueError('invalid source plant ID or week')
        pid=int(pid)
        if k not in plants or (pid in pid_to_key and pid_to_key[pid]!=k) or (k in key_to_pid and key_to_pid[k]!=pid):raise ValueError('ambiguous plant linkage')
        pid_to_key[pid]=k;key_to_pid[k]=pid
        samples[k].append((int(week),number(r['grains'])))
    for k,p in plants.items():
        values=[v for _,v in samples[k] if v is not None]
        week=collections.defaultdict(list)
        for w,v in samples[k]:
            if v is not None:week[w].append(v)
        p['n_stigmas']=len(samples[k]);p['n_grains_observed']=len(values);p['n_weeks']=len(week)
        p['pollen_mean']=float(np.mean(values)) if values else None
        p['pollen_equal_week']=float(np.mean([np.mean(v) for v in week.values()])) if week else None
        p['pollen_incidence']=float(np.mean([v>0 for v in values])) if values else None
        positive=[v for v in values if v>0]
        p['pollen_positive_mean']=float(np.mean(positive)) if positive else None
        # Identity is exact for equal-stigma mean, not for group products.
        if values and positive and abs(p['pollen_mean']-p['pollen_incidence']*p['pollen_positive_mean'])>1e-10:raise ValueError('pollen decomposition mismatch')
    return plants
def audit(plants):
    fields=['success_over_total_fruit','total_fruit_over_fruit_plus_aborts','success_over_fruit_plus_aborts','success_over_success_plus_aborts','collected_success_over_fruit']
    def equality(a,b):
        eligible=[(p[a],p[b]) for p in plants.values() if p[a] is not None and p[b] is not None]
        return {'eligible':len(eligible),'matches':sum(abs(x-y)<1e-7 for x,y in eligible),
                'max_abs_error':max((abs(x-y) for x,y in eligible),default=None)}
    out={'source_recorded_fruit_fraction_vs':{f:equality('prop_fruit_set',f) for f in fields},
         'component_identities':{'total_successful':equality('total_successful','success_identity_expected'),'total_fruit':equality('total_fruit','total_identity_expected')},'groups':{}}
    for a in ARMS:
        ps=[p for (t,_),p in plants.items() if t==a]
        g={'allocated':len(ps),'stigmas':sum(p['n_stigmas'] for p in ps),'observed_grains':sum(p['n_grains_observed'] for p in ps),
           'pollen_plants':sum(p['pollen_mean'] is not None for p in ps),'positive_pollen_plants':sum(p['pollen_positive_mean'] is not None for p in ps)}
        for f in ['pollen_mean','pollen_equal_week','pollen_incidence','pollen_positive_mean','prop_fruit_set','total_seeds_plant','seeds_fruit_plant','browse']+fields:
            v=[p[f] for p in ps if p[f] is not None]
            g[f]={'n':len(v),'mean':float(np.mean(v)) if v else None,'zero':sum(x==0 for x in v)}
        out['groups'][a]=g
    return out
def summarize(plants,fields,seed=20261124,B=20000,browse_free=False):
    """Identical plant subset across endpoints within each variant; shared draws across contrasts."""
    rng=np.random.default_rng(seed)
    groups={}; means={}; boot={}; selected={}; n={}
    for a in ARMS:
        keys=[k for k,p in sorted(plants.items()) if k[0]==a and (not browse_free or p['browse']==0) and all(p[f] is not None for f in fields)]
        x=np.array([[plants[k][f] for f in fields] for k in keys],float);n[a]=len(keys);selected[a]=[k[1] for k in keys]
        if len(keys)<2 or np.any(x.mean(axis=0)<=0):return {'status':'INSUFFICIENT_POSITIVE_ARM_MEANS','n':n,'fields':fields}
        groups[a]=x;means[a]=x.mean(axis=0)
        draws=rng.integers(0,len(x),size=(B,len(x)))
        boot[a]=x[draws].mean(axis=1)
    effects={}; all_draws=[];names=[]
    for t,c in CONTRASTS:
        name=t+'/'+c
        valid=np.all((boot[t]>0)&(boot[c]>0),axis=1)
        z=np.full((B,len(fields)),np.nan);z[valid]=np.log(boot[t][valid]/boot[c][valid])
        obs=np.log(means[t]/means[c])
        d=z[:,1:]-z[:,:1]
        def stats(v,b):
            ok=b[np.isfinite(b)]
            return {'estimate':float(v),'ci95':[float(i) for i in np.quantile(ok,[.025,.975])] if len(ok) else None,'valid_draws':len(ok)}
        effects[name]={'lnRR':{f:stats(obs[i],z[:,i]) for i,f in enumerate(fields)},
                       'downstream_minus_upstream':{f:stats(obs[i]-obs[0],d[:,i-1]) for i,f in enumerate(fields[1:],1)},
                       'bootstrap_covariance_lnRR':np.cov(z[valid],rowvar=False).tolist() if valid.sum()>1 else None}
        all_draws.append(z);names.extend(name+':'+f for f in fields)
    matrix=np.concatenate(all_draws,axis=1);ok=np.all(np.isfinite(matrix),axis=1)
    return {'status':'DESCRIPTIVE_PAIRED_PLANT_BOOTSTRAP','fields':fields,'n':n,'plant_numbers':selected,'means':{a:{f:float(means[a][i]) for i,f in enumerate(fields)} for a in ARMS},
            'effects':effects,'joint_covariance_order':names,'joint_covariance':np.cov(matrix[ok],rowvar=False).tolist() if ok.sum()>1 else None,'joint_valid_draws':int(ok.sum()),'B':B,'seed':seed}
def run(path):
    pollen,fruit,meta=load_original(path);plants=assemble(pollen,fruit)
    variants={
       'primary_pollen_fruit':(('pollen_mean','prop_fruit_set'),False),
       'matched_pollen_fruit_total_seeds':(('pollen_mean','prop_fruit_set','total_seeds_plant'),False),
       'equal_week_pollen_fruit':(('pollen_equal_week','prop_fruit_set'),False),
       'alternative_metadata_fraction':(('pollen_mean','total_fruit_over_fruit_plus_aborts'),False),
       'alternative_success_all_recorded':(('pollen_mean','success_over_fruit_plus_aborts'),False),
       'alternative_success_plus_aborts':(('pollen_mean','success_over_success_plus_aborts'),False),
       'pollen_incidence_fruit':(('pollen_incidence','prop_fruit_set'),False),
       'positive_stigma_load_fruit':(('pollen_positive_mean','prop_fruit_set'),False),
       'browse_free_sensitivity':(('pollen_mean','prop_fruit_set'),True)}
    d={'source_sha256':SHA,'source_md5':MD5,'scope':'Same treatment and plant keys; different flowers, haphazard allocation, no secondary-only treatment, complete-case and missingness sensitivity; descriptive plant-level resampling, not causal mediation or original model replay.',
       'treatments':{'C':'control','P':'primary','S':'primary+secondary'},'metadata':meta,'audit':audit(plants),
       'variants':{k:summarize(plants,f,browse_free=b) for k,(f,b) in variants.items()}}
    return d
def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=pathlib.Path);p.add_argument('--out',required=True,type=pathlib.Path);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    r=run(a.source);a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    compact={k:v for k,v in r.items() if k!='variants'}
    compact['variants']={k:{x:y for x,y in v.items() if x not in ('plant_numbers','joint_covariance','joint_covariance_order')} for k,v in r['variants'].items()}
    print('RICHMAN_PLANT_RESULT '+json.dumps(compact,ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Exploratory paper-cluster meta-analysis of archived Zhong lnRR, not causal mediation."""
from __future__ import annotations
import argparse, json, math, sys
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean
from scipy.stats import t
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts.audit_larceny_meta_stage_pairability import source_rows, CONTEXT, SOURCE_SHA256

STAGES=('nectar volume','visitation rate','pollen deposition','fruit set','seed set')
PAIRS=(('fruit set','seed set'),('nectar volume','visitation rate'),
       ('visitation rate','pollen deposition'),('pollen deposition','fruit set'))
RHO=(0.,0.5,1.)
MODERATORS=('pollen_limitation','self_compatible','damage')
MIN_K=5

def collapse(blocks):
    """Each block equal weight; within each block each signed arm equal weight."""
    coef=defaultdict(float); rows={}
    for block in blocks:
        for sign,arm in block:
            if not arm: raise ValueError('empty arm')
            for row in arm:
                ident=row['ID']; rows[ident]=row
                coef[ident]+=sign/(len(blocks)*len(arm))
    y=sum(c*rows[i]['yi'] for i,c in coef.items())
    vind=sum(c*c*rows[i]['vi'] for i,c in coef.items())
    vmax=sum(abs(c)*math.sqrt(rows[i]['vi']) for i,c in coef.items())**2
    if not (math.isfinite(y) and 0< vind<=vmax+1e-12): raise ValueError('invalid contrast')
    return {'y':y,'v_ind':vind,'v_upper':max(vind,vmax),'ids':sorted(rows),'blocks':len(blocks)}

def pool(items,rho):
    """DL + modified KH; paper is sampling cluster; working variance sensitivity."""
    n=len(items)
    if n<MIN_K: return {'k':n,'status':'INSUFFICIENT_STUDIES','equal_paper_mean':mean(x['y'] for x in items) if n else None}
    y=[x['y'] for x in items]
    v=[(1-rho)*x['v_ind']+rho*x['v_upper'] for x in items]
    w=[1/a for a in v]; s=sum(w); fixed=sum(a*b for a,b in zip(w,y))/s
    q=sum(a*(b-fixed)**2 for a,b in zip(w,y))
    c=s-sum(a*a for a in w)/s
    tau=max(0.,(q-(n-1))/c)
    w=[1/(a+tau) for a in v]; s=sum(w); mu=sum(a*b for a,b in zip(w,y))/s
    q_re=sum(a*(b-mu)**2 for a,b in zip(w,y))/(n-1)
    se=math.sqrt(max(1.,q_re)/s); critical=t.ppf(.975,n-1)
    return {'status':'EXPLORATORY_FIT','k':n,'mu':mu,'ci95':[mu-critical*se,mu+critical*se],
            'se_mkh':se,'p_two_sided_nominal':float(2*t.sf(abs(mu/se),n-1)),
            'tau2_DL':tau,'I2_percent':100*max(0.,(q-(n-1))/q) if q>0 else 0.,
            'equal_paper_mean':mean(y),'positive_papers':sum(a>0 for a in y),'negative_papers':sum(a<0 for a in y)}

def sensitivity(items):
    return {str(r):pool(items,r) for r in RHO}

def collect(rows,first,second=None,scope='context'):
    buckets=defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row['sub_response_variable'] not in (first,second): continue
        key=(row['ref-ID'],row['species'])
        if second and scope in ('context','unique_context'):
            key+=tuple(row[k] for k in CONTEXT)
        buckets[key][row['sub_response_variable']].append(row)
    grouped=defaultdict(list)
    for key,stages in buckets.items():
        if first not in stages or second and second not in stages: continue
        if scope=='unique_context' and second and any(len(stages[s])!=1 for s in (first,second)): continue
        arm=[(1,stages[first])] if second is None else [(-1,stages[first]),(1,stages[second])]
        grouped[key[0]].append(arm)
    return {p:collapse(blocks) for p,blocks in grouped.items()}

def moderator(rows,items,field):
    byid={r['ID']:r for r in rows}; grouped=defaultdict(list); excluded=0
    missing={'','na','n/a','nan','none','unknown','not available','not reported','-','?'}
    for x in items.values():
        values={str(byid[i][field]).strip() if byid[i][field] is not None else '' for i in x['ids']}
        if len(values)!=1 or any(v.lower() in missing for v in values): excluded+=1;continue
        grouped[next(iter(values))].append(x)
    groups={k:sensitivity(v) for k,v in sorted(grouped.items())}
    contrast={}
    # Not a formal causal moderator test; exploratory independent subgroup estimates.
    if len(grouped)==2 and all(len(v)>=MIN_K for v in grouped.values()):
        a,b=sorted(grouped)
        for rho in RHO:
            x,y=groups[a][str(rho)],groups[b][str(rho)]
            varx=x['se_mkh']**2; vary=y['se_mkh']**2
            se=math.sqrt(varx+vary); df=(varx+vary)**2/(varx**2/(x['k']-1)+vary**2/(y['k']-1))
            diff=y['mu']-x['mu']; crit=t.ppf(.975,df)
            contrast[str(rho)]={'levels':[b,a],'difference':diff,'ci95':[diff-crit*se,diff+crit*se],
                                'nominal_p':float(2*t.sf(abs(diff/se),df)),'df':df}
    return {'paper_count_by_exact_archive_label':{k:len(v) for k,v in sorted(grouped.items())},
            'ambiguous_or_missing_papers':excluded,'groups':groups,'binary_subgroup_contrast':contrast}

def run(rows):
    result={'source_sha256':SOURCE_SHA256,'n_effects':len(rows),'n_papers':len({r['ref-ID'] for r in rows}),
            'endpoint_counts':dict(Counter(r['sub_response_variable'] for r in rows)),
            'method':'Equal effects within arm, equal blocks within paper, DL + modified KH across papers. Working variance grid from independence to Cauchy upper bound. No phylogenetic correction.',
            'scope':'Exploratory archived category contrasts, not same experimental cohort or causal transmission; no positive-case filtering; unadjusted intervals across secondary tests.',
            'marginal_stage_meta':{},'within_paper_stage_meta':{},'primary_moderators':{}}
    for stage in STAGES:
        p=collect(rows,stage)
        result['marginal_stage_meta'][stage]=sensitivity(list(p.values()))
    for a,b in PAIRS:
        key=b+' minus '+a
        result['within_paper_stage_meta'][key]={}
        for scope in ('paper_species','context','unique_context'):
            p=collect(rows,a,b,scope)
            result['within_paper_stage_meta'][key][scope]={
                'n_paper_clusters':len(p),'n_blocks':sum(x['blocks'] for x in p.values()),
                'fits':sensitivity(list(p.values())),
                'paper_effects':{str(k):v for k,v in sorted(p.items())}}
    primary=collect(rows,*PAIRS[0],'context')
    for m in MODERATORS:
        result['primary_moderators'][m]=moderator(rows,primary,m)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    result=run(source_rows(a.source));a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    compact={**result,'within_paper_stage_meta':{k:{s:{i:v for i,v in d.items() if i!='paper_effects'} for s,d in m.items()} for k,m in result['within_paper_stage_meta'].items()}}
    print('BALANCE_STAGE_META_RESULT_BEGIN')
    print(json.dumps(compact,ensure_ascii=False,allow_nan=False))
    print('BALANCE_STAGE_META_RESULT_END')
if __name__=='__main__':main()

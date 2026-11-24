#!/usr/bin/env python3
"""Archived stage profiles with uncertainty and authenticated Richman fate/missingness audit."""
from __future__ import annotations
import argparse, collections, json, math, pathlib, sys
from statistics import mean
import numpy as np
from scipy.stats import norm
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.fit_larceny_study_stage_meta import collapse, PAIRS
from scripts.audit_larceny_stage_direction_robustness import trace, species_components
from scripts.audit_larceny_meta_stage_pairability import source_rows, SOURCE_SHA256
from scripts.audit_richman_2017_archive_mapping import acquire
from scripts.fit_richman_plant_stage import load_original, assemble, ARMS, CONTRASTS, SHA

EPS={'zero':0.,'10pct':-math.log(.90),'25pct':-math.log(.75)}
LABELS=('amplification','attenuation','stable_negative','threshold_crossing_down','threshold_crossing_up','neither_below_threshold')
Z=float(norm.ppf(1-.05/(2*3)))

def profile(u,d,e):
    if u< -e and d< -e:
        return 'amplification' if d-u< -e else 'attenuation' if d-u>e else 'stable_negative'
    if u>=-e and d< -e:return 'threshold_crossing_down'
    if u< -e and d>=-e:return 'threshold_crossing_up'
    return 'neither_below_threshold'
def certify(ui,di,xi,e):
    # Sufficient conditions for every point in a simultaneous working interval set.
    uneg=ui[1]<-e; dneg=di[1]<-e
    unon=ui[0]>=-e; dnon=di[0]>=-e
    if uneg and dneg:
        if xi[1]<-e:return 'amplification'
        if xi[0]>e:return 'attenuation'
        if xi[0]>=-e and xi[1]<=e:return 'stable_negative'
    if unon and dneg:return 'threshold_crossing_down'
    if uneg and dnon:return 'threshold_crossing_up'
    if unon and dnon:return 'neither_below_threshold'
    return 'unresolved'
def interval(q):
    y=float(q['y']);h=Z*math.sqrt(q['v_upper'])
    return [y-h,y+h]
def combine(qs):
    return {'y':mean(q['y'] for q in qs),
            'v_upper':(sum(math.sqrt(q['v_upper']) for q in qs)/len(qs))**2}
def describe(items):
    out={}
    for name,e in EPS.items():
        pts=collections.Counter();certs=collections.Counter();detail={}
        for k,v in sorted(items.items(),key=lambda p:str(p[0])):
            u,d,x=(v[a] for a in ('up','down','delta'))
            ui,di,xi=map(interval,(u,d,x))
            p=profile(u['y'],d['y'],e);c=certify(ui,di,xi,e)
            pts[p]+=1;certs[c]+=1
            detail[str(k)]={'point_profile':p,'working_certified_profile':c,
                            'up':u['y'],'down':d['y'],'delta':x['y'],
                            'simultaneous_working_intervals':{'up':ui,'down':di,'delta':xi}}
        out[name]={'n':len(items),'point_counts':dict(pts),'certified_counts':dict(certs),'details':detail}
    return out
def archive_stage(rows,a,b):
    byid={r['ID']:r for r in rows};blocks=collections.defaultdict(list)
    for q in trace(rows,a,b):
        u=[byid[i] for i in q['upstream_ids']];d=[byid[i] for i in q['downstream_ids']]
        blocks[q['paper_id']].append((u,d))
    items={}
    for k,bl in blocks.items():
        u=collapse([[(1,x)] for x,y in bl])
        d=collapse([[(1,y)] for x,y in bl])
        delta=collapse([[(-1,x),(1,y)] for x,y in bl])
        if abs(d['y']-u['y']-delta['y'])>1e-10:raise ValueError('contrast mismatch')
        items[k]={'up':u,'down':d,'delta':delta}
    comps=species_components({k:q['delta'] for k,q in items.items()},rows)
    merged={k:{a:combine([items[p][a] for p in v['papers']]) for a in ('up','down','delta')} for k,v in comps.items()}
    return {'papers':describe(items),'species_reuse_components':describe(merged),
            'multi_paper_components':[v['papers'] for v in comps.values() if len(v['papers'])>1]}
def archive(path):
    rows=source_rows(path)
    return {'source_sha256':SOURCE_SHA256,'n_effects':len(rows),
            'method':'All eligible exact archived contexts; one equal-block summary per paper. Normal working Bonferroni intervals for upstream, downstream and delta using Cauchy upper sampling variance. Nominal simultaneous within paper only, not across studies, not exact confidence under unknown source variances or matching. No inferred class prevalence, no phylogenetic correction. Thresholds are post-open sensitivity, not clinical or biological equivalence margins.',
            'z':Z,'thresholds':EPS,
            'stages':{b+' minus '+a:archive_stage(rows,a,b) for a,b in PAIRS},
            'pollen_fruit_Glechoma_incidence_only':archive_stage([r for r in rows if r['ID']!=387],'pollen deposition','fruit set')}
def vals(plants,arm,field):
    return [p[field] for (a,k),p in plants.items() if a==arm and p[field] is not None]
def missing_bounds(plants):
    g={}
    for a in ARMS:
        x=vals(plants,a,'pollen_mean');f=vals(plants,a,'prop_fruit_set')
        if len(f)!=40 or not x:raise ValueError('unexpected allocation/fruit coverage')
        g[a]={'n':len(x),'mean':mean(x),'fruit_mean_all_40':mean(f),'n_missing':40-len(x)}
    scenarios={}
    for multiplier in (1.,2.,3.,5.):
        m={a:[v['n']*v['mean']/40,(v['n']+multiplier*v['n_missing'])*v['mean']/40] for a,v in g.items()}
        scenarios[str(multiplier)]={t+'/'+c:[
            math.log(g[t]['fruit_mean_all_40']/g[c]['fruit_mean_all_40'])-math.log(m[t][1]/m[c][0]),
            math.log(g[t]['fruit_mean_all_40']/g[c]['fruit_mean_all_40'])-math.log(m[t][0]/m[c][1])] for t,c in CONTRASTS}
    missing_outcomes={}
    for a in ARMS:
        observed=[p for (t,k),p in plants.items() if t==a and p['pollen_mean'] is not None]
        missing=[p for (t,k),p in plants.items() if t==a and p['pollen_mean'] is None]
        missing_outcomes[a]={label:{'n':len(ps),'fruit_mean':mean(p['prop_fruit_set'] for p in ps),'seed_mean':mean(p['total_seeds_plant'] for p in ps)} for label,ps in [('observed',observed),('unobserved_or_quarantined',missing)]}
    return {'groups':g,'missingness_outcomes':missing_outcomes,'ranges':scenarios,
            'interpretation':'Deterministic hypothetical bounds on full-allocation mean pollen if all missing plant pollen means lie between zero and m times arm observed mean. Fruit is observed for all. Not imputation, no confidence interval, no assumption missing at random; no claim unobserved pollen is physically defined for nonsampled flowers.'}
def bootstrap_profiles(plants,B=20000):
    rng=np.random.default_rng(20261124);boot={};obs={};n={}
    for a in ARMS:
        x=np.asarray([[p['pollen_mean'],p['prop_fruit_set'],p['total_seeds_plant']] for (t,k),p in sorted(plants.items()) if t==a and all(p[f] is not None for f in ('pollen_mean','prop_fruit_set','total_seeds_plant'))],float)
        n[a]=len(x);obs[a]=x.mean(0);boot[a]=x[rng.integers(0,len(x),(B,len(x)))].mean(1)
    out={}
    for t,c in CONTRASTS:
        ok=np.all((boot[t]>0)&(boot[c]>0),axis=1);draw=np.log(boot[t][ok]/boot[c][ok]);point=np.log(obs[t]/obs[c])
        by={}
        for j,endpoint in [(1,'recorded_fruit_fraction'),(2,'total_seeds')]:
            by[endpoint]={}
            for label,e in EPS.items():
                counts=collections.Counter(profile(float(u),float(d),e) for u,d in draw[:,[0,j]])
                by[endpoint][label]={'point_profile':profile(float(point[0]),float(point[j]),e),'bootstrap_fraction':{k:v/len(draw) for k,v in counts.items()},'valid_draws':len(draw)}
        out[t+'/'+c]=by
    return {'n':n,'B':B,'results':out,'scope':'Joint resampling fractions of estimated profiles, not posterior probabilities of biological mechanisms or confirmatory equivalence.'}
def fate_audit(plants):
    checks=[];zero=[];groups={}
    for k,p in sorted(plants.items()):
        fs,ab,lost,tot=[p[x] for x in ('total_successful','aborts','deh, drop, hyl','total_fruit')]
        if any(x is None for x in (fs,ab,lost,tot)):raise ValueError('missing count fields')
        if abs(fs+ab+lost-tot)>1e-8:checks.append({'treatment':k[0],'plant':k[1],'residual':tot-fs-ab-lost})
        if tot==0:zero.append(list(k))
    out={'count_identity_success_plus_aborts_plus_other_equals_total':{'n':len(plants),'matches':len(plants)-len(checks),'mismatches':checks},'zero_denominator_keys':zero}
    if checks:
        out['status']='HOLD_NONCLOSING_FATE_COUNTS';return out
    out['status']='CLOSED_RECORDED_FRUIT_FATES'
    def scope(matched):
        rng=np.random.default_rng(20261124);means={};boots={};n={}
        for a in ARMS:
            ps=[p for (t,k),p in sorted(plants.items()) if t==a and p['total_fruit']>0 and (not matched or p['pollen_mean'] is not None)]
            x=np.array([[p['total_successful']/p['total_fruit'],p['aborts']/p['total_fruit'],p['deh, drop, hyl']/p['total_fruit']] for p in ps],float)
            if not np.allclose(x.sum(1),1):raise ValueError('invalid fate shares')
            n[a]=len(ps);means[a]=x.mean(0);boots[a]=x[rng.integers(0,len(x),(20000,len(x)))].mean(1)
        contrast={}
        for t,c in CONTRASTS:
            diff=means[t]-means[c];b=boots[t]-boots[c]
            contrast[t+'/'+c]={'success_difference':float(diff[0]),'abort_difference':float(diff[1]),'combined_other_difference':float(diff[2]),
                              'ci95_by_share':np.quantile(b,[.025,.975],axis=0).T.tolist(),
                              'success_difference_if_other_fate_can_be_any_success_fraction_by_arm':[
                                float(means[t][0]-means[c][0]-means[c][2]),float(means[t][0]+means[t][2]-means[c][0])]}
        return {'n':n,'mean_share_order':['successful_or_developing','recorded_abort','combined_dehisced_dropped_or_fly_damaged'],
                'mean_shares':{a:v.tolist() for a,v in means.items()},'contrasts':contrast}
    out['all_positive_denominator_plants']=scope(False);out['matched_positive_denominator_plants']=scope(True)
    out['scope']='Accounting partition of recorded fruits, not complete flower cohorts. The other category pools dehiscence, collection loss and insect destruction; unknown viability. Worst assignment is hypothetical, not confidence interval or proof of equal survival. Do not infer causal postfertilization mortality.'
    return out
def richman(path):
    pollen,fruit,meta=load_original(path);p=assemble(pollen,fruit,link_mode='quarantine')
    return {'source_sha256':SHA,'missingness':missing_bounds(p),'fate_audit':fate_audit(p),'profile_resampling':bootstrap_profiles(p)}
def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['archive','richman'],required=True);p.add_argument('--source',type=pathlib.Path);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    if a.kind=='archive':r=archive(acquire(a.out))
    else:
        if not a.source:raise ValueError('authenticated Richman source required')
        r=richman(a.source)
    (a.out/'RESULT.json').write_text(json.dumps(r,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    if a.kind=='archive':
        def compact(s):return {k:{th:{x:y for x,y in v.items() if x!='details'} for th,v in q.items()} if k!='multi_paper_components' else q for k,q in s.items()}
        r={**r,'stages':{k:compact(v) for k,v in r['stages'].items()},'pollen_fruit_Glechoma_incidence_only':compact(r['pollen_fruit_Glechoma_incidence_only'])}
    print('BALANCE_STAGE_PROFILE_'+a.kind.upper()+' '+json.dumps(r,ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()

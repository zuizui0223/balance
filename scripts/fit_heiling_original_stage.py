#!/usr/bin/env python3
"""Authenticated Heiling original plant/raceme linked stage analysis; no new independent archive study."""
from __future__ import annotations
import argparse, collections, hashlib, json, math, pathlib, sys
import numpy as np
from openpyxl import load_workbook
SHA='e11d6e9ef1aacc796c95ced562117c8760197fb62be0e505b9148644106a8fa9'
MD5='31e7e67fa98c5ffb7b4b133686191b90'
POLL=('treatment','plant','raceme','flower','fruit','grains')
FRUIT=('plant_num','raceme_num','flr_count','treatment','total_good_fruit','total_aborted_fruit','total_good_seed','total_aborted_seed')
def num(x):
    if x is None or isinstance(x,str) and x.strip().lower() in ('','na','nan','n/a','.'):return None
    if isinstance(x,bool):raise ValueError('unexpected bool')
    y=float(x)
    if not math.isfinite(y) or y<0:raise ValueError('nonnegative count required')
    return y
def ident(x):
    y=num(x)
    if y is None or y<1 or int(y)!=y:raise ValueError('invalid key '+str(x))
    return int(y)
def norm(x):
    if x is None or isinstance(x,(str,int,float,bool)):return x
    return str(x)
def safe(a,b):return a/b if b and a is not None else None
def extract(path):
    b=path.read_bytes()
    if len(b)!=122150 or hashlib.md5(b).hexdigest()!=MD5 or hashlib.sha256(b).hexdigest()!=SHA:raise ValueError('source mismatch')
    w=load_workbook(path,read_only=True,data_only=True)
    meta=[[norm(v) for v in row] for row in w['Metadata'].values]
    pol=list(w['2015.experimental.rob.poll.dep'].values);fr=list(w['2015.fruitset'].values)
    if tuple(pol[0][:len(POLL)])!=POLL or tuple(fr[0][:len(FRUIT)])!=FRUIT:raise ValueError('header mismatch')
    p=[];f=[];extra=[]
    for i,row in enumerate(pol[1:],2):
        if all(v is None for v in row[:6]):continue
        p.append(dict(zip(POLL,row[:6]))|{'xlsx_row':i})
    for i,row in enumerate(fr[1:],2):
        a=row[:8]
        if all(v is None for v in a):continue
        # Source data table is the first 8 columns; other worksheet notes are not plant data.
        if not isinstance(a[0],(int,float)) or not isinstance(a[1],(int,float)) or not isinstance(a[3],str):
            extra.append({'row':i,'values':[norm(v) for v in a]});continue
        f.append(dict(zip(FRUIT,a))|{'xlsx_row':i})
    print('HEILING_SCHEMA_FULL '+json.dumps({'metadata':meta,'pollen_rows':len(p),'fruit_candidate_rows':len(f),'fruit_extra_rows':extra[:20],'extra_count':len(extra),'pollen_labels':sorted({str(r['treatment']) for r in p}),'fruit_labels':sorted({str(r['treatment']) for r in f})},ensure_ascii=False))
    w.close();return p,f,meta,extra
def aggregate(p,f):
    fruits={};poll=collections.defaultdict(list);flowerkeys=set();arms=collections.defaultdict(set)
    for r in f:
        t=str(r['treatment']);plant=ident(r['plant_num']);rac=ident(r['raceme_num']);k=(t,plant,rac)
        if k in fruits:raise ValueError('duplicate fruit raceme '+str(k))
        a={x:num(r[x]) for x in FRUIT if x not in ('treatment','plant_num','raceme_num')}
        if any(v is None for v in a.values()):raise ValueError('missing fruit count '+str(k))
        a['fruit_fraction']=safe(a['total_good_fruit'],a['total_good_fruit']+a['total_aborted_fruit'])
        a['fruit_per_recorded_flower']=safe(a['total_good_fruit'],a['flr_count'])
        a['seed_per_recorded_flower']=safe(a['total_good_seed'],a['flr_count'])
        if a['fruit_fraction'] is not None and not 0<=a['fruit_fraction']<=1:raise ValueError('fraction')
        fruits[k]=a;arms[t].add(plant)
    for r in p:
        t=str(r['treatment']);plant=ident(r['plant']);rac=ident(r['raceme']);fl=ident(r['flower']);k=(t,plant,rac)
        fk=k+(fl,)
        if fk in flowerkeys:raise ValueError('duplicate flower key '+str(fk))
        flowerkeys.add(fk);poll[k].append({'flower':fl,'fruit':norm(r['fruit']),'grains':num(r['grains']),'xlsx_row':r['xlsx_row']})
    keys=set(fruits)&set(poll)
    print('HEILING_LINK_DIAG '+json.dumps({'fruit_racemes':len(fruits),'pollen_racemes':len(poll),'linked_racemes':len(keys),'fruit_only':[list(k) for k in sorted(set(fruits)-set(poll))],'pollen_only':[list(k) for k in sorted(set(poll)-set(fruits))],'fruit_plants_per_label':{t:sorted(v) for t,v in arms.items()},'fruit_status_values':dict(collections.Counter(str(r['fruit']) for rs in poll.values() for r in rs))},ensure_ascii=False))
    if len(arms)!=3 or any(len(v)!=5 for v in arms.values()) or len(fruits)!=75:raise ValueError('expected 3 arms / 5 plants / 75 racemes; inspect source')
    if not set(poll)<=set(fruits):raise ValueError('unmatched pollen raceme')
    details=[];plants=collections.defaultdict(list)
    for k,a in sorted(fruits.items()):
        rs=poll.get(k,[]);g=[x['grains'] for x in rs if x['grains'] is not None]
        b=dict(a);b['pollen_rows']=len(rs);b['pollen_nonmissing']=len(g)
        b['pollen_mean']=float(np.mean(g)) if g else None
        b['sqrt_raceme_mean']=math.sqrt(b['pollen_mean']) if g else None
        b['pollen_positive_fraction']=float(np.mean([x>0 for x in g])) if g else None
        b['status_value_counts']=dict(collections.Counter(str(x['fruit']) for x in rs))
        b['count_residual']=a['flr_count']-a['total_good_fruit']-a['total_aborted_fruit']
        details.append({'treatment':k[0],'plant':k[1],'raceme':k[2],**b})
        plants[k[:2]].append(b)
    fields=('pollen_mean','sqrt_raceme_mean','pollen_positive_fraction','fruit_fraction','fruit_per_recorded_flower','total_good_seed','seed_per_recorded_flower')
    plant=[]
    for (t,k),rs in sorted(plants.items()):
        if len(rs)!=5:raise ValueError('expected 5 racemes per plant')
        b={'treatment':t,'plant':k,'n_racemes':len(rs),'n_pollen_racemes':sum(r['pollen_mean'] is not None for r in rs)}
        for field in fields:
            vs=[r[field] for r in rs if r[field] is not None]
            b[field]=float(np.mean(vs)) if vs else None
        # Same-raceme complete subset for paired endpoint sensitivity.
        good=[r for r in rs if r['pollen_mean'] is not None and r['fruit_fraction'] is not None]
        for field in ('pollen_mean','fruit_fraction','total_good_seed'):
            b['matched_raceme_'+field]=float(np.mean([r[field] for r in good])) if good else None
        plant.append(b)
    return details,plant,arms
def fit(plant,fields,control,B=20000):
    rng=np.random.default_rng(20261126);arms=sorted({r['treatment'] for r in plant});obs={};boot={};n={}
    for t in arms:
        x=np.array([[r[f] for f in fields] for r in plant if r['treatment']==t and all(r[f] is not None for f in fields)],float)
        n[t]=len(x)
        if len(x)<2 or np.any(x.mean(0)<=0):return {'status':'HOLD','n':n,'fields':fields}
        obs[t]=x.mean(0);boot[t]=x[rng.integers(0,len(x),(B,len(x)))].mean(1)
    effects={}
    for t in arms:
        if t==control:continue
        ok=np.all((boot[t]>0)&(boot[control]>0),axis=1);z=np.log(boot[t][ok]/boot[control][ok]);y=np.log(obs[t]/obs[control])
        def s(v,b):return {'estimate':float(v),'percentile95':[float(a) for a in np.quantile(b,[.025,.975])],'valid_draws':len(b)}
        effects[t+'/'+control]={'lnRR':{f:s(y[i],z[:,i]) for i,f in enumerate(fields)},
           'delta':{f:s(y[i]-y[0],z[:,i]-z[:,0]) for i,f in enumerate(fields) if i>0},
           'covariance_lnRR':np.cov(z,rowvar=False).tolist()}
    return {'status':'DESCRIPTIVE_5_PLANT_PER_ARM','n':n,'fields':fields,'means':{t:{f:float(v[i]) for i,f in enumerate(fields)} for t,v in obs.items()},'contrasts':effects,'B':B}
def main():
    a=argparse.ArgumentParser();a.add_argument('--source',type=pathlib.Path,required=True);a.add_argument('--out',type=pathlib.Path,required=True);p=a.parse_args()
    pollen,fruit,meta,extra=extract(p.source);rac,plant,arms=aggregate(pollen,fruit)
    ctrl=[t for t in arms if t.strip().lower()=='control']
    if len(ctrl)!=1:raise ValueError('control label not resolved')
    c=ctrl[0]
    variants={'raw_pollen_fruit_seed':('pollen_mean','fruit_fraction','total_good_seed'),
        'matched_racemes':('matched_raceme_pollen_mean','matched_raceme_fruit_fraction','matched_raceme_total_good_seed'),
        'recorded_flower_denominator':('pollen_mean','fruit_per_recorded_flower','seed_per_recorded_flower'),
        'sqrt_scale_diagnostic_not_lnRR_comparable':('sqrt_raceme_mean','fruit_fraction','total_good_seed')}
    out={'sha256':SHA,'n_pollen_rows':len(pollen),'n_fruit_racemes':len(rac),'n_plants':len(plant),'n_extra_nondata_rows':len(extra),'metadata':meta,
         'count_closure':dict(collections.Counter(str(x['count_residual']) for x in rac)),
         'pollen_raceme_count':sum(x['pollen_mean'] is not None for x in rac),'plant_records':plant,
         'raceme_records':rac,'variants':{k:fit(plant,v,c) for k,v in variants.items()},
         'scope':'Original same treatment/plant/raceme key linkage, distinct stigma and seed recording grain. Five haphazardly assigned plants per treatment, not 75 independent plants. Equal-raceme means then equal-plant means; 20k arm-stratified bootstrap descriptive with n=5, not original mixed-model replay or equivalence. No same-flower seed data, no mechanistic mediation, no new independent archive study.'}
    p.out.mkdir(parents=True,exist_ok=False);(p.out/'RESULT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('HEILING_PLANT_RESULT '+json.dumps({k:v for k,v in out.items() if k not in ('raceme_records','metadata')},ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()

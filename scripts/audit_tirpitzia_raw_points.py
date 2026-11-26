#!/usr/bin/env python3
"""Descriptive exact-source Tirpitzia raw-row reconstruction, no plant-ID inference."""
import argparse,collections,hashlib,json,math,pathlib,statistics
import xlrd
from scripts.audit_tirpitzia_stage_contrast import DATA
MANIFEST=pathlib.Path('results/stage_dependence_small_n/TIRPITZIA_FEMALE_FILE_MANIFEST_20261126.json')
def load(root,spec):
    p=root/spec['name'];b=p.read_bytes()
    if len(b)!=spec['size'] or hashlib.sha256(b).hexdigest()!=spec['sha256'] or hashlib.md5(b).hexdigest()!=spec['md5']:raise ValueError('source identity mismatch')
    w=xlrd.open_workbook(file_contents=b)
    if w.nsheets!=1:raise ValueError('unexpected sheet count')
    s=w.sheet_by_index(0);return s.row_values(0),[s.row_values(i) for i in range(1,s.nrows)]
def summarize(x):
    return {'n_rows':len(x),'mean':statistics.mean(x),'sd_rows':statistics.stdev(x) if len(x)>1 else None,'naive_row_se':statistics.stdev(x)/math.sqrt(len(x)) if len(x)>1 else None,'min':min(x),'max':max(x),'zero_rows':sum(v==0 for v in x)}
def group(rows,endpoint):
    out=collections.defaultdict(list);missing=[]
    for i,r in enumerate(rows,2):
        v,t,m=r[:3]
        if not isinstance(t,(int,float)) or not isinstance(m,(int,float)) or t!=int(t) or m!=int(m) or m not in (1,2) or t not in (range(1,6) if endpoint=='seed' else range(1,4)):raise ValueError('unrecognized row grouping '+str((i,r)))
        if v=='' or (isinstance(v,str) and v.strip().lower() in ('na','n/a','nan')):missing.append(i);continue
        if not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 or (endpoint!='tube' and v>100):raise ValueError('invalid outcome '+str((i,r)))
        out[int(m),int(t)].append(v)
    return out,missing
def ratio(a,b):
    if min(a,b)<=0:raise ValueError('nonpositive arm mean')
    return math.log(a/b)
def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
    manifest=json.loads(MANIFEST.read_text())
    tables={};groups={}
    for endpoint,prefix in [('germination','7_'),('tube','8_'),('seed','9_')]:
        spec=next(x for x in manifest['files'] if x['name'].startswith(prefix))
        header,rows=load(a.source,spec);g,missing=group(rows,endpoint);groups[endpoint]=g
        tables[endpoint]={'header':header,'raw_rows':len(rows),'missing_outcome_rows':missing,'groups_by_original_code':{str(m)+'/'+str(t):summarize(v) for (m,t),v in sorted(g.items())}}
    expected={'germination':169,'tube':179,'seed':412}
    if any(tables[k]['raw_rows']!=n for k,n in expected.items()):raise ValueError('source row count drift')
    contrasts={};reconstruction=[]
    for m,mc in [('L',1),('S',2)]:
        contrasts[m]={}
        for arm,gcode,scode in [('H',2,4),('N',3,5)]:
            gm=lambda i:statistics.mean(groups['germination'][mc,i])
            sm=lambda i:statistics.mean(groups['seed'][mc,i])
            up=ratio(gm(gcode),gm(1));down=ratio(sm(scode),sm(3))
            contrasts[m][arm]={'germination_lnRR':up,'seed_lnRR':down,'delta':down-up}
        for arm,gcode,scode in [('C',1,3),('H',2,4),('N',3,5)]:
            for endpoint,code,j in [('germination',gcode,0),('seed',scode,2)]:
                ss=summarize(groups[endpoint][mc,code]);reported=DATA[m][arm][j]
                reconstruction.append({'morph':m,'arm':arm,'endpoint':endpoint,'raw_mean':ss['mean'],'reported_mean':reported,'difference':ss['mean']-reported,'raw_naive_row_se':ss['naive_row_se'],'reported_se':DATA[m][arm][j+1]})
    for convention,maps in [('sheet_header',{'L':2,'S':1}),('README',{'L':1,'S':2})]:
        for m,mc in maps.items():
            contrasts[m]['tube_'+convention]={arm:ratio(statistics.mean(groups['tube'][mc,code]),statistics.mean(groups['tube'][mc,1])) for arm,code in [('H',2),('N',3)]}
    r={'tables':tables,'germination_seed_reconstruction':reconstruction,'morph_stage_contrasts':contrasts,'L_minus_S_delta':{t:contrasts['L'][t]['delta']-contrasts['S'][t]['delta'] for t in ('H','N')},
       'scope':'Original raw row summaries only. Germination and seed code L=1/S=2 agreed by headers and README; tube code disagrees (sheet S=1/L=2, README L=1/S=2). Report both tube mappings, do not choose on outcome. No plant IDs, no cross-stage cohort linkage, no valid cluster covariance from archive. Naive row SE diagnostic only; no row-based hypothesis tests or bootstrap. Seed table includes distinct natural-robbing and hand-pollination experiments. No causal mediation or new independent study count.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False,allow_nan=False)+'\n');print('TIRPITZIA_RAW_POINTS '+json.dumps(r,ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()

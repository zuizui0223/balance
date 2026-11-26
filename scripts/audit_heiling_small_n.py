#!/usr/bin/env python3
"""Sensitivity of Heiling's plant-level stage contrast; no randomization claim."""
import itertools,json,math,pathlib,statistics,argparse
SOURCE='results/distyly_stage/HEILING_FLOWER_STAGE_VERIFIED_20261126.json'
def delta(a,b):
    m=lambda x,k:statistics.mean(r[k] for r in x)
    return math.log(m(a,'flower_code_success_fraction')/m(b,'flower_code_success_fraction'))-math.log(m(a,'pollen_mean')/m(b,'pollen_mean'))
def run(plant):
    out={}
    for t in ('pr','cr'):
        a=[r for r in plant if r['treatment']==t];b=[r for r in plant if r['treatment']=='control']
        if len(a)!=5 or len(b)!=5:raise ValueError('expected five plants per arm')
        obs=delta(a,b);x=a+b;per=[]
        for idx in itertools.combinations(range(10),5):
            ii=set(idx);per.append(delta([v for i,v in enumerate(x) if i in ii],[v for i,v in enumerate(x) if i not in ii]))
        leave=[{'arm':v['treatment'],'plant':v['plant'],'delta':delta([p for p in a if p is not v],[p for p in b if p is not v])} for v in x]
        leave2=[{'removed_treated':u['plant'],'removed_control':v['plant'],'delta':delta([p for p in a if p is not u],[p for p in b if p is not v])} for u in a for v in b]
        k=sum(abs(v)>=abs(obs)-1e-12 for v in per)
        out[t]={'estimate':obs,'exchangeability_diagnostic':{'enumerated':len(per),'at_least_as_extreme':k,'p_two_sided':k/len(per)},'leave_one':leave,'leave_one_per_arm':leave2}
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=pathlib.Path,default=pathlib.Path(SOURCE));p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
    d=json.loads(a.source.read_text());assert d['sha256']=='e11d6e9ef1aacc796c95ced562117c8760197fb62be0e505b9148644106a8fa9'
    x=run(d['plant_records']);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
    print('HEILING_SMALL_N '+json.dumps(x,allow_nan=False))

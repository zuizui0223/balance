#!/usr/bin/env python3
"""Post-open directional robustness and primary-source trace queue; not causal mediation."""
from __future__ import annotations
import argparse, json, math, sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from scipy.stats import binomtest
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts.fit_larceny_study_stage_meta import collect, collapse, pool, PAIRS, RHO
from scripts.audit_larceny_meta_stage_pairability import source_rows, CONTEXT, SOURCE_SHA256

SCOPES=('paper_species','context','unique_context')
# Three fields necessary to distinguish the basic exposure; no claim that other missing labels are harmless.
CORE=('experiment_level','larceny_type','damage')
MISSING={'','na','n/a','nan','none','unknown','not reported','not available','?','-'}
def present(v):return v is not None and str(v).strip().lower() not in MISSING

def holm(pvals):
    ordered=sorted(pvals,key=lambda k:pvals[k]); out={}; running=0.
    for i,k in enumerate(ordered):
        running=max(running,(len(ordered)-i)*pvals[k]);out[k]=min(1.,running)
    return out

def sign_summary(items):
    ys=[x['y'] for x in items.values()]
    pos=sum(y>0 for y in ys); neg=sum(y<0 for y in ys); n=pos+neg
    return {'k':len(ys),'positive':pos,'negative':neg,'ties':len(ys)-n,
            'median':median(ys) if ys else None,'equal_cluster_mean':mean(ys) if ys else None,
            'sign_p_nominal':float(binomtest(pos,n,.5).pvalue) if n else 1.0}

def loo(items):
    if len(items)<6:return {'status':'INSUFFICIENT_FOR_LEAVE_ONE_OUT'}
    result={}
    for r in RHO:
        fits={str(k):pool([v for p,v in items.items() if p!=k],r) for k in items}
        mus=[f['mu'] for f in fits.values()]; full=pool(list(items.values()),r)['mu']
        result[str(r)]={'mu_range':[min(mus),max(mus)],
            'same_sign':sum(mu*full>0 for mu in mus),'n':len(mus),
            'intervals_excluding_zero':sum(f['ci95'][0]*f['ci95'][1]>0 for f in fits.values()),
            'largest_influence_paper':max(fits,key=lambda k:abs(fits[k]['mu']-full))}
    return result

def species_components(items,rows):
    """Conservative connected components across papers sharing any included plant species.
    This is a sensitivity to species reuse, NOT phylogenetic independence."""
    byid={r['ID']:r for r in rows}
    bysp=defaultdict(set)
    for p,item in items.items():
        for i in item['ids']:bysp[byid[i]['species']].add(p)
    parent={p:p for p in items}
    def root(p):
        while parent[p]!=p:p=parent[p]
        return p
    for ps in bysp.values():
        ps=sorted(ps)
        for p in ps[1:]:parent[root(p)]=root(ps[0])
    groups=defaultdict(list)
    for p in items:groups[root(p)].append(p)
    components={}
    for ps in groups.values():
        vals=[items[p] for p in ps]
        components[str(min(ps))]={'y':mean(v['y'] for v in vals),
            'v_ind':sum(v['v_ind'] for v in vals)/len(vals)**2,
            'v_upper':(sum(math.sqrt(v['v_upper']) for v in vals)/len(vals))**2,
            'papers':sorted(ps)}
    return components

def trace(rows,a,b):
    groups=defaultdict(lambda:defaultdict(list))
    for r in rows:
        if r['sub_response_variable'] in (a,b):
            groups[(r['ref-ID'],r['species'],*(r[k] for k in CONTEXT))][r['sub_response_variable']].append(r)
    out=[]
    for k,g in sorted(groups.items(),key=lambda x:str(x[0])):
        if not {a,b}.issubset(g):continue
        context=dict(zip(CONTEXT,k[2:]))
        record={'paper_id':k[0],'species':k[1],'title':g[a][0]['title'],'reference':g[a][0]['reference'],
                'upstream':a,'downstream':b,
                'upstream_ids':[r['ID'] for r in g[a]],'downstream_ids':[r['ID'] for r in g[b]],
                'context':context,'unique_per_endpoint':len(g[a])==len(g[b])==1,
                'core_present':all(present(context[c]) for c in CORE),
                'same_experiment_verified':False,'same_denominator_verified':False,
                'sampling_covariance_known':False}
        out.append(record)
    return out

def run(rows):
    byid={r['ID']:r for r in rows}
    scopes={s:{} for s in SCOPES+('core_complete_context',)}
    inventories={}
    contexts={}
    for a,b in PAIRS:
        name=b+' minus '+a
        inventory=trace(rows,a,b);inventories[name]=inventory
        contexts[name]={(q['paper_id'],q['species'],tuple(q['context'][c] for c in CONTEXT)) for q in inventory}
        coreids={i for q in inventory if q['core_present'] for i in q['upstream_ids']+q['downstream_ids']}
        for scope in scopes:
            p=collect([r for r in rows if r['ID'] in coreids],a,b,'context') if scope=='core_complete_context' else collect(rows,a,b,scope)
            comp=species_components(p,rows)
            scopes[scope][name]={'paper_sign':sign_summary(p),
                 'leave_one_paper_out':loo(p),
                 'species_reuse_components':sign_summary(comp),
                 'multi_paper_components':[v['papers'] for v in comp.values() if len(v['papers'])>1],
                 'component_fits':{str(r):pool(list(comp.values()),r) for r in RHO},
                 'paper_queue':[{'paper_id':k,'y':v['y'],'species':sorted({byid[i]['species'] for i in v['ids']}),
                       'reference':byid[v['ids'][0]]['reference'],'title':byid[v['ids'][0]]['title']} for k,v in sorted(p.items())]}
    # The 4 endpoints are a natural family; additional scopes are post-open sensitivity.
    for s,results in scopes.items():
        ps={k:v['paper_sign']['sign_p_nominal'] for k,v in results.items()}
        for k,padj in holm(ps).items():results[k]['paper_sign']['holm_within_scope']=padj
    # Extra conservative family encompassing all scopes and all stage contrasts.
    p_all={(s,k):v['paper_sign']['sign_p_nominal'] for s,res in scopes.items() for k,v in res.items()}
    for (s,k),p in holm(p_all).items():scopes[s][k]['paper_sign']['holm_all_16']=p
    n1='visitation rate minus nectar volume'; n2='fruit set minus pollen deposition'
    joint=contexts[n1]&contexts[n2]
    overlap={q[0] for q in contexts[n1]}&{q[0] for q in contexts[n2]}
    return {'source_sha256':SOURCE_SHA256,'n_effects':len(rows),
        'scope':'Post-open descriptive sign-symmetry diagnostics; four-stage Holm within each scope and across all 16. Not a confirmatory test of causal attenuation. No independence guaranteed across papers/species.',
        'results':scopes,'primary_source_queue':inventories,
        'joint_focal_stage_coverage':{'shared_paper_ids':sorted(overlap),
            'same_archived_context_count':len(joint),'same_archived_context_papers':sorted({q[0] for q in joint}),
            'verified_same_experiment_count':0,'verified_same_experiment_count_interpretation':'Not verified here, not evidence of biological absence.'}}
def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    result=run(source_rows(a.source));a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    compact={'source_sha256':result['source_sha256'],'n_effects':result['n_effects'],'joint':result['joint_focal_stage_coverage'],
        'scopes':{s:{k:{x:v[x] for x in ('paper_sign','leave_one_paper_out','species_reuse_components','multi_paper_components','component_fits')} for k,v in z.items()} for s,z in result['results'].items()},
        'focal_queue':{k:result['primary_source_queue'][k] for k in ('visitation rate minus nectar volume','fruit set minus pollen deposition')}}
    print('BALANCE_DIRECTION_RESULT_BEGIN')
    print(json.dumps(compact,ensure_ascii=False,allow_nan=False))
    print('BALANCE_DIRECTION_RESULT_END')
if __name__=='__main__':main()

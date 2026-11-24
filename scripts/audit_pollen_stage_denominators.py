#!/usr/bin/env python3
"""Primary-source endpoint semantics and worst-case archived pairing sensitivity."""
from __future__ import annotations
import argparse, json, math, pathlib, sys
from collections import defaultdict
from statistics import mean
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.audit_larceny_meta_stage_pairability import source_rows, SOURCE_SHA256
from scripts.audit_richman_2017_archive_mapping import acquire
from scripts.fit_larceny_study_stage_meta import collect, pool, RHO
from scripts.audit_larceny_stage_direction_robustness import trace, sign_summary, species_components

UP='pollen deposition'; DOWN='fruit set'
GLECHOMA_DOI='10.1007/s11258-006-9244-y'
WU_DOI='10.1093/jpe/rtad036'
def lr(t,c):return math.log(t/c)
def interval(y,v):return [y-1.959963984540054*math.sqrt(v),y+1.959963984540054*math.sqrt(v)]
def pairing_envelope(rows):
    """All possible one-row-per-endpoint selections within each exact context.
    Average block extrema within paper. This bounds selections, not real matches."""
    byid={r['ID']:r for r in rows}; grouped=defaultdict(list)
    for q in trace(rows,UP,DOWN):
        u=[byid[i]['yi'] for i in q['upstream_ids']]
        d=[byid[i]['yi'] for i in q['downstream_ids']]
        grouped[q['paper_id']].append({'species':q['species'],'up_ids':q['upstream_ids'],
            'down_ids':q['downstream_ids'],'candidate_pairs':len(u)*len(d),
            'min':min(d)-max(u),'max':max(d)-min(u)})
    out=[]
    for paper,blocks in sorted(grouped.items()):
        lo=mean(b['min'] for b in blocks);hi=mean(b['max'] for b in blocks)
        out.append({'paper_id':paper,'min':lo,'max':hi,
                    'sign_invariant':'negative' if hi<0 else 'positive' if lo>0 else 'not_strictly_invariant',
                    'blocks':blocks,'treatment_pair_verified':False})
    return out
def source_mapping(rows):
    byid={r['ID']:r for r in rows}
    expected={'incidence':lr(64.86,83.33),'conditional_load':lr(15.96,13.85),'fruit':lr(58.89,80.35)}
    ids=[384,387,385]; mapping={}
    for name,y in expected.items():
        hits=[i for i in ids if abs(byid[i]['yi']-y)<1e-10]
        if len(hits)!=1:raise ValueError('Glechoma original-point identity not reproduced '+name)
        mapping[name]=hits[0]
    if len(set(mapping.values()))!=3 or any(byid[i]['ref-ID']!=72 for i in ids):raise ValueError('archive mapping invalid')
    for name,i in mapping.items():
        if byid[i]['sub_response_variable']!=(DOWN if name=='fruit' else UP):raise ValueError('endpoint category drift')
    old=expected['fruit']-mean([expected['incidence'],expected['conditional_load']])
    new=expected['fruit']-expected['incidence']
    return {'doi':GLECHOMA_DOI,'study':'Zhang et al. 2007, Glechoma longituba',
        'source':'Original Results and Methods, author manuscript copy: https://www.academia.edu/4001739/Nectar_robbing_of_a_carpenter_bee_and_its_effects_on_the_reproductive_fitness_of_Glechoma_longituba_Lamiaceae',
        'published':{'robbed':{'pollinated_percent':64.86,'conditional_pollen_load':15.96,'fruit_percent':58.89,'n_pollination_reported':575,'n_load_reported':373},
                     'unrobbed':{'pollinated_percent':83.33,'conditional_pollen_load':13.85,'fruit_percent':80.35,'n_pollination_reported':584,'n_load_reported':469}},
        'lnRR':expected,'archive_id_map':mapping,'archived_rows':[byid[i] for i in ids],
        'mixed_upstream_delta':old,'incidence_only_delta':new,'conditional_load_only_delta':expected['fruit']-expected['conditional_load'],
        'absolute_delta_reduction_fraction':1-abs(new)/abs(old),
        'scope':'Exact reported point identities. Destructive stigma sampling and other tagged flowers for fruit: not same flower, not known common cohort or covariance. Pollination incidence and conditional positive load are biologically different. Natural robbery association, not randomized treatment.'}
def wu_audit(rows):
    byid={r['ID']:r for r in rows}
    data={'pollen_deposition':{'id':481,'t':9.73,'c':30.79,'se_t':3.37,'se_c':2.13},
          'fruit_set':{'id':482,'t':8.18,'c':28.71,'se_t':3.39,'se_c':2.08}}
    for d in data.values():
        d['lnRR']=lr(d['t'],d['c'])
        d['source_delta_variance']=(d['se_t']/d['t'])**2+(d['se_c']/d['c'])**2
        d['archived_vi']=byid[d['id']]['vi']
        if abs(d['lnRR']-byid[d['id']]['yi'])>1e-10:raise ValueError('Wu archive point mismatch')
    p,f=data['pollen_deposition'],data['fruit_set']; delta=f['lnRR']-p['lnRR']
    v1,v2=p['source_delta_variance'],f['source_delta_variance'];x=math.sqrt(v1);y=math.sqrt(v2)
    return {'doi':WU_DOI,'study':'Wu & Gao 2024, Thunia alba','n_inflorescences':{'removed':43,'intact':40},
        'source_reported_mean_SE':data,'delta':delta,
        'working_normal95_independence':interval(delta,v1+v2),
        'working_normal95_min_variance':interval(delta,(x-y)**2),
        'working_normal95_max_variance':interval(delta,(x+y)**2),
        'rho_needed_for_negative_normal95':(v1+v2-(delta/1.959963984540054)**2)/(2*x*y),
        'scope':'First-order log ratio delta method on reported SEs; not recovered joint covariance. Same intervention and inflorescence groups; unverified parent plant dependence and no common flower rows. No causal effect of robbery isolated.'}
def fit_scope(rows):
    p=collect(rows,UP,DOWN,'context');comp=species_components(p,rows)
    return {'paper_sign':sign_summary(p),'paper_fits':{str(r):pool(list(p.values()),r) for r in RHO},
        'species_sign':sign_summary(comp),'species_fits':{str(r):pool(list(comp.values()),r) for r in RHO}}
def run(rows):
    g=source_mapping(rows);w=wu_audit(rows);env=pairing_envelope(rows)
    conditional_id=g['archive_id_map']['conditional_load']
    incidence_id=g['archive_id_map']['incidence']
    variants={
        'original_archive':rows,
        'Glechoma_2007_incidence_only':[r for r in rows if r['ID']!=conditional_id],
        'Glechoma_2007_conditional_load_only':[r for r in rows if r['ID']!=incidence_id],
        'Glechoma_2007_excluded_for_distinct_cohorts':[r for r in rows if r['ref-ID']!=72],
        'both_Glechoma_studies_excluded':[r for r in rows if r['ref-ID'] not in (71,72)]}
    return {'source_sha256':SOURCE_SHA256,'n_original_effects':len(rows),'source_endpoint_audit':{'glechoma':g,'wu':w},
        'archive_pairing_envelope':env,'pairing_sign_counts':{k:sum(e['sign_invariant']==k for e in env) for k in ('negative','positive','not_strictly_invariant')},
        'sensitivity':{k:fit_scope(v) for k,v in variants.items()},
        'scope':'Post-open source audit and partial correction sensitivity only. Other studies have not been fully denominator-harmonized. No causal transmission, no matched cohort, no new independent study, no V4 changes.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    result=run(source_rows(acquire(a.out)))
    (a.out/'POLLEN_DENOMINATOR_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('BALANCE_DENOMINATOR_RESULT '+json.dumps(result,ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()

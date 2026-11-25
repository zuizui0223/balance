#!/usr/bin/env python3
"""Published morph-resolved female germination-to-seed contrasts, no raw cohort inference."""
from __future__ import annotations
import argparse,json,math,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.audit_richman_2017_archive_mapping import acquire
from scripts.audit_larceny_meta_stage_pairability import source_rows,SOURCE_SHA256
SOURCE='https://doi.org/10.1002/ece3.10714'
# Fig. 4/results, morph-specific printed mean and SE in percent; no pooled means substituted.
DATA={'L':{'C':[83.55,4.59,80.11,5.62],'H':[58.59,1.30,33.50,3.89],'N':[59.55,1.78,40.00,4.39]},
      'S':{'C':[87.13,4.71,61.21,5.66],'H':[49.212,4.52,42.90,3.20],'N':[49.02,3.33,47.25,3.73]}}
VISIT={'L':{'C':[75.36,6.42,52.70,3.63],'R':[64.32,7.22,39.47,3.85]},
       'S':{'C':[74.90,6.82,48.50,2.66],'R':[48.63,9.01,39.77,4.98]}}
def contrast(t,c):
    u=math.log(t[0]/c[0]);d=math.log(t[2]/c[2]);delta=d-u
    se=[t[1]/t[0],c[1]/c[0],t[3]/t[2],c[3]/c[2]]
    indep=math.sqrt(sum(x*x for x in se));upper=sum(se)
    ci=lambda s:[delta-1.959963984540054*s,delta+1.959963984540054*s]
    return {'upstream_lnRR':u,'downstream_lnRR':d,'delta':delta,
            'upstream_reduction':-math.expm1(u),'downstream_reduction':-math.expm1(d),
            'se_independence':indep,'se_Cauchy_upper':upper,
            'normal95_independence':ci(indep),'normal95_Cauchy_upper':ci(upper)}
def morph_difference(a,b):
    d=a['delta']-b['delta']
    si=math.hypot(a['se_independence'],b['se_independence'])
    sm=math.hypot(a['se_Cauchy_upper'],b['se_Cauchy_upper'])
    su=a['se_Cauchy_upper']+b['se_Cauchy_upper']
    ci=lambda s:[d-1.959963984540054*s,d+1.959963984540054*s]
    return {'L_minus_S':d,'normal95_independence':ci(si),'normal95_within_morph_upper_assume_independent_morphs':ci(sm),'normal95_full_Cauchy_upper':ci(su)}
def report(rows):
    focal=[r for r in rows if r['ref-ID']==104]
    if not focal or any(r['species']!='Tirpitzia_sinensis' for r in focal):raise ValueError('archive identity mismatch')
    d={m:{t:contrast(DATA[m][t],DATA[m]['C']) for t in ('H','N')} for m in DATA}
    v={m:contrast(VISIT[m]['R'],VISIT[m]['C']) for m in VISIT}
    matched=[]
    # List exact arithmetic candidates without promoting their provenance or metric identity.
    for m in DATA:
        for t in ('H','N'):
            for stage,k in [('female_germination',0),('seed_set',2)]:
                y=math.log(DATA[m][t][k]/DATA[m]['C'][k])
                matches=[{'ID':r['ID'],'archive_endpoint':r['sub_response_variable'],'yi':r['yi'],'vi':r['vi']} for r in focal if abs(r['yi']-y)<1e-8]
                matched.append({'morph':m,'arm':t,'source_endpoint':stage,'source_lnRR':y,'exact_point_candidates':matches,'same_metric_verified':False})
    return {'source_doi':SOURCE,'dataset_doi':'10.5061/dryad.6hdr7sr62','archive_sha256':SOURCE_SHA256,
      'published_points_mean_SE_percent':DATA,'published_natural_visitation_and_seed_mean_SE_percent':VISIT,
      'hand_pollination_germination_seed':d,'hand_pollination_morph_delta':{t:morph_difference(d['L'][t],d['S'][t]) for t in ('H','N')},
      'natural_visitation_seed_descriptive':v,'natural_morph_delta':morph_difference(v['L'],v['S']),
      'archive_focal_count':len(focal),'archive_focal_endpoint_counts':{s:sum(r['sub_response_variable']==s for r in focal) for s in sorted({r['sub_response_variable'] for r in focal})},
      'archive_focal_rows':[{'id':r['ID'],'endpoint':r['sub_response_variable'],'response':r['response_variable'],'yi':r['yi'],'vi':r['vi'],'experiment_level':r['experiment_level']} for r in focal],
      'point_identity_candidates':matched,
      'source_reporting_checks':{'germination_interaction_table2_p':.931,'germination_interaction_prose_says_significant':True,'seed_set_interaction_table2_p':.036,
        'pooled_germination_control_reported':83.81,'pooled_germination_control_se_reported':11.72,
        'pooled_values_not_used_for_morph_estimates':True},
      'scope':'Reported morph-specific summary point reanalysis, not original plant-level refit. H=artificial rob hole; N=nectar removal without intentional damage; C=undamaged intermorph hand pollination. Germination experiment about 25 plants per morph, three buds randomly allocated, destructive pistil collection at 6 h. Seed experiment initially 50 plants per morph, different flowers with losses to herbivory/other factors, >20 per treatment reported. Unknown actual sample overlap, denominators and covariance; seed fraction conditional on recovered material. Normal working intervals rely on printed SE and first-order delta approximation, not verified sampling inference; shared controls and multiplicity preclude treating four contrasts as independent. Germination rate is not pollen deposition. The natural visitation-seed comparisons are observational and separate from hand pollination. No inference of causal mediation or structural BALANCE, no added independent archive study.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=pathlib.Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    d=report(source_rows(acquire(a.out)));(a.out/'RESULT.json').write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print('BALANCE_DISTYLY_RESULT '+json.dumps(d,ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()

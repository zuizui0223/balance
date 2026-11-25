#!/usr/bin/env python3
"""Irwin 2009: full-flower denominator source and archived effects, no fabricated pairing."""
from __future__ import annotations
import argparse,json,math,pathlib,sys
from statistics import mean
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.audit_richman_2017_archive_mapping import acquire
from scripts.audit_larceny_meta_stage_pairability import source_rows,SOURCE_SHA256
from scripts.audit_larceny_stage_direction_robustness import trace
DOI='10.1093/aob/mcp056'
PUBLISHED_MORE={'pollen deposition':.17,'fruit set':.56,'seed set':.34,'total seeds':.58}
def report(rows):
    focal=[r for r in rows if r['ref-ID']==81]
    if not focal or any(r['species']!='Ipomopsis_aggregata' for r in focal):raise ValueError('source identity')
    points={k:-math.log1p(v) for k,v in PUBLISHED_MORE.items()}
    bounds={k:[-math.log1p(v+.005),-math.log1p(v-.005)] for k,v in PUBLISHED_MORE.items()}
    delta={k:points[k]-points['pollen deposition'] for k in ('fruit set','seed set','total seeds')}
    delta_bounds={k:[bounds[k][0]-bounds['pollen deposition'][1],bounds[k][1]-bounds['pollen deposition'][0]] for k in delta}
    by={}
    for stage in sorted({r['sub_response_variable'] for r in focal}):
        rs=[r for r in focal if r['sub_response_variable']==stage]
        by[stage]={'rows':[{'id':r['ID'],'yi':r['yi'],'vi':r['vi'],'experiment_level':r['experiment_level']} for r in rs],
                   'equal_row_mean':mean(r['yi'] for r in rs),'range':[min(r['yi'] for r in rs),max(r['yi'] for r in rs)]}
    candidates=[]
    for q in trace(rows,'pollen deposition','fruit set'):
        if q['paper_id']!=81:continue
        byid={r['ID']:r for r in rows}
        d=[byid[j]['yi']-byid[i]['yi'] for i in q['upstream_ids'] for j in q['downstream_ids']]
        candidates.append({'up_ids':q['upstream_ids'],'down_ids':q['downstream_ids'],
            'n_candidate_combinations':len(d),'delta_range':[min(d),max(d)],
            'all_negative':max(d)<0,'same_group_mapping_verified':False})
    return {'source_sha256':SOURCE_SHA256,'paper_doi':DOI,'original_full_text':'https://pmc.ncbi.nlm.nih.gov/articles/PMC2701760/',
        'study':'Irwin 2009, Ipomopsis aggregata',
        'original_reported_low_relative_to_high_fraction_more':PUBLISHED_MORE,
        'reported_F_tests':{'pollen_deposition':{'F':5.68,'df':[1,48],'p':.02},'fruit_set':{'F':34.88,'df':[1,48],'p':'<.0001'},'seeds_per_fruit':{'F':20.22,'df':[1,48],'p':'<.0001'},'total_seeds':{'F':17.90,'df':[1,48],'p':.0001}},
        'high_vs_low_lnRR_from_rounded_prose':points,'stage_delta':delta,'rounded_percentage_sensitivity_not_ci':delta_bounds,
        'archive_rows':by,'archive_pollen_fruit_pairing_candidates':candidates,
        'claim_ceiling':'Original authors report one overall female-reproduction comparison and eight group means; all fruits collected/scored seeded or aborted, fruit fraction seed-bearing fruits/all flowers. Pollen receipt on destructive stigma samples, not same flowers. Rounded reported point ratios, no reconstructed joint uncertainty. Group identities, sample covariance, raw plant data not retrieved. No independent species replication of Richman. No combining subgroup effects as independent studies or causal stage amplification.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=pathlib.Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    d=report(source_rows(acquire(a.out)));(a.out/'RESULT.json').write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print('IRWIN_2009_DENOMINATOR '+json.dumps(d,ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()

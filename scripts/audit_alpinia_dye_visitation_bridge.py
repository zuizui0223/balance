#!/usr/bin/env python3
"""Source-gated one-study Alpinia S1 dye, S2 fruits and published visitor mean audit.

Fluorescent dye is not genetic paternity. The stages were not measured on the
same individual flowers and cannot identify mediation, fitness or BALANCE Phi.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
S1_SHA='c7eb1f2b416d876d30d7750f977d3d5f58cdc32f166684b50112ef95c758e25f'
S1_CSV_SHA='76258463cba9a34dbce10837d33c21af2ed1a4028c98543fdeedf6b509b1b4a1'
S2_CSV_SHA='ad52b6ca136b63b9dd049ec01993636869c5e16635c4e2e6b77e96f741ab374c'
DIRS=('W-E','N-S','E-W','S-N')
BINS=((0,2),(4,6),(8,10),(12,14),(16,18),(20,22),(24,26),(28,30))
S1_HEADER=['direction','distance_lo_m','distance_hi_m','mean_dye_positive_robbed','mean_dye_positive_unrobbed']
S2_HEADER=['year','treatment','direction','inflorescences','flowers','fruits','seeds_in_sample','sampled_fruits']

def _sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _validate_s1(rows:list[dict])->list[dict]:
    expected={(d,*b) for d in DIRS for b in BINS}
    if len(rows)!=32 or {(r['direction'],r['distance_lo_m'],r['distance_hi_m']) for r in rows}!=expected:
        raise ValueError('S1 source requires all 32 unique direction/distance bins')
    for r in rows:
        if list(r)!=S1_HEADER:
            raise ValueError('S1 header changed')
        if any(type(r[k]) is not float or not 0<=r[k]<=1.0 for k in S1_HEADER[3:]):
            raise ValueError('S1 nonfinite or out-of-range dye mean')
    return rows

def _parse_s1_text(text:str)->list[dict]:
    rows=[];direction=None
    for line in text.splitlines():
        if not line.strip().startswith('|'):continue
        p=[v.strip() for v in line.strip().strip('|').split('|')]
        if len(p)!=3:continue
        if p[0] in DIRS:
            direction=p[0];continue
        m=re.fullmatch(r'(\d+)-(\d+)m?',p[0])
        if m and direction and p[1] and p[2]:
            rows.append(dict(zip(S1_HEADER,(direction,int(m[1]),int(m[2]),float(p[1]),float(p[2])))))
    return _validate_s1(rows)

def _load_s1(root:Path,source_doc:Path|None,text:Path|None)->list[dict]:
    if source_doc is not None and _sha(source_doc)!=S1_SHA:
        raise ValueError('Official S1 DOC SHA256 mismatch')
    path=root/'data/external/alpinia_2015/S1_FLUORESCENT_TRANSFER_32_CELLS.csv'
    if _sha(path)!=S1_CSV_SHA:
        raise ValueError('S1 source CSV SHA256 mismatch')
    rd=csv.DictReader(io.StringIO(path.read_text(encoding='utf-8')))
    if rd.fieldnames!=S1_HEADER:raise ValueError('S1 source CSV header changed')
    rows=_validate_s1([{'direction':r['direction'],
                       'distance_lo_m':int(r['distance_lo_m']),
                       'distance_hi_m':int(r['distance_hi_m']),
                       'mean_dye_positive_robbed':float(r['mean_dye_positive_robbed']),
                       'mean_dye_positive_unrobbed':float(r['mean_dye_positive_unrobbed'])} for r in rd])
    if text is not None and _parse_s1_text(text.read_text(encoding='utf-8'))!=rows:
        raise ValueError('S1 source antiword text and 32-cell CSV disagree')
    return rows

def _load_s2(root:Path)->list[dict]:
    path=root/'data/external/alpinia_2015/S2_EXTRACTED_16_CELLS.csv'
    if _sha(path)!=S2_CSV_SHA:raise ValueError('S2 source CSV SHA256 mismatch')
    rd=csv.DictReader(io.StringIO(path.read_text(encoding='utf-8')))
    if rd.fieldnames!=S2_HEADER:raise ValueError('S2 source header changed')
    rows=[{k:(v if k in ('treatment','direction') else int(v)) for k,v in row.items()} for row in rd]
    expected={(y,t,d) for y in (2005,2007) for t in ('Robbed','Unrobbed') for d in DIRS}
    if len(rows)!=16 or {(r['year'],r['treatment'],r['direction']) for r in rows}!=expected:
        raise ValueError('S2 source requires 16 year/treatment/direction cells')
    for row in rows:
        if row['inflorescences']!=60 or not 0<row['sampled_fruits']<=row['fruits']<=row['flowers']:
            raise ValueError('S2 impossible source denominator')
    return rows

def audit(root:Path=ROOT,source_doc:Path|None=None,s1_text:Path|None=None)->dict:
    s1=_load_s1(root,source_doc,s1_text);s2=_load_s2(root)
    near=[r for r in s1 if r['distance_lo_m']<=12]
    def sign(r):
        return (r['mean_dye_positive_robbed']>r['mean_dye_positive_unrobbed'])-(r['mean_dye_positive_robbed']<r['mean_dye_positive_unrobbed'])
    def counts(rows):
        return {'robbed_lower':sum(sign(r)<0 for r in rows),'robbed_higher':sum(sign(r)>0 for r in rows),
                'same':sum(sign(r)==0 for r in rows)}
    s1_out={'source_cells':len(s1),'measure':'published per-distance-bin mean of fluorescent-dye-positive stigma, not paternity',
            'near_0_to_14_bins':{'n_comparisons':len(near),'lower_in_robbed':counts(near)['robbed_lower'],
                                 'higher_in_robbed':counts(near)['robbed_higher'],'tied':counts(near)['same']},
            'full_distance_bins':counts(s1),
            'by_direction':[{'direction':d,'near_robbed_lower':counts([r for r in near if r['direction']==d])['robbed_lower'],
                             'near_robbed_mean_sum':sum(r['mean_dye_positive_robbed'] for r in near if r['direction']==d),
                             'near_guarded_mean_sum':sum(r['mean_dye_positive_unrobbed'] for r in near if r['direction']==d)} for d in DIRS]}
    guilds={'robbed':{'Bombus_eximius':6.15,'Apis_cerana':3.06},
            'guarded':{'Bombus_eximius':7.86,'Apis_cerana':1.33}}
    for g in guilds.values():
        g['two_guild_sum']=g['Bombus_eximius']+g['Apis_cerana']
        g['Bombus_fraction_within_two']=g['Bombus_eximius']/g['two_guild_sum']
    main={'source':'Deng et al. 2015 PLOS ONE, Flower visitors/Figure 6/Table 4',
          'scope':'two species six-day published mean visits/hour, not raw time-series or all flower visitors',
          'reported_two_bee_rates_per_hour':guilds,
          'derived_two_guild_Bombus_share_difference_percentage_points':100*(guilds['robbed']['Bombus_fraction_within_two']-guilds['guarded']['Bombus_fraction_within_two']),
          'rounded_two_guild_visit_sum_difference':guilds['robbed']['two_guild_sum']-guilds['guarded']['two_guild_sum'],
          'two_guild_sum_statistically_equivalent':False,
          'species_visitation_difference_causally_robbery':False}
    fruits={}
    for t in ('Robbed','Unrobbed'):
        rr=[r for r in s2 if r['treatment']==t]
        nf=sum(r['flowers'] for r in rr);ng=sum(r['fruits'] for r in rr)
        fruits['robbed' if t=='Robbed' else 'guarded']={'flower_n':nf,'fruit_n':ng,'fruit_set_fraction':ng/nf}
    per_fruit=[];per_seed=[]
    for y in (2005,2007):
        for d in DIRS:
            r=next(z for z in s2 if (z['year'],z['direction'],z['treatment'])==(y,d,'Robbed'))
            u=next(z for z in s2 if (z['year'],z['direction'],z['treatment'])==(y,d,'Unrobbed'))
            per_fruit.append(r['fruits']/r['flowers']-u['fruits']/u['flowers'])
            per_seed.append(r['seeds_in_sample']/r['sampled_fruits']-u['seeds_in_sample']/u['sampled_fruits'])
    stage={'observed_fruit_set':fruits,
           'fruit_set_difference_percentage_points':100*(fruits['robbed']['fruit_set_fraction']-fruits['guarded']['fruit_set_fraction']),
           'fruit_set_negative_year_direction_strata':sum(x<0 for x in per_fruit),
           'sampled_seed_count_effect':{'negative_strata':sum(x<0 for x in per_seed),
                                        'positive_strata':sum(x>0 for x in per_seed),
                                        'tied_strata':sum(x==0 for x in per_seed)},
           'years_for_fruit_set':'2005 and 2007; not same-flower pairing to S1/visitor study'}
    return {'schema':'BALANCE_ALPINIA_S1_DYE_S2_FRUIT_BEE_GUILD_V1',
            'original_paper_doi':'10.1371/journal.pone.0144585',
            's1_doc_sha256':S1_SHA,'s1_csv_sha256':S1_CSV_SHA,'s2_csv_sha256':S2_CSV_SHA,
            's1':s1_out,'s2':stage,'main_article':main,
            'interpretation':'source_only_within_study_noncausal','source_population_programmes_added':0,
            'claim_gates':{
                'all_stage_measures_on_same_individual_flower':False,
                'dye_positive_stigmas_identify_genetic_paternity':False,
                'published_two_bee_means_identify_total_visitor_rate_equivalence':False,
                'difference_in_Bombus_fraction_is_randomized_by_squirrel_access':False,
                'composition_mediates_fruit_set_estimated':False,
                'raw_individual_or_plot_replicates_available_in_S1_S2':False,
                'cross_study_generalization_identified':False,
                'direct_structural_balance_worldline_estimated':False}}
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-doc',type=Path)
    p.add_argument('--source-text',type=Path)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    z=audit(ROOT,args.source_doc,args.source_text)
    if args.out.exists():raise FileExistsError('Refuse source audit overwrite')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(z,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'s1':z['s1'],'s2':z['s2'],'main_article':z['main_article']},indent=2))
if __name__=='__main__':main()

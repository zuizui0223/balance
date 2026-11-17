#!/usr/bin/env python3
"""Source-hashed 2025 larceny meta-stage matchability audit; not causal mediation."""
from __future__ import annotations
import argparse, hashlib, json, math, re, statistics
from collections import defaultdict, Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

SOURCE_SHA256='6554409f22b09156ee1c2a35ee2547eb5ae28c4a25934b9c639d8a19ea7fe9b4'
ORIGINAL_FIGSHARE_ZIP_SHA256='84d310948e1da97c091ca27e9dcc45521cf72512ba14e30d3cd269d46e5b274c'
FIELDS=('ID','ref-ID','title','reference','country','longitude','latitude','altitude','climate','species',
        'rob_location','nectar_production','sugar_concentration','flower_lifespan','growth_form','autonomous',
        'self_compatible','pollen_limitation','origin','damage','larcenist_type','larceny_type',
        'secondary_robber','pollinator_type','larceny_rate','experiment_level','response_variable',
        'sub_response_variable','yi','vi')
CONTEXT=('country','longitude','latitude','climate','rob_location','growth_form','autonomous',
         'self_compatible','pollen_limitation','origin','damage','larcenist_type','larceny_type',
         'secondary_robber','pollinator_type','larceny_rate','experiment_level')
STAGE_ROUTES={
  'nectar_visits_pollen_fruit_seed':('nectar volume','visitation rate','pollen deposition','fruit set','seed set'),
  'visits_pollen_fruit_seed':('visitation rate','pollen deposition','fruit set','seed set'),
  'pollen_fruit_seed':('pollen deposition','fruit set','seed set'),
  'visits_fruit_seed':('visitation rate','fruit set','seed set'),
  'pollen_fruit':('pollen deposition','fruit set'),
  'fruit_seed':('fruit set','seed set'),
}
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
STAGE_NAMES={'nectar volume','visitation rate','pollen deposition','fruit set','seed set','pollen donation',
             'sugar concentration','flower lifespan','No. flowers per bout','flower handling time',
             'seed quality','pollen dispersal','pollen quality','flight distance'}

def source_rows(path:Path)->list[dict]:
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=SOURCE_SHA256:
        raise ValueError('Official Figshare XLSX SHA256 mismatch; refuse altered dataset')
    with ZipFile(path) as z:
        if 'xl/sharedStrings.xml' not in z.namelist() or 'xl/worksheets/sheet1.xml' not in z.namelist():
            raise ValueError('Unexpected original Excel workbook schema')
        shared=[''.join(t.text or '' for t in si.iter(NS+'t')) for si in
                ET.fromstring(z.read('xl/sharedStrings.xml')).findall(NS+'si')]
        root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    lines=[]
    for row in root.iter(NS+'row'):
        values=[None]*len(FIELDS)
        for cell in row.findall(NS+'c'):
            match=re.match(r'[A-Z]+',cell.attrib['r'])
            if match is None:raise ValueError('Invalid original cell coordinate')
            col=0
            for ch in match.group():col=col*26+ord(ch)-64
            col-=1
            if col>=len(FIELDS):continue
            v=cell.find(NS+'v')
            if v is None or v.text is None:continue
            if cell.attrib.get('t')=='s': value=shared[int(v.text)]
            elif cell.attrib.get('t') in ('str','inlineStr'):value=v.text
            else:
                num=float(v.text)
                value=int(num) if num.is_integer() else num
            values[col]=value
        if any(v is not None for v in values):lines.append(values)
    if tuple(lines[0])!=FIELDS:raise ValueError('Source column names changed')
    records=[dict(zip(FIELDS,r)) for r in lines[1:] if r[0] is not None]
    return validate(records)

def validate(records:list[dict])->list[dict]:
    if len(records)!=776:raise ValueError('Original dataset requires 776 effects')
    if [r['ID'] for r in records]!=list(range(1,777)):raise ValueError('Unexpected record ID sequence')
    if len({r['ref-ID'] for r in records})!=153:raise ValueError('Expected 153 distinct papers')
    if len({r['species'] for r in records})!=120:raise ValueError('Expected 120 distinct plant species')
    for r in records:
        if r['sub_response_variable'] not in STAGE_NAMES:
            raise ValueError('Original endpoint vocabulary changed')
        if not (isinstance(r['yi'],(int,float)) and math.isfinite(r['yi'])
                and isinstance(r['vi'],(int,float)) and math.isfinite(r['vi']) and r['vi']>0):
            raise ValueError('Nonfinite log response ratio or nonpositive sampling variance')
    return records

def audit(records:list[dict])->dict:
    validate(records)
    groups=defaultdict(list)
    for row in records:groups[(row['ref-ID'],row['species'])].append(row)
    coverage={}
    for name,stages in STAGE_ROUTES.items():
        matched=sorted(key for key,rs in groups.items() if set(stages).issubset({r['sub_response_variable'] for r in rs}))
        coverage[name]={
            'paper_species_groups':len(matched),'distinct_papers':len({key[0] for key in matched}),
            'source_keys':[{'ref_ID':k[0],'species':k[1]} for k in matched]}
    candidates=[];strict=[];level_agreement=0
    for key,rs in sorted(groups.items()):
        f=[r for r in rs if r['sub_response_variable']=='fruit set']
        s=[r for r in rs if r['sub_response_variable']=='seed set']
        if not f or not s:continue
        overlap=bool({r['experiment_level'] for r in f}&{r['experiment_level'] for r in s})
        level_agreement+=overlap
        candidates.append({'ref_ID':key[0],'species':key[1],'fruit_effects':len(f),
                           'seed_effects':len(s),'shared_experiment_level':overlap})
        if len(f)!=1 or len(s)!=1 or not overlap:continue
        if any(f[0][x]!=s[0][x] for x in CONTEXT):continue
        strict.append({
            'ref_ID':key[0],'species':key[1],'publication':f[0]['reference'],
            'fruit_record':f[0]['ID'],'seed_record':s[0]['ID'],
            'fruit_lnRR':f[0]['yi'],'seed_lnRR':s[0]['yi'],
            'seed_minus_fruit_lnRR':s[0]['yi']-f[0]['yi'],
            'within_experiment_contrast_verified':False,
            'same_flower_followup_verified':False,
            'shared_response_sampling_covariance_known':False})
    differences=[x['seed_minus_fruit_lnRR'] for x in strict]
    return {'schema':'BALANCE_FLORAL_LARCENY_META_2025_STAGE_PAIRABILITY_V1',
      'source_paper_doi':'10.1016/j.pld.2024.12.004',
      'original_figshare_doi':'10.6084/m9.figshare.27129204',
      'original_xlsx_sha256':SOURCE_SHA256,
      'population':{'effects':len(records),'papers':len({r['ref-ID'] for r in records}),
                    'species':len({r['species'] for r in records}),
                    'paper_species_groups':len(groups)},
      'endpoint_row_counts':dict(sorted(Counter(r['sub_response_variable'] for r in records).items())),
      'co_reported_stage_coverage':coverage,
      'fruit_seed_candidate_scope':{
         'paper_species_upper_bound':len(candidates),
         'distinct_papers_upper_bound':len({x['ref_ID'] for x in candidates}),
         'shared_experiment_level_groups':level_agreement,
         'uniquely_screened_groups':len(strict),
         'uniquely_screened_papers':len({x['ref_ID'] for x in strict}),
         'delta_positive':sum(d>0 for d in differences),
         'delta_negative':sum(d<0 for d in differences),
         'delta_zero':sum(d==0 for d in differences),
         'descriptive_mean_seed_minus_fruit_lnRR':statistics.mean(differences),
         'descriptive_median_seed_minus_fruit_lnRR':statistics.median(differences),
         'no_pooled_p_value_or_causal_interpretation':True},
      'candidate_group_inventory':candidates,
      'strict_one_to_one_candidates':strict,
      'claim_ceiling':{
          'same_experimental_contrast_unverified':True,
          'cross_response_covariance_unknown':True,
          'seed_set_denominator_not_standardized':True,
          'reported_effects_are_not_independent_trials':True,
          'cannot_infer_a_transmitted_fitness_cost':True,
          'cannot_add_six_or_seven_new_evolutionary_replicates':True,
          'structural_fitness_WD_minus_WS_unmeasured':True,
          'original_U6_42_coders_and_V4_untouched':True},
      'interpretation':'Publication-species stage co-reporting only. Matched treatment identity, joint individual-level data and effect covariance are unavailable; descriptive candidate differences are not a stage-mediated causal result.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    a=ap.parse_args()
    result=audit(source_rows(a.source))
    if a.out.exists():raise FileExistsError('Refuse overwrite')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'population':result['population'],
      'coverage':{k:[v['paper_species_groups'],v['distinct_papers']] for k,v in result['co_reported_stage_coverage'].items()},
      'fruit_seed_candidate_scope':result['fruit_seed_candidate_scope']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

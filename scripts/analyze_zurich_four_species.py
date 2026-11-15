#!/usr/bin/env python3
"""Exploratory, source-locked garden-level visitation vs reproduction analysis.

The EnviDat source is a 2025/2026 published four-phytometer study, not a
new experiment or direct structural BALANCE fitness comparison. Only original
source bytes are admissible. No confirmatory U6/V4 coding is accessed.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from hashlib import sha256
from io import BytesIO, StringIO
import json
import math
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

SOURCE_SHA256 = 'b1ea0dc54d0c6e33bfacb44d7285377ec3e113807cc945fc2dfbfcc3e534bcc9'
SOURCE_DOI = '10.16904/envidat.676'
SPECIES = ('Carrot', 'Radish', 'Sainfoin', 'Comfrey')
GROUPS = ('apis', 'other_bee', 'other_nonbee', 'robber')
RESP_FILES = {
    'Carrot': 'daucus_carota_seed_set.csv',
    'Radish': 'raphanus_sativus_fruit_set.csv',
    'Sainfoin': 'onobrychis_viciifolia_fruit_set.csv',
    'Comfrey': 'symphytum_officinale_fruit_set.csv',
}
ROOT = '07_pollination_success/'
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def check_source(path: Path):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('Original EnviDat source checksum mismatch')
    with ZipFile(BytesIO(raw)) as z:
        required = {ROOT + x for x in RESP_FILES.values()} | {
            '05_field_data/raw_sampling_data.xlsx',
            '06_trait_data/species_temporal_flower_visitation_matrix.csv',
            '06_trait_data/individual_traits.csv',
            '04_taxonomic_data/taxa_checklist.csv',
        }
        if not required.issubset(set(z.namelist())):
            raise ValueError('Original EnviDat source members missing')
    return ZipFile(BytesIO(raw))


def csv_source(z: ZipFile, path: str):
    return list(csv.DictReader(StringIO(z.read(path).decode('utf-8-sig'))))


def xlsx_source(z: ZipFile):
    """Read the original raw sampling sheet with XLSX OOXML, without editing it."""
    with ZipFile(BytesIO(z.read('05_field_data/raw_sampling_data.xlsx'))) as w:
        shared = []
        if 'xl/sharedStrings.xml' in w.namelist():
            st = ET.fromstring(w.read('xl/sharedStrings.xml'))
            shared = [''.join((t.text or '') for t in si.iter(NS+'t'))
                      for si in st.findall(NS+'si')]
        root = ET.fromstring(w.read('xl/worksheets/sheet1.xml'))
        table = []
        for rr in root.iter(NS+'row'):
            fields = {}
            for cell in rr.findall(NS+'c'):
                ref = cell.attrib['r']
                letters = re.match(r'[A-Z]+', ref).group(0)
                col = 0
                for char in letters: col = col*26 + ord(char) - 64
                typ = cell.get('t', 'n')
                v = cell.find(NS+'v')
                if v is None:
                    inline = cell.find(NS+'is')
                    value = ''.join(inline.itertext()) if inline is not None else None
                elif typ == 's':
                    value = shared[int(v.text)]
                elif typ == 'b':
                    value = int(v.text)
                elif typ in ('n', '', None):
                    value = float(v.text) if '.' in v.text else int(v.text)
                else:
                    value = v.text
                fields[col-1] = value
            if fields:
                table.append([fields.get(i) for i in range(21)])
        header = table[0]
        expected = ['Id','capture_period','capture_window','total_sampling_effort_min']
        if not all(name in header for name in expected):
            raise ValueError('Unexpected raw original sampling fields')
        return [dict(zip(header, row)) for row in table[1:]]


def date_serial(x):
    return (datetime(1899,12,30) + timedelta(days=float(x))).strftime('%d.%m.%Y')


def source_frame(z: ZipFile):
    observed = xlsx_source(z)
    if len(observed) != 670:
        raise ValueError('Original raw sampling sample size changed')
    survey = {}
    for row in observed:
        key = (int(row['Id']),date_serial(row['capture_period']),int(row['capture_window']))
        if key in survey: raise ValueError('Duplicate raw survey key')
        effort = float(row['total_sampling_effort_min'])
        if not math.isfinite(effort) or effort <= 0:
            raise ValueError('Survey effort must be positive')
        survey[key] = {'hours':effort/60, 'flowers':{
            s:float(row['n_flowers_'+s.lower()]) if row['n_flowers_'+s.lower()] not in ('',None) else None
            for s in SPECIES}}
    taxa = csv_source(z,'04_taxonomic_data/taxa_checklist.csv')
    taxonomy={r['taxon']:r['pollinator_group'] for r in taxa}
    if len(taxonomy) != 167: raise ValueError('Expected 167 unique visitor taxa')
    trait = csv_source(z,'06_trait_data/individual_traits.csv')
    if len(trait) != 5794: raise ValueError('Original visitor count changed')
    captures=[]
    for r in trait:
        tax=r['taxon']
        if tax not in taxonomy: raise ValueError('Unmatched visitor taxon')
        if r['nectar_robber'] not in ('0','1'): raise ValueError('Unexpected robber status')
        key=(int(r['Id']),r['capture_date'],int(r['capture_window']))
        cat=('robber' if r['nectar_robber']=='1' else
             'apis' if tax=='Apis mellifera' else
             'other_bee' if taxonomy[tax]=='Anthophila' else 'other_nonbee')
        captures.append((key,r['phytometer_plant'],cat))
    if len({x[0][0] for x in captures}) != 24:
        raise ValueError('Unexpected observed garden count')
    return survey,captures


def independent_matrix_receipt(z:ZipFile,survey):
    """Separate raw matrix audit: unsampled zero slots must never be exposure."""
    text=z.read('06_trait_data/species_temporal_flower_visitation_matrix.csv').decode('utf-8-sig')
    reader=csv.reader(StringIO(text));header=next(reader)
    if len(header)!=171: raise ValueError('Unexpected 171 matrix fields')
    observed_rows=positive_rows=unsurveyed_positive=unsurveyed_count=visit_sum=0
    for r in reader:
        observed_rows+=1
        if len(r)!=171:raise ValueError('Matrix row width changed')
        counts=[float(k) if k else 0.0 for k in r[4:]]
        if not all(k>=0 and k.is_integer() for k in counts):
            raise ValueError('Matrix contains invalid visitor count')
        v=int(sum(counts));visit_sum+=v
        if v:positive_rows+=1
        if (int(r[0]),r[2],int(r[3])) not in survey:
            if v:unsurveyed_positive+=1;unsurveyed_count+=v
    if (observed_rows,visit_sum)!=(21120,5794):
        raise ValueError('Original visitation matrix size/count changed')
    return {'matrix_rows':observed_rows,'matrix_positive_rows':positive_rows,
            'matrix_structural_zero_rows':observed_rows-positive_rows,
            'matrix_survey_matched_rows':len(survey)*4,
            'matrix_unsurveyed_positive_rows':unsurveyed_positive,
            'matrix_unsurveyed_visit_count':unsurveyed_count}


def site_outcomes(z:ZipFile, pooled:bool=False):
    out={}
    for s,path in RESP_FILES.items():
        rows=csv_source(z,ROOT+path)
        plants=defaultdict(lambda:[0.0,0.0,0])
        for row in rows:
            if row.get('exclude',row.get('excluded','0')) in ('1','TRUE'):
                continue
            site=int(row['Id']);plant=(site,row['plant_id'])
            if s=='Carrot':
                v=float(row['n_seeds'])
                if not math.isfinite(v) or v<0:raise ValueError('Bad seed count')
                plants[plant][0]+=v;plants[plant][2]+=1
            else:
                a='n_flowers_with_seeds' if s=='Comfrey' else 'n_flowers_with_fruits'
                b='n_flowers_without_seeds' if s=='Comfrey' else 'n_flowers_without_fruits'
                v=float(row[a]);w=float(row[b])
                if min(v,w)<0 or not all(map(math.isfinite,(v,w))):
                    raise ValueError('Invalid reproductive fraction')
                if v+w==0:continue
                plants[plant][0]+=v;plants[plant][1]+=v+w;plants[plant][2]+=1
        by_site=defaultdict(list)
        for (site,_), (num,den,n) in plants.items():
            if n and (s=='Carrot' or den>0):
                by_site[site].append((num,den,n))
        if len(by_site)!=24:raise ValueError('Outcome garden support differs from 24')
        for site,values in by_site.items():
            if s=='Carrot':
                val=sum(x[0] for x in values)/sum(x[2] for x in values) if pooled else sum(x[0]/x[2] for x in values)/len(values)
                y=math.log1p(val)
            else:
                val=(sum(x[0] for x in values)/sum(x[1] for x in values)) if pooled else sum(x[0]/x[1] for x in values)/len(values)
                y=math.asin(math.sqrt(min(1,max(0,val))))
            out[(site,s)]={'raw_outcome':val,'response':y,'n_independent_plants':len(values)}
    return out


def assembled(survey,captures,outcomes, flower_only=False, unmatched_included=False):
    gardens=sorted({k[0] for k in survey})
    stats=defaultdict(Counter)
    lost=Counter()
    for (site,date,window),s,cat in captures:
        valid=(site,date,window) in survey
        if not valid:
            lost[(site,s)]+=1
            if not unmatched_included:continue
        if flower_only:
            flower=survey.get((site,date,window),{}).get('flowers',{}).get(s)
            if flower is None or flower<=0:continue
        stats[(site,s)][cat]+=1
    sites=[]
    for site in gardens:
        for s in SPECIES:
            hrs=sum(row['hours'] for k,row in survey.items()
                    if k[0]==site and (not flower_only or
                    (row['flowers'][s] is not None and row['flowers'][s]>0)))
            if not hrs>0:raise ValueError('No observer exposure for garden and plant')
            if (site,s) not in outcomes:raise ValueError('Missing reproductive outcome')
            counts={c:stats[(site,s)][c] for c in GROUPS}
            total=sum(counts.values())
            sites.append({'garden':site,'species':s,'observer_hours':hrs,
                          'n_visits':total,'rate':total/hrs,'counts':counts,
                          **outcomes[(site,s)]})
    if len(sites)!=96:raise ValueError('Expected 24 gardens * 4 plants')
    return sites,{'unmatched_individual_visits':sum(lost.values()),
                  'unmatched_garden_species_counts':{f'{site}_{sp}':k for (site,sp),k in sorted(lost.items())}}


def fit_site_models(sites):
    import numpy as np
    out={}
    for species in SPECIES:
        x=sorted([r for r in sites if r['species']==species],key=lambda r:r['garden'])
        y=np.array([r['response'] for r in x],dtype=float)
        total=np.array([r['n_visits'] for r in x],float)
        rate=np.array([r['rate'] for r in x],float)
        active=[c for c in GROUPS if sum(r['counts'][c] for r in x)>0]
        if len(active)<2:
            out[species]={'status':'NOT_ESTIMABLE_FEWER_THAN_TWO_VISITOR_CATEGORIES'}
            continue
        reference=max(active,key=lambda c:sum(r['counts'][c] for r in x))
        extra=[c for c in active if c!=reference]
        intercept=np.ones(len(x))
        mat0=np.column_stack([intercept,np.log1p(rate)])
        fractions=np.column_stack([np.divide([r['counts'][c] for r in x],total,
                         out=np.zeros(len(x)),where=total>0) for c in extra])
        mat1=np.column_stack([mat0,fractions])
        mat2=np.column_stack([intercept]+[np.log1p(np.array([r['counts'][c]/r['observer_hours'] for r in x],float)) for c in active])
        arrays=[np.ones((len(x),1)),mat0,mat1,mat2]
        fits={}
        for name,X in zip(('intercept_only','total_only','total_plus_composition','log_group_rates'),arrays):
            if np.linalg.matrix_rank(X)<X.shape[1] or len(x)<=X.shape[1]+2:
                raise ValueError('Design not estimable for '+species+' '+name)
            err=[]
            for i in range(len(x)):
                keep=np.arange(len(x))!=i
                if np.linalg.matrix_rank(X[keep])<X.shape[1]:
                    raise ValueError('Fold design not estimable '+species+' '+name)
                beta=np.linalg.lstsq(X[keep],y[keep],rcond=None)[0]
                err.append(float(y[i]-X[i] @ beta))
            coeff=np.linalg.lstsq(X,y,rcond=None)[0]
            fits[name]={'rmse':float(np.sqrt(np.mean(np.square(err)))),
                        'r2_in_sample':float(1-sum((y-X@coeff)**2)/sum((y-y.mean())**2)),
                        'coefficients':coeff.tolist(),'errors_by_garden':{str(r['garden']):e for r,e in zip(x,err)}}
        v0=fits['total_only'];v1=fits['total_plus_composition']
        out[species]={'status':'EXPLORATORY_COMPARISON','n_gardens':len(x),
                      'active_categories':active,'reference_category':reference,
                      'additional_shares':extra,
                      'n_visits':int(total.sum()),
                      'n_zero_visit_gardens':int((total==0).sum()),
                      'rmse_change_fraction':1-v1['rmse']/v0['rmse'],
                      'n_gardens_better_by_squared_error':sum(v1['errors_by_garden'][str(r['garden'])]**2 <
                              v0['errors_by_garden'][str(r['garden'])]**2 for r in x),
                      'models':fits}
    return out


def audit(original_path:Path):
    z=check_source(original_path)
    survey,captures=source_frame(z)
    matrix=independent_matrix_receipt(z,survey)
    out=site_outcomes(z)
    site,quality=assembled(survey,captures,out)
    main=fit_site_models(site)
    alt=fit_site_models(assembled(survey,captures,site_outcomes(z,pooled=True))[0])
    flower=fit_site_models(assembled(survey,captures,out,flower_only=True)[0])
    included=fit_site_models(assembled(survey,captures,out,unmatched_included=True)[0])
    omits={}
    for s in SPECIES:
        obs=[r for r in site if r['species']==s]
        changes=[]
        for garden in sorted({r['garden'] for r in obs}):
            subs=[r for r in obs if r['garden']!=garden]
            res=fit_site_models(subs)
            if res[s]['status']=='EXPLORATORY_COMPARISON':changes.append(res[s]['rmse_change_fraction'])
        omits[s]={'reruns':len(changes),'min':min(changes),'max':max(changes),
                  'positive':sum(x>0 for x in changes)}
    return {'schema':'BALANCE_ZURICH_FOUR_SPECIES_EXPLORATORY_V1',
            'dataset_doi':SOURCE_DOI,'source_zip_sha256':SOURCE_SHA256,
            'study_year':2016,'original_data_publication_year':2025,
            'existing_authors_analytical_paper':'10.1111/1365-2664.70384',
            'independent_biological_taxa':4,'independent_sampling_gardens':24,
            'source_observation_windows':len(survey),'visitors_total':len(captures),
            'source_nectar_robbers':sum(c=='robber' for k,s,c in captures),
            'matrix_audit':matrix,'capture_quality':quality,
            'primary':main,
            'sensitivity_pooled_garden_outcome':{s:{'rmse_change_fraction':r['rmse_change_fraction']} for s,r in alt.items()},
            'sensitivity_flower_positive_samples':{s:{'rmse_change_fraction':r['rmse_change_fraction']} for s,r in flower.items()},
            'sensitivity_include_27_unmatched_without_extra_effort':{s:{'rmse_change_fraction':r['rmse_change_fraction']} for s,r in included.items()},
            'sensitivity_drop_each_garden':omits,
            'gardens':site,
            'claim_ceilings':[
               'Original authors analyzed same experiment in 2026; this is not independent experimental replication',
               'Different outcome measures and transformations; cannot pool raw RMSE across species',
               'Source 21120-row matrix has many unobserved all-zero slots; use actual 670 observed survey windows',
               'Missing 27 visitor records cannot be silently imputed as zero; keep separate eligibility sensitivity',
               'Garden and plant species are observational; no causal visitor intervention or realized architecture payoff',
               'Nectar robbers explicitly distinguished from legitimate visitors; group identity is not validated efficiency',
               'Outcome-selected pruning and multiple model search are not confirmatory tests',
               'Independent structural architecture CODER_A/B and V4 frozen responses were not opened or changed'
            ]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out-dir',type=Path,required=True)
    a=p.parse_args()
    data=audit(a.source)
    a.out_dir.mkdir(parents=True,exist_ok=False)
    (a.out_dir/'RESULTS.json').write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    with (a.out_dir/'GARDEN_SPECIES_96.csv').open('w',newline='',encoding='utf-8') as f:
        cols=['garden','species','observer_hours','n_visits','rate','apis','other_bee','other_nonbee','robber','raw_outcome','response','n_independent_plants']
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
        for row in data['gardens']:
            writer.writerow({**{k:row[k] for k in cols if k in row},**row['counts']})
    with (a.out_dir/'MODEL_COMPARISON.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['species','model','n_gardens','rmse','r2_in_sample'])
        for sp,spdata in data['primary'].items():
            if spdata['status']!='EXPLORATORY_COMPARISON':continue
            for model,x in spdata['models'].items():
                writer.writerow([sp,model,spdata['n_gardens'],x['rmse'],x['r2_in_sample']])
    print(json.dumps({'source_audit':data['matrix_audit'],
           'main':{s:{'rmse_change_fraction':v['rmse_change_fraction'], 'categories':v['active_categories']} for s,v in data['primary'].items()},
           'flower_positive':data['sensitivity_flower_positive_samples'],
           'drop_each_garden':data['sensitivity_drop_each_garden']},indent=2))

if __name__=='__main__':main()

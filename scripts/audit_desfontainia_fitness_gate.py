#!/usr/bin/env python3
"""Read-only audit: resource removal versus same-shrub seed outcome (one 2026 original study).

Inputs MUST be the official Zenodo 18895003 XLSX original. This is an exploratory
paired difference and source-eligibility analysis, NOT causal architecture BALANCE.
"""
from __future__ import annotations
import argparse, hashlib, json, math, random, re, statistics
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ORIGINAL_MD5='e7e59a06cc3eb7aed636620a85a1ea98'
XLSX_MAIN='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
T_CRITICAL_DF39_975=2.0226909200367604


def source_sheet(path:Path, sheet_number:int, expected_header:list[str]):
    """Minimal OOXML reader for a source-MD5 locked .xlsx, preserving missing cells."""
    original=Path(path).read_bytes()
    if hashlib.md5(original).hexdigest()!=ORIGINAL_MD5:
        raise ValueError('Original Zenodo XLSX MD5 mismatch')
    with ZipFile(path) as z:
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            root=ET.fromstring(z.read('xl/sharedStrings.xml'))
            shared=[''.join(t.text or '' for t in si.iter(XLSX_MAIN+'t'))
                    for si in root.findall(XLSX_MAIN+'si')]
        root=ET.fromstring(z.read(f'xl/worksheets/sheet{sheet_number}.xml'))
        records=[]
        for rr in root.iter(XLSX_MAIN+'row'):
            values={}
            for c in rr.findall(XLSX_MAIN+'c'):
                ref=c.attrib['r'];letters=re.match(r'^[A-Z]+',ref).group()
                i=0
                for letter in letters:i=i*26+ord(letter)-64
                typ=c.attrib.get('t','n')
                v=c.find(XLSX_MAIN+'v')
                if v is None:
                    inline=c.find(XLSX_MAIN+'is')
                    x=''.join(inline.itertext()) if inline is not None else None
                elif typ=='s':x=shared[int(v.text)]
                elif typ in ('n','b'):x=float(v.text) if v.text is not None else None
                else:x=v.text
                values[i-1]=x
            if values:
                records.append([values.get(i) for i in range(len(expected_header))])
    if records[0]!=expected_header:
        raise ValueError('Original XLSX sheet/header mapping changed')
    return records[1:]


def t_interval(vals):
    """Two-sided Student t mean interval for the frozen 40 shrub paired units."""
    if len(vals)!=40:raise ValueError('40 paired shrubs required for parametric 95% interval')
    m=statistics.mean(vals)
    se=statistics.stdev(vals)/math.sqrt(40)
    return [m-T_CRITICAL_DF39_975*se,m+T_CRITICAL_DF39_975*se]


def pair_bootstrap(vals, draws=20000, seed=20261115):
    n=len(vals); rng=random.Random(seed);out=[]
    for _ in range(draws):
        out.append(sum(vals[rng.randrange(n)] for j in range(n))/n)
    out.sort()
    return [out[int(.025*draws)],out[int(.975*draws)-1]]


def summarize_seed(rows):
    if len(rows)!=40 or len({r[0] for r in rows})!=40 or any(r[0] is None for r in rows):
        raise ValueError('Require 40 unique plant identities')
    if any(len(r)!=4 or any(not isinstance(x,(int,float)) or not math.isfinite(x) for x in r)
           for r in rows):raise ValueError('Invalid or missing original seed record')
    if any(x<0 for r in rows for x in r[1:]):raise ValueError('Seed numbers must be nonnegative')
    if set(int(r[0]) for r in rows)!=set(range(1,41)):raise ValueError('Original shrub IDs changed')
    fields=('minusP_minusR','plusP_minusR','plusP_plusR')
    means={fld:statistics.mean(row[i+1] for row in rows) for i,fld in enumerate(fields)}
    positive={fld:sum(row[i+1]>0 for row in rows) for i,fld in enumerate(fields)}
    delta=[row[3]-row[2] for row in rows]
    no_vs_open=[row[2]-row[1] for row in rows]
    bin_delta=[int(row[3]>0)-int(row[2]>0) for row in rows]
    return {'n_shrubs':40,'treatment_grain':'one original flower per treatment per shrub',
         'mean_seeds_by_treatment':means,
         'seed_presence_by_treatment':positive,
         'paired_seed_difference_plusR_minusR':{
              'mean':statistics.mean(delta), 't_95_interval':t_interval(delta),
              'paired_bootstrap95_interval':pair_bootstrap(delta),
              'n_higher_n_lower_n_equal':[sum(d>0 for d in delta),sum(d<0 for d in delta),sum(d==0 for d in delta)],
              'percentage_of_plusP_minusR_mean':100*statistics.mean(delta)/means['plusP_minusR']},
         'paired_seed_presence_difference_plusR_minusR':{
              'mean':statistics.mean(bin_delta),
              'paired_bootstrap95_interval':pair_bootstrap(bin_delta),
              'discordant_noR_positive_R_negative':sum(row[2]>0 and row[3]==0 for row in rows),
              'discordant_noR_negative_R_positive':sum(row[2]==0 and row[3]>0 for row in rows)},
         'paired_pollinator_access_minus_exclusion':{'mean':statistics.mean(no_vs_open),
                                                      't_95_interval':t_interval(no_vs_open)}}


def summarize_nectar(rows, expected_total=400,expected_per_state=200):
    if len(rows)!=expected_total:raise ValueError('Original flower record count differs')
    if any(len(r)!=5 or r[2] not in ('Robada','No dañada') for r in rows):
        raise ValueError('Unexpected original flower status/row')
    count=Counter(r[2] for r in rows)
    if count!={'Robada':expected_per_state,'No dañada':expected_per_state}:
        raise ValueError('Original nectar state denominator changed')
    by=defaultdict(list);missing=Counter()
    ids=set()
    for plant,flower,status,volume,sugar in rows:
        if not isinstance(plant,(int,float)) or not 1<=plant<=40:raise ValueError('Unrecognized plant')
        ids.add(int(plant))
        if volume is None:
            missing[status]+=1
            continue
        if isinstance(volume,bool) or not isinstance(volume,(int,float)) or not math.isfinite(volume) or volume<0:
            raise ValueError('Nectar volume must be nonnegative and finite')
        by[(int(plant),status)].append(volume)
    if len(ids)!=40:raise ValueError('Expected 40 shrub nectar observations')
    paired=[]
    for plant in sorted(ids):
        a=by.get((plant,'Robada'))
        b=by.get((plant,'No dañada'))
        if a and b:
            paired.append([statistics.mean(a),statistics.mean(b)])
    pierced=statistics.mean(x[0] for x in paired)
    undam=statistics.mean(x[1] for x in paired)
    res={'n_flower_rows':len(rows),'n_paired_shrubs':len(paired),
         'missing_volume_by_status':{'Robada':missing['Robada'],'No dañada':missing['No dañada']},
         'mean_pierced_ul':pierced,'mean_undamaged_ul':undam,
         'pierced_to_undamaged_mean_ratio':pierced/undam if undam>0 else None,
         'within_shrub_difference_pierced_minus_undamaged_ul':statistics.mean(a-b for a,b in paired)}
    if len(paired)==40:
        diff=[a-b for a,b in paired]
        res['paired_mean_difference_t95_interval']=t_interval(diff)
        res['paired_mean_difference_bootstrap95_interval']=pair_bootstrap(diff)
    return res


def audit(path:Path):
    seeds=source_sheet(path,6,['Plant','Seed (-P-R)','Seeds (+P-R)','Seeds (+P+R)'])
    nect=source_sheet(path,3,['Plant','Flower','Status','Nectar volumen (microliter)','Nectar concentration (% w/w)'])
    return {'schema':'BALANCE_DESFONTAINIA_RESOURCE_FITNESS_DISCONNECT_AUDIT_V1',
         'source_doi':'10.5281/zenodo.18895003','paper_doi':'10.1002/ece3.73933',
         'source_md5':ORIGINAL_MD5,'seed':summarize_seed(seeds),'nectar':summarize_nectar(nect),
         'source_evidence_ceiling':{
          'equivalence_of_seed_output_demonstrated':False,
          'fully_randomized_robbery_intention_to_treat':False,
          'missing_minusP_plusR_factorial_cell':True,
          'same_flower_nectar_and_seed_causal_mediation_identified':False,
          'male_reproductive_fitness_measured':False,
          'architecture_WD_minus_WS_identified':False,
          'V4_independent_architecture_coder_data_opened':False},
         'interpretation':'Post-publication independent paired-shrub reanalysis; +P+R selected naturally robbed open flowers whereas +P-R was a taped bud, so no clean randomized robbery effect. CI spanning harm and benefit is not equivalence. Original submitted R GLMM code and final published GEE must not be represented as numerically identical.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path);a=p.parse_args()
    result=audit(a.source)
    if a.out.exists():raise FileExistsError('Refuse overwrite frozen receipt')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('seed','nectar')},ensure_ascii=False))
    print('SEED',json.dumps(result['seed'],ensure_ascii=False))
    print('NECTAR',json.dumps(result['nectar'],ensure_ascii=False))

if __name__=='__main__':main()
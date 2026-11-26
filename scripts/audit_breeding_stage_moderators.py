#!/usr/bin/env python3
"""Exploratory breeding-system moderator analysis of authenticated floral-larceny archive."""
from __future__ import annotations
import argparse, collections, json, math, pathlib, sys
from statistics import mean
from scipy.stats import t, f
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.audit_larceny_meta_stage_pairability import source_rows, SOURCE_SHA256
from scripts.audit_richman_2017_archive_mapping import acquire
from scripts.fit_larceny_study_stage_meta import collect, sensitivity, RHO, MIN_K
from scripts.audit_larceny_stage_direction_robustness import species_components, holm

FIELDS=('autonomous','self_compatible','pollen_limitation')
PAIRS=(('pollen deposition','fruit set'),('pollen deposition','seed set'),('visitation rate','fruit set'),('visitation rate','seed set'),('fruit set','seed set'),('nectar volume','visitation rate'),('visitation rate','pollen deposition'))
MARGINS=('pollen deposition','fruit set','seed set')

def label(ids,byid,field):
    # Only exact binary source labels, case-insensitive; unknown and heterogeneous never coded no.
    vals={str(byid[i][field]).strip().lower() for i in ids}
    return next(iter(vals)) if len(vals)==1 and vals<=set(('yes','no')) else None

def subgroup(items,rows,field,components=False):
    byid={r['ID']:r for r in rows}
    groups={'yes':[],'no':[]}; dropped=[]
    if components:
        units={}
        for k,x in species_components(items,rows).items():
            ids=sorted({i for p in x['papers'] for i in items[p]['ids']})
            units[k]={**x,'ids':ids}
    else:units={str(k):v for k,v in items.items()}
    for k,x in units.items():
        g=label(x['ids'],byid,field)
        if g is None:dropped.append(k);continue
        groups[g].append(x)
    out={'n_total':len(units),'n_excluded':len(dropped),'excluded_unit_ids':dropped,
         'n_yes':len(groups['yes']),'n_no':len(groups['no']),
         'equal_unit_means':{k:mean(v['y'] for v in a) if a else None for k,a in groups.items()},
         'groups':{k:sensitivity(v) for k,v in groups.items()},'contrasts':{}}
    if all(len(v)>=MIN_K for v in groups.values()):
        for rho in RHO:
            a=out['groups']['yes'][str(rho)];b=out['groups']['no'][str(rho)]
            v1=a['se_mkh']**2;v2=b['se_mkh']**2;se=math.sqrt(v1+v2)
            df=(v1+v2)**2/(v1*v1/(a['k']-1)+v2*v2/(b['k']-1))
            d=a['mu']-b['mu'];q=t.ppf(.975,df)
            out['contrasts'][str(rho)]={'yes_minus_no':float(d),'ci95':[float(d-q*se),float(d+q*se)],
                'p_nominal':float(2*t.sf(abs(d/se),df)),'df':float(df)}
    out['status']='EXPLORATORY_FIT' if out['contrasts'] else 'INSUFFICIENT_SUPPORT'
    return out

def run(rows):
    byid={r['ID']:r for r in rows}
    out={'source_sha256':SOURCE_SHA256,'n_effects':len(rows),'n_papers':len({r['ref-ID'] for r in rows}),
         'label_vocabulary':{m:dict(collections.Counter(str(r[m]) for r in rows)) for m in FIELDS},
         'stage_differences':{},'marginal_outcomes':{},
         'scope':'Post-open exploratory moderator comparisons on all eligible archived effects, not causal mating-system contrasts. Within-paper exact recorded contexts, paper as unit, species connected-component sensitivity, no phylogenetic correction. Binary archive labels only; ambiguous or mixed units excluded without imputing absence. Marginal outcome differences are separate from stage interactions. At least five units per moderator level before fitting. Holm across the 21 planned stage-pair/field comparisons within each scope and variance scenario; non-estimable comparisons p=1 for correction only.'}
    for a,b in PAIRS:
        name=b+' minus '+a
        p=collect(rows,a,b,'context')
        out['stage_differences'][name]={s:{m:subgroup(p,rows,m,s=='species') for m in FIELDS} for s in ('paper','species')}
    for a in MARGINS:
        p=collect(rows,a)
        out['marginal_outcomes'][a]={s:{m:subgroup(p,rows,m,s=='species') for m in FIELDS} for s in ('paper','species')}
    for family in ('stage_differences','marginal_outcomes'):
        for s in ('paper','species'):
            for rho in RHO:
                q=str(rho);pvals={}
                for stage,v in out[family].items():
                    for m,x in v[s].items():
                        pvals[(stage,m)]=x['contrasts'].get(q,{}).get('p_nominal',1.)
                for (stage,m),adj in holm(pvals).items():
                    c=out[family][stage][s][m]['contrasts'].get(q)
                    if c is not None:c['p_holm_family']=adj
    out['prior_art_F_p_audit']={'Corydalis_incisa_reported_F':1.145,'df':[1,232],'reported_p':.042,'computed_survival':float(f.sf(1.145,1,232))}
    return out
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=pathlib.Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    r=run(source_rows(acquire(a.out)))
    (a.out/'RESULT.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    def compact(v):return {k:{s:{m:{q:x[q] for q in ('n_total','n_excluded','n_yes','n_no','equal_unit_means','contrasts','status')} for m,x in a.items()} for s,a in b.items()} for k,b in v.items()}
    r['stage_differences']=compact(r['stage_differences']);r['marginal_outcomes']=compact(r['marginal_outcomes'])
    print('BALANCE_BREEDING_STAGE_RESULT '+json.dumps(r,ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()

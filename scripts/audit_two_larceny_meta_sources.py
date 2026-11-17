#!/usr/bin/env python3
"""Cross-audit TWO original 2025 nectar-larceny meta datasets, not causal inference."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,re,sys,zipfile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts.audit_larceny_meta_stage_pairability import source_rows,SOURCE_SHA256
LZIP='3f6e9b5b55ad8090f41f62faeb2f306c6700a9beb274ac6467106ebab9573c2d'
LCSV='4ecd656251f778189d8c13f3608ba99f4de942656fecfe6f2edc8d2509a3d2cb'
LR='9d60311b102cf27c234f9d6c63eeae602c91768950466e7579ed3a03f0488013'
LMETA='e35cb0b9fb62e2ded07c5bdc8bae039ea9b19085a55f023c0f314057774a85fd'
def hashof(b):return hashlib.sha256(b).hexdigest()
def load_leal(p):
    b=Path(p).read_bytes()
    if hashof(b)!=LZIP:raise ValueError('Zenodo 14773082 ZIP SHA256 mismatch')
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        def read(suffix,sha):
            matches=[x for x in z.namelist() if x.endswith('/'+suffix)]
            if len(matches)!=1:raise ValueError('Original Zenodo source file missing/duplicate '+suffix)
            b=z.read(matches[0])
            if hashof(b)!=sha:raise ValueError('Original Zenodo source SHA256 mismatch '+suffix)
            return b
        data=read('complete_hedges.csv',LCSV)
        script=read('Script_Leal et al_Ecology.R',LR).decode('utf-8-sig')
        metadata=read('Metadata_Leal et al_Ecology.csv',LMETA).decode('utf-8-sig')
    if not re.search(r'escalc\s*\(\s*["\']ROM["\']',script):raise ValueError('Original Leal R ROM call changed')
    if "Hedges'g" not in metadata or "Hedges'g" not in script:
        raise ValueError('Original source Hedges label not verified')
    rows=list(csv.DictReader(io.StringIO(data.decode('utf-8-sig')),delimiter=';'))
    if (len(rows),len({r['study'] for r in rows}),len({r['sp_plant'] for r in rows}))!=(267,69,60):
        raise ValueError('Source 267/69/60 contract changed')
    return rows
def sciname(s):
    return re.sub('[^a-z]','',str(s).lower()).replace('ipomopis','ipomopsis')
def paperkey(s):
    s=str(s).lower()
    for a,b in [('heilling','heiling'),('mallof','maloof'),('arizmendie','arizmendi'),('elyiahu','eliyahu')]:
        s=s.replace(a,b)
    year=re.findall(r'(?:19|20)\d{2}[a-z]?',s)
    if not year:return None
    head=re.sub(r'et\s*al\.?','',s.split(year[-1])[0]).split('&')[0]
    name=re.sub('[^a-z]','',head)
    return name+year[-1][:4] if name else None
def audit(zhong,leal):
    Z=source_rows(zhong);L=load_leal(leal)
    yi_bad=[];vi_bad=[]
    for r in L:
        m1,m2,s1,s2,n1,n2=[float(r[k]) for k in
            ('mean_larcenist','mean_control','sd_larcenist','sd_control','n_larcenist','n_control')]
        yi,vi=float(r['yi']),float(r['vi'])
        if min(m1,m2,n1,n2)<=0 or min(s1,s2)<0:raise ValueError('Invalid Leal source input')
        y=math.log(m1/m2)
        v=(s1/m1)**2/n1+(s2/m2)**2/n2
        base={'sample_id':r['sample'],'study':r['study'],'type':r['Larcenist_type'],
              'metric':r['Type_of_metric'],'source_yi':yi,'calculated_ROM_yi':y,
              'source_vi':vi,'calculated_ROM_vi':v}
        if abs(y-yi)>1e-6:yi_bad.append({**base,'opposite_sign':y*yi<0})
        if abs(v-vi)>1e-6:vi_bad.append(base)
    if len(yi_bad)!=3 or len(vi_bad)!=7 or not all(x['opposite_sign'] for x in yi_bad):
        raise ValueError('Leal source arithmetic discrepancy count changed')
    zg=defaultdict(list);lg=defaultdict(list)
    for r in Z:
        key=(sciname(r['species']),paperkey(r['reference']))
        if key[1]:zg[key].append(r)
    for r in L:
        key=(sciname(r['sp_plant']),paperkey(r['study']))
        if key[1]:lg[key].append(r)
    shared=[];diffs=[]
    for k in sorted(set(zg)&set(lg)):
        zr,lr=zg[k],lg[k]
        ztypes=sorted({r['larceny_type'] for r in zr})
        ltypes=sorted({r['Larcenist_type'].lower().replace('robbers','robber').replace('thieves','thief') for r in lr})
        item={'species':k[0],'candidate_paper_key':k[1],
              'zhong_IDs':sorted({r['ref-ID'] for r in zr}),
              'leal_study_labels':sorted({r['study'] for r in lr}),
              'zhong_types':ztypes,'leal_types':ltypes,
              'ambiguity':'author-year-species candidate, not verified DOI or same experimental effect'}
        shared.append(item)
        if ztypes!=ltypes:diffs.append(item)
    def with_both(rows,keycols,typekey):
        d=defaultdict(list)
        for r in rows:d[tuple(r[k] for k in keycols)].append(r[typekey])
        return [list(k) for k,v in sorted(d.items()) if len(set(v))>=2]
    Z0=with_both(Z,('ref-ID','species'),'larceny_type')
    Z1=with_both(Z,('ref-ID','species','sub_response_variable'),'larceny_type')
    L0=with_both(L,('study','sp_plant'),'Larcenist_type')
    L1=with_both(L,('study','sp_plant','Type_of_metric'),'Larcenist_type')
    if (len(shared),len(diffs),len(Z0),len(Z1),len(L0),len(L1))!=(45,6,3,5,1,1):
        raise ValueError('Source overlap/grain results drifted: review before promotion')
    return {'schema':'BALANCE_TWO_2025_LARCENY_META_CROSS_SOURCE_AUDIT_V1',
     'sources':{'Zhong_2025_DOI':'10.1016/j.pld.2024.12.004',
                'Leal_2025_DOI':'10.1002/ecy.70036',
                'Zhong_XLSX_SHA256':SOURCE_SHA256,'Leal_Zenodo_ZIP_SHA256':LZIP,
                'Leal_CSV_SHA256':LCSV,'Leal_R_SHA256':LR},
     'source_counts':{'zhong_effects':len(Z),'zhong_papers':len({r['ref-ID'] for r in Z}),
       'leal_effects':len(L),'leal_papers':len({r['study'] for r in L})},
     'leal_source_effect_metric':{
       'R_code_escalc_measure':'ROM: natural logarithm of group mean ratio',
       'metadata_and_R_labels':'Hedges g (inconsistent with ROM computation)',
       'yi_mismatch_n':len(yi_bad),'vi_mismatch_n':len(vi_bad),
       'yi_mismatched':yi_bad,'vi_mismatched':vi_bad,
       'original_published_metaanalysis_not_refit':True},
     'cross_meta_linkability':{'provisional_author_year_species_matches':len(shared),
       'different_source_type_sets':len(diffs),'type_mismatch_cases':diffs,
       'collision_keys':sum(len(x['zhong_IDs'])!=1 or len(x['leal_study_labels'])!=1 for x in shared),
       'all_candidate_keys':shared},
     'same_study_type_opportunities':{'zhong_both_paper_species':Z0,'zhong_both_endpoint':Z1,
      'leal_both_paper_species':L0,'leal_both_endpoint':L1},
     'claim_ceiling':{'type_disagreements_not_proven_coding_errors':True,
       'no_causal_within_study_comparison_inferred':True,
       'author_year_species_candidate_does_not_identify_original_contrast':True,
       'original_Leal_mismatched_rows_NOT_silently_corrected':True,
       'no_cross_effect_independent_replication_assumed':True,
       'no_fitness_worldline_or_structural_BALANCE_Phi_identified':True,
       'original_U6_21_taxa_42_coders_V4_unchanged':True}}
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--zhong-original',type=Path,required=True)
    p.add_argument('--leal-original-zip',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError('Refuse overwritten source audit')
    r=audit(a.zhong_original,a.leal_original_zip)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print(json.dumps({'sources':r['source_counts'],
      'ROM_issue':{k:v for k,v in r['leal_source_effect_metric'].items() if k.endswith('_n')},
      'candidate_matches':r['cross_meta_linkability']['provisional_author_year_species_matches'],
      'source_type_differences':r['cross_meta_linkability']['different_source_type_sets']},indent=2))
if __name__=='__main__':main()

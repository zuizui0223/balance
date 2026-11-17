#!/usr/bin/env python3
"""Provenance of seven Leal 2025 ROM variance discrepancies and two source taxa.

Read-only, source SHA256 locked. This is an integrity and lineage audit, NOT a
corrected meta-analysis, causal treatment estimate, or phylogenetic model fit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.audit_larceny_meta_stage_pairability import source_rows, SOURCE_SHA256
LZIP = "3f6e9b5b55ad8090f41f62faeb2f306c6700a9beb274ac6467106ebab9573c2d"
LC = "4ecd656251f778189d8c13f3608ba99f4de942656fecfe6f2edc8d2509a3d2cb"
LR = "9d60311b102cf27c234f9d6c63eeae602c91768950466e7579ed3a03f0488013"
LM = "e35cb0b9fb62e2ded07c5bdc8bae039ea9b19085a55f023c0f314057774a85fd"

SD_CASE_IDS = ('56','79','81','83','84','88','178')
YI_CASE_IDS = ('79','88','178')
SOURCE_CASES = (
    dict(source_study='Gelvez-Zuningaetal2016', ids=('87','88'),
         archived_species='Collaea_speciosa', published_species='Collaea_cipoensis',
         published_article_doi='10.1016/j.rmb.2016.09.004',
         primary_article_url='https://revista.ib.unam.mx/index.php/bio/article/view/1353',
         source_status='published original article identifies Collaea cipoensis; both taxa listed separately by Kew'),
    dict(source_study='Fumero-Caban&Melendez-Ackerman_2013', ids=tuple(map(str, range(77,85))),
         archived_species='Pitcairnia_augustifolia', published_species='Pitcairnia_angustifolia',
         published_article_doi='10.1111/j.1442-1984.2012.00388.x',
         primary_article_url='https://esj-journals.onlinelibrary.wiley.com/doi/10.1111/j.1442-1984.2012.00388.x',
         source_status='published original species is Pitcairnia angustifolia; Kew lists accepted spelling'),
)


def load_original_leal(path:Path)->list[dict[str,str]]:
    """Independently parse published Zenodo ZIP and verify internal CSV, R and metadata."""
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=LZIP:
        raise ValueError('Official Leal Zenodo source ZIP SHA256 mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        def unique(suffix,sha):
            names=[n for n in z.namelist() if n.endswith('/'+suffix)]
            if len(names)!=1:raise ValueError('Expected exactly one official '+suffix)
            b=z.read(names[0])
            if hashlib.sha256(b).hexdigest()!=sha:
                raise ValueError('Leal nested source SHA256 mismatch '+suffix)
            return b
        dat=unique('complete_hedges.csv',LC)
        code=unique('Script_Leal et al_Ecology.R',LR).decode('utf-8-sig')
        meta=unique('Metadata_Leal et al_Ecology.csv',LM).decode('utf-8-sig')
    if not re.search(r'escalc\s*\(\s*["\']ROM["\']',code) or 'Hedges' not in meta:
        raise ValueError('Expected source ROM computation/metadata contract changed')
    rows=list(csv.DictReader(io.StringIO(dat.decode('utf-8-sig')),delimiter=';'))
    if (len(rows),len({x['study'] for x in rows}),len({x['sp_plant'] for x in rows}))!=(267,69,60):
        raise ValueError('Original Leal effect/study/taxon denominator changed')
    if len({x['sample'] for x in rows})!=267:raise ValueError('Original sample IDs not unique')
    return rows


def _naive_study_pairs(zhong,leal):
    """Replicate pre-reconciliation author+year+species heuristic independently."""
    def species(x):
        return re.sub('[^a-z]','',str(x).lower()).replace('ipomopis','ipomopsis')
    def paper(x):
        s=str(x).lower()
        for before,after in [('heilling','heiling'),('mallof','maloof'),
                             ('arizmendie','arizmendi'),('elyiahu','eliyahu')]:
            s=s.replace(before,after)
        years=re.findall(r'(?:19|20)\d{2}[a-z]?',s)
        if not years:return None
        head=re.sub(r'et\s*al\.?','',s.split(years[-1])[0]).split('&')[0]
        p=re.sub('[^a-z]','',head)
        return p+years[-1][:4] if p else None
    a={(species(r['species']),paper(r['reference'])) for r in zhong}
    b={(species(r['sp_plant']),paper(r['study'])) for r in leal}
    return sorted({x for x in a & b if x[1]})

def _variance(r:dict[str,str], flip_sd:bool=False)->float:
    m1,m2,s1,s2,n1,n2=(float(r[k]) for k in (
        'mean_larcenist','mean_control','sd_larcenist','sd_control','n_larcenist','n_control'))
    if min(m1,m2,n1,n2)<=0 or min(s1,s2)<0:
        raise ValueError('Invalid original positive means, group N or nonnegative SD')
    if flip_sd:
        s1,s2=s2,s1
    return s1**2/(n1*m1**2)+s2**2/(n2*m2**2)


def _load_tree(zip_path:Path)->str:
    raw=zip_path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=LZIP:
        raise ValueError('Official Leal Zenodo source ZIP SHA256 mismatch')
    with zipfile.ZipFile(zip_path) as z:
        sources=[x for x in z.namelist() if x.endswith('/visit.tre')]
        if len(sources)!=1:
            raise ValueError('Original phylogeny tree not uniquely available')
        return z.read(sources[0]).decode('utf-8-sig')


def _cross_meta_source_overlaps(zhong_source:Path,leal_rows:list[dict])->dict:
    """Recover two author-DOI-verified paper identities missed by string joins."""
    zhong=source_rows(zhong_source)  # original 2025 Figshare XLSX SHA gate
    prior=_naive_study_pairs(zhong,leal_rows)
    if len(prior)!=45:
        raise ValueError('Previous 45 candidate author-year-species joins changed')
    pairs=[]
    originals=((23,'Pitcairnia_angustifolia',tuple(range(562,572)),
                'Fumero-Caban&Melendez-Ackerman_2013',tuple(range(77,85)),
                '10.1111/j.1442-1984.2012.00388.x',
                '2012 online publication vs 2013 issue-year; original primary species spelling'),
               (24,'Collaea_cipoensis',(572,573),
                'Gelvez-Zuningaetal2016',(87,88),'10.1016/j.rmb.2016.09.004',
                'first-author accent/transcription and wrong source species tag'))
    for z_id,primary_species,zids,l_study,lids,doi,why in originals:
        zrows=[r for r in zhong if r['ref-ID']==z_id and r['species']==primary_species]
        lrows=[r for r in leal_rows if r['study']==l_study]
        if tuple(sorted((int(r['ID']) for r in zrows)))!=zids:
            raise ValueError('Zhong source paper effects changed for verified original publication')
        if tuple(sorted((int(r['sample']) for r in lrows)))!=lids:
            raise ValueError('Leal source study IDs changed for verified original publication')
        if len(zrows)==0 or len(lrows)==0:
            raise ValueError('Original primary source study missing')
        pairs.append({'primary_publication_doi':doi,
                      'primary_species':primary_species,
                      'zhong_ref_ID':z_id,'zhong_effect_IDs':list(zids),
                      'leal_study':l_study,'leal_effect_samples':list(lids),
                      'leal_archive_species':lrows[0]['sp_plant'],
                      'missed_by_naive_join_reason':why,
                      'same_study_identification_supported_by_primary_DOI':True,
                      'identical_experimental_contrast_IDs_verified':False,
                      'shared_effect_covariance_known':False})
    return {'prior_provisional_first_author_year_species_candidate_pairs':len(prior),
            'recoverable_additional_primary_paper_species_candidate_pairs':len(pairs),
            'updated_paper_species_candidate_upper_bound':len(prior)+len(pairs),
            'additional_primary_identified_sources':pairs,
            'all_47_are_DOI_verified_independent_effects':False,
            'distinct_primary_studies_not_distinct_effect_contrasts':True,
            'original_zhong_source_XLSX_SHA256':SOURCE_SHA256}


def audit(original:Path,zhong_source:Path|None=None)->dict:
    rows=load_original_leal(original)  # independent original Zenodo CSV/R/metadata SHA gates
    byid={r['sample']:r for r in rows}
    if len(byid)!=len(rows):raise ValueError('Duplicate source effect ID')
    results=[]
    yi_flipped=[]
    valid_direct=0
    for r in rows:
        vid=r['sample']
        actual=float(r['vi'])
        calc=_variance(r)
        calc_flipped=_variance(r,True)
        if abs(actual-calc)>1e-6:
            if abs(actual-calc_flipped)>1e-8:
                raise ValueError('Unexpected ROM variance cannot be reconstructed by SD transposition')
            results.append({'sample_id':vid,'study':r['study'],'species_archive':r['sp_plant'],
                            'metric':r['Type_of_metric'],
                            'vi_archived':actual,'vi_recomputed_archived_SD_columns':calc,
                            'vi_recomputed_with_SD_columns_exchanged':calc_flipped,
                            'relative_vi_change_if_recalculated_from_current_SD':calc/actual,
                            'sd_larcenist_archived':float(r['sd_larcenist']),
                            'sd_control_archived':float(r['sd_control'])})
        else:valid_direct+=1
        y=math.log(float(r['mean_larcenist'])/float(r['mean_control']))
        if abs(float(r['yi'])-y)>1e-6:
            if abs(float(r['yi'])+y)>1e-8:
                raise ValueError('Original ROM yi has non-sign-only discrepancy')
            yi_flipped.append({'sample_id':vid,'study':r['study'],
                               'yi_archived':float(r['yi']),
                               'ln_group_mean_ratio':y,
                               'source_orientation_unexplained':True})
    if tuple(sorted((z['sample_id'] for z in results),key=int))!=SD_CASE_IDS:
        raise ValueError('Changed set of seven source SD/variance anomalies')
    if tuple(sorted((z['sample_id'] for z in yi_flipped),key=int))!=YI_CASE_IDS:
        raise ValueError('Changed set of three signed effect anomalies')
    if valid_direct!=260:raise ValueError('Unexpected number of direct ROM variance matches')
    cross_meta=_cross_meta_source_overlaps(zhong_source,rows) if zhong_source is not None else None
    tree=_load_tree(original)
    taxa=[]
    bad_rows=0
    for item in SOURCE_CASES:
        present=[r for r in rows if r['study']==item['source_study']]
        ids=tuple(sorted((r['sample'] for r in present),key=int))
        if ids!=item['ids'] or any(r['sp_plant']!=item['archived_species'] for r in present):
            raise ValueError('Published study attribution/source-archived taxon labels changed')
        if any(r['tips_phylo']!=item['archived_species'] for r in present):
            raise ValueError('Source phylogenetic tips do not match archived species names')
        if item['archived_species'] not in tree:
            raise ValueError('Archived study phylogeny tip absent')
        if item['published_species'] in tree:
            raise ValueError('Original phylogeny unexpectedly contains primary-study correct name')
        taxa.append({**item,'effect_row_count':len(present),
                     'archived_name_appears_in_original_phylogeny':True,
                     'primary_study_name_appears_in_original_phylogeny':False,
                     'does_not_establish_dna_misplacement_or_model_change':True})
        bad_rows+=len(present)
    r88=byid['88']
    if (r88['study']!='Gelvez-Zuningaetal2016'
            or float(r88['mean_larcenist'])!=3.44
            or float(r88['mean_control'])!=17.11
            or int(r88['n_larcenist'])!=44
            or int(r88['n_control'])!=237):
        raise ValueError('Primary-published 2016 visit study means / published N changed')
    se1,se2=1.05,2.70  # Gelvez et al. 2016 original article PDF, page 1354
    reconstructed=(se1*math.sqrt(44),se2*math.sqrt(237))
    sds=(float(r88['sd_larcenist']),float(r88['sd_control']))
    if abs(sds[0]-reconstructed[1])>1e-5 or abs(sds[1]-reconstructed[0])>0.0002:
        raise ValueError('2016 primary SE/N do not support reverse-SD evidence')
    return {'schema':'BALANCE_LEAL_2025_SOURCE_SD_TAXON_IDENTIFICATION_V1',
            'original_zenodo_doi':'10.5281/zenodo.14773082',
            'original_ecology_paper_doi':'10.1002/ecy.70036',
            'original_zip_sha256':LZIP,
            'source_effect_count':len(rows),
            'ROM_variance':{
                'original_source_vi_unmodified':True,
                'source_vi_matches_archived_SD_order':valid_direct,
                'source_vi_matches_only_exchanged_SD_order':len(results),
                'source_vi_discordant_sample_ids':list(SD_CASE_IDS),
                'discrepancies':results,
                'max_absolute_error_of_swapped_SD_formula':max(abs(r['vi_archived']-r['vi_recomputed_with_SD_columns_exchanged']) for r in results),
                'no_claim_that_all_seven_source_SD_values_independently_recovered':True,
            },
            'ROM_effect_sign':{'archived_sign_opposite_to_group_means_n':len(yi_flipped),
                               'cases':yi_flipped,
                               'source_direction_recode_unknown':True},
            'primary_source_2016_sample88':{
                'paper_doi':'10.1016/j.rmb.2016.09.004',
                'paper_species':'Collaea_cipoensis',
                'robbed_visitation_mean':3.44,
                'robbed_visitation_SE':se1,
                'robbed_reported_N':44,
                'intact_visitation_mean':17.11,
                'intact_visitation_SE':se2,
                'intact_reported_N':237,
                'SD_derived_from_paper_SE_and_N_if_SE_is_mean_SE':list(reconstructed),
                'archived_SD_columns':list(sds),
                'original_2016_plant_n_for_fruit_census':44,
                'reported_N_for_visitation_must_not_be_assumed_to_be_independent_plants':True,
                'original_paper_is_not_Collaea_speciosa':True,
                'original_yi_sign_in_archive_opposite_ln_treatment_control':True},
            'primary_article_taxon_discrepancies':taxa,
            'effect_rows_with_paper_taxon_label_disagreement':bad_rows,
            'cross_meta_original_paper_recovery':cross_meta,
            'phylogeny_rebuilding_required_before_any_verified_taxonomy_correction':True,
            'claim_guards':{
                'original_fitted_meta_model_not_refitted':True,
                'no_silent_change_to_study_2025_archived_csv':True,
                'original_source_sd_order_problem_does_not_prove_saved_vi_is_wrong':True,
                'primary_papers_and_taxon_dbs_are_provenance_not_reanalysed_field_records':True,
                'taxonomy_mismatch_not_10_independent_taxonomic_errors':True,
                'direction_reversal_not_a_demonstrated_publication_error':True,
                'no_plant_architecture_Phi_or_contrast_cost_estimated':True,
                'original_U6_21_taxa_42_coders_V4_and_SLK_not_changed':True}}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original-zenodo',type=Path,required=True)
    p.add_argument('--original-zhong',type=Path)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    z=audit(a.original_zenodo,a.original_zhong)
    if a.out.exists():raise FileExistsError('Refuse overwrite of audit receipt')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(z,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'source_effect_count':z['source_effect_count'],
          'SD_variance_cases':z['ROM_variance']['source_vi_discordant_sample_ids'],
          'max_error_after_SD_swap':z['ROM_variance']['max_absolute_error_of_swapped_SD_formula'],
          'signed_effect_cases':[q['sample_id'] for q in z['ROM_effect_sign']['cases']],
          'source_taxon_disagreements':[q['source_study'] for q in z['primary_article_taxon_discrepancies']],
          'affected_source_effect_rows':z['effect_rows_with_paper_taxon_label_disagreement'],
          'cross_meta_recovered':z['cross_meta_original_paper_recovery']['recoverable_additional_primary_paper_species_candidate_pairs'] if z['cross_meta_original_paper_recovery'] else None},indent=2))

if __name__=='__main__':main()

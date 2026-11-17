#!/usr/bin/env python3
"""2018 Corydalis paper summary vs 2025 Figshare meta treatment identity (noncausal).

No original Dryad worksheet is available in this audit; source metadata and
the original paper's printed values support only selected treatment attribution.
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts.audit_larceny_meta_stage_pairability import SOURCE_SHA256, source_rows

DOI='10.1111/oik.05440'
DRYAD='10.5061/dryad.bh6hs70'
PUBLISHED={
 'control':{'seed_per_raceme':7.56,'fruit_proportion':.74,'sqrt_pollen':24.83},
 'PR':{'seed_per_raceme':6.73,'fruit_proportion':.73,'sqrt_pollen':28.16},
 'CR':{'seed_per_raceme':8.65,'fruit_proportion':.83,'sqrt_pollen':28.54},
}
META_TRIPLETS={'PR':{'pollen deposition':254,'fruit set':255,'seed set':256},
               'CR':{'pollen deposition':257,'fruit set':258,'seed set':259}}

def audit(original_meta:Path)->dict:
    rows=source_rows(original_meta) # source SHA256 and 776 source effects checked here
    heiling={r['ID']:r for r in rows if r['ref-ID']==29 and r['species']=='Corydalis_caseana'}
    if set(heiling)!=set(range(253,264)):raise ValueError('Changed Heiling source effect IDs')
    results={}
    for treatment,stages in META_TRIPLETS.items():
        group={}
        for stage,effect_id in stages.items():
            record=heiling[effect_id]
            if record['sub_response_variable']!=stage:
                raise ValueError('Changed Heiling source endpoint ID')
            group[stage]={'effect_id':effect_id,'lnRR':record['yi'],
                          'sampling_variance':record['vi'],
                          'recorded_experiment_level':record['experiment_level']}
        published_seed_ratio=math.log(PUBLISHED[treatment]['seed_per_raceme']/PUBLISHED['control']['seed_per_raceme'])
        seed_error=group['seed set']['lnRR']-published_seed_ratio
        if not math.isclose(seed_error,0,rel_tol=0,abs_tol=2e-13):
            raise ValueError('Original-paper seed treatment identity does not match meta')
        published_fruit_ratio=math.log(PUBLISHED[treatment]['fruit_proportion']/PUBLISHED['control']['fruit_proportion'])
        results[treatment]={
          'candidate_meta_stage_group':group,
          'seed_means_from_2018_paper_match_meta_to_machine_precision':True,
          'seed_lnRR_reported_paper_means':published_seed_ratio,
          'seed_lnRR_meta_minus_original':seed_error,
          'fruit_lnRR_reported_paper_means':published_fruit_ratio,
          'fruit_lnRR_meta_minus_original_means':group['fruit set']['lnRR']-published_fruit_ratio,
          'fruit_lnRR_reproducible_from_rounded_2018_means':math.isclose(
               group['fruit set']['lnRR'],published_fruit_ratio,rel_tol=0,abs_tol=1e-3),
          'candidate_meta_seed_minus_fruit_lnRR':group['seed set']['lnRR']-group['fruit set']['lnRR'],
          'fruit_and_pollen_treatment_identity_verified_with_raw_Dryad':False,
          'stage_difference_estimates_a_matched_individual_level_effect':False,
        }
    correct=sum(abs(results[t]['seed_lnRR_meta_minus_original']) for t in ('PR','CR'))
    wrong=(abs(heiling[256]['yi']-results['CR']['seed_lnRR_reported_paper_means'])
          +abs(heiling[259]['yi']-results['PR']['seed_lnRR_reported_paper_means']))
    return {
       'schema':'BALANCE_HEILING_2018_PAPER_META_TREATMENT_IDENTITY_V1',
       'source_2025_meta_sha256':SOURCE_SHA256,
       'source_2018_paper_doi':DOI,
       'source_2018_Dryad_doi':DRYAD,
       'Dryad_file_id':41496,
       'Dryad_file_md5_from_original_metadata':'31e7e67fa98c5ffb7b4b133686191b90',
       'original_Dryad_workbook_recovered':False,
       'original_Dryad_delivery_status':{'web_file_stream_HTTP':403,'REST_file_download_HTTP':401},
       'published_experimental_design':{
           'year':2015,'location':'Kebler Pass',
           'plant_allocation':'haphazard, NOT independently confirmed randomized',
           'groups':['control','PR','CR'],'plants_per_group':5,'total_plants':15,
           'lateral_racemes_per_plant':5,'flowers_treated_percent_per_plant':[10,20],
           'pollen_receipt_fruit_and_seed_reported_in_one_experimental_programme':True,
           'separate_behavioral_and_single_visit_experiments_not_joined':True},
       'published_paper_summary_means':PUBLISHED,
       'candidate_treatment_groups':results,
       'seed_treatment_uniqueness':{
           'correct_abs_lnRR_residual_sum':correct,'wrong_assignment_residual_sum':wrong,
           'unique_seed_ID_attribution_confirmed':wrong>correct+0.01},
       'interpretive_firewall':{
           'no_unvalidated_raw_plant_records_used':True,
           'no_claim_of_full_five_stage_cohort_tracking':True,
           'no_individual_outcome_covariance_available':True,
           'no_causal_mediation_or_treatment_pvalue_recomputed':True,
           'unmatched_fruit_and_pollen_meta_ID_assignments_tentative':True,
           'already_published_three_mechanisms_are_prior_art':True,
           'no_fitness_of_differentiated_vs_shared_architecture_measured':True,
           'original_U6_21_taxa_42_coders_V4_SLK_unchanged':True,
       },
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError('Refuse overwrite source readout')
    result=audit(a.source)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'experiment':result['published_experimental_design'],
      'treatment_groups':result['candidate_treatment_groups'],
      'seed_treatment_uniqueness':result['seed_treatment_uniqueness']},indent=2))

if __name__=='__main__':main()

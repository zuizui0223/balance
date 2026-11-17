#!/usr/bin/env python3
"""Two primary 2016 source studies vs Leal 2025 visitor/abortion endpoint meaning.

Original PDFs and both published meta originals must pass byte-level hash gates.
No re-estimation of the published multilevel phylogenetic model.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, statistics, subprocess, sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts.audit_leal_sd_taxon_provenance import load_original_leal, LZIP
from scripts.audit_larceny_meta_stage_pairability import source_rows, SOURCE_SHA256

CUEVAS_SHA='216750e6c649d8472420e54f272c5448caab875e59aab51603fd5b5e9afb5cdf'
GELVEZ_SHA='1e8ef9017756cacd5f893cef6e42abe2669cd0baf7ea506999324c9f386b0a0a'
CUEVAS_DOI='10.1111/plb.12311'
GELVEZ_DOI='10.1016/j.rmb.2016.09.004'
CASES={'56':('Cuevas&Guerrero_2016','Salvia_gesnerifolia','visitation'),
       '87':('Gelvez-Zuningaetal2016','Collaea_speciosa','female'),
       '88':('Gelvez-Zuningaetal2016','Collaea_speciosa','visitation')}

def _pdf_source(path:Path,sha:str,phrases:tuple[str,...])->str:
    b=path.read_bytes()
    if hashlib.sha256(b).hexdigest()!=sha:
        raise ValueError('Original primary PDF SHA256 mismatch '+str(path))
    if not b.startswith(b'%PDF-'):raise ValueError('Original primary-source PDF signature absent')
    proc=subprocess.run(['pdftotext','-layout',str(path),'-'],capture_output=True,text=True,timeout=30)
    if proc.returncode!=0:raise ValueError('Cannot extract original primary PDF text: '+proc.stderr[:150])
    s=' '.join(proc.stdout.replace('\u00ad','').split())
    low=s.lower()
    for p in phrases:
        if p.lower() not in low:raise ValueError('Original primary paper text differs: '+p)
    return s

def _summary(rows:list[dict])->dict:
    if not rows:raise ValueError('Empty source metric class')
    study=defaultdict(list)
    for r in rows:study[r['study']].append(float(r['yi']))
    effects=[float(r['yi']) for r in rows]
    inv=[1/float(r['vi']) for r in rows]
    return {
       'effect_rows':len(rows),'primary_study_labels':len(study),
       'unweighted_mean_of_archived_lnRR':statistics.mean(effects),
       'inverse_archived_vi_weighted_mean_of_archived_lnRR':
           sum(y*w for y,w in zip(effects,inv))/sum(inv),
       'equal_study_averaged_archived_lnRR':
           statistics.mean(statistics.mean(q) for q in study.values()),
       'not_an_effect_size_meta_regression_or_original_model_replay':True,
    }

def audit(zenodo_original:Path,zhong_original:Path,cuevas_original:Path,gelvez_original:Path)->dict:
    _pdf_source(cuevas_original,CUEVAS_SHA,(
       'Spatio-temporal variation of nectar robbing in Salvia gesneriflora',
       'filmed seven','44 h of observation in 204 flowers',
       'primary (D. baritula)', 'secondary nectar robbers',
       'P = 0.276', 'P = 0.083'))
    _pdf_source(gelvez_original,GELVEZ_SHA,(
       'Nectar robbing in Collaea cipoensis', '44 flowering plants',
       '17.11','3.44','0.38','0.22','p = 0.11',
       'plant was included as a random'))
    original=load_original_leal(zenodo_original)
    Z=source_rows(zhong_original)
    ids={r['sample']:r for r in original}
    for name,(study,species,metric) in CASES.items():
        r=ids[name]
        if (r['study'],r['sp_plant'],r['Type_of_metric'])!=(study,species,metric):
            raise ValueError('Frozen Leal 2016 source record context changed '+name)
    r56,r87,r88=(ids[k] for k in ('56','87','88'))
    if ([float(r56[k]) for k in ('mean_larcenist','mean_control','sd_larcenist','sd_control')]
        !=[.21,.07,.04,.06]):
        raise ValueError('Leal Salvia figure-approximate values changed')
    if [int(r56[k]) for k in ('n_larcenist','n_control')]!=[7,7]:
        raise ValueError('Source seven video plant groups changed')
    if [float(r87[k]) for k in ('mean_larcenist','mean_control')]!=[.38,.22]:
        raise ValueError('Primary abortion means changed')
    if [int(r87[k]) for k in ('n_larcenist','n_control')]!=[570,716]:
        raise ValueError('Primary grouped floral counts changed')
    if abs(float(r87['sd_larcenist'])-.061*math.sqrt(570))>.001 or (
        abs(float(r87['sd_control'])-.057*math.sqrt(716))>.001):
        raise ValueError('Archive abortion SD no longer matches original SE times sqrt flower N')
    if [float(r88[k]) for k in ('mean_larcenist','mean_control')]!=[3.44,17.11]:
        raise ValueError('Gelvez reported hummingbird visits mean changed')
    if [int(r88[k]) for k in ('n_larcenist','n_control')]!=[44,237]:
        raise ValueError('Gelvez original flower sample numbers changed')
    if abs(float(r88['yi']) + math.log(3.44/17.11))>1e-9:
        raise ValueError('Archived direction-reversed visit rate identity changed')
    z_salvia=[r for r in Z if r['ref-ID']==13 and r['species']=='Salvia_gesneriflora']
    if sorted(r['ID'] for r in z_salvia)!=list(range(501,507)):
        raise ValueError('Zhong first source original Salvia program changed')
    z506=next(r for r in z_salvia if r['ID']==506)
    if z506['sub_response_variable']!='visitation rate':
        raise ValueError('Original Zhong source visitor endpoint changed')
    if z506['yi']!=.677562449543247:
        raise ValueError('Original Zhong source visit effect value changed')
    # The archived response class does not distinguish actual visitor guild.
    # Exact figure digitization/individual events were NOT recovered.
    f=[r for r in original if r['Larcenist_type']=='Robbers' and r['Type_of_metric']=='female']
    v=[r for r in original if r['Larcenist_type']=='Robbers' and r['Type_of_metric']=='visitation']
    if (len(f),len(v))!=(130,44):
        raise ValueError('Original archived response-by-type denominators changed')
    r88b=[dict(r) for r in v]
    for r in r88b:
        if r['sample']=='88':r['yi']=str(math.log(3.44/17.11))
    source87_y=math.log(.38/.22)
    if abs(float(r87['yi'])-source87_y)>1e-9:raise ValueError('Published abortion lnRR identity drift')
    retain=math.log((1-.38)/(1-.22))
    return {
      'schema':'BALANCE_LEAL_2016_VISITOR_GUILD_ABORTION_SOURCE_GATE_V1',
      'verified_primary_source_receipts':{
        'Cuevas_RosasGuerrero_2016_original_DOI':CUEVAS_DOI,
        'Cuevas_RosasGuerrero_2016_author_pdf_SHA256':CUEVAS_SHA,
        'Gelvez_Zuniga_2016_original_DOI':GELVEZ_DOI,
        'Gelvez_Zuniga_2016_journal_pdf_SHA256':GELVEZ_SHA,
        'Leal_2025_original_Zenodo_sha256':LZIP,
        'Zhong_2025_original_XLSX_sha256':SOURCE_SHA256},
      'salvia_source_sample_56':{
        'sample_id':56,'original_primary_species':'Salvia_gesneriflora',
        'archived_species':'Salvia_gesnerifolia',
        'archived_visitor_metric':'visitation',
        'original_primary_video_plants':7,'original_total_film_hours':44,
        'original_flower_count_film':204,
        'primary_robber_visitor':'Diglossa baritula',
        'legitimate_hummingbird_visitor':'Eugenes fulgens',
        'source_figure_primary_robber_approximate_robbed_vs_unrobbed':[.21,.07],
        'source_figure_legitimate_visitor_approximate_robbed_vs_unrobbed':[.19,.10],
        'archived_effect_ynatural_log_ROM':float(r56['yi']),
        'guild_fingerprint':'primary-robber Fig.4 candidate; exact source extraction/digitization unverified',
        'not_verified_legitimate_pollinator_service_effect':True,
        'paired_video_plants_are_NOT_two_independent_groups_of_7':True,
        'original_figure_shows_no_significant_hummingbird_preference':True,
        'Zhong_same_primary_effect_IDs':[r['ID'] for r in z_salvia],
        'Zhong_same_primary_visitor_effect_ID':506,
        'Zhong_visit_lnRR':float(z506['yi']),
        'Zhong_visitor_guild_cannot_be_confirmed_from_meta_label_alone':True,
        'one_new_primary_source_overlap_candidate_beyond_previous_at_least_48':True,
        'previous_primary_study_candidate_count_at_least':48,
        'after_salvia_primary_source_reconciliation_candidate_count_at_least':49,
        'not_49_verified_identical_experimental_effects':True,
      },
      'collaea_source_sample_87':{
        'sample_id':87,'archived_species':'Collaea_speciosa',
        'primary_species':'Collaea_cipoensis',
        'archived_metric':'female','primary_measured_metric':'flower_abortion_fraction',
        'original_primary_plant_count':44,
        'original_damaged_flower_count':570,
        'original_intact_flower_count':716,
        'abortion_robbed_mean':.38,'abortion_robbed_SE':.061,
        'abortion_intact_mean':.22,'abortion_intact_SE':.057,
        'original_plant_random_effect_in_abortion_GLMM':True,
        'original_p_value_of_abortion_test':.11,
        'original_reported_abortion_difference_not_significant':True,
        'archived_abortion_lnRR':float(r87['yi']),
        'sample_mean_abortion_ROM_source':source87_y,
        'illustrative_nonabortion_ratio_not_fruit_set':retain,
        'do_not_negate_yi_to_translate_abortion_to_fitness':True,
        'archived_SD_could_be_SE_times_sqrt_flower_N':True,
        'original_source_SE_based_on_per_plant_analysis_not_570_independent_plants':True,
        'not_a_verified_maternal_fitness_yield_measure':True,
      },
      'collaea_source_sample_88':{
        'sample_id':88,
        'original_robbed_visits_per_reported_units':3.44,
        'original_intact_visits_per_reported_units':17.11,
        'original_reported_n_robbed':44,'original_reported_n_intact':237,
        'original_robbed_lnRR':math.log(3.44/17.11),
        'archived_visitation_lnRR':float(r88['yi']),
        'archived_visitation_sign_is_opposite_original_robbed_over_intact':True,
        'original_visits_not_independent_maternal_plant_n':True,
        'still_observational_natural_damage_contrast':True},
      'subset_sensitivity_descriptive_not_refit':{
        'female_robbers_as_archived':_summary(f),
        'female_robbers_excluding_abortion_87':_summary([r for r in f if r['sample']!='87']),
        'visitation_robbers_as_archived':_summary(v),
        'visitation_robbers_excluding_candidate_robber_visit_56':_summary([r for r in v if r['sample']!='56']),
        'visitation_robbers_excluding_observational_56_and_misoriented_88':_summary([r for r in v if r['sample'] not in ('56','88')]),
        'visitation_robbers_hypothetical_reorient_88':_summary(r88b),
        'visitation_robbers_hypothetical_reorient_88_and_exclude_56':_summary([r for r in r88b if r['sample']!='56']),
        'no_correction_to_published_random_effects_or_phylogenetic_model':True,
        'original_meta_inputs_not_mutated':True},
      'remaining_review_queue':{
        'all_original_seven_SD_swap_samples':[56,79,81,83,84,88,178],
        'prior_source_reconciled':[88,178],
        'Salvia_56_figure_guild_and_SD_source_stage_audited_but_exact_SE_SD_pending':True,
        'original_Fumero_2013_full_table_data_not_acquired':[79,81,83,84],
        'Fumero_79_effect_direction_still_unresolved':True,
        'Gelvez_88_original_direction_identified_but_published_meta_original_unmodified':True,
      },
      'claim_guards':{
        'no_evidence_of_plant_reproductive_fitness_gain_from_higher_abortion':True,
        'never_pool_diglossan_robber_visits_as_confirmed_legitimate_visits':True,
        'no_prior_study_label_matches_verified_as_same_original_effect':True,
        'source_original_2016_papers_not_new_studies':True,
        'no_primary_pdf_figure_coordinates_digitized_or_fabricated':True,
        'no_multilevel_meta_effect_refit_or_p_value':True,
        'no_structural_BALANCE_L_K_Phi_or_architecture_fitness':True,
        'U6_21_sources_42_coder_fields_V4_SLK_unmodified':True,
      },
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--leal-zip',type=Path,required=True)
    ap.add_argument('--zhong-xlsx',type=Path,required=True)
    ap.add_argument('--cuevas-original',type=Path,required=True)
    ap.add_argument('--gelvez-original',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.out.exists():raise FileExistsError('Cannot overwrite source audit result')
    a=audit(args.leal_zip,args.zhong_xlsx,args.cuevas_original,args.gelvez_original)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(a,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print(json.dumps({
       'salvia':a['salvia_source_sample_56'],
       'collaea87':a['collaea_source_sample_87'],
       'collaea88':a['collaea_source_sample_88'],
       'sensitivity':a['subset_sensitivity_descriptive_not_refit']},indent=2,ensure_ascii=False))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Source-MD5-locked test of the Desfontainia sugar-filter/fitness link.

The original submitted R sugar gate, not the paper, requires nectar >=5 uL.
This audit never writes to frozen V4 or treats observational shrubs as experiments.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from scripts.audit_desfontainia_fitness_gate import (
    ORIGINAL_MD5, source_sheet, summarize_nectar, summarize_seed,
)

AUTHOR_R_MD5 = '9fd405c399ecad9c3fe54d1cd70b21c0'
FINAL_AUTHOR_R_MD5='8e72799d10773c70a77089bd7efc4fab'
NECTAR_HEADER = ['Plant','Flower','Status','Nectar volumen (microliter)',
                 'Nectar concentration (% w/w)']
SEED_HEADER = ['Plant','Seed (-P-R)','Seeds (+P-R)','Seeds (+P+R)']
INCI_HEADER = ['Plant','N° of undamaged flowers','N° of pierced flowers','% of pierced flowers']
THRESHOLDS = [0.0,0.5,1.0,2.0,3.0,5.0]


def original_code_has_5ul_gate(source: str) -> bool:
    return bool(re.search(
        r'filter\s*\(\s*nectar_ul\s*>=\s*5\s*,\s*!is\.na\(sugar_pct\)\s*,\s*sugar_pct\s*>\s*0\s*\)',
        source,
    ))


def pair_sugar_by_shrub(rows: list[list], threshold: float) -> dict:
    """Mean of positive sugar observations within each shrub/status, if available.

    threshold=0 additionally requires positive nectar, matching source n=9.
    Higher thresholds are post-open measurement-support sensitivity analyses.
    """
    if threshold < 0:raise ValueError('Invalid threshold')
    groups=defaultdict(list)
    seen=set()
    for r in rows:
        if len(r)!=5:raise ValueError('Source nectar row shape changed')
        plant, flower, status, volume, sugar=r
        if status not in ('Robada','No dañada'):raise ValueError('Status unexpected')
        if not isinstance(plant,(int,float)) or not isinstance(flower,(int,float)):
            raise ValueError('Source plant/flower identity not numeric')
        if (int(plant),int(flower),status) in seen:raise ValueError('Duplicate flower/status source identity')
        seen.add((int(plant),int(flower),status))
        if volume is not None and (not isinstance(volume,(int,float)) or not math.isfinite(volume) or volume<0):
            raise ValueError('Invalid source nectar volume')
        if sugar is not None and (not isinstance(sugar,(int,float)) or not math.isfinite(sugar) or sugar<0):
            raise ValueError('Invalid source sugar concentration')
        if (volume is not None and sugar is not None and sugar>0 and volume>0 and volume>=threshold):
            groups[int(plant),status].append(float(sugar))
    a={pid for pid,status in groups if status=='Robada'}
    b={pid for pid,status in groups if status=='No dañada'}
    common=sorted(a&b)
    vals_rob=[statistics.mean(groups[pid,'Robada']) for pid in common]
    vals_und=[statistics.mean(groups[pid,'No dañada']) for pid in common]
    return {'n_shrubs':len(common),'shrub_ids':common,
            'means':{'Robada':vals_rob,'No dañada':vals_und},
            'n_source_flowers_with_sugar':sum(len(z) for z in groups.values()),
            'n_robbed_shrubs_with_measurable_sugar':len(a),
            'n_undamaged_shrubs_with_measurable_sugar':len(b)}


def final_code_uses_positive_sugar(source:str)->bool:
    return 'filter(`Nectar concentration (% w/w)` > 0)' in source


def analyze(source_xlsx:Path, author_r:Path, final_r:Path|None=None, final_xlsx:Path|None=None) -> dict:
    import numpy as np
    from scipy.stats import spearmanr,ttest_rel

    author_bytes=Path(author_r).read_bytes()
    if hashlib.md5(author_bytes).hexdigest()!=AUTHOR_R_MD5:
        raise ValueError('Original author R script MD5 mismatch; refuse unverified code comparison')
    code=author_bytes.decode('utf-8-sig')
    concordance={
        'march_submission_R_md5':AUTHOR_R_MD5,
        'final_paper_r_code_checked':False,
        'final_paper_code_reproduces_nine_pair_statistic':False,
        'same_underlying_spreadsheet_between_records':False,
        'march_source_gate_is_final_paper_bug':False,
    }
    if final_r is not None or final_xlsx is not None:
        if final_r is None or final_xlsx is None:raise ValueError('Both final-paper R and XLSX files needed')
        final_rb=Path(final_r).read_bytes()
        if hashlib.md5(final_rb).hexdigest()!=FINAL_AUTHOR_R_MD5:
            raise ValueError('Final paper R source MD5 mismatch')
        final_code=final_rb.decode('utf-8-sig')
        if not final_code_uses_positive_sugar(final_code):
            raise ValueError('Final paper sugar filter changed unexpectedly')
        if hashlib.md5(Path(final_xlsx).read_bytes()).hexdigest()!=ORIGINAL_MD5:
            raise ValueError('Final paper workbook no longer shares verified MD5')
        concordance.update(final_paper_r_code_checked=True,
            final_paper_code_reproduces_nine_pair_statistic=True,
            same_underlying_spreadsheet_between_records=True,
            final_paper_R_md5=FINAL_AUTHOR_R_MD5)
    if not original_code_has_5ul_gate(code):
        raise ValueError('Author published 5-uL sugar filter does not match audit')
    nect=source_sheet(source_xlsx,3,NECTAR_HEADER)
    seeds=source_sheet(source_xlsx,6,SEED_HEADER)
    incid=source_sheet(source_xlsx,2,INCI_HEADER)
    summary_nectar=summarize_nectar(nect)
    summary_seed=summarize_seed(seeds)
    if len(incid)!=100 or len(set(int(r[0]) for r in incid))!=100:
        raise ValueError('Expected 100 separate incidence survey shrubs')
    if any(r[1]+r[2]!=10 for r in incid):
        raise ValueError('Non-ten-flower incidence row unsupported')
    incidence_robbed=sum(int(r[2]) for r in incid)
    # Shrubs, not flowers, are the resampling units for exposure frequency.
    rng_exposure=np.random.default_rng(20261117)
    per_shrub_pierced=np.asarray([int(r[2]) for r in incid],dtype=float)
    exposure_draws=rng_exposure.choice(per_shrub_pierced,(20000,100),replace=True).mean(axis=1)/10
    exposure_ci=np.quantile(exposure_draws,[.025,.975]).tolist()
    prevalence={'n_shrubs':len(incid),'flowers_per_shrub':10,
                'cluster_bootstrap95_fraction':exposure_ci,'cluster_bootstrap_replicates':20000,
                'pierced_flowers':incidence_robbed,'flowers_surveyed':1000,
                'pierced_flower_share':incidence_robbed/1000,
                'shrubs_with_any_piercing':sum(r[2]>0 for r in incid),
                'distinct_survey_and_nectar_identity_namespaces_must_not_be_joined_on_integer_id':True}

    level=[]
    for min_vol in THRESHOLDS:
        paired=pair_sugar_by_shrub(nect,min_vol)
        out={'minimum_flower_volume_ul':min_vol,
             'n_paired_shrubs':paired['n_shrubs'],
             'number_robbed_shrubs_with_observed_sugar':paired['n_robbed_shrubs_with_measurable_sugar'],
             'number_undamaged_shrubs_with_observed_sugar':paired['n_undamaged_shrubs_with_measurable_sugar']}
        if paired['n_shrubs']>=2:
            a=np.asarray(paired['means']['Robada']);b=np.asarray(paired['means']['No dañada'])
            stat=ttest_rel(a,b)
            out.update(paired_t=float(stat.statistic),paired_p_two_sided=float(stat.pvalue),
                       mean_pierced_sugar_pct=float(a.mean()),mean_undamaged_sugar_pct=float(b.mean()),
                       pierced_to_undamaged_ratio=float(a.mean()/b.mean()))
        else:
            out.update(paired_t=None,paired_p_two_sided=None,
                       mean_pierced_sugar_pct=None,mean_undamaged_sugar_pct=None,
                       pierced_to_undamaged_ratio=None)
        level.append(out)
    original_gate=level[-1]
    paper_reconstruction=level[0]
    assert original_gate['n_paired_shrubs']==1 and paper_reconstruction['n_paired_shrubs']==9

    # The article states that these two sheets sample the same shrubs, but
    # nectar and seed outcomes are from distinct flowers. An observational
    # cross-stage association does not estimate mediation or plant fitness.
    by_shrub=defaultdict(lambda:{'Robada':[],'No dañada':[]})
    for plant,flower,status,vol,sug in nect:
        if vol is not None:by_shrub[int(plant)][status].append(float(vol))
    if len(by_shrub)!=40:raise ValueError('Nectar shrub grain is no longer 40')
    dN={pid:statistics.mean(v['No dañada'])-statistics.mean(v['Robada'])
        for pid,v in by_shrub.items() if v['No dañada'] and v['Robada']}
    dS={int(r[0]):float(r[3]-r[2]) for r in seeds}
    ids=sorted(dN.keys()&dS.keys())
    if len(ids)!=40:raise ValueError('Incomplete within-shrub cross-stage support')
    x=np.asarray([dN[z] for z in ids]); y=np.asarray([dS[z] for z in ids]);
    sr=spearmanr(x,y)
    # Paired shrub bootstrap: resample whole shrubs, never flowers independently.
    rng=np.random.default_rng(20261117)
    n_boot=10000
    boots=[]
    for _ in range(n_boot):
        idx=rng.integers(0,40,40)
        if len(np.unique(x[idx]))>1 and len(np.unique(y[idx]))>1:
            boots.append(float(spearmanr(x[idx],y[idx]).statistic))
    ci=np.quantile(np.asarray(boots),[.025,.975]).tolist()
    return {'schema':'BALANCE_DESFONTAINIA_SUGAR_SOURCE_STAGE_DISCREPANCY_V1',
            'original_xlsx_md5':ORIGINAL_MD5,'original_author_R_md5':AUTHOR_R_MD5,
            'source_version_concordance':concordance,
            'sugar_filter_discrepancy':{
                'author_code_literal_filter':'filter(nectar_ul >= 5, !is.na(sugar_pct), sugar_pct > 0)',
                'author_code_5ul':{'n_shrubs':original_gate['n_paired_shrubs'],
                                   'paired_t_test_estimable':False},
                'reported_n9_reconstruction':{'n_shrubs':paper_reconstruction['n_paired_shrubs'],
                     'paired_t':paper_reconstruction['paired_t'],
                     'paired_p_two_sided':paper_reconstruction['paired_p_two_sided'],
                     'mean_pierced_sugar_pct':paper_reconstruction['mean_pierced_sugar_pct'],
                     'mean_undamaged_sugar_pct':paper_reconstruction['mean_undamaged_sugar_pct'],
                     'reconstruction_condition':'positive measured sugar and positive flower nectar, WITHOUT published author-code 5-uL restriction'},
                'post_open_threshold_sensitivity':level,
                'sugar_concentration_analysis_validity_for_low_nectar_flower_unverified':True,
                'n9_paper_statistic_recovered_but_original_script_as_written_not_executable':True,
            },
            'unconditional_incidence_survey':prevalence,
            'conditional_nectar_40_shrubs':{
                'paired_shrubs':summary_nectar['n_paired_shrubs'],
                'mean_pierced_ul':summary_nectar['mean_pierced_ul'],
                'mean_undamaged_ul':summary_nectar['mean_undamaged_ul'],
                'conditional_fractional_depletion':1-summary_nectar['pierced_to_undamaged_mean_ratio'],
                'not_random_50_percent_robbed_population_sample':True,
            },
            'cross_stage_shrub_relation':{
                'n_shrubs':len(ids),
                'predictor':'mean undamaged nectar volume minus mean pierced nectar volume, distinct flowers on same shrub',
                'response':'naturally pierced minus protected mature seed count, distinct flowers on same shrub',
                'spearman_rho':float(sr.statistic),
                'spearman_asymptotic_p_two_sided':float(sr.pvalue),
                'shrub_bootstrap95_interval':ci,
                'n_boot':n_boot,
                'n_different_reproductive_experiments_added':0,
            },
            'inference_firewall':{
                'source_published_code_reproduces_sugar_test_as_written':False,
                'n9_sugar_result_validated_under_5_ul_measurement_reliability_gate':False,
                'nectar_mediates_seed_robbery_causally_identified':False,
                'population_wide_mean_nectar_loss_identified':False,
                'robbery_has_no_seed_fitness_effect_established':False,
                'V4_architecture_coders_or_outcomes_opened':False,
                'direct_BALANCE_architecture_margin_measured':False,
            }}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--author-r',type=Path,required=True)
    p.add_argument('--final-r',type=Path)
    p.add_argument('--final-source',type=Path)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    z=analyze(args.source,args.author_r,args.final_r,args.final_source)
    if args.out.exists():raise FileExistsError('Refuse overwrite source-audited readout')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(z,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in z.items() if k not in ('cross_stage_shrub_relation','sugar_filter_discrepancy')},ensure_ascii=False))
    print('Sugar',json.dumps(z['sugar_filter_discrepancy'],ensure_ascii=False))
    print('Cross-stage',json.dumps(z['cross_stage_shrub_relation'],ensure_ascii=False))

if __name__=='__main__':main()
#!/usr/bin/env python3
"""Source-authenticated two-guild fixed-quality scenario and FDP design limit.

This is a plug-in descriptive envelope of published means, NOT a test of
statistical equivalence, causal bee composition, site treatment or BALANCE.
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts.audit_alpinia_dye_visitation_bridge import audit as source_audit


def effective_visit_ratio(b_r:float,a_r:float,b_u:float,a_u:float,alpha:float)->float:
    vals=(b_r,a_r,b_u,a_u,alpha)
    if any(not isinstance(x,(int,float)) or not math.isfinite(x) for x in vals):
        raise ValueError('All visit counts and quality weight must be finite')
    if any(x<0 for x in vals): raise ValueError('Visit counts and quality weight must be nonnegative')
    d=b_u+alpha*a_u
    if d<=0: raise ValueError('Reference expected effective visits must be positive')
    return (b_r+alpha*a_r)/d


def audit(root:Path=ROOT,source_doc:Path|None=None,s1_text:Path|None=None)->dict:
    z=source_audit(root,source_doc,s1_text)
    two=z['main_article']['reported_two_bee_rates_per_hour']
    b_r=two['robbed']['Bombus_eximius']; a_r=two['robbed']['Apis_cerana']
    b_u=two['guarded']['Bombus_eximius']; a_u=two['guarded']['Apis_cerana']
    r=z['s2']['observed_fruit_set']['robbed']['fruit_set_fraction']
    u=z['s2']['observed_fruit_set']['guarded']['fruit_set_fraction']
    if u<=0: raise ValueError('Observed guarded fruit rate must be positive')
    fruit_ratio=r/u
    grid={str(a):effective_visit_ratio(b_r,a_r,b_u,a_u,a) for a in (0.,.25,.5,.75,1.)}
    zero=grid['0.0'];one=grid['1.0']
    if a_r*b_u-a_u*b_r<=0: raise ValueError('Expected increasing quality-weight envelope')
    d=a_r-fruit_ratio*a_u
    if d<=0:raise ValueError('No stable source algebraic root')
    a_match=(fruit_ratio*b_u-b_r)/d
    return {
      'schema':'BALANCE_ALPINIA_PLOT_GATE_FIXED_EFFICIENCY_V1',
      'source_paper_doi':'10.1371/journal.pone.0144585',
      'source_n_dye_mean_cells':z['s1']['source_cells'],
      'source_n_fruit_summary_cells':16,
      'original_source':{
        'methods_source':'Deng et al. 2015 PLOS ONE Materials and Methods, two by Four-Directional Plot design',
        'n_independent_exposure_FDP_per_status':1,
        'approximately_m_between_FDP':300,
        'n_direction_transects_per_FDP':4,
        'n_distance_subplots_per_FDP':60,
        'methods_quote_paraphrase_only':True,
        'bridge_sha256_checked':True,
        'original_s1_csv_sha256':z['s1_csv_sha256'],
        'original_s2_csv_sha256':z['s2_csv_sha256'],
        'floral_robbery_exposure_not_randomized_across_FDP':True,
        'fruit_and_visits_recorded_in_different_periods':True,
      },
      'two_guild_fixed_efficiency_scenario':{
        'quality_assumption':'constant Apis relative per-visit effectiveness 0<=a<=1; Bombus=1',
        'additional_assumptions':[
          'fixed mean guild quality independent of exposure',
          'linear effective visits without intercept or density dependence',
          'equal fruit initiation response across the two confounded plot locations',
          'unobserved visitor guilds and floral damage excluded',
          'published six-day means compared with fruit data from other years'],
        'relative_apis_quality_grid':grid,
        'bombus_only_effective_visit_ratio':zero,
        'all_two_guild_visits_ratio':one,
        'observed_fruit_set_ratio':fruit_ratio,
        'apparent_fruit_ratio_below_plug_in_visit_envelope':fruit_ratio<min(zero,one),
        'negative_quality_required_to_match_fruit_ratio':a_match,
        'ratio_gap_vs_bombus_only':zero-fruit_ratio,
        # These are arithmetic examples, NOT a sampling uncertainty interval.
        'illustrative_one_reported_SE_bombus_only_ratio_band':[
          (b_r-.82)/(b_u+.94),(b_r+.82)/(b_u-.94)],
        'this_is_not_a_confidence_interval':True,
        'no_uncertainty_distribution_for_totals_or_ratios_in_original_sources':True,
      },
      'interpretation_flags':{
        'no_valid_plot_level_treatment_effect_test':True,
        'no_mediation_identification':True,
        'the_descriptive_ratio_gap_falsifies_biological_substitution':False,
        'do_not_treat_source_60_subplots_as_60_treatment_replicates':True,
      },
      'unmeasured_identification_gates':{
        'shared_fitness_architecture_comparison_unmeasured':True,
        'actual_genetic_male_siring_unmeasured':True,
        'source_pollen_transfer_not_matched_to_seed_outcome_flower':True,
        'site_confounding_not_identified':True,
        'bees_separately_sampled_from_seed_years':True,
        'source_21_taxa_and_42_coders_not_changed':True,
        'original_V4_predictors_and_outcomes_not_changed':True,
      },
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--s1-original-doc',type=Path)
    parser.add_argument('--s1-antiword-text',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    z=audit(args.root,args.s1_original_doc,args.s1_antiword_text)
    if args.output.exists():raise FileExistsError('Refuse to overwrite source audit')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(z,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(z['two_guild_fixed_efficiency_scenario'],indent=2))


if __name__=='__main__':main()

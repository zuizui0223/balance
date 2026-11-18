#!/usr/bin/env python3
"""Source-transcribed 2007 visit and stigma-pollen evidence; no fitness effect.

Fumero-Cabán & Meléndez-Ackerman (2007), DOI 10.3732/ajb.94.3.419.
The publication supplies published totals and *approximate* efficiency ratios,
not a re-usable visit-by-patch record or seed/paternity outcomes. Read-only.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/external/pitcairnia_2007/VISITOR_ROLE_SOURCE_V1.csv'
DOI='10.3732/ajb.94.3.419'
# Source's observed study is one plant species, six patches, 60 plants, in 2002.
EXPECTED={
    'Anthracothorax viridis':('legitimate_nectar',111,'detected',1.0),
    'Apis mellifera':('legitimate_pollen',338,'detected',1/3),
    'Coereba flaveola':('primary_robber',664,'detected',0.067),
    'Chlorostilbon maugaeus':('secondary_robber',33,'not_distinguishable_from_control',None),
}

def audit(path:Path=SOURCE)->dict:
    with path.open(newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        expected_fields={'source_doi','source_year','plant_species','visitor_species',
                         'behavioral_route','total_observed_visits','pollen_load_evidence',
                         'relative_per_visit_load_approx_vs_anthracothorax'}
        if set(reader.fieldnames or [])!=expected_fields:
            raise ValueError('Original source table columns changed')
        rows=list(reader)
    if len(rows)!=4 or len({r['visitor_species'] for r in rows})!=4:
        raise ValueError('Original four unique visitor species required')
    result={}
    for row in rows:
        taxon=row['visitor_species']
        if taxon not in EXPECTED or row['source_doi']!=DOI or row['source_year']!='2007' or row['plant_species']!='Pitcairnia angustifolia':
            raise ValueError('Unknown source/plant/visitor in source-transcribed table')
        route,n,pollen,rel=EXPECTED[taxon]
        try:
            count=int(row['total_observed_visits'])
        except (TypeError,ValueError) as e:
            raise ValueError('Visit total is not an integer') from e
        approx=(float(row['relative_per_visit_load_approx_vs_anthracothorax'])
                if row['relative_per_visit_load_approx_vs_anthracothorax'] else None)
        if row['behavioral_route']!=route or count!=n or row['pollen_load_evidence']!=pollen or (
            (approx is None)!=(rel is None) or (rel is not None and abs(approx-rel)>1e-12)
        ):
            raise ValueError('Original source role, count or reported approximate efficiency changed: '+taxon)
        result[taxon]={'behavioral_route':route,'observed_visits':count,
                       'reported_stigma_pollen_evidence':pollen,
                       'approx_relative_pollen_load_per_single_visit':approx}
    total=sum(row['observed_visits'] for row in result.values())
    if total!=1146: raise ValueError('Original observed flower visit denominator changed')
    robber=sum(q['observed_visits'] for q in result.values() if 'robber' in q['behavioral_route'])
    robber_with_detected=sum(q['observed_visits'] for q in result.values()
                             if 'robber' in q['behavioral_route'] and q['reported_stigma_pollen_evidence']=='detected')
    return {
      'schema':'BALANCE_PITCAIRNIA_2007_BEHAVIOR_STIGMA_EVIDENCE_V1',
      'source':{'doi':DOI,'publisher_url':'https://bsapubs.onlinelibrary.wiley.com/doi/10.3732/ajb.94.3.419',
                'primary_study_count':1,'plant_species_count':1,'study_year':2002,
                'patches_observed':6,'plants_observed':60,'observation_hours':90,
                'single_visit_stigmas_per_visitor_taxon':20,'unvisited_controls':20,
                'source_status':'human_transcribed_publisher_full_text; no independent byte-hash validation'},
      'visitor_species':result,
      'source_descriptive_visit_counts':{
          'total_visits':total,'robber_behavior_visits':robber,
          'robber_behavior_visits_fraction':robber/total,
          'robber_species_with_source_reported_stigma_pollen_visits':robber_with_detected,
          'robber_species_with_source_reported_stigma_pollen_fraction_of_all_visits':robber_with_detected/total,
      },
      'interpretation_guards':{
          'behavioral_robbing_does_not_automatically_mean_absent_stigma_pollen':True,
          'source_detected_some_stigma_pollen_not_each_of_664_visits_proven_successful':True,
          'control_indistinguishable_not_exact_zero':True,
          'published_approximate_efficiency_not_exact_experimental_estimate':True,
          'raw_visits_times_efficiency_not_equivalent_to_patch_level_effectiveness':True,
          'pollen_on_stigma_not_outcross_paternity_or_viable_seed_yield':True,
          '2007_and_2013_same_author_plant_not_independent_species_replications':True,
          'study_selected_for_mechanistic_audit_not_species_first_prevalence_denominator':True,
          'no_direct_BALANCE_L_K_Phi_or_optimized_worldlines':True,
      },
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=SOURCE)
    parser.add_argument('--out',type=Path)
    a=parser.parse_args()
    r=audit(a.source)
    encoded=json.dumps(r,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
    if a.out:
        if a.out.exists():raise FileExistsError('Readout exists: cannot overwrite')
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(encoded)
    else:print(encoded,end='')
if __name__=='__main__':main()

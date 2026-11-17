#!/usr/bin/env python3
"""Source-locked primary-paper audit: Leal 2025 sample 178 is VOC scent, not nectar.

This uses a 2019 original JATS Table 2 witness, two independent published
2025 meta source workbooks and NO new biological causal or phylogenetic fit.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,statistics,sys,xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts.audit_leal_sd_taxon_provenance import load_original_leal,LZIP
from scripts.audit_larceny_meta_stage_pairability import source_rows,SOURCE_SHA256

SOURCE_JATS_SHA256='73faada0de428ccb4f83420d4e545e77e8cf9768c89f1480d60158aff28e7c55'
PAPER_DOI='10.1371/journal.pone.0225252'
SOUZA_LEAL_SAMPLE='178'
SOUZA_ZHONG_EFFECT=508
MILET_ZHONG_EFFECT=510

def paper_table2(source:Path)->dict:
    raw=Path(source).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_JATS_SHA256:
        raise ValueError('Exact original Souza 2019 JATS SHA256 mismatch')
    root=ET.fromstring(raw)
    ids=[(i.text or '').strip() for i in root.iter('article-id') if i.attrib.get('pub-id-type')=='doi']
    if PAPER_DOI not in ids:raise ValueError('Original paper DOI mismatch')
    tab=[x for x in root.iter('table-wrap') if x.attrib.get('id')=='pone.0225252.t002']
    if len(tab)!=1:raise ValueError('Original Table 2 not uniquely identified')
    t=tab[0]
    caption=' '.join(' '.join(t.find('caption').itertext()).split())
    if ('mean of total scent emitted' not in caption or 'Jacaranda caroba' not in caption):
        raise ValueError('Published Table 2 scent response or species changed')
    trs=list(t.iter('tr'))
    if len(trs)<4:raise ValueError('Original table structure changed')
    head=[' '.join(''.join(x.itertext()).split()) for x in trs[0]]
    subhead=[' '.join(''.join(x.itertext()).split()) for x in trs[1]]
    cells=[' '.join(''.join(x.itertext()).split()) for x in trs[3]]
    if ('Control flower' not in head[3] or 'Experimentally damaged flower' not in head[4]):
        raise ValueError('Published treatment group headings changed')
    if 'with nectar(n = 2)' not in subhead[2] or 'with nectar(n = 3)' not in subhead[4]:
        raise ValueError('Published control/damaged original nectar-presence or N changed')
    if 'scent emitted per flower (ng/h' not in cells[0]:
        raise ValueError('Original reported outcome is NOT scent')
    import re
    def pair(x):
        match=re.fullmatch(r'(\d+\.\d+)\s*±\s*(\d+\.\d+)',x)
        if not match:raise ValueError('Original scent mean/SD cell changed: '+x)
        return [float(match.group(1)),float(match.group(2))]
    control=pair(cells[3]);damaged=pair(cells[5])
    if control!=[29.90,22.48] or damaged!=[58.24,11.39]:
        raise ValueError('Printed original Table 2 scent values changed')
    return {
        'source_doi':PAPER_DOI,'JATS_sha256':SOURCE_JATS_SHA256,
        'paper_species':'Jacaranda_caroba',
        'outcome_label':'Mean total floral scent emitted per flower',
        'outcome_units':'ng/hour, NOT nectar volume in microliters',
        'comparison_intervention':'experimentally made corolla slits; both cells nectar present',
        'control_intact_with_nectar':{'n':2,'mean_ng_per_hour':control[0],'SD_ng_per_hour':control[1]},
        'experimentally_damaged_with_nectar':{'n':3,'mean_ng_per_hour':damaged[0],'SD_ng_per_hour':damaged[1]},
        'mean_table2_values_not_nectar_means':True,
    }

def calc_rom(m1,s1,n1,m0,s0,n0):
    return math.log(m1/m0),(s1/m1)**2/n1+(s0/m0)**2/n0

def _group_summary(rows):
    if not rows:raise ValueError('Empty source group')
    effects=[float(x['yi']) for x in rows]
    vars=[float(x['vi']) for x in rows]
    studies=defaultdict(list)
    for x in rows:studies[x['study']].append(float(x['yi']))
    return {'n_effects':len(rows),'n_primary_studies':len(studies),
      'unweighted_mean_archived_lnRR':statistics.mean(effects),
      'inverse_archived_vi_weighted_lnRR':sum(y/v for y,v in zip(effects,vars))/sum(1/v for v in vars),
      'equal_primary_study_mean_archived_lnRR':statistics.mean(
          statistics.mean(ys) for ys in studies.values()),
      'sampling_uncertainty_and_phylogeny_not_modeled':True}

def audit(leal_zip:Path,zhong_xlsx:Path,original_jats:Path)->dict:
    t=paper_table2(original_jats)
    leal=load_original_leal(leal_zip)
    zhong=source_rows(zhong_xlsx)
    original=[r for r in leal if r['sample']==SOUZA_LEAL_SAMPLE]
    if len(original)!=1:raise ValueError('Leal sample 178 not unique')
    r=original[0]
    if (r['study']!='Souzaetal_2019' or r['sp_plant']!='Jacaranda_rugosa' or
        r['Type_of_metric']!='nectar' or r['Larcenist_type']!='Robbers'):
        raise ValueError('Leal source record 178 context has changed')
    damaged=t['experimentally_damaged_with_nectar']
    control=t['control_intact_with_nectar']
    cm,cs,cn=control['mean_ng_per_hour'],control['SD_ng_per_hour'],control['n']
    dm,ds,dn=damaged['mean_ng_per_hour'],damaged['SD_ng_per_hour'],damaged['n']
    # Source mean / n labels are reverse to the actual scent experimental contrast.
    if [float(r[k]) for k in ('mean_larcenist','mean_control','n_larcenist','n_control')]!=[cm,dm,cn,dn]:
        raise ValueError('Leal sample 178 does not match original table 2 control/damaged means')
    if [float(r[k]) for k in ('sd_larcenist','sd_control')]!=[ds,cs]:
        raise ValueError('Leal sample 178 SD columns changed; expected opposite source groups')
    paper_y,paper_v=calc_rom(dm,ds,dn,cm,cs,cn)
    archive_y,archive_v=float(r['yi']),float(r['vi'])
    if abs(archive_y-paper_y)>1e-8 or abs(archive_v-paper_v)>1e-8:
        raise ValueError('Leal saved yi/vi do not reconstruct primary scent treatment values')
    archived_column_y,archived_column_v=calc_rom(cm,ds,cn,dm,cs,dn)
    original_y,original_v=calc_rom(cm,cs,cn,dm,ds,dn)
    if not abs(archived_column_y+archive_y)<1e-8:
        raise ValueError('Source orientation reversal not identified')
    z_s=[x for x in zhong if x['ID']==SOUZA_ZHONG_EFFECT]
    z_r=[x for x in zhong if x['ID']==MILET_ZHONG_EFFECT]
    if (len(z_s)!=1 or len(z_r)!=1 or z_s[0]['ref-ID']!=136 or
        z_s[0]['species']!='Jacaranda_caroba' or z_s[0]['sub_response_variable']!='nectar volume' or
        z_r[0]['species']!='Jacaranda_rugosa' or z_r[0]['ref-ID']!=42):
        raise ValueError('Cross-meta original publication labels changed')
    # Separate 2019 original nectar experiment and scent Table 2.
    if 'robbed' not in str(z_s[0]['title']).lower():
        raise ValueError('Matching primary 2019 original paper title differs')
    s=[x for x in leal if x['Type_of_metric']=='nectar' and x['Larcenist_type']=='Robbers']
    if len(s)!=39 or len({x['study'] for x in s})!=23:raise ValueError('Original Leal robber nectar population changed')
    s_no=[x for x in s if x['sample']!='178']
    if len(s_no)!=38:raise ValueError('Source exclusion failed')
    return {
      'schema':'BALANCE_LEAL_SOUZA_2019_PRIMARY_SCENT_RECLASSIFICATION_GATE_V1',
      'original_Leal_meta_source_sha256':LZIP,
      'original_Zhong_meta_source_sha256':SOURCE_SHA256,
      'source_primary_PLOS_fullTextJATS':t,
      'leal_sample_178':{
          'sample_id':178,'original_study_label':r['study'],
          'archived_species':r['sp_plant'],'archived_metric':r['Type_of_metric'],
          'actual_original_species':t['paper_species'],'actual_original_metric':'floral_scent_ng_per_hour',
          'original_comparison_not_nectar_removed_vs_intact':True,
          'archived_sd_larcenist_is_original_damaged_SD':True,
          'archived_sd_control_is_original_intact_SD':True,
          'archived_mean_larcenist_is_original_intact_mean':True,
          'archived_mean_control_is_original_damaged_mean':True,
          'archived_yi':archive_y,'scent_damaged_over_intact_lnRR':paper_y,
          'archived_vi':archive_v,'scent_damaged_over_intact_ROM_variance':paper_v,
          'naive_archived_column_lnRR':archived_column_y,
          'naive_archived_column_variance':archived_column_v,
          'original_aligned_intact_over_damaged_lnRR':original_y,
          'original_aligned_intact_over_damaged_variance':original_v,
          'original_damaged_and_intact_both_with_nectar':True,
          'incorrect_inference_if_treated_as_resource_nectar':True,
      },
      'zhong_primary_paper_link':{
          '2019_souza_original_paper_effect_ID':508,
          '2019_souza_original_paper_ref_ID':136,
          '2019_souza_species':'Jacaranda_caroba',
          '2019_souza_outcome':'nectar volume',
          '2019_souza_original_nectar_effect_lnRR':z_s[0]['yi'],
          'actual_same_2019_primary_paper_but_DIFFERENT_outcome_from_Leal_178':True,
          '2007_milet_pinheiro_different_paper_effect_ID':510,
          '2007_milet_pinheiro_ref_ID':42,
          '2007_milet_pinheiro_species':'Jacaranda_rugosa',
          'not_same_primary_study_as_2019_souza':True,
          'previous_47_candidate_paper_species_linkages_plus_one_Souza_candidate':48,
          'new_48_not_DOI_contrast_confirmed':True,
      },
      'descriptive_existing_Leal_Robber_nectar_group':{
          'archived_treat_scent_as_nectar':_group_summary(s),
          'remove_primary_scent_comparison':_group_summary(s_no),
          'not_a_phylogenetic_multilevel_refit':True,
          'removed_effect_is_NOT_explicitly_reclassified_in_2025_original_data':True,
      },
      'claim_guards':{
          'same_2019_original_has_actual_robbed_nectar_study_but_leal_178_is_scent':True,
          'published_original_data_rows_not_mutated':True,
          'no_2025_author_model_refix_or_p_value':True,
          '2019_table2_median_nectar_not_used_to_invent_nectar_mean':True,
          '2019_scent_sample_size_not_maternal_plant_population':True,
          'one_source_record_not_an_independent_biological_replication':True,
          'no_structural_BALANCE_K_Phi_or_architecture_fitness_measure':True,
          'original_U6_21_taxa_42_coders_V4_and_SLK_unmodified':True,
      },
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--leal-zip',required=True,type=Path)
    p.add_argument('--zhong-xlsx',required=True,type=Path)
    p.add_argument('--source-jats',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError('Refuse overwrite original source audit')
    a=audit(args.leal_zip,args.zhong_xlsx,args.source_jats)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(a,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print(json.dumps({'publication':a['source_primary_PLOS_fullTextJATS']['source_doi'],
                       'leal_record':a['leal_sample_178'],
                       'cross_meta':a['zhong_primary_paper_link'],
                       'sensitivity':a['descriptive_existing_Leal_Robber_nectar_group']},
                     indent=2,ensure_ascii=False))

if __name__=='__main__': main()

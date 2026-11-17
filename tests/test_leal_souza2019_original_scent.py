"""Primary JATS table witness for Souza 2019 vs Leal 2025 sample 178.

No automatic mutation of meta archives or refitting of the phylogenetic model.
"""
import importlib.util,os,math
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/audit_leal_souza2019_original_scent.py"
def module():
    spec=importlib.util.spec_from_file_location("souza2019_scent",SCRIPT)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
@pytest.fixture(scope='module')
def actual():
    env=[os.getenv(s) for s in ('BALANCE_LEAL_ORIGINAL_ZIP','BALANCE_ZHONG_ORIGINAL_XLSX','BALANCE_SOUZA2019_JATS')]
    if not all(env):pytest.skip('Dedicated workflow supplies 3 independently verified original sources')
    return module().audit(*(Path(x) for x in env))
def test_published_primary_article_scent_not_nectar(actual):
    p=actual['source_primary_PLOS_fullTextJATS']
    assert p['source_doi']=='10.1371/journal.pone.0225252'
    assert p['paper_species']=='Jacaranda_caroba'
    assert p['comparison_intervention']=='experimentally made corolla slits; both cells nectar present'
    assert p['outcome_units']=='ng/hour, NOT nectar volume in microliters'
    assert p['control_intact_with_nectar']=={'n':2,'mean_ng_per_hour':29.90,'SD_ng_per_hour':22.48}
    assert p['experimentally_damaged_with_nectar']=={'n':3,'mean_ng_per_hour':58.24,'SD_ng_per_hour':11.39}
def test_leal_sample178_has_both_wrong_endpoint_and_species(actual):
    x=actual['leal_sample_178']
    assert x['sample_id']==178
    assert x['archived_species']=='Jacaranda_rugosa'
    assert x['actual_original_species']=='Jacaranda_caroba'
    assert x['archived_metric']=='nectar'
    assert x['actual_original_metric']=='floral_scent_ng_per_hour'
    assert x['original_damaged_and_intact_both_with_nectar'] is True
    assert x['incorrect_inference_if_treated_as_resource_nectar'] is True
def test_saved_y_and_variance_match_original_scent_damaged_vs_control(actual):
    x=actual['leal_sample_178']
    assert x['archived_yi']==pytest.approx(math.log(58.24/29.9),abs=1e-9)
    var=(11.39/58.24)**2/3+(22.48/29.90)**2/2
    assert x['archived_vi']==pytest.approx(var,abs=1e-9)
    assert x['scent_damaged_over_intact_ROM_variance']==pytest.approx(var,abs=1e-10)
    assert x['naive_archived_column_lnRR']==pytest.approx(-x['archived_yi'],abs=1e-9)
    assert all(x[k] for k in (
      'archived_sd_larcenist_is_original_damaged_SD',
      'archived_sd_control_is_original_intact_SD',
      'archived_mean_larcenist_is_original_intact_mean',
      'archived_mean_control_is_original_damaged_mean'))
def test_2019_same_source_and_2007_different_source(actual):
    x=actual['zhong_primary_paper_link']
    assert x['2019_souza_original_paper_effect_ID']==508
    assert x['2019_souza_original_paper_ref_ID']==136
    assert x['2019_souza_species']=='Jacaranda_caroba'
    assert x['2019_souza_outcome']=='nectar volume'
    assert x['2007_milet_pinheiro_different_paper_effect_ID']==510
    assert x['2007_milet_pinheiro_ref_ID']==42
    assert x['2007_milet_pinheiro_species']=='Jacaranda_rugosa'
    assert x['not_same_primary_study_as_2019_souza'] is True
    assert x['previous_47_candidate_paper_species_linkages_plus_one_Souza_candidate']==48
def test_descriptive_sample178_exclusion_not_phylo_meta_refit(actual):
    a=actual['descriptive_existing_Leal_Robber_nectar_group']
    full=a['archived_treat_scent_as_nectar']
    clean=a['remove_primary_scent_comparison']
    assert full['n_effects']==39 and clean['n_effects']==38
    assert full['n_primary_studies']==23 and clean['n_primary_studies']==22
    assert full['unweighted_mean_archived_lnRR']==pytest.approx(-.68951182218,abs=2e-9)
    assert clean['unweighted_mean_archived_lnRR']==pytest.approx(-.72520197337,abs=2e-9)
    assert full['inverse_archived_vi_weighted_lnRR']==pytest.approx(-.17987794028,abs=2e-9)
    assert clean['inverse_archived_vi_weighted_lnRR']==pytest.approx(-.18028853509,abs=2e-9)
    assert a['not_a_phylogenetic_multilevel_refit'] is True
def test_untrusted_original_JATS_fails_closed(tmp_path):
    m=module()
    bad=tmp_path/'non-source.xml'
    bad.write_text('<article>not original</article>')
    with pytest.raises(ValueError,match='SHA256 mismatch'):
        m.paper_table2(bad)
def test_immutable_source_eligibility_and_algebra():
    m=module()
    a,v=m.calc_rom(58.24,11.39,3,29.90,22.48,2)
    assert a==pytest.approx(.6667139234917898,abs=1e-12)
    assert v==pytest.approx(.2953805059414724,abs=1e-12)
    assert m.SOURCE_JATS_SHA256=='73faada0de428ccb4f83420d4e545e77e8cf9768c89f1480d60158aff28e7c55'
    assert m.SOUZA_LEAL_SAMPLE=='178'
def test_source_claim_guards(actual):
    assert all(actual['claim_guards'].values())
    assert actual['schema'].endswith('_V1')

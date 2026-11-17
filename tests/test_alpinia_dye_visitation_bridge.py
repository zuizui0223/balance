"""Source-backed tests for S1 dye, published Figure 6, and original S2 fruit stages."""
import importlib.util
import os
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/audit_alpinia_dye_visitation_bridge.py'
SOURCE_TEXT=Path(os.getenv('BALANCE_ALPINIA_S1_TEXT',ROOT/'source/S1_TEXT.txt'))
SOURCE_DOC=Path(os.getenv('BALANCE_ALPINIA_S1_DOC',ROOT/'source/pone.0144585.s001.doc'))

def module():
    spec=importlib.util.spec_from_file_location('alpinia_stage_bridge',SCRIPT)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def source_paths():
    if SOURCE_TEXT.exists() and SOURCE_DOC.exists():
        return SOURCE_DOC,SOURCE_TEXT
    return None,None

def test_all_near_distance_bins_reduced_in_original_32_cell_source():
    m=module()
    doc,txt=source_paths()
    z=m.audit(ROOT,source_doc=doc,s1_text=txt)
    assert z['s1']['source_cells']==32
    assert z['s1']['near_0_to_14_bins']=={'n_comparisons':16,'lower_in_robbed':16,'higher_in_robbed':0,'tied':0}
    assert z['s1']['full_distance_bins']=={'robbed_lower':25,'robbed_higher':2,'same':5}
    assert all(row['near_robbed_lower']==4 for row in z['s1']['by_direction'])

def test_visitor_two_group_means_and_bombus_fraction():
    m=module()
    z=m.audit(ROOT)
    d=z['main_article']['reported_two_bee_rates_per_hour']
    assert d['robbed']['Bombus_eximius']==6.15
    assert d['guarded']['Bombus_eximius']==7.86
    assert d['robbed']['Apis_cerana']==3.06
    assert d['guarded']['Apis_cerana']==1.33
    assert d['robbed']['two_guild_sum']==pytest.approx(9.21)
    assert d['guarded']['two_guild_sum']==pytest.approx(9.19)
    assert d['robbed']['Bombus_fraction_within_two']==pytest.approx(6.15/9.21)
    assert d['guarded']['Bombus_fraction_within_two']==pytest.approx(7.86/9.19)
    assert z['main_article']['derived_two_guild_Bombus_share_difference_percentage_points']==pytest.approx(-18.7525032520)

def test_fruit_and_sampled_seed_stage_not_conflated():
    z=module().audit(ROOT)
    assert z['s2']['observed_fruit_set']['robbed']['flower_n']==17231
    assert z['s2']['observed_fruit_set']['robbed']['fruit_n']==5174
    assert z['s2']['observed_fruit_set']['guarded']['flower_n']==16845
    assert z['s2']['observed_fruit_set']['guarded']['fruit_n']==7001
    assert z['s2']['fruit_set_negative_year_direction_strata']==8
    assert z['s2']['sampled_seed_count_effect']=={'negative_strata':4,'positive_strata':3,'tied_strata':1}

def test_stages_remain_noncausal_and_not_independent_programmes():
    z=module().audit(ROOT)
    assert z['source_population_programmes_added']==0
    assert z['interpretation']=='source_only_within_study_noncausal'
    assert all(v is False for v in z['claim_gates'].values())
    assert not z['main_article']['two_guild_sum_statistically_equivalent']

def test_true_original_s1_doc_matches_32_cell_csv_and_rejects_tampering(tmp_path):
    if not SOURCE_DOC.exists() or not SOURCE_TEXT.exists():
        pytest.skip('Source replay workflow supplies official PLOS S1 DOC and antiword text')
    m=module()
    m.audit(ROOT,source_doc=SOURCE_DOC,s1_text=SOURCE_TEXT)
    changed=tmp_path/'changed.doc'
    changed.write_bytes(SOURCE_DOC.read_bytes()+b'X')
    with pytest.raises(ValueError,match='S1 DOC'):
        m.audit(ROOT,source_doc=changed,s1_text=SOURCE_TEXT)
    altered=tmp_path/'altered.txt'
    altered.write_text(SOURCE_TEXT.read_text(encoding='utf-8').replace('0.71','0.79',1),encoding='utf-8')
    with pytest.raises(ValueError,match='S1 source antiword'):
        m.audit(ROOT,source_doc=SOURCE_DOC,s1_text=altered)

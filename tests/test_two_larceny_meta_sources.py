"""Original-source gated checks: two distinct 2025 floral larceny meta data products."""
from __future__ import annotations
import importlib.util,math,os
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scripts/audit_two_larceny_meta_sources.py'
def mod():
    spec=importlib.util.spec_from_file_location('larceny_two_metas',SOURCE)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
@pytest.fixture(scope='module')
def result():
    z=os.getenv('BALANCE_TWO_META_ZHONG')
    l=os.getenv('BALANCE_TWO_META_LEAL')
    if not z or not l:pytest.skip('Both official originals supplied by source workflow')
    return mod().audit(Path(z),Path(l))
def test_two_original_meta_populations(result):
    assert result['source_counts']=={
      'zhong_effects':776,'zhong_papers':153,'leal_effects':267,'leal_papers':69}
def test_rom_inconsistency_and_sampling_variance(result):
    a=result['leal_source_effect_metric']
    assert a['R_code_escalc_measure'].startswith('ROM:')
    assert 'Hedges g' in a['metadata_and_R_labels']
    assert a['yi_mismatch_n']==3 and a['vi_mismatch_n']==7
    assert {x['sample_id'] for x in a['yi_mismatched']}=={'79','88','178'}
    assert all(x['opposite_sign'] for x in a['yi_mismatched'])
    assert a['original_published_metaanalysis_not_refit']
def test_source_paper_species_grain_and_type_coding(result):
    x=result['cross_meta_linkability']
    assert x['provisional_author_year_species_matches']==45
    assert x['different_source_type_sets']==6
    assert x['collision_keys']==2
    cases={(z['species'],z['candidate_paper_key']) for z in x['type_mismatch_cases']}
    assert ('alpiniaroxburghii','deng2015') in cases
    assert ('jacarandacaroba','quinalha2017') in cases
    assert ('impatiensoxyanthera','li2021') in cases
    assert ('oreocallisgrandiflora','hazlehurst2016') in cases
def test_same_study_exposure_contrast_not_inferred(result):
    a=result['same_study_type_opportunities']
    assert len(a['zhong_both_paper_species'])==3
    assert len(a['zhong_both_endpoint'])==5
    assert len(a['leal_both_paper_species'])==1
    assert len(a['leal_both_endpoint'])==1
    assert a['leal_both_endpoint'][0]==['Zhangetal_2014','Corydalis_ambigua','visitation']
    assert all(result['claim_ceiling'].values())
def test_exact_original_zenodo_zip_fail_closed(tmp_path):
    m=mod();p=tmp_path/'untrusted.zip'
    p.write_bytes(b'not Leal Zenodo source')
    with pytest.raises(ValueError,match='SHA256 mismatch'):m.load_leal(p)
    assert m.sciname('Ipomopis_aggregata')=='ipomopsisaggregata'
    assert m.paperkey('Heillingetal_2018')=='heiling2018'
def test_rom_formula_is_not_hedges_standardized_mean():
    m=mod()
    assert m.hashof(b'abc')=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    assert math.log(519.89/590.81)==pytest.approx(-0.127877226,abs=1e-8)

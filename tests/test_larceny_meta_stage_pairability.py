"""Source-gated regression tests for 153-publication, 120-species, 776-effect stage audit."""
import importlib.util
import os
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
CODE=ROOT/'scripts/audit_larceny_meta_stage_pairability.py'

def module():
    spec=importlib.util.spec_from_file_location('larceny_meta_stage',CODE)
    x=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(x)
    return x

@pytest.fixture(scope='module')
def original():
    p=os.getenv('BALANCE_LARCENY_2025_ORIGINAL')
    if not p:pytest.skip('Original Figshare share ZIP is acquired in dedicated source workflow')
    return module().source_rows(Path(p))

def test_original_776_effects_and_153_sources(original):
    assert len(original)==776
    assert original[0]['ID']==1 and original[-1]['ID']==776
    assert len({r['ref-ID'] for r in original})==153
    assert len({r['species'] for r in original})==120

def test_real_stage_co_reporting(original):
    z=module().audit(original)
    assert z['population']['paper_species_groups']==170
    c=z['co_reported_stage_coverage']
    assert c['nectar_visits_pollen_fruit_seed']['paper_species_groups']==2
    assert c['visits_pollen_fruit_seed']['paper_species_groups']==4
    assert c['pollen_fruit_seed']['paper_species_groups']==8
    assert c['visits_fruit_seed']['paper_species_groups']==10
    assert c['pollen_fruit']['paper_species_groups']==13
    assert c['fruit_seed']['paper_species_groups']==37
    assert c['fruit_seed']['distinct_papers']==36
    assert c['nectar_visits_pollen_fruit_seed']['source_keys']==[
      {'ref_ID':29,'species':'Corydalis_caseana'},
      {'ref_ID':101,'species':'Gentiana_straminea'}]

def test_exact_one_to_one_screen_does_not_assume_mediation(original):
    z=module().audit(original)
    x=z['fruit_seed_candidate_scope']
    assert x['paper_species_upper_bound']==37
    assert x['shared_experiment_level_groups']==35
    assert x['uniquely_screened_groups']==17
    assert x['uniquely_screened_papers']==16
    assert (x['delta_positive'],x['delta_negative'],x['delta_zero'])==(8,9,0)
    assert x['descriptive_mean_seed_minus_fruit_lnRR']==pytest.approx(-.03640561665549)
    assert x['descriptive_median_seed_minus_fruit_lnRR']==pytest.approx(-.01184119562060)
    assert all(q['within_experiment_contrast_verified'] is False for q in z['strict_one_to_one_candidates'])
    assert all(q['shared_response_sampling_covariance_known'] is False for q in z['strict_one_to_one_candidates'])
    assert all(z['claim_ceiling'].values())

def test_source_bytes_rejected_if_modified(original,tmp_path):
    m=module()
    source=Path(os.environ['BALANCE_LARCENY_2025_ORIGINAL'])
    raw=source.read_bytes()
    bad=tmp_path/'modified.xlsx'
    bad.write_bytes(raw[:len(raw)//2]+bytes([raw[len(raw)//2]^1])+raw[len(raw)//2+1:])
    with pytest.raises(ValueError,match='SHA256 mismatch'):
        m.source_rows(bad)

def test_changed_variance_and_effect_identity_rejected(original):
    m=module()
    d=[dict(r) for r in original]
    d[8]['vi']=0
    with pytest.raises(ValueError,match='sampling variance'):
        m.validate(d)
    d=[dict(r) for r in original]
    d[8]['ID']=999
    with pytest.raises(ValueError,match='ID sequence'):
        m.validate(d)

def test_differs_if_one_seed_endpoint_not_same_approach(original):
    m=module()
    z=m.audit(original)
    keep=z['strict_one_to_one_candidates'][0]['seed_record']
    altered=[dict(r) for r in original]
    next(r for r in altered if r['ID']==keep)['experiment_level']='UNMATCHED'
    x=m.audit(altered)['fruit_seed_candidate_scope']
    assert x['uniquely_screened_groups']==16
    assert x['shared_experiment_level_groups']==34

def test_no_external_source_no_false_paper_results():
    m=module()
    assert m.SOURCE_SHA256=='6554409f22b09156ee1c2a35ee2547eb5ae28c4a25934b9c639d8a19ea7fe9b4'
    assert set(m.STAGE_ROUTES['nectar_visits_pollen_fruit_seed'])=={
        'nectar volume','visitation rate','pollen deposition','fruit set','seed set'}

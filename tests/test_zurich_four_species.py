"""Source-locked exploratory 4-taxon, 24-garden audit tests."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'analyze_zurich_four_species.py'


def module():
    spec = importlib.util.spec_from_file_location('zurich4', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def original():
    path = os.environ.get('BALANCE_ZURICH_ORIGINAL_ARCHIVE')
    if not path:
        pytest.skip('Official source archive only provided to source-replay workflow')
    p = Path(path)
    assert p.is_file(), 'Required original archive was not materialized'
    return p


def test_official_archive_sha_tamper_fails(tmp_path):
    m=module()
    path=original()
    changed=tmp_path/'changed.zip'
    changed.write_bytes(path.read_bytes()+b'X')
    with pytest.raises(ValueError,match='checksum'):
        m.check_source(changed)


def test_original_survey_and_matrix_do_not_treat_unobserved_zeros_as_visits():
    m=module();z=m.check_source(original())
    sample,visit=m.source_frame(z)
    assert len(sample)==670 and len({k[0] for k in sample})==24
    assert len(visit)==5794
    assert sum(c=='robber' for k,s,c in visit)==256
    receipt=m.independent_matrix_receipt(z,sample)
    assert receipt['matrix_rows']==21120
    assert receipt['matrix_survey_matched_rows']==2680
    assert receipt['matrix_structural_zero_rows']==19919
    assert receipt['matrix_unsurveyed_positive_rows']==6
    assert receipt['matrix_unsurveyed_visit_count']==27


def test_garden_level_replication_does_not_count_rows_as_independent_species():
    m=module();z=m.check_source(original())
    survey,vis=m.source_frame(z)
    outcomes=m.site_outcomes(z)
    assert len(outcomes)==96
    garden,qual=m.assembled(survey,vis,outcomes)
    assert len(garden)==96
    assert sum(r['n_visits'] for r in garden)==5767
    assert len({r['garden'] for r in garden})==24
    assert len({r['species'] for r in garden})==4
    assert qual['unmatched_individual_visits']==27
    assert all(r['n_independent_plants']>=1 for r in garden)


def test_four_species_cv_and_sensitivity_are_recomputed_from_exact_source():
    pytest.importorskip('numpy')
    m=module();data=m.audit(original())
    delta={'Carrot':.19395301692225,'Radish':-.00102581994736,
           'Sainfoin':-.05073513781363,'Comfrey':.06415406270142}
    flower={'Carrot':.18070125332760,'Radish':-.00772383443096,
            'Sainfoin':.01236207741671,'Comfrey':.00233539798222}
    for sp in m.SPECIES:
        item=data['primary'][sp]
        assert item['n_gardens']==24
        assert item['rmse_change_fraction']==pytest.approx(delta[sp],abs=1e-10)
        assert data['sensitivity_flower_positive_samples'][sp]['rmse_change_fraction']==pytest.approx(flower[sp],abs=1e-10)
        assert item['models']['total_only']['rmse']>0
        assert item['models']['total_plus_composition']['rmse']>0
    assert data['primary']['Carrot']['n_gardens_better_by_squared_error']==11
    assert data['sensitivity_drop_each_garden']['Carrot']['positive']==24
    assert data['sensitivity_drop_each_garden']['Sainfoin']['positive']==0
    assert data['primary']['Comfrey']['additional_shares']==['robber']
    assert data['independent_sampling_gardens']==24
    assert data['independent_biological_taxa']==4


def test_no_source_predictor_support_cannot_be_fabricated():
    pytest.importorskip('numpy')
    m=module();z=m.check_source(original())
    sample,vis=m.source_frame(z)
    sites,_=m.assembled(sample,vis,m.site_outcomes(z))
    for row in sites:
        if row['species']=='Comfrey':
            row['counts']['robber']=0
            row['n_visits']=row['counts']['other_bee']
            row['rate']=row['n_visits']/row['observer_hours']
    results=m.fit_site_models(sites)
    assert results['Comfrey']['status']=='NOT_ESTIMABLE_FEWER_THAN_TWO_VISITOR_CATEGORIES'


def test_formula_and_size_contracts_exist_without_original_download():
    m=module()
    assert m.SOURCE_DOI=='10.16904/envidat.676'
    assert len(m.SOURCE_SHA256)==64
    assert len(m.SPECIES)==4
    assert set(m.GROUPS)=={'apis','other_bee','other_nonbee','robber'}

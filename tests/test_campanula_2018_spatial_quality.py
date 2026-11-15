"""Source-hash-gated within-species geographic transport and fixed visitor-quality index."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/audit_campanula_2018_spatial_quality.py'


def module():
    spec = importlib.util.spec_from_file_location('campanula_spatial_quality', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_exact_original_single_visit_seed_counts_and_site_asymmetry():
    m=module()
    rows=m.load_single_visits()
    assert len(rows)==118
    assert m.seed_weights(rows)==pytest.approx([11.516129032258064,7.2407407407407405,3.0303030303030303])
    assert m.seed_counts(rows)=={'B':31,'M':54,'H':33}
    assert m.site_counts(rows)['B']['FV']==26
    assert m.site_counts(rows)['H']['K']==32
    assert len({row['FlwID'] for row in rows})==118


def test_modified_source_seedset_rejected(tmp_path):
    m=module()
    bad=tmp_path/'changed.csv'
    raw=m.SEED_FILE.read_bytes()
    assert b',MN,12' in raw
    bad.write_bytes(raw.replace(b',MN,12', b',MN,99',1))
    with pytest.raises(ValueError,match='SHA256'):
        m.load_single_visits(bad)


def test_groupwise_crossvalidation_no_training_leakage():
    np=pytest.importorskip('numpy')
    m=module()
    X=np.array([[1,0],[1,1],[1,2],[1,3],[1,4],[1,5]],float)
    y=np.array([2,4,6,7,10,12],float)
    labels=['a','a','b','b','c','c']
    groups=m.make_group_splits(labels)
    preds,n_train=m.cv_predict(X,y,groups)
    for j, grp in enumerate(labels):
        mask=np.array([z!=grp for z in labels])
        assert preds[j]==pytest.approx(float(X[j]@np.linalg.lstsq(X[mask],y[mask],rcond=None)[0]))
    assert min(n_train)==4


def test_insufficient_or_rank_deficient_training_fails_closed():
    np=pytest.importorskip('numpy')
    m=module()
    X=np.array([[1,0],[1,1],[1,1],[1,1]],float)
    y=np.arange(4.0)
    with pytest.raises(ValueError,match='rank|estimable'):
        m.cv_predict(X,y,m.make_group_splits(['a','b','a','a']))


def test_real_spatial_holdouts_and_quality_index_do_not_promote_causal_claims():
    pytest.importorskip('numpy')
    m=module()
    d=m.analyze()
    assert d['population_count']==23
    assert d['original_plant_species']==1
    assert d['state_count']==14
    assert d['state_wins_for_composition']==9
    assert d['seed_visit_counts']=={'B':31,'M':54,'H':33}
    assert d['source_quality_site_confounded'] is True
    state=d['cv']['state']['models']
    assert state['total']['rmse']==pytest.approx(0.21314,abs=1e-4)
    assert state['total_plus_composition']['rmse']==pytest.approx(0.18031,abs=1e-4)
    assert state['three_group_rates']['rmse']==pytest.approx(0.15051,abs=1e-4)
    assert state['single_visit_seedset_weighted']['rmse']==pytest.approx(0.22537,abs=1e-4)
    local=d['cv']['buffer_250km']['models']
    assert local['total']['rmse']==pytest.approx(0.21689,abs=1e-4)
    assert local['total_plus_composition']['rmse']==pytest.approx(0.18384,abs=1e-4)
    assert d['cv']['buffer_250km']['train_min']>=18
    assert d['structural_architecture_fitness_identified'] is False
    assert d['global_floral_prevalence_inferred'] is False
    assert d['V4_inputs_modified'] is False


def test_cv_predictions_are_exactly_one_per_original_population():
    pytest.importorskip('numpy')
    m=module()
    output=m.analyze()
    assert len(output['population_predictions'])==23
    for r in output['population_predictions']:
        assert r['population']
        assert r['state']
        assert r['state_holdout_train_count']>=19
        assert r['250km_buffer_train_count']>=18
        assert set(r['models'])=={'total','total_plus_composition','three_group_rates','single_visit_seedset_weighted'}


def test_250km_buffer_excludes_neighboring_population_training():
    np=pytest.importorskip('numpy')
    m=module()
    coordinates=np.array([[35.0, -90.0], [35.5, -90.0], [40.0, -90.0]])
    groups=m.buffered_splits(coordinates, radius_km=250)
    assert len(groups)==3
    assert 1 not in groups[0][0]  # ~56 km neighbor cannot train for first sample
    assert 0 not in groups[1][0]
    assert 2 in groups[0][0]     # distant source can train
    assert len(groups[0][1])==1


def test_duplicate_test_index_fails_closed():
    np=pytest.importorskip('numpy')
    m=module()
    X=np.array([[1,0],[1,1],[1,2],[1,3],[1,4]],float)
    y=np.arange(5.0)
    with pytest.raises(ValueError,match='Repeated'):
        m.cv_predict(X,y,[(np.array([0,1,2]),np.array([3,3]))])


def test_original_extremes_posthoc_state_holdout_stress_is_not_hidden():
    pytest.importorskip('numpy')
    m=module()
    out=m.analyze()['posthoc_extreme_population_stress']
    assert out['max_archived_PL']['omitted'] == ['MN_117']
    assert out['max_archived_PL']['population_count']==22
    assert out['max_archived_PL']['relative_composition_RMSE_reduction']==pytest.approx(0.1166,abs=1e-3)
    assert out['max_PL_and_two_archived_zeros']['omitted']==['MN_117','PA_27','TN_19']
    assert out['max_PL_and_two_archived_zeros']['population_count']==20
    assert out['max_PL_and_two_archived_zeros']['relative_composition_RMSE_reduction']==pytest.approx(0.0665,abs=1e-3)
    assert out['posthoc_not_p_value_or_outlier_correction'] is True

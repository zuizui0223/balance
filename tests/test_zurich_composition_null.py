"""Independent null-calibration for the frozen four-species source sample."""
import importlib.util
from pathlib import Path
import os
import pytest

pytest.importorskip('numpy')
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/audit_zurich_composition_null.py'
SOURCE=os.environ.get('BALANCE_ZURICH_ORIGINAL_ARCHIVE')


def module():
    spec=importlib.util.spec_from_file_location('null_composition', SCRIPT)
    z=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)
    return z


def test_loo_operator_matches_exact_training_fold_refits():
    m=module();x=np.linspace(-2,2,13);y=np.cos(x)+.3*x
    X=np.column_stack([np.ones(13),x,np.sin(x)])
    R=m.loo_operator(X)
    independent=[]
    for i in range(len(y)):
        k=np.arange(len(y))!=i
        b=np.linalg.lstsq(X[k],y[k],rcond=None)[0]
        independent.append(y[i]-X[i]@b)
    assert np.allclose(R@y,np.asarray(independent),atol=1e-12)


def test_rank_deficient_input_rejected():
    m=module();x=np.arange(10,dtype=float)
    with pytest.raises(ValueError,match='rank'):
        m.loo_operator(np.column_stack([np.ones(10),x,x]))


def test_original_deterministic_four_species_diagnostics():
    if not SOURCE:pytest.skip('Requires independently SHA-verified source ZIP')
    m=module();v=m.audit(Path(SOURCE),draws=1200,seed=20261115)
    assert v['n_gardens']==24
    assert v['independent_research_programmes']==1
    assert v['species_order']==['Carrot','Radish','Sainfoin','Comfrey']
    assert v['frozen_V4_modified'] is False
    assert v['causal_intervention_test'] is False
    assert v['source_sha256']=='b1ea0dc54d0c6e33bfacb44d7285377ec3e113807cc945fc2dfbfcc9'
    assert v['species']['Carrot']['gain_fraction']==pytest.approx(.19395301692,abs=1e-9)
    assert v['species']['Radish']['gain_fraction']==pytest.approx(-.001025819947,abs=1e-9)
    assert v['species']['Sainfoin']['gain_fraction']==pytest.approx(-.0507351378136,abs=1e-9)
    assert v['species']['Comfrey']['gain_fraction']==pytest.approx(.06415406270,abs=1e-9)
    assert v['species']['Carrot']['top_positive_garden']==19
    assert v['species']['Carrot']['gardens_with_lower_loss']==11
    for sp in v['species'].values():
        assert 0<sp['residual_permutation_p_fwer']<=1
        assert 0<sp['wild_signflip_p_fwer']<=1
        assert sp['residual_permutation_p_fwer']>=sp['residual_permutation_p_raw']
        assert sp['wild_signflip_p_fwer']>=sp['wild_signflip_p_raw']
        assert sp['paired_bootstrap_ci95'][0]<=sp['paired_bootstrap_ci95'][1]


def test_original_source_denominator_cannot_be_inflated():
    if not SOURCE:pytest.skip('Requires independently SHA-verified source ZIP')
    m=module();u=m.load_sites(Path(SOURCE));assert len(u)==96
    with pytest.raises(ValueError,match='96'):
        m.make_designs(u[:-1])
    with pytest.raises(ValueError,match='duplicate'):
        m.make_designs(u+[u[0]])


def test_shuffle_calibration_reproducible_with_seed():
    if not SOURCE:pytest.skip('Requires independently SHA-verified source ZIP')
    m=module();s=Path(SOURCE)
    a=m.audit(s,draws=300,seed=123)
    b=m.audit(s,draws=300,seed=123)
    assert a['species']==b['species']

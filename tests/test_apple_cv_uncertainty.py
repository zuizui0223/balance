"""Group-respecting uncertainty of the previously source-audited orchard CV."""
import importlib.util
import os
from pathlib import Path
import pytest
pytest.importorskip('numpy')
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/audit_apple_cv_uncertainty.py'
SOURCE=os.getenv('BALANCE_APPLE_ORIGINAL')

def module():
    spec=importlib.util.spec_from_file_location('orchard_cv_uncertainty',SCRIPT)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_heldout_loss_uses_whole_orchards():
    m=module()
    rows=[]
    for orchard in range(1,13):
        for year in [2012,2013]:
            rows.append({'orchard':orchard,'year':year,'total':1.4+orchard/4,
                         'share':.35+orchard/40,'rich':4+orchard%3,
                         'frost':orchard/30,'fruit':.2+(orchard%4)*.04,'organic':0})
    losses=m.heldout_orchard_mse(rows,('year','frost','total'))
    assert len(losses)==12
    assert set(losses)==set(range(1,13))
    assert all(np.isfinite(list(losses.values())))


def test_original_source_and_grouped_cv_match_reproduced_result():
    if not SOURCE:pytest.skip('Needs MD5-verified original fruit-set workbook')
    m=module()
    result=m.audit(Path(SOURCE),draws=1500,seed=20261115)
    assert result['n_independent_orchards']==21
    assert result['n_orchard_years_usable']==36
    assert result['source_md5']=='5445fb585421e6d9b1f5b5869342bbb4'
    x=result['main_year_and_frost_adjusted']
    assert x['gain_fraction']==pytest.approx(.06763157814435,abs=1e-9)
    assert x['largest_positive_orchard']==20
    assert x['orchards_with_lower_loss']==12
    assert x['paired_bootstrap_ci95'][0]<0<x['paired_bootstrap_ci95'][1]
    assert result['untouched_original_2011_missing_year']==11
    assert result['independent_plant_species']==1
    assert result['frozen_V4_modified'] is False


def test_source_digest_guard_fails(tmp_path):
    if not SOURCE:pytest.skip('Needs MD5-verified original fruit-set workbook')
    m=module()
    raw=Path(SOURCE).read_bytes()
    bad=tmp_path/'corrupt.xlsx'; bad.write_bytes(raw[:-1]+b'X')
    with pytest.raises(ValueError,match='MD5'):
        m.audit(bad,draws=100)

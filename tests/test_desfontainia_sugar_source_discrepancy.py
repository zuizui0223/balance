"""Source-version sugar-filter audit tests, no V4 architecture outcome promotion."""
from pathlib import Path
import os
import subprocess
import sys

import pytest

from scripts.audit_desfontainia_sugar_source_discrepancy import (
    analyze, original_code_has_5ul_gate, final_code_uses_positive_sugar,
    pair_sugar_by_shrub,
)

ROOT=Path(__file__).resolve().parents[1]


def test_low_volume_reproduces_pair_loss_under_historical_5ul_gate():
    rows=[
        [1,1,'Robada',0.8,3.0],[1,2,'Robada',1.2,5.0],
        [1,1,'No dañada',6.0,20.0],
        [2,1,'Robada',6.1,7.0],[2,1,'No dañada',5.2,15.0],
        [3,1,'Robada',0,0],[3,1,'No dañada',8.0,18.0],
    ]
    low=pair_sugar_by_shrub(rows,0)
    high=pair_sugar_by_shrub(rows,5)
    assert low['n_shrubs']==2
    assert low['shrub_ids']==[1,2]
    assert low['means']['Robada'][0]==pytest.approx(4)
    assert high['n_shrubs']==1
    assert high['shrub_ids']==[2]


def test_invalid_source_rows_are_fail_closed():
    rows=[[1,1,'Robada',5,2],[1,1,'No dañada',5,3]]
    with pytest.raises(ValueError,match='Duplicate'):
        pair_sugar_by_shrub(rows+[[1,1,'Robada',5,2]],0)
    with pytest.raises(ValueError,match='Status'):
        pair_sugar_by_shrub([[1,1,'mystery',5,2]],0)
    with pytest.raises(ValueError,match='volume'):
        pair_sugar_by_shrub([[1,1,'Robada',-1,2]],0)


def test_code_version_pattern_does_not_confuse_march_and_final():
    old="filter(nectar_ul >= 5, !is.na(sugar_pct), sugar_pct > 0)"
    final="filter(`Nectar concentration (% w/w)` > 0)"
    assert original_code_has_5ul_gate(old)
    assert not original_code_has_5ul_gate(final)
    assert final_code_uses_positive_sugar(final)
    assert not final_code_uses_positive_sugar(old)


def test_cli_help_no_pythonpath():
    env=dict(os.environ)
    env.pop('PYTHONPATH',None)
    p=subprocess.run([sys.executable,str(ROOT/'scripts/audit_desfontainia_sugar_source_discrepancy.py'),'--help'],
                     cwd=ROOT,env=env,text=True,capture_output=True,check=False)
    assert p.returncode==0,p.stderr
    assert '--final-r' in p.stdout and '--final-source' in p.stdout


def test_both_author_versions_and_real_40_shrub_stage_gate():
    original=os.getenv('BALANCE_DESFONTAINIA_SOURCE')
    old_r=os.getenv('BALANCE_DESFONTAINIA_R_SOURCE')
    final_r=os.getenv('BALANCE_DESFONTAINIA_FINAL_R')
    final_xlsx=os.getenv('BALANCE_DESFONTAINIA_FINAL_SOURCE')
    if not all([original,old_r,final_r,final_xlsx]):
        pytest.skip('Original/final published MD5-verified Zenodo sources required')
    pytest.importorskip('scipy')
    result=analyze(Path(original),Path(old_r),Path(final_r),Path(final_xlsx))
    assert result['source_version_concordance']['final_paper_code_reproduces_nine_pair_statistic']
    assert result['source_version_concordance']['same_underlying_spreadsheet_between_records']
    assert result['source_version_concordance']['march_source_gate_is_final_paper_bug'] is False
    assert result['sugar_filter_discrepancy']['author_code_5ul']['n_shrubs']==1
    paper=result['sugar_filter_discrepancy']['reported_n9_reconstruction']
    assert paper['n_shrubs']==9
    assert paper['paired_t']==pytest.approx(-2.1293105807689403,abs=1e-9)
    assert paper['paired_p_two_sided']==pytest.approx(.06586362587566166,abs=1e-9)
    inc=result['unconditional_incidence_survey']
    assert inc['pierced_flowers']==165 and inc['flowers_surveyed']==1000
    assert inc['shrubs_with_any_piercing']==43
    assert inc['cluster_bootstrap95_fraction']==pytest.approx([.116,.218],abs=.0006)
    stage=result['cross_stage_shrub_relation']
    assert stage['n_shrubs']==40
    assert stage['spearman_rho']==pytest.approx(.13805758810073251,abs=1e-9)
    assert stage['shrub_bootstrap95_interval']==pytest.approx([-.20155292458,.46153458132],abs=.001)
    assert not result['inference_firewall']['nectar_mediates_seed_robbery_causally_identified']
    assert not result['inference_firewall']['direct_BALANCE_architecture_margin_measured']

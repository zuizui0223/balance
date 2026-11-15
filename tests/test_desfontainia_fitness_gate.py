"""40-shrub independent paired-contrast audit for published 2026 source."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/audit_desfontainia_fitness_gate.py'


def module():
    spec = importlib.util.spec_from_file_location('desfontainia_source_gate', SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_paired_analysis_refuses_duplicate_plant_or_negative_seed_count():
    m=module()
    valid=[[i,0,i,i+1] for i in range(1,41)]
    assert m.summarize_seed(valid)['n_shrubs']==40
    dup=[list(v) for v in valid]; dup[1][0]=1
    with pytest.raises(ValueError,match='40 unique'):
        m.summarize_seed(dup)
    neg=[list(v) for v in valid]; neg[20][3]=-1
    with pytest.raises(ValueError,match='nonnegative'):
        m.summarize_seed(neg)


def test_missing_nectar_not_silently_replaced_by_zero():
    m=module()
    rows=[]
    for i in range(1,41):
        rows.extend([[i,1,'Robada',0,None],[i,2,'No dañada',2,None]])
    out=m.summarize_nectar(rows, expected_total=80,expected_per_state=40)
    assert out['n_paired_shrubs']==40
    assert out['mean_pierced_ul']==0
    assert out['mean_undamaged_ul']==2
    rows[2][3]=None
    out=m.summarize_nectar(rows, expected_total=80,expected_per_state=40)
    assert out['n_paired_shrubs']==39
    assert out['missing_volume_by_status']['Robada']==1


def test_original_real_40_shrub_stage_gates(monkeypatch):
    source=os.environ.get('BALANCE_DESFONTAINIA_SOURCE')
    if not source: pytest.skip('Dedicated verified-source workflow supplies XLSX')
    m=module()
    out=m.audit(Path(source))
    seed=out['seed']
    assert seed['n_shrubs']==40
    assert seed['seed_presence_by_treatment']=={'minusP_minusR':2,'plusP_minusR':32,'plusP_plusR':28}
    assert seed['mean_seeds_by_treatment']['plusP_minusR']==pytest.approx(26.125)
    assert seed['mean_seeds_by_treatment']['plusP_plusR']==pytest.approx(31.35)
    assert seed['paired_seed_difference_plusR_minusR']['mean']==pytest.approx(5.225)
    assert seed['paired_seed_difference_plusR_minusR']['t_95_interval'][0]==pytest.approx(-12.8500,abs=.002)
    assert seed['paired_seed_difference_plusR_minusR']['t_95_interval'][1]==pytest.approx(23.3000,abs=.002)
    assert seed['paired_seed_difference_plusR_minusR']['n_higher_n_lower_n_equal']==[19,19,2]
    assert out['nectar']['missing_volume_by_status']=={'Robada':14,'No dañada':20}
    assert out['nectar']['n_paired_shrubs']==40
    assert out['nectar']['mean_pierced_ul']/out['nectar']['mean_undamaged_ul']==pytest.approx(.1081233,rel=1e-4)
    assert out['source_evidence_ceiling']['equivalence_of_seed_output_demonstrated'] is False
    assert out['source_evidence_ceiling']['fully_randomized_robbery_intention_to_treat'] is False
    assert out['source_evidence_ceiling']['architecture_WD_minus_WS_identified'] is False
    assert out['source_evidence_ceiling']['missing_minusP_plusR_factorial_cell'] is True


def test_corrupt_source_fails_hash_before_numbers(tmp_path):
    source=os.environ.get('BALANCE_DESFONTAINIA_SOURCE')
    if not source: pytest.skip('Dedicated verified-source workflow supplies XLSX')
    m=module(); altered=tmp_path/'changed.xlsx'; altered.write_bytes(Path(source).read_bytes()+b'bad')
    with pytest.raises(ValueError,match='MD5'):
        m.audit(altered)
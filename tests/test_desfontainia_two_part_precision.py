"""Two-part and equivalence precision checks; never a robbery causal analysis."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/audit_desfontainia_two_part_precision.py'


def module():
    spec=importlib.util.spec_from_file_location('desfontainia_two_part_precision',SCRIPT)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_two_part_reconstruction_and_validation():
    m=module()
    # Under noR all flowers seed; under R 20 seed 20 do not.
    rows=[[i,0,10,20 if i<=20 else 0] for i in range(1,41)]
    result=m.summarize_two_part(rows)
    assert result['seed_presence']['protected']==40
    assert result['seed_presence']['naturally_pierced']==20
    assert result['positive_only_means']['protected']==pytest.approx(10)
    assert result['positive_only_means']['naturally_pierced']==pytest.approx(20)
    assert result['arithmetic_decomposition']['prevalence_component']==pytest.approx(-5)
    assert result['arithmetic_decomposition']['positive_magnitude_component']==pytest.approx(5)
    assert result['arithmetic_decomposition']['reconstructed_mean_difference']==pytest.approx(0)
    assert result['paired_difference']['median']==pytest.approx(0)
    assert result['paired_difference']['n_positive']==20
    assert result['paired_difference']['n_negative']==20
    assert result['paired_presence']['exact_discordance_two_sided_reference_p']==pytest.approx(2**-19)  # 20 vs 0 discordances


def test_invalid_source_rows_are_rejected():
    m=module()
    rows=[[i,0,10,20] for i in range(1,41)]
    bad=[list(x) for x in rows];bad[1][0]=1
    with pytest.raises(ValueError,match='unique'):
        m.summarize_two_part(bad)
    bad=[list(x) for x in rows];bad[0][3]=-1
    with pytest.raises(ValueError,match='nonnegative'):
        m.summarize_two_part(bad)


def test_exact_sign_reference_and_equivalence_gate():
    m=module()
    assert m.exact_two_sided_binomial(19,38)==pytest.approx(1)
    assert m.exact_two_sided_binomial(10,16)==pytest.approx(0.454498291015625)
    assert m.exact_two_sided_binomial(20,20)==pytest.approx(2/2**20)
    rows=[[i,0,10,10] for i in range(1,41)]
    z=m.summarize_two_part(rows)
    assert z['equivalence_sensitivity']['relative_10_percent']['90ci_within_bounds'] is True
    assert z['paired_difference']['median']==0


def test_original_40_shrubs_and_no_equivalence_claim():
    source=os.getenv('BALANCE_DESFONTAINIA_SOURCE')
    if not source:pytest.skip('Dedicated workflow provides original MD5-locked Zenodo XLSX')
    m=module()
    z=m.audit(Path(source))
    assert z['n_shrubs']==40
    assert z['seed_presence']=={'protected':32,'naturally_pierced':28}
    assert z['positive_only_means']['protected']==pytest.approx(32.65625)
    assert z['positive_only_means']['naturally_pierced']==pytest.approx(44.785714285714285)
    assert z['arithmetic_decomposition']['prevalence_component']==pytest.approx(-3.265625)
    assert z['arithmetic_decomposition']['positive_magnitude_component']==pytest.approx(8.490625)
    assert z['paired_difference']['mean']==pytest.approx(5.225)
    assert z['paired_difference']['median']==0
    assert (z['paired_difference']['n_positive'],z['paired_difference']['n_negative'],z['paired_difference']['n_equal'])==(19,19,2)
    assert z['paired_presence']['exact_discordance_two_sided_reference_p']==pytest.approx(0.454498291015625)
    assert z['equivalence_sensitivity']['90ci_bounds'][0]==pytest.approx(-9.831268,abs=0.002)
    assert z['equivalence_sensitivity']['90ci_bounds'][1]==pytest.approx(20.281268,abs=0.002)
    for label in ['relative_10_percent','relative_20_percent','relative_50_percent']:
        assert z['equivalence_sensitivity'][label]['90ci_within_bounds'] is False
    assert z['equivalence_sensitivity']['minimum_symmetric_half_width_for_90ci']==pytest.approx(20.281268,abs=0.002)
    assert z['interpretation_guardrails']['absence_of_seed_cost_proven']==False
    assert z['interpretation_guardrails']['causal_robbery_effect_identified']==False
    assert z['interpretation_guardrails']['conditional_positive_mean_causal']==False
    assert z['interpretation_guardrails']['structural_BALANCE_worldline_measured']==False

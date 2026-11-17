"""No-claim-inflation tests for fixed-quality visitation and one-FDP design."""
import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/audit_alpinia_fixed_efficiency_envelope.py'

def module():
    spec=importlib.util.spec_from_file_location('alpinia_fixed_efficiency',SCRIPT)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def test_source_bound_envelope_and_fruit_ratio():
    z=module().audit(ROOT)
    s=z['two_guild_fixed_efficiency_scenario']
    assert z['original_source']['n_independent_exposure_FDP_per_status']==1
    assert z['original_source']['approximately_m_between_FDP']==300
    assert z['source_n_dye_mean_cells']==32
    assert z['source_n_fruit_summary_cells']==16
    assert s['quality_assumption']=='constant Apis relative per-visit effectiveness 0<=a<=1; Bombus=1'
    assert s['bombus_only_effective_visit_ratio']==pytest.approx(6.15/7.86)
    assert s['all_two_guild_visits_ratio']==pytest.approx(9.21/9.19)
    assert s['observed_fruit_set_ratio']==pytest.approx((5174/17231)/(7001/16845))
    assert s['apparent_fruit_ratio_below_plug_in_visit_envelope'] is True
    assert s['negative_quality_required_to_match_fruit_ratio']==pytest.approx(-0.224521761027,abs=1e-10)
    assert s['ratio_gap_vs_bombus_only']==pytest.approx(0.0599610007673,abs=1e-10)
    assert z['interpretation_flags']['no_valid_plot_level_treatment_effect_test'] is True
    assert z['interpretation_flags']['no_mediation_identification'] is True
    assert z['interpretation_flags']['the_descriptive_ratio_gap_falsifies_biological_substitution'] is False
    assert 'p_value' not in str(z)

def test_bounded_positive_quality_weight_is_monotone():
    m=module()
    rr=[m.effective_visit_ratio(6.15,3.06,7.86,1.33,a) for a in [0,.25,.5,.75,1]]
    assert rr == sorted(rr)
    assert rr[0]==pytest.approx(.7824427481)
    assert rr[-1]==pytest.approx(1.00217627856)

def test_invalid_efficiency_weight_rejected():
    m=module()
    with pytest.raises(ValueError,match='nonnegative'):
        m.effective_visit_ratio(-1,3,8,1,.5)
    with pytest.raises(ValueError,match='nonnegative'):
        m.effective_visit_ratio(6,3,8,1,-.3)
    with pytest.raises(ValueError,match='positive'):
        m.effective_visit_ratio(6,3,0,0,.5)
    with pytest.raises(ValueError,match='finite'):
        m.effective_visit_ratio(float('nan'),3,8,1,.5)

def test_prevent_plot_level_n_inflation_and_strict_identification():
    z=module().audit(ROOT)
    assert z['original_source']['n_independent_exposure_FDP_per_status']==1
    assert z['original_source']['n_direction_transects_per_FDP']==4
    assert z['original_source']['n_distance_subplots_per_FDP']==60
    assert z['original_source']['methods_quote_paraphrase_only'] is True
    assert all(z['unmeasured_identification_gates'].values())

def test_source_integrity_dependency():
    z=module().audit(ROOT)
    assert z['original_source']['bridge_sha256_checked'] is True
    assert z['source_n_dye_mean_cells']==32
    assert z['source_n_fruit_summary_cells']==16

def test_one_reported_standard_error_shift_erases_plug_in_gap():
    s=module().audit(ROOT)['two_guild_fixed_efficiency_scenario']
    lo,hi=s['illustrative_one_reported_SE_bombus_only_ratio_band']
    assert lo==pytest.approx((6.15-.82)/(7.86+.94))
    assert hi==pytest.approx((6.15+.82)/(7.86-.94))
    assert lo < s['observed_fruit_set_ratio'] < hi
    assert s['this_is_not_a_confidence_interval'] is True

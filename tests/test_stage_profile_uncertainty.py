import pytest
pytest.importorskip('numpy');pytest.importorskip('scipy');pytest.importorskip('openpyxl')
from scripts.audit_stage_profile_uncertainty import profile,certify,fate_audit,missing_bounds
def test_profile_thresholds_and_certification():
    assert profile(-.3,-.5,.1)=='amplification'
    assert profile(-.5,-.3,.1)=='attenuation'
    assert profile(-.04,-.4,.1)=='threshold_crossing_down'
    assert profile(-.4,-.04,.1)=='threshold_crossing_up'
    assert profile(-.3,-.35,.1)=='stable_negative'
    assert certify([-.5,-.2],[-.8,-.4],[-.6,-.2],.1)=='amplification'
    assert certify([-.3,.3],[-.8,-.4],[-.9,-.1],.1)=='unresolved'
def test_fate_audit_keeps_combined_category():
    p={(a,i):{'total_successful':5.,'aborts':1.,'deh, drop, hyl':4.,'total_fruit':10.,'pollen_mean':1.} for a in ('C','P','S') for i in (1,2,3)}
    d=fate_audit(p)
    assert d['count_identity_success_plus_aborts_plus_other_equals_total']['matches']==9
    assert d['all_positive_denominator_plants']['contrasts']['P/C']['success_difference_if_other_fate_can_be_any_success_fraction_by_arm']==pytest.approx([-.4,.4])
    p['C',1]['total_fruit']=11.
    assert fate_audit(p)['status']=='HOLD_NONCLOSING_FATE_COUNTS'
def test_missing_bounds_are_not_confidence_intervals():
    p={(a,i):{'pollen_mean':None if i>35 else 10.,'prop_fruit_set':.5 if a=='C' else .25,'total_seeds_plant':1.} for a in ('C','P','S') for i in range(1,41)}
    d=missing_bounds(p)
    assert d['ranges']['2.0']['P/C'][1]<0

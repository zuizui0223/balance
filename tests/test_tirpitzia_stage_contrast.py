import math,pytest
from scripts.audit_tirpitzia_stage_contrast import contrast,morph_difference,DATA
def test_opposite_stage_directions():
    l=contrast(DATA['L']['H'],DATA['L']['C']);s=contrast(DATA['S']['H'],DATA['S']['C'])
    assert l['delta']==pytest.approx(-.5169740299112991)
    assert s['delta']==pytest.approx(.21582501111626562)
    assert morph_difference(l,s)['L_minus_S']==pytest.approx(-.7327990410275648)
def test_worst_covariance_does_not_shrink_interval():
    a=contrast(DATA['L']['H'],DATA['L']['C'])
    assert a['se_Cauchy_upper']>=a['se_independence']
    d=morph_difference(a,contrast(DATA['S']['H'],DATA['S']['C']))
    assert d['normal95_full_Cauchy_upper'][0]<0<d['normal95_full_Cauchy_upper'][1]

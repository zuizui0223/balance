import pytest
pytest.importorskip('scipy')
from scripts.audit_pollen_stage_denominators import pairing_envelope, lr, interval, UP, DOWN
from scripts.audit_larceny_meta_stage_pairability import CONTEXT
def row(i,p,s,y):
    d={k:'context' for k in CONTEXT}
    d.update({'ID':i,'ref-ID':p,'species':'x','title':'x','reference':'x','sub_response_variable':s,'yi':y,'vi':.1})
    return d
def test_pairing_envelope_not_invariant_when_one_candidate_reverses():
    q=pairing_envelope([row(1,1,UP,-1),row(2,1,UP,1),row(3,1,DOWN,0)])[0]
    assert q['min']==-1 and q['max']==1
    assert q['sign_invariant']=='not_strictly_invariant'
    assert not q['treatment_pair_verified']
def test_glechoma_source_arithmetic():
    inc=lr(64.86,83.33);load=lr(15.96,13.85);fruit=lr(58.89,80.35)
    assert fruit-inc==pytest.approx(-.0601432677120987)
    assert fruit-(inc+load)/2==pytest.approx(-.256332211163728)
def test_zero_variance_working_interval():
    assert interval(-.1,0)==[-.1,-.1]

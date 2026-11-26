import pytest
pytest.importorskip('scipy')
from scripts.audit_breeding_stage_moderators import label, subgroup
def test_exact_binary_labels():
    r={1:{'autonomous':'yes'},2:{'autonomous':'no'},3:{'autonomous':None},4:{'autonomous':'unknown'}}
    assert label([1],r,'autonomous')=='yes'
    assert label([1,2],r,'autonomous') is None
    assert label([3],r,'autonomous') is None
    assert label([4],r,'autonomous') is None
def test_underpowered_subgroups_not_fitted():
    r=[{'ID':1,'autonomous':'yes'},{'ID':2,'autonomous':'no'}]
    x={1:{'ids':[1],'y':.2,'v_ind':.1,'v_upper':.1},2:{'ids':[2],'y':-.4,'v_ind':.1,'v_upper':.1}}
    d=subgroup(x,r,'autonomous')
    assert d['n_yes']==d['n_no']==1
    assert d['status']=='INSUFFICIENT_SUPPORT' and not d['contrasts']

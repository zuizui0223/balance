import pytest
pytest.importorskip('numpy')
pytest.importorskip('openpyxl')
import math
from scripts.fit_richman_plant_stage import assemble, audit, summarize, ARMS
def fruit(a,p):
    return {'treatment':a,'plant':p,'successful_fruits':2,'DF':0,'total_successful':2,'aborts':1,'deh, drop, hyl':1,'total_fruit':3,'prop_fruit_set':2/3,'total_seeds_plant':4,'seeds_fruit_plant':2,'browse':0,'height':1}
def sample(a,p,pid,v):
    return {'treatment':a,'plant':p,'plant_id':pid,'week':1,'grains':v}
def test_link_and_fruit_denominator():
    f=[fruit(a,p) for a in ARMS for p in range(1,41)]
    pp=assemble([sample('C',1,1,0),sample('C',1,1,10)],f)
    assert pp['C',1]['pollen_mean']==5 and pp['C',1]['pollen_incidence']==.5
    assert audit(pp)['source_recorded_fruit_fraction_vs']['success_over_total_fruit']['matches']==120
    with pytest.raises(ValueError,match='ambiguous'):
        assemble([sample('C',1,1,0),sample('C',2,1,10)],f)
def test_joint_same_plant_bootstrap():
    pp={(a,p):{'x':x,'y':y,'browse':0} for a,x,y in [('C',10,8),('P',5,2),('S',2.5,1)] for p in (1,2,3)}
    r=summarize(pp,('x','y'),B=100)
    assert r['effects']['P/C']['downstream_minus_upstream']['y']['estimate']==pytest.approx(-math.log(2))
    assert r['effects']['S/P']['downstream_minus_upstream']['y']['estimate']==pytest.approx(0)
    assert len(r['joint_covariance'])==6

def test_quarantine_keeps_all_fruit_plants_and_excludes_entire_ambiguous_component():
    from scripts.fit_richman_plant_stage import linkage_audit
    f=[fruit(a,p) for a in ARMS for p in range(1,41)]
    z=[sample('C',1,1,3),sample('C',1,2,4),sample('C',2,2,8),sample('C',3,3,7)]
    bad,detail=linkage_audit(z)
    assert bad=={('C',1),('C',2)} and detail['n_quarantined_stigma_rows']==3
    q=assemble(z,f,link_mode='quarantine')
    assert len(q)==120 and q['C',1]['pollen_mean'] is None and q['C',3]['pollen_mean']==7
    assert assemble(z,f,link_mode='within_key_only')['C',1]['pollen_mean']==3.5

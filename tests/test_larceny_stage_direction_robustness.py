import pytest
pytest.importorskip('scipy')
from scripts.audit_larceny_stage_direction_robustness import holm, sign_summary, species_components, trace, present, stage_profile
from scripts.fit_larceny_study_stage_meta import collect, CONTEXT
def row(i,p,s,y,sp='plant',**kw):
    r={k:'x' for k in CONTEXT};r.update(ID=i,species=sp,title='title',reference='ref',yi=y,vi=.1)
    r.update({'ref-ID':p,'sub_response_variable':s});r.update(kw);return r
def test_holm_and_sign_counts():
    assert holm({'a':.01,'b':.04,'c':.06})==pytest.approx({'a':.03,'b':.08,'c':.08})
    x=sign_summary({i:{'y':y} for i,y in enumerate([1]*9+[-1,0])})
    assert (x['positive'],x['negative'],x['ties'])==(9,1,1)
    assert x['sign_p_nominal']==pytest.approx(.021484375)
def test_component_connects_transitively():
    rows=[row(1,1,'fruit set',1,'a'),row(2,2,'fruit set',2,'a'),row(3,2,'fruit set',3,'b'),row(4,3,'fruit set',4,'b')]
    p=collect(rows,'fruit set')
    groups=species_components(p,rows)
    assert len(groups)==1 and next(iter(groups.values()))['papers']==[1,2,3]
def test_source_trace_not_treatment_verification():
    rows=[row(1,1,'fruit set',-1,damage=None),row(2,1,'seed set',0,damage=None)]
    q=trace(rows,'fruit set','seed set')[0]
    assert q['unique_per_endpoint'] and not q['core_present']
    assert not q['same_experiment_verified'] and not q['sampling_covariance_known']
    assert not present('NA') and present('no')

def test_stage_direction_not_necessarily_negative_cost():
    assert stage_profile(-1,-.5)=='both_negative_attenuation'
    assert stage_profile(-.5,-1)=='both_negative_amplification'
    assert stage_profile(-.5,.5)=='negative_to_nonnegative'
    assert stage_profile(.5,-.5)=='nonnegative_to_negative'
    assert stage_profile(.5,1)=='both_nonnegative'

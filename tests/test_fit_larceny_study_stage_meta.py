import pytest
from scripts.fit_larceny_study_stage_meta import collapse, collect, pool, sensitivity, CONTEXT
def row(i,p,stage,y,v=1.,sp='a',**kw):
    r={k:'x' for k in CONTEXT}
    r.update({'ID':i,'ref-ID':p,'species':sp,'sub_response_variable':stage,'yi':y,'vi':v})
    r.update(kw)
    return r
def test_signed_variance_bound_and_equal_arms():
    a,b,c=row(1,1,'fruit set',-1),row(2,1,'seed set',0),row(3,1,'seed set',2)
    x=collapse([[(-1,[a]),(1,[b,c])]])
    assert x['y']==2
    assert x['v_ind']==1.5
    assert x['v_upper']==4
def test_scope_and_paper_dependence():
    rows=[row(1,1,'fruit set',-1),row(2,1,'seed set',0),row(3,1,'fruit set',-2,sp='b'),row(4,1,'seed set',-1,sp='b'),row(5,2,'fruit set',-3),row(6,2,'seed set',0,damage='different')]
    p=collect(rows,'fruit set','seed set','context')
    assert set(p)=={1}
    assert p[1]['blocks']==2 and p[1]['y']==1
    assert set(collect(rows,'fruit set','seed set','paper_species'))=={1,2}
def test_null_and_negative_retained():
    rows=[row(i,i,'fruit set',float(i-3)) for i in range(1,6)]
    p=collect(rows,'fruit set')
    f=pool(list(p.values()),0.)
    assert f['k']==5 and f['mu']==pytest.approx(0)
    assert f['positive_papers']==2 and f['negative_papers']==2
    assert f['ci95'][0]<0<f['ci95'][1]
def test_variance_sensitivity_and_small_k():
    x=collapse([[(1,[row(1,1,'fruit set',1),row(2,1,'fruit set',1)])]])
    assert pool([x],0)['status']=='INSUFFICIENT_STUDIES'
    fits=sensitivity([x]*5)
    assert fits['1.0']['se_mkh']>=fits['0.0']['se_mkh']

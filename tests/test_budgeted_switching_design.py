from fractions import Fraction as F
import random
import pytest
from balance_domain.bounded_switching_design import identify_bounded_switching, plan_reset_refinement
from balance_domain.budgeted_switching_design import (
    condition_reset_outcome, plan_budgeted_reset_refinement, worst_span_after_queries,
)


def receipt(wf='.03', wr='.04'):
    return identify_bounded_switching(
        [(0,0,'shared'),(wf,wf,'differentiated')],
        [(0,0,'differentiated'),(-F(wr),-F(wr),'shared')],
        common_phi_scale='synthetic',fixed_context='fixed',
        latent_monotone_and_instantaneous_declared=True,horizon_bounds=(10,10))


def plan(r=None, **kwargs):
    args=dict(budget=4,forward_query_error='.005',reverse_query_error='.005',
              matched_reset_available_declared=True)
    args.update(kwargs)
    return plan_budgeted_reset_refinement(r or receipt(),**args)


def test_four_query_frontier_and_precision_budget():
    r=plan(target_width_span='.033')
    assert [(a.forward_queries,a.reverse_queries) for a in r.frontier]==[(0,0),(0,1),(1,1),(1,2),(2,2)]
    assert [F(a.width_worst_span_exact) for a in r.frontier]==list(map(F,['.07','.055','.045','.0375','.0325']))
    assert r.minimum_budget_for_target==4
    assert r.target_status=='attainable_within_budget'


def test_one_step_agrees_with_previous_planner():
    old=plan_reset_refinement(receipt(),forward_query_error='.005',reverse_query_error='.005',
                              matched_reset_available_declared=True)
    new=plan(budget=1)
    assert new.optimal.guaranteed_reduction_lower==old.guaranteed_width_span_reduction
    assert old.best_directions==('reverse',)


def test_unequal_costs_defeat_gain_per_cost_greedy():
    # Forward's immediate gain/cost .015/2 exceeds reverse's .020/3,
    # but a budget of 3 cannot buy both: reverse alone is the true optimum.
    r=plan(budget=3,forward_query_error=0,reverse_query_error=0,forward_cost=2,reverse_cost=3)
    assert r.optimal.forward_queries==0 and r.optimal.reverse_queries==1
    assert F(r.optimal.width_worst_span_exact)==F('.05')


def test_zero_budget_spends_nothing():
    r=plan(budget=0)
    assert r.optimal.spent==0
    assert F(r.optimal.width_worst_span_exact)==F('.07')


def test_floor_does_not_inflate_already_narrow_initial_brackets():
    r=plan(receipt('.001','.002'),budget=10)
    assert r.optimal.spent==0
    assert F(r.limiting_span_exact)==F('.003')


@pytest.mark.parametrize('target,status',[('.02','unattainable_in_finite_queries_under_declared_error_model'),
    ('.01','unattainable_in_finite_queries_under_declared_error_model'),
    ('.033','not_reached_within_budget_cap'),('.07','attainable_within_budget')])
def test_attainability_is_separate_from_finite_search_cap(target,status):
    r=plan(budget=3,target_width_span=target)
    assert r.target_status==status
    if target=='.07': assert r.minimum_budget_for_target==0


def test_closed_form_matches_independent_recurrence():
    for w in map(F,['0','.001','.01','.1']):
        for e in map(F,['0','.002','.03']):
            actual=w
            for n in range(10):
                assert worst_span_after_queries(w,e,n)==actual
                actual=min(actual,actual/2+e)


def test_noiseless_bisection_limits_zero_but_not_finite_exact_identification():
    r=plan(budget=5,forward_query_error=0,reverse_query_error=0,target_width_span=0)
    assert F(r.limiting_span_exact)==0
    assert r.target_status.startswith('unattainable_in_finite')


def test_condition_actual_reverse_outcome_then_replan():
    r=receipt()
    for state in ('shared','differentiated'):
        updated=condition_reset_outcome(r,direction='reverse',query_phi='-.02',
            query_error='.005',observed_state=state,matched_reset_available_declared=True)
        span=F(updated.hysteresis_width.exact_upper)-F(updated.hysteresis_width.exact_lower)
        assert span==F('.055')
        assert updated.total_cost is None
        assert F(plan(updated,budget=3).optimal.width_worst_span_exact)==F('.0325')


def test_cost_reprojection_requires_supplied_independent_horizon():
    updated=condition_reset_outcome(receipt(),direction='reverse',query_phi='-.02',query_error='.005',
        observed_state='shared',matched_reset_available_declared=True,horizon_bounds=(10,10))
    assert F(updated.total_cost.exact_upper)==F('.55')


def test_incompatible_selected_outcome_rejected():
    with pytest.raises(ValueError,match='empty'):
        condition_reset_outcome(receipt(),direction='forward',query_phi='.2',query_error=0,
            observed_state='shared',matched_reset_available_declared=True)


@pytest.mark.parametrize('overrides',[{'budget':True},{'budget':-1},{'budget':2001},
    {'forward_cost':0},{'reverse_cost':1.2},{'forward_query_error':'nan'},
    {'reverse_query_error':-1},{'target_width_span':-1},
    {'matched_reset_available_declared':False}])
def test_invalid_inputs_fail_closed(overrides):
    with pytest.raises(ValueError): plan(**overrides)


def test_unbounded_censored_threshold_needs_new_bracket_before_midpoint_budget():
    r=identify_bounded_switching([(0,0,'shared')],[(0,0,'differentiated')],
        common_phi_scale='synthetic',fixed_context='fixed',latent_monotone_and_instantaneous_declared=True)
    with pytest.raises(ValueError,match='finite'):
        plan(r)


def test_seeded_cost_allocations_match_brute_force_recurrence():
    rng=random.Random(9038)
    for _ in range(100):
        wf,wr=F(rng.randint(1,30),100),F(rng.randint(1,30),100)
        ef,er=F(rng.randint(0,10),100),F(rng.randint(0,10),100)
        cf,cr=rng.randint(1,4),rng.randint(1,4)
        B=rng.randint(0,12)
        got=plan(receipt(wf,wr),budget=B,forward_query_error=ef,reverse_query_error=er,
                 forward_cost=cf,reverse_cost=cr)
        def iterate(w,e,n):
            for _ in range(n): w=min(w,w/2+e)
            return w
        brute=min((iterate(wf,ef,nf)+iterate(wr,er,nr),cf*nf+cr*nr,nf+nr,nf,nr)
                  for nf in range(B//cf+1) for nr in range(B//cr+1) if cf*nf+cr*nr<=B)
        r=got.optimal
        assert (F(r.width_worst_span_exact),r.spent,r.forward_queries+r.reverse_queries,
                r.forward_queries,r.reverse_queries)==brute

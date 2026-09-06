from fractions import Fraction as F

import pytest

from balance_domain.bounded_switching_design import (
    identify_bounded_switching, plan_reset_refinement,
)
from balance_domain.empirical_identification import identify_switching_records


UP = [('0.095','0.105','shared'),('0.115','0.125','differentiated')]
DOWN = [('-0.055','-0.045','differentiated'),('-0.085','-0.075','shared')]
KW = dict(common_phi_scale='synthetic',fixed_context='matched',
          latent_monotone_and_instantaneous_declared=True)


def test_measurement_error_widens_intervals_and_cost_scale_remains_explicit():
    r = identify_bounded_switching(UP,DOWN,**KW,horizon_bounds=(10,10))
    assert (F(r.hysteresis_width.exact_lower),F(r.hysteresis_width.exact_upper)) == (F('0.14'),F('0.21'))
    assert r.hysteresis_width.lower_closed and not r.hysteresis_width.upper_closed
    assert (F(r.total_cost.exact_lower),F(r.total_cost.exact_upper)) == (F('1.4'),F('2.1'))
    assert identify_bounded_switching(UP,DOWN,**KW).total_cost is None


def test_zero_error_recovers_error_free_route():
    up=[(.1,'shared'),(.12,'differentiated')]
    down=[(-.05,'differentiated'),(-.08,'shared')]
    old=identify_switching_records(up,down,common_phi_scale='test',fixed_context='test',
                                  instantaneous_rule_declared=True)
    new=identify_bounded_switching([(x,x,s) for x,s in up],[(x,x,s) for x,s in down],**KW)
    assert new.hysteresis_width.lower == pytest.approx(old.width.lower)
    assert new.hysteresis_width.upper == pytest.approx(old.width.upper)
    assert new.hysteresis_width.lower_closed == old.width.lower_closed
    assert new.hysteresis_width.upper_closed == old.width.upper_closed


def test_all_records_not_only_adjacent_records_constrain_latent_monotone_path():
    up=[('0.10','0.11','shared'),('0.08','0.12','shared'),
        ('0.09','0.20','differentiated'),('0.13','0.14','differentiated')]
    r=identify_bounded_switching(up,DOWN,**KW)
    assert F(r.forward_cost_over_horizon.exact_lower)==F('0.10')
    assert F(r.forward_cost_over_horizon.exact_upper)==F('0.14')


def test_censored_paths_keep_unbounded_upper_limits():
    r=identify_bounded_switching(UP[:1],DOWN[:1],**KW)
    assert r.hysteresis_width.upper is None
    assert not r.forward_switch_observed and not r.reverse_switch_observed
    with pytest.raises(ValueError,match='finite'):
        plan_reset_refinement(r,forward_query_error=0,reverse_query_error=0,
                              matched_reset_available_declared=True)


def test_next_reverse_query_gives_larger_guaranteed_width_refinement():
    r=identify_bounded_switching(UP,DOWN,**KW)
    p=plan_reset_refinement(r,forward_query_error='.005',reverse_query_error='.005',
                           matched_reset_available_declared=True)
    assert p.best_directions==('reverse',)
    assert p.options[1].query_phi==-.065
    assert p.guaranteed_width_span_reduction==pytest.approx(.015)
    assert p.options[1].worst_case_next_span==pytest.approx(.025)


def test_no_guaranteed_refinement_below_query_noise_floor():
    r=identify_bounded_switching(UP,DOWN,**KW)
    p=plan_reset_refinement(r,forward_query_error='.015',reverse_query_error='.02',
                           matched_reset_available_declared=True)
    assert p.best_directions==()
    assert p.status=='query_error_floor'
    assert p.guaranteed_width_span_reduction==0


def test_midpoint_requires_restoring_old_state_not_unreset_trajectory():
    r=identify_bounded_switching(UP,DOWN,**KW)
    with pytest.raises(ValueError,match='reset'):
        plan_reset_refinement(r,forward_query_error=0,reverse_query_error=0,
                              matched_reset_available_declared=False)


@pytest.mark.parametrize('up', [[], [('.1','.11','differentiated')],
    [('.2','.3','shared'),('.1','.15','differentiated')],
    [('0','1','shared'),('0','1','differentiated'),('0','1','shared')],
    [('.2','.1','shared')],[(float('nan'),1,'shared')],[(0,1,'unknown')],
    [(0,0,'shared'),(0,0,'differentiated')]])
def test_inconsistent_or_invalid_paths_rejected(up):
    with pytest.raises(ValueError):
        identify_bounded_switching(up,DOWN,**KW)


@pytest.mark.parametrize('horizon', [(0,1),(2,1),(1,float('inf'))])
def test_invalid_horizon_rejected(horizon):
    with pytest.raises(ValueError):
        identify_bounded_switching(UP,DOWN,**KW,horizon_bounds=horizon)


def test_worst_case_query_formula_by_direct_branch_widths():
    for lo in (F(0),F('0.1')):
        for w in (F('0.01'),F('0.1'),F('0.3')):
            for e in (F(0),F('0.002'),F('0.03'),F('0.3')):
                hi=lo+w
                q=(lo+hi)/2
                stay_span=hi-max(lo,q-e)
                switch_span=min(hi,q+e)-lo
                assert max(stay_span,switch_span)==min(w,w/2+e)

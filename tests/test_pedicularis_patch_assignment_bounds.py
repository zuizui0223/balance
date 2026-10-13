"""Exact relaxed-partition algebra tests, never artificial empirical patch IDs."""
import itertools
import pytest
from balance_domain.pedicularis_patch_assignment_bounds import (
    equal_patch_mean_envelope, density_contrast_envelope,
)


def brute(vals,k,m):
    lower=float("inf")
    upper=-float("inf")
    for assigned in itertools.product(range(k),repeat=len(vals)):
        sizes=[assigned.count(group) for group in range(k)]
        if min(sizes)<m:
            continue
        v=sum(sum(x for x,j in zip(vals,assigned) if j==group)/sizes[group]
              for group in range(k))/k
        lower=min(lower,v)
        upper=max(upper,v)
    return lower,upper


@pytest.mark.parametrize("values,k,m",[
    ([0,0,10,20,30,100],3,1),
    ([1,4,6,9,14,17],3,2),
    ([2,3,4,90,95,98],2,2),
    ([1,2,2,5,9,10],2,1),
])
def test_closed_form_matches_exhaustive_small_partition_oracle(values,k,m):
    actual=equal_patch_mean_envelope(values,k,m)
    expected=brute(values,k,m)
    assert actual["hypothetical_equal_patch_mean_lower_percent"]==pytest.approx(expected[0])
    assert actual["hypothetical_equal_patch_mean_upper_percent"]==pytest.approx(expected[1])
    assert actual["actual_patch_ids_observed"] is False


def test_reordering_original_records_does_not_change_extremes():
    vals=[0,15,22,80,85,98]
    expected=equal_patch_mean_envelope(vals,3,1)
    actual=equal_patch_mean_envelope(vals[::-1],3,1)
    assert actual==expected
    assert vals==[0,15,22,80,85,98]
    assert actual["extreme_allocation_group_sizes_only"]==[1,1,4]
    assert actual["patch_level_confidence_interval"] is False


def test_identical_values_have_zero_hypothetical_density_contrast():
    a=density_contrast_envelope([50]*10,[50]*13,2,3)
    assert a["relaxed_equal_patch_dense_minus_sparse_lower_pp"]==0
    assert a["relaxed_equal_patch_dense_minus_sparse_upper_pp"]==0
    assert a["causal_density_effect_identified"] is False


@pytest.mark.parametrize("vals,k,m",[
    ([1.,None,3.],2,1),
    ([1.,float("nan"),3.],2,1),
    ([1.,101.,3.],2,1),
    ([1.,True,3.],2,1),
    ([1.,2.,3.],2,0),
    ([1.,2.,3.],True,1),
    ([1.,2.,3.],2,2),
])
def test_fail_closed_on_invalid_source_support(vals,k,m):
    with pytest.raises(ValueError):
        equal_patch_mean_envelope(vals,k,m)


def test_minimum_patch_size_requires_total_support():
    with pytest.raises(ValueError):
        density_contrast_envelope([10]*26,[20]*32,5,6,6)

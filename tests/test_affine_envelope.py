import pytest

from balance_domain.affine_envelope import (
    affine_upper_envelope_segments,
    alternative_reserve,
    endpoint_reserve_certificate,
    threat_switch_bound,
)


def test_each_affine_alternative_appears_on_at_most_one_envelope_segment():
    segments = affine_upper_envelope_segments(
        slopes=[-1.0, 0.0, 1.0],
        intercepts=[2.0, 1.5, 0.0],
        start=0.0,
        end=3.0,
    )
    active = [segment.active_alternative for segment in segments]
    assert len(active) == len(set(active))
    assert len(segments) - 1 <= threat_switch_bound(3)


def test_multi_alternative_reserve_is_concave_on_affine_example():
    kwargs = dict(
        shared_slope=0.25,
        shared_intercept=2.5,
        alternative_slopes=[-0.5, 0.5, 1.25],
        alternative_intercepts=[1.0, 0.5, -1.0],
    )
    left = alternative_reserve(environment=0.5, **kwargs)
    right = alternative_reserve(environment=2.5, **kwargs)
    middle = alternative_reserve(environment=1.5, **kwargs)
    assert middle >= 0.5 * (left + right) - 1e-12


def test_positive_reserve_cannot_reenter_on_affine_path():
    kwargs = dict(
        shared_slope=0.0,
        shared_intercept=2.0,
        alternative_slopes=[0.0, 1.0],
        alternative_intercepts=[1.0, 0.0],
    )
    values = [alternative_reserve(environment=x, **kwargs) for x in [0, 1, 2, 3, 4]]
    positive_indices = [i for i, value in enumerate(values) if value > 0]
    assert positive_indices == list(range(min(positive_indices), max(positive_indices) + 1))


def test_positive_endpoint_reserves_certify_whole_interval():
    kwargs = dict(
        shared_slope=0.0,
        shared_intercept=4.0,
        alternative_slopes=[-0.5, 0.5],
        alternative_intercepts=[1.0, 1.0],
    )
    cert = endpoint_reserve_certificate(start=0.0, end=4.0, **kwargs)
    assert cert.positive_throughout_interval
    assert cert.interval_lower_bound == pytest.approx(1.0)
    for x in [0.5, 1.0, 2.0, 3.5]:
        assert alternative_reserve(environment=x, **kwargs) >= cert.interval_lower_bound - 1e-12


def test_nonpositive_endpoint_fails_positive_interval_certificate():
    cert = endpoint_reserve_certificate(
        start=0.0,
        end=4.0,
        shared_slope=0.0,
        shared_intercept=2.0,
        alternative_slopes=[1.0],
        alternative_intercepts=[0.0],
    )
    assert not cert.positive_throughout_interval
    assert cert.right_reserve == pytest.approx(-2.0)


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        affine_upper_envelope_segments([], [], start=0.0, end=1.0)
    with pytest.raises(ValueError):
        threat_switch_bound(0)

import pytest

from balance_domain.multi_alternative import classify_multi_alternative_middle_world
from balance_domain.phase import normalized_phase_point
from balance_domain.world import balance_domain_geometry, classify_middle_world
from balance_domain.worldlines import compare_worldlines


def test_world_geometry_rejects_boolean_parameters_before_float_coercion():
    with pytest.raises(ValueError, match="boolean"):
        balance_domain_geometry(True, 1.0)
    with pytest.raises(ValueError, match="boolean"):
        balance_domain_geometry(0.5, True)


def test_middle_world_scalar_route_rejects_boolean_evidence_and_tolerance():
    for args, kwargs in (
        ((True, 0.5, 1.0), {}),
        ((1.0, True, 1.0), {}),
        ((1.0, 0.5, True), {}),
        ((1.0, 0.5, 1.0), {"tolerance": True}),
    ):
        with pytest.raises(ValueError, match="boolean"):
            classify_middle_world(*args, **kwargs)


def test_normalized_phase_scalar_route_rejects_boolean_evidence_and_tolerance():
    for args, kwargs in (
        ((True, 0.5, 1.0), {}),
        ((1.0, True, 1.0), {}),
        ((1.0, 0.5, True), {}),
        ((1.0, 0.5, 1.0), {"tolerance": True}),
    ):
        with pytest.raises(ValueError, match="boolean"):
            normalized_phase_point(*args, **kwargs)


def test_direct_worldline_scalar_route_rejects_boolean_evidence():
    calls = (
        lambda: compare_worldlines(True, 9.0, 1.0),
        lambda: compare_worldlines(10.0, True, 1.0),
        lambda: compare_worldlines(10.0, 9.0, True),
        lambda: compare_worldlines(10.0, 9.0, 1.0, tolerance=True),
        lambda: compare_worldlines(10.0, 9.0, 1.0, decoupling=True, architecture_cost=1.0),
        lambda: compare_worldlines(10.0, 9.0, 1.0, decoupling=0.5, architecture_cost=True),
    )
    for call in calls:
        with pytest.raises(ValueError, match="boolean"):
            call()


def test_multi_alternative_scalar_route_rejects_boolean_evidence_and_tolerance():
    calls = (
        lambda: classify_multi_alternative_middle_world(True, (1.0, 2.0)),
        lambda: classify_multi_alternative_middle_world(1.0, (True, 2.0)),
        lambda: classify_multi_alternative_middle_world(1.0, (1.0, 2.0), atol=True),
    )
    for call in calls:
        with pytest.raises(ValueError, match="boolean"):
            call()

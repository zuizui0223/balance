import pytest

from balance_domain.domain_existence import classify_domain_path
from balance_domain.static import analyze_balance_path
from balance_domain.worldline_path import analyze_worldline_path


def test_static_balance_path_rejects_boolean_series_evidence():
    valid = dict(
        environment=[0.0, 1.0],
        conflict_load=[1.0, 1.0],
        decoupling=[0.5, 0.5],
        architecture_cost=[1.0, 1.0],
    )
    for field in valid:
        malformed = {name: list(values) for name, values in valid.items()}
        malformed[field][0] = True
        with pytest.raises(ValueError, match="boolean"):
            analyze_balance_path(**malformed)


def test_direct_worldline_path_rejects_boolean_series_and_tolerance():
    valid = dict(
        environment=[0.0, 1.0],
        shared_optimum_fitness=[10.0, 10.0],
        differentiated_optimum_fitness=[9.0, 9.0],
        conflict_load=[1.0, 1.0],
    )
    for field in valid:
        malformed = {name: list(values) for name, values in valid.items()}
        malformed[field][0] = True
        with pytest.raises(ValueError, match="boolean"):
            analyze_worldline_path(**malformed)

    with pytest.raises(ValueError, match="boolean"):
        analyze_worldline_path(**valid, tolerance=True)


def test_sampled_domain_path_rejects_boolean_series_and_tolerance():
    with pytest.raises(ValueError, match="boolean"):
        classify_domain_path([True, 1.0], [-1.0, -1.0])
    with pytest.raises(ValueError, match="boolean"):
        classify_domain_path([1.0, 1.0], [True, -1.0])
    with pytest.raises(ValueError, match="boolean"):
        classify_domain_path([1.0, 1.0], [-1.0, -1.0], tolerance=True)

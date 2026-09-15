import pytest

from balance_domain.factorial_selection import analyze_factorial_agent_selection
from balance_domain.q1b_pooling import dl_mkh


IDENTITY4 = (
    (1.0, 0.0, 0.0, 0.0),
    (0.0, 1.0, 0.0, 0.0),
    (0.0, 0.0, 1.0, 0.0),
    (0.0, 0.0, 0.0, 1.0),
)


def test_factorial_selection_rejects_boolean_treatment_slopes():
    for index in range(4):
        slopes = [1.0, 0.0, -1.0, 0.5]
        slopes[index] = True
        with pytest.raises(ValueError, match="boolean"):
            analyze_factorial_agent_selection(slopes)


def test_factorial_selection_rejects_boolean_covariance_cells_before_ready_state():
    covariance = [list(row) for row in IDENTITY4]
    covariance[1][2] = True
    covariance[2][1] = True
    with pytest.raises(ValueError, match="boolean"):
        analyze_factorial_agent_selection(
            [1.0, 0.0, -1.0, 0.5],
            slope_covariance=covariance,
            covariance_source="joint_model",
        )


def test_factorial_selection_rejects_boolean_tolerance():
    with pytest.raises(ValueError, match="boolean"):
        analyze_factorial_agent_selection(
            [1.0, 0.0, -1.0, 0.5],
            slope_covariance=IDENTITY4,
            covariance_source="joint_model",
            tolerance=True,
        )


def test_valid_factorial_joint_covariance_route_remains_ready():
    receipt = analyze_factorial_agent_selection(
        [1.0, 0.0, -1.0, 0.5],
        slope_covariance=IDENTITY4,
        covariance_source="joint_model",
    )
    assert receipt.state == "JOINT_MULTICONTRAST_READY"
    assert receipt.effect_size_ready


def test_q1b_pooling_rejects_boolean_effects_and_variances():
    with pytest.raises(ValueError, match="boolean"):
        dl_mkh([1.0, True, 3.0], [1.0, 1.0, 1.0])
    with pytest.raises(ValueError, match="boolean"):
        dl_mkh([1.0, 2.0, 3.0], [1.0, True, 1.0])


def test_valid_frozen_k3_pool_contract_remains_available():
    result = dl_mkh([1.0, 2.0, 3.0], [1.0, 1.0, 1.0])
    assert result["k"] == 3
    assert result["mu_fixed"] == pytest.approx(2.0)
    assert result["mu_random"] == pytest.approx(2.0)

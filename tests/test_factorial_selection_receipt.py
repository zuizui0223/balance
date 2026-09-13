import math

import pytest

from balance_domain.factorial_selection import (
    CONTRAST_ORDER,
    TREATMENT_ORDER,
    analyze_factorial_agent_selection,
)


def test_registered_orders_are_explicit():
    assert TREATMENT_ORDER == (
        "open_antagonist_present",
        "supplemented_antagonist_present",
        "open_antagonist_absent",
        "supplemented_antagonist_absent",
    )
    assert CONTRAST_ORDER == (
        "pollinator_given_antagonist_present",
        "pollinator_given_antagonist_absent",
        "antagonist_given_open_pollination",
        "antagonist_given_supplemented_pollination",
    )


def test_point_estimates_are_available_but_not_ready_without_joint_covariance():
    receipt = analyze_factorial_agent_selection((1.0, 2.0, 3.0, 4.0))
    assert receipt.mediated_contrasts == pytest.approx((-1.0, -1.0, -2.0, -2.0))
    assert receipt.interaction_contrast == pytest.approx(0.0)
    assert receipt.contrast_covariance is None
    assert receipt.contrast_standard_errors is None
    assert receipt.interaction_standard_error is None
    assert receipt.state == "POINT_ESTIMATES_ONLY_NOT_READY"
    assert not receipt.effect_size_ready


def test_joint_covariance_is_propagated_to_all_dependent_contrasts():
    identity = (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )
    receipt = analyze_factorial_agent_selection(
        (1.0, 2.0, 3.0, 4.0),
        slope_covariance=identity,
        covariance_source="joint_model",
    )

    assert receipt.mediated_contrasts == pytest.approx((-1.0, -1.0, -2.0, -2.0))
    expected = (
        (2.0, 0.0, 1.0, -1.0),
        (0.0, 2.0, -1.0, 1.0),
        (1.0, -1.0, 2.0, 0.0),
        (-1.0, 1.0, 0.0, 2.0),
    )
    assert receipt.contrast_covariance is not None
    for observed, wanted in zip(receipt.contrast_covariance, expected):
        assert observed == pytest.approx(wanted)
    assert receipt.contrast_standard_errors == pytest.approx(
        (math.sqrt(2.0),) * 4
    )
    assert receipt.interaction_standard_error == pytest.approx(2.0)
    assert receipt.covariance_source == "joint_model"
    assert receipt.state == "JOINT_MULTICONTRAST_READY"
    assert receipt.effect_size_ready


def test_interaction_is_the_same_context_difference_from_either_agent_axis():
    receipt = analyze_factorial_agent_selection((2.0, 1.0, 4.0, 1.0))
    p_present, p_absent, h_open, h_supplemented = receipt.mediated_contrasts
    assert receipt.interaction_contrast == pytest.approx(p_present - p_absent)
    assert receipt.interaction_contrast == pytest.approx(h_open - h_supplemented)
    assert receipt.interaction_contrast == pytest.approx(-2.0)


def test_covariance_provenance_is_required_for_readiness():
    covariance = (
        (0.1, 0.01, 0.0, 0.0),
        (0.01, 0.1, 0.0, 0.0),
        (0.0, 0.0, 0.1, 0.01),
        (0.0, 0.0, 0.01, 0.1),
    )
    with pytest.raises(ValueError, match="covariance_source"):
        analyze_factorial_agent_selection((0.1, 0.2, 0.3, 0.4), slope_covariance=covariance)
    with pytest.raises(ValueError, match="covariance_source"):
        analyze_factorial_agent_selection(
            (0.1, 0.2, 0.3, 0.4),
            slope_covariance=covariance,
            covariance_source="independent_standard_errors",
        )

    bootstrap = analyze_factorial_agent_selection(
        (0.1, 0.2, 0.3, 0.4),
        slope_covariance=covariance,
        covariance_source="raw_bootstrap",
    )
    assert bootstrap.effect_size_ready
    assert bootstrap.covariance_source == "raw_bootstrap"


def test_covariance_source_without_matrix_is_rejected():
    with pytest.raises(ValueError, match="requires slope_covariance"):
        analyze_factorial_agent_selection(
            (0.1, 0.2, 0.3, 0.4), covariance_source="joint_model"
        )


def test_invalid_covariance_shapes_asymmetry_and_indefiniteness_are_rejected():
    with pytest.raises(ValueError, match="4x4"):
        analyze_factorial_agent_selection(
            (0.1, 0.2, 0.3, 0.4),
            slope_covariance=((1.0, 0.0), (0.0, 1.0)),
            covariance_source="joint_model",
        )

    asymmetric = (
        (1.0, 0.2, 0.0, 0.0),
        (0.1, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )
    with pytest.raises(ValueError, match="symmetric"):
        analyze_factorial_agent_selection(
            (0.1, 0.2, 0.3, 0.4),
            slope_covariance=asymmetric,
            covariance_source="joint_model",
        )

    # Symmetric with non-negative diagonal, but the leading 2x2 block has
    # eigenvalues 3 and -1 and therefore cannot be a covariance matrix.
    indefinite = (
        (1.0, 2.0, 0.0, 0.0),
        (2.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )
    with pytest.raises(ValueError, match="positive semidefinite"):
        analyze_factorial_agent_selection(
            (0.1, 0.2, 0.3, 0.4),
            slope_covariance=indefinite,
            covariance_source="joint_model",
        )


def test_indefinite_covariance_rejection_is_invariant_to_positive_rescaling():
    base = (
        (1.0, 2.0, 0.0, 0.0),
        (2.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )
    for scale in (1e-12, 1.0, 1e12):
        scaled = tuple(tuple(scale * value for value in row) for row in base)
        with pytest.raises(ValueError, match="positive semidefinite"):
            analyze_factorial_agent_selection(
                (0.1, 0.2, 0.3, 0.4),
                slope_covariance=scaled,
                covariance_source="joint_model",
            )


def test_psd_covariance_readiness_and_standard_errors_scale_consistently():
    identity = (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )
    base = analyze_factorial_agent_selection(
        (0.1, 0.2, 0.3, 0.4),
        slope_covariance=identity,
        covariance_source="joint_model",
    )
    for scale in (1e-12, 1e12):
        scaled_covariance = tuple(
            tuple(scale * value for value in row)
            for row in identity
        )
        scaled = analyze_factorial_agent_selection(
            (0.1, 0.2, 0.3, 0.4),
            slope_covariance=scaled_covariance,
            covariance_source="joint_model",
        )
        assert scaled.effect_size_ready
        assert scaled.contrast_standard_errors is not None
        assert base.contrast_standard_errors is not None
        expected_factor = math.sqrt(scale)
        assert scaled.contrast_standard_errors == pytest.approx(
            tuple(expected_factor * value for value in base.contrast_standard_errors)
        )
        assert scaled.interaction_standard_error == pytest.approx(
            expected_factor * base.interaction_standard_error
        )


def test_singular_positive_semidefinite_covariance_is_allowed():
    singular = (
        (1.0, 1.0, 0.0, 0.0),
        (1.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0, 0.0),
    )
    receipt = analyze_factorial_agent_selection(
        (0.1, 0.2, 0.3, 0.4),
        slope_covariance=singular,
        covariance_source="joint_model",
    )
    assert receipt.effect_size_ready
    assert receipt.contrast_standard_errors is not None
    assert all(value >= 0 for value in receipt.contrast_standard_errors)


def test_zero_covariance_is_a_valid_singular_psd_receipt():
    zero = tuple((0.0, 0.0, 0.0, 0.0) for _ in range(4))
    receipt = analyze_factorial_agent_selection(
        (0.1, 0.2, 0.3, 0.4),
        slope_covariance=zero,
        covariance_source="raw_bootstrap",
    )
    assert receipt.effect_size_ready
    assert receipt.contrast_standard_errors == (0.0, 0.0, 0.0, 0.0)
    assert receipt.interaction_standard_error == 0.0


def test_nonfinite_inputs_are_rejected():
    with pytest.raises(ValueError, match="finite"):
        analyze_factorial_agent_selection((0.1, float("nan"), 0.3, 0.4))
    with pytest.raises(ValueError, match="tolerance"):
        analyze_factorial_agent_selection((0.1, 0.2, 0.3, 0.4), tolerance=0.0)

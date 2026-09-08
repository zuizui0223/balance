import math

import pytest

from balance_domain.reported_factorial import (
    REPORTED_CONTRAST_ORDER,
    reconstruct_reported_factorial_contrasts,
)


def _fragaria_receipt():
    return reconstruct_reported_factorial_contrasts(
        (-0.022, 0.572, -0.391, 0.203),
        (0.314, 0.224, 0.125, 0.365),
        combined_contrast=0.181,
        combined_standard_error=0.213,
        interaction_f=2.366,
    )


def test_registered_reported_contrast_order_matches_q1b_contract():
    assert REPORTED_CONTRAST_ORDER == (
        "pollinator_given_antagonist_present",
        "pollinator_given_antagonist_absent",
        "antagonist_given_open_pollination",
        "antagonist_given_supplemented_pollination",
    )


def test_fragaria_table_s2_s3_reconstructs_joint_covariance_without_zero_assumption():
    receipt = _fragaria_receipt()
    assert receipt.effect_size_ready
    assert receipt.state == "REPORTED_FACTORIAL_JOINT_COVARIANCE_READY"
    assert receipt.covariance_source == "reported_contrasts_plus_combined_se_plus_interaction_f"
    assert receipt.interaction_contrast == pytest.approx(-0.594)
    assert receipt.interaction_standard_error == pytest.approx(0.3861704825451837)

    expected = (
        (0.098596, -0.000177820794590014, 0.005547820794590035, -0.093226),
        (-0.000177820794590014, 0.050176, -0.010216, 0.040137820794590016),
        (0.005547820794590035, -0.010216, 0.015625, -0.00013882079459003743),
        (-0.093226, 0.040137820794590016, -0.00013882079459003743, 0.133225),
    )
    for observed, wanted in zip(receipt.contrast_covariance, expected):
        assert observed == pytest.approx(wanted)

    # Critical safeguard: several reconstructed covariances are materially nonzero.
    assert receipt.contrast_covariance[0][3] == pytest.approx(-0.093226)
    assert receipt.contrast_covariance[1][3] == pytest.approx(0.040137820794590016)


def test_fragaria_factorial_identity_is_exact_in_points_and_covariance():
    receipt = _fragaria_receipt()
    a, b, c, d = receipt.mediated_contrasts
    assert a + d == pytest.approx(receipt.combined_contrast)
    assert b + c == pytest.approx(receipt.combined_contrast)
    assert a - b == pytest.approx(c - d)

    identity = (1.0, -1.0, -1.0, 1.0)
    for row in receipt.contrast_covariance:
        assert sum(w * x for w, x in zip(identity, row)) == pytest.approx(0.0, abs=1e-10)


def test_interaction_f_supplies_interaction_uncertainty():
    receipt = _fragaria_receipt()
    assert (receipt.interaction_contrast / receipt.interaction_standard_error) ** 2 == pytest.approx(2.366)


def test_incomplete_or_inconsistent_reported_statistics_fail_closed():
    with pytest.raises(ValueError, match="a \+ d"):
        reconstruct_reported_factorial_contrasts(
            (-0.022, 0.572, -0.391, 0.204),
            (0.314, 0.224, 0.125, 0.365),
            combined_contrast=0.181,
            combined_standard_error=0.213,
            interaction_f=2.366,
        )

    with pytest.raises(ValueError, match="interaction_f"):
        reconstruct_reported_factorial_contrasts(
            (-0.022, 0.572, -0.391, 0.203),
            (0.314, 0.224, 0.125, 0.365),
            combined_contrast=0.181,
            combined_standard_error=0.213,
            interaction_f=0.0,
        )

    with pytest.raises(ValueError, match="zero interaction estimate"):
        reconstruct_reported_factorial_contrasts(
            (0.1, 0.1, 0.2, 0.2),
            (0.1, 0.1, 0.1, 0.1),
            combined_contrast=0.3,
            combined_standard_error=0.2,
            interaction_f=1.0,
        )

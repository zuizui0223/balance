import json
import math
from fractions import Fraction as F
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "data" / "BALANCE_GYMNADENIA_Q1B_RECEIPT_V1.json"

# Rows map the frozen treatment order C+H, HP+H, C+E, HP+E to the
# registered Q1B mediated-contrast order.
C = (
    (1, -1, 0, 0),
    (0, 0, 1, -1),
    (1, 0, -1, 0),
    (0, 1, 0, -1),
)


def _load():
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def _linear_transform(matrix, vector):
    v = tuple(F.from_float(float(value)) for value in vector)
    return tuple(
        sum((F(weight) * value for weight, value in zip(row, v)), F(0))
        for row in matrix
    )


def _covariance_transform_from_independent_groups(standard_errors):
    variances = tuple(
        F.from_float(float(se)) ** 2
        for se in standard_errors
    )
    return tuple(
        tuple(
            sum(
                (
                    F(C[i][k]) * variances[k] * F(C[j][k])
                    for k in range(4)
                ),
                F(0),
            )
            for j in range(4)
        )
        for i in range(4)
    )


def test_gymnadenia_receipt_is_exact_linear_reconstruction_of_reported_groups():
    receipt = _load()
    assert receipt["treatment_group_independence"] == (
        "distinct plants in four factorial treatment groups"
    )
    assert receipt["covariance_source"] == (
        "linear contrasts of four independent treatment-group beta estimates using reported Table A2 SEs"
    )

    reconstructed_theta = _linear_transform(C, receipt["treatment_slopes"])
    assert tuple(float(value) for value in reconstructed_theta) == pytest.approx(
        receipt["mediated_contrasts"]
    )

    reconstructed_covariance = _covariance_transform_from_independent_groups(
        receipt["treatment_standard_errors"]
    )
    for observed, expected in zip(receipt["contrast_covariance"], reconstructed_covariance):
        assert observed == pytest.approx(tuple(float(value) for value in expected))

    reconstructed_se = tuple(
        math.sqrt(float(reconstructed_covariance[i][i]))
        for i in range(4)
    )
    assert receipt["contrast_standard_errors"] == pytest.approx(reconstructed_se)


def test_gymnadenia_receipt_preserves_registered_positive_q1b_pattern_and_ceiling():
    receipt = _load()
    p_present, p_absent, h_open, h_supplemented = receipt["mediated_contrasts"]
    assert p_present > 0
    assert p_absent > 0
    assert h_open < 0
    assert h_supplemented < 0
    assert receipt["q1b_positive_point_pattern"] is True
    assert receipt["effect_size_status"] == "EFFECT_SIZE_READY_REPORTED_FACTORIAL_RECONSTRUCTION"
    assert "not direct BALANCE occupancy" in receipt["claim_ceiling"]

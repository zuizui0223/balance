import json
from pathlib import Path

import pytest

from balance_domain.reported_factorial import reconstruct_reported_factorial_contrasts


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "data" / "BALANCE_FRAGARIA_Q1B_RECEIPT_V1.json"


def _receipt_json():
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_fragaria_receipt_is_first_q1b_effect_ready_but_not_pool_ready():
    receipt = _receipt_json()
    assert receipt["effect_size_status"] == "EFFECT_SIZE_READY_REPORTED_FACTORIAL_RECONSTRUCTION"
    assert receipt["q1b_effect_size_ready_clusters"] == 1
    assert receipt["q1b_min_independent_clusters"] == 3
    assert receipt["pooling_ready"] is False
    assert receipt["covariance_rank"] == 3
    assert receipt["covariance_psd"] is True


def test_fragaria_receipt_recomputes_from_registered_source_statistics():
    stored = _receipt_json()
    rebuilt = reconstruct_reported_factorial_contrasts(
        stored["mediated_contrasts"],
        stored["contrast_standard_errors"],
        combined_contrast=stored["combined_contrast"],
        combined_standard_error=stored["combined_standard_error"],
        interaction_f=stored["interaction_f"],
    )

    assert rebuilt.effect_size_ready
    assert rebuilt.mediated_contrasts == pytest.approx(stored["mediated_contrasts"])
    assert rebuilt.contrast_standard_errors == pytest.approx(stored["contrast_standard_errors"])
    assert rebuilt.interaction_contrast == pytest.approx(stored["interaction_contrast"])
    assert rebuilt.interaction_standard_error == pytest.approx(stored["interaction_standard_error"])
    for observed, expected in zip(rebuilt.contrast_covariance, stored["contrast_covariance"]):
        assert observed == pytest.approx(expected)


def test_fragaria_receipt_keeps_direct_balance_parameters_unidentified():
    receipt = _receipt_json()
    assert receipt["claim_ceiling"] == "joint_multicontrast_selection_pattern_not_direct_BALANCE_occupancy"
    assert set(receipt["not_identified"]) == {"W_S_star", "W_D_star", "rho", "Phi", "xi", "d_B"}

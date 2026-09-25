from pathlib import Path

from balance_domain.plant_u3_partial_identification import (
    build_u3_conflict_partial_identification,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
ADJ = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv"
EXTRACT = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv"


def _readout():
    return build_u3_conflict_partial_identification(
        EXTRACT, ADJ, PAIRS, CASES, U3
    )


def test_current_binary_conflict_bounds_are_narrow_despite_osbeckia_unknown():
    out = _readout()
    assert out["n_pairs"] == 4
    assert out["case_positive_fraction_bounds"] == [1.0, 1.0]
    assert out["control_positive_fraction_bounds"] == [0.75, 1.0]
    assert out["case_minus_control_positive_fraction_bounds"] == [0.0, 0.25]
    assert out["case_positive_control_negative_pair_count_bounds"] == [0, 1]
    assert out["case_positive_control_negative_pair_fraction_bounds"] == [0.0, 0.25]
    assert out["case_negative_control_positive_pair_count_bounds"] == [0, 0]
    assert out["binary_informative_pair_count_bounds"] == [0, 1]
    assert (
        out["finite_conditional_binary_effect_estimable_under_any_admissible_completion"]
        is False
    )


def test_binary_conflict_presence_cannot_deterministically_separate_heteranthery():
    out = _readout()
    assert out["binary_conflict_presence_deterministically_separates_heteranthery"] is False
    assert out["positive_control_taxa"] == [
        "Senna covesii",
        "Senna spectabilis",
        "Solanum lycocarpum",
    ]
    assert out["unresolved_control_taxa"] == ["Osbeckia chinensis"]


def test_claim_ceiling_forbids_population_prevalence_and_causal_effect():
    out = _readout()
    assert "not_population_prevalence" in out["claim_ceiling"]
    assert "not_causal_effect" in out["claim_ceiling"]

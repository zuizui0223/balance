from pathlib import Path

from balance_domain.plant_u3_conflict_identification import (
    build_u3_binary_conflict_identification,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
ADJ = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv"
EXTRACT = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv"
DEPEND = ROOT / "data" / "BALANCE_PLANT_U3_DEPENDENCE_V1.csv"


def _readout():
    return build_u3_binary_conflict_identification(
        EXTRACT, DEPEND, ADJ, PAIRS, CASES, U3
    )


def test_every_registered_osbeckia_completion_has_nonfinite_binary_coefficient():
    out = _readout()
    assert out["n_matched_pairs"] == 4
    assert out["n_unresolved_conflict_rows"] == 1
    assert out["unresolved_conflict_rows"] == [
        {
            "pair_id": "U3_PAIR_MELMA_001",
            "taxon_role": "CONTROL",
            "taxon": "Osbeckia chinensis",
        }
    ]
    assert out["n_binary_completions"] == 2
    assert out["completion_identification_status_counts"] == {
        "NO_WITHIN_PAIR_CONFLICT_VARIATION": 1,
        "POSITIVE_DIRECTION_COMPLETE_SEPARATION": 1,
    }
    assert out["any_completion_has_finite_matched_log_odds_mle"] is False
    assert out["all_registered_completions_nonfinite"] is True
    assert (
        out["binary_conflict_discriminant_status"]
        == "NONIDENTIFYING_UNDER_ALL_REGISTERED_COMPLETIONS"
    )


def test_positive_conflict_is_not_sufficient_for_heteranthery():
    out = _readout()
    assert out["resolved_positive_nonheterantherous_controls"] == [
        "Senna covesii",
        "Senna spectabilis",
        "Solanum lycocarpum",
    ]
    assert out["n_resolved_positive_nonheterantherous_controls"] == 3
    assert out["resolved_positive_control_dependence_blocks"] == [
        "U3_DEP_SENNA_01",
        "U3_DEP_SOLANUM_01",
    ]
    assert out["n_resolved_positive_control_dependence_blocks"] == 2
    assert out["conflict_positive_sufficient_for_heteranthery"] is False
    assert out["sufficiency_falsified_by_positive_controls"] is True


def test_completion_with_osbeckia_positive_has_no_predictor_variation():
    out = _readout()
    row = next(
        r for r in out["completions"]
        if r["completion"]["U3_PAIR_MELMA_001:CONTROL"] == "POSITIVE"
    )
    assert row["identification_status"] == "NO_WITHIN_PAIR_CONFLICT_VARIATION"
    assert row["n_concordant_positive_pairs"] == 4
    assert row["conditional_log_odds_mle"] is None


def test_completion_with_osbeckia_negative_is_separated_not_finite():
    out = _readout()
    row = next(
        r for r in out["completions"]
        if r["completion"]["U3_PAIR_MELMA_001:CONTROL"]
        == "NO_DEMONSTRATED_CONFLICT"
    )
    assert row["identification_status"] == "POSITIVE_DIRECTION_COMPLETE_SEPARATION"
    assert row["n_case_positive_control_negative"] == 1
    assert row["n_case_negative_control_positive"] == 0
    assert row["conditional_log_odds_mle"] == "+inf"

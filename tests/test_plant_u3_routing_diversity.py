from pathlib import Path

from balance_domain.plant_u3_routing_diversity import (
    build_u3_routing_diversity_identification,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
ADJ = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv"
EXTRACT = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv"
DEPEND = ROOT / "data" / "BALANCE_PLANT_U3_DEPENDENCE_V1.csv"


def _readout():
    return build_u3_routing_diversity_identification(
        EXTRACT, DEPEND, ADJ, PAIRS, CASES, U3
    )


def test_positive_nonheterantherous_controls_have_at_least_two_routing_states():
    out = _readout()
    assert out["n_positive_controls"] == 3
    assert out["n_resolved_positive_controls"] == 2
    assert out["unresolved_positive_controls"] == ["Senna covesii"]
    assert out["minimum_observed_distinct_routing_states"] == 2
    assert out["resolved_routing_states"] == [
        "AMONG_FLOWER_MODULE_DIVISION",
        "WITHIN_FLOWER_DIVISION_OF_LABOUR",
    ]


def test_minimum_routing_diversity_spans_two_frozen_dependence_blocks():
    out = _readout()
    assert out["minimum_observed_dependence_blocks"] == 2
    assert out["resolved_dependence_blocks"] == [
        "U3_DEP_SENNA_01",
        "U3_DEP_SOLANUM_01",
    ]
    assert out["routing_non_degenerate_under_all_unresolved_completions"] is True
    assert out["binary_conflict_does_not_determine_unique_routing_state"] is True


def test_unresolved_completions_cannot_erase_observed_routing_diversity():
    out = _readout()
    receipts = {
        (r["taxon"], r["architecture_mode"], r["dependence_block_id"])
        for r in out["resolved_route_receipts"]
    }
    assert receipts == {
        (
            "Solanum lycocarpum",
            "AMONG_FLOWER_MODULE_DIVISION",
            "U3_DEP_SOLANUM_01",
        ),
        (
            "Senna spectabilis",
            "WITHIN_FLOWER_DIVISION_OF_LABOUR",
            "U3_DEP_SENNA_01",
        ),
    }
    assert "cannot erase" in out["completion_argument"]


def test_certificate_does_not_promote_routing_diversity_to_prevalence():
    out = _readout()
    assert "not_population_frequency" in out["claim_ceiling"]
    assert "not_causal_effect" in out["claim_ceiling"]

from pathlib import Path

from balance_domain.plant_u3_morphology_routing_identification import (
    build_u3_morphology_routing_identification,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
ADJ = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv"
EXTRACT = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv"


def _readout():
    return build_u3_morphology_routing_identification(
        EXTRACT, ADJ, PAIRS, CASES, U3
    )


def test_same_within_flower_route_occurs_across_heteranthery_contrast():
    out = _readout()
    receipts = out["same_route_counterexamples"]
    assert len(receipts) == 1
    r = receipts[0]
    assert r["case_taxon"] == "Senna alata"
    assert r["control_taxon"] == "Senna spectabilis"
    assert r["case_route"] == "WITHIN_FLOWER_DIVISION_OF_LABOUR"
    assert r["control_route"] == "WITHIN_FLOWER_DIVISION_OF_LABOUR"
    assert r["same_route"] is True


def test_nonheterantherous_control_falsifies_necessity_of_heteranthery_for_within_flower_division():
    out = _readout()
    assert out["heteranthery_not_necessary_for_within_flower_division_of_labour"] is True
    assert out["heteranthery_morphology_does_not_uniquely_identify_functional_routing"] is True
    assert out["nonheterantherous_positive_controls_with_within_flower_division"] == [
        {
            "pair_id": "U3_PAIR_SENAL_001",
            "taxon": "Senna spectabilis",
            "architecture_mode": "WITHIN_FLOWER_DIVISION_OF_LABOUR",
        }
    ]


def test_current_evaluable_pairs_include_same_and_different_routing_responses():
    out = _readout()
    assert out["n_evaluable_pairs_both_conflict_positive_and_route_resolved"] == 2
    assert out["n_same_route_morphology_discordant_pairs"] == 1
    assert out["n_different_route_morphology_discordant_pairs"] == 1
    by_pair = {r["pair_id"]: r for r in out["evaluable_pair_receipts"]}
    assert by_pair["U3_PAIR_SOLRO_001"]["same_route"] is False
    assert by_pair["U3_PAIR_SENAL_001"]["same_route"] is True


def test_certificate_does_not_overclaim_population_or_causation():
    out = _readout()
    assert "not_population_frequency" in out["claim_ceiling"]
    assert "not_causal_effect" in out["claim_ceiling"]

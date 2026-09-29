from pathlib import Path

from balance_domain.plant_u3_morphology_routing_nonidentifiability import (
    build_u3_morphology_routing_nonidentifiability,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
ADJ = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv"
EXTRACT = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv"
DEPEND = ROOT / "data" / "BALANCE_PLANT_U3_DEPENDENCE_V1.csv"


def _readout():
    return build_u3_morphology_routing_nonidentifiability(
        EXTRACT, DEPEND, ADJ, PAIRS, CASES, U3
    )


def test_nonheteranthery_maps_to_multiple_resolved_routes_across_blocks():
    out = _readout()
    assert out["same_nonheterantherous_morphology_different_routing_states"] is True
    assert out["minimum_nonheterantherous_routing_states"] == 2
    assert out["minimum_nonheterantherous_routing_dependence_blocks"] == 2
    receipts = {
        (r["taxon"], r["architecture_mode"], r["dependence_block_id"])
        for r in out["nonheterantherous_resolved_route_receipts"]
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


def test_same_within_flower_route_occurs_across_morphology_contrast():
    out = _readout()
    assert out["same_routing_state_different_heteranthery_morphologies"] is True
    receipts = out["matched_same_route_morphology_contrast_receipts"]
    assert len(receipts) == 1
    receipt = receipts[0]
    assert receipt["case_taxon"] == "Senna alata"
    assert receipt["control_taxon"] == "Senna spectabilis"
    assert receipt["case_route"] == "WITHIN_FLOWER_DIVISION_OF_LABOUR"
    assert receipt["control_route"] == "WITHIN_FLOWER_DIVISION_OF_LABOUR"


def test_morphology_and_routing_are_bidirectionally_nonidentifying_proxies():
    out = _readout()
    assert out["morphology_does_not_uniquely_identify_routing"] is True
    assert out["routing_does_not_uniquely_identify_morphology"] is True
    assert out["bidirectional_proxy_equivalence_rejected"] is True
    assert "not_population_frequency" in out["claim_ceiling"]
    assert "not_historical_causation" in out["claim_ceiling"]

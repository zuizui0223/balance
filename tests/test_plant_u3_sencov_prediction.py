from pathlib import Path

from balance_domain.plant_u3_sencov_prediction import (
    build_sencov_prediction_readout,
    load_sencov_prediction,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
ADJ = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv"
EXTRACT = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv"
DEPEND = ROOT / "data" / "BALANCE_PLANT_U3_DEPENDENCE_V1.csv"
PRED = ROOT / "data" / "BALANCE_PLANT_U3_SENCOV_ROUTING_PREDICTION_V1.json"


def _readout():
    return build_sencov_prediction_readout(
        PRED, EXTRACT, DEPEND, ADJ, PAIRS, CASES, U3
    )


def test_prediction_receipt_is_frozen_before_target_outcome():
    payload = load_sencov_prediction(PRED)
    assert payload["target"]["taxon"] == "Senna covesii"
    assert payload["target"]["routing_outcome_at_freeze"] == "UNRESOLVED"
    assert payload["target"]["predicted_routing_state"] == (
        "WITHIN_FLOWER_DIVISION_OF_LABOUR"
    )


def test_prediction_is_derived_from_two_resolved_control_routes():
    out = _readout()
    assert out["n_discovery_controls"] == 2
    assert out["n_discovery_dependence_blocks"] == 2
    receipts = {
        (r["taxon"], r["module_substrate"], r["routing_state"])
        for r in out["discovery_receipts"]
    }
    assert receipts == {
        (
            "Solanum lycocarpum",
            "REPEATED_FLOWERS",
            "AMONG_FLOWER_MODULE_DIVISION",
        ),
        (
            "Senna spectabilis",
            "SERIAL_WITHIN_FLOWER",
            "WITHIN_FLOWER_DIVISION_OF_LABOUR",
        ),
    }


def test_sencov_prediction_is_directional_and_falsifiable():
    out = _readout()
    assert out["target_conflict_status"] == "POSITIVE"
    assert out["target_module_substrate"] == "SERIAL_WITHIN_FLOWER"
    assert out["target_routing_status_at_freeze"] == "UNRESOLVED"
    assert out["predicted_routing_state"] == "WITHIN_FLOWER_DIVISION_OF_LABOUR"
    assert "falsifies" in out["falsification_rule"]


def test_prediction_does_not_claim_independent_block_replication():
    out = _readout()
    assert out["target_dependence_block_id"] == "U3_DEP_SENNA_01"
    assert out["target_is_independent_new_dependence_block"] is False
    assert "not_independent_block_replication" in out["claim_ceiling"]

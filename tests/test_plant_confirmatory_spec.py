import json
from pathlib import Path

from balance_domain.plant_confirmatory import load_plant_predictor_receipts
from balance_domain.plant_macro import PRIMARY_ARCHITECTURE_CLASSES, primary_architecture_class


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data" / "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V1.json"
TEMPLATE = ROOT / "data" / "BALANCE_PLANT_CONFIRMATORY_PREDICTOR_RECEIPT_TEMPLATE_V1.csv"


def test_frozen_model_spec_matches_executable_primary_mapping():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    mapping = spec["primary_response"]["mapping"]
    assert set(mapping) == set(PRIMARY_ARCHITECTURE_CLASSES)
    for class_name, modes in mapping.items():
        assert set(modes) == set(PRIMARY_ARCHITECTURE_CLASSES[class_name])
        for mode in modes:
            assert primary_architecture_class(mode) == class_name


def test_frozen_primary_model_has_no_data_dependent_fallback():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    assert spec["primary_model"]["no_data_dependent_fallback"] is True
    assert spec["primary_model"]["family"] == "hierarchical_multinomial"
    assert len(spec["registered_interaction_extensions"]) == 2


def test_signal_separation_is_explicitly_retained():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    assert "SIGNAL_SEPARATION" in spec["primary_response"]["mapping"]["NONSTRUCTURAL_SEPARATION"]


def test_mosaic_is_primary_even_without_binary_structural_classification():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    assert spec["primary_response"]["mapping"]["MOSAIC"] == ["POLYMORPHIC_OR_MOSAIC"]


def test_predictor_receipt_template_is_schema_valid():
    rows = load_plant_predictor_receipts(TEMPLATE)
    assert {row["predictor"] for row in rows} == {
        "module_substrate",
        "conflict_timing_geometry",
        "conflict_spatial_geometry",
    }
    rejected = [row for row in rows if row["adjudication_status"] == "REJECTED"]
    assert len(rejected) == 1
    assert rejected[0]["evidence_type"] == "OUTCOME_DERIVED"
    assert rejected[0]["outcome_independence"] == "FALSE"

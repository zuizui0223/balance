from pathlib import Path

from balance_domain.plant_u3_routing_readiness import build_u3_routing_readiness


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
ADJ = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv"
EXTRACT = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv"
DEPEND = ROOT / "data" / "BALANCE_PLANT_U3_DEPENDENCE_V1.csv"


def _readout():
    return build_u3_routing_readiness(EXTRACT, DEPEND, ADJ, PAIRS, CASES, U3)


def test_current_positive_control_routing_is_only_partly_resolved():
    out = _readout()
    assert out["n_controls"] == 4
    assert out["n_positive_conflict_controls"] == 3
    assert out["n_positive_controls_with_resolved_architecture"] == 2
    assert out["positive_control_architecture_resolution_fraction"] == 2 / 3
    assert out["positive_controls_with_unresolved_architecture"] == ["Senna covesii"]
    assert out["controls_with_unresolved_conflict"] == ["Osbeckia chinensis"]


def test_resolved_positive_controls_already_show_two_routing_architectures():
    out = _readout()
    assert out["resolved_positive_control_architectures"] == [
        "AMONG_FLOWER_MODULE_DIVISION",
        "WITHIN_FLOWER_DIVISION_OF_LABOUR",
    ]
    assert out["resolved_positive_control_dependence_blocks"] == [
        "U3_DEP_SENNA_01",
        "U3_DEP_SOLANUM_01",
    ]
    assert out["n_resolved_positive_control_dependence_blocks"] == 2
    assert out["n_shared_integrated_positive_controls"] == 0


def test_current_routing_model_is_not_ready_and_acquisition_remains_blinded():
    out = _readout()
    assert out["routing_model_ready"] is False
    assert out["next_evidence_targets"] == [
        "resolve_Senna_covesii_broader_routing_architecture",
        "resolve_Osbeckia_chinensis_conflict_then_routing_architecture",
        "expand_with_prospectively_matched_positive_conflict_controls_in_new_dependence_blocks",
    ]
    assert "selected under the frozen predictor-blind matching" in out["acquisition_guard"]

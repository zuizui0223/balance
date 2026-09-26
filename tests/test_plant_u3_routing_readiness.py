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


def test_current_routing_model_is_not_ready_and_expansion_is_exhausted():
    out = _readout()
    assert out["binary_conflict_identification_certificate"] == (
        "docs/BALANCE_PLANT_U3_BINARY_CONFLICT_IDENTIFICATION_V1.md"
    )
    assert (
        out["binary_conflict_discriminant_status"]
        == "NONIDENTIFYING_UNDER_ALL_REGISTERED_COMPLETIONS"
    )
    assert out["binary_conflict_any_completion_finite_mle"] is False
    assert out["binary_conflict_sufficiency_falsified"] is True
    assert out["routing_diversity_identification_certificate"] == (
        "docs/BALANCE_PLANT_U3_ROUTING_DIVERSITY_IDENTIFICATION_V1.md"
    )
    assert out["minimum_observed_positive_control_routing_states"] == 2
    assert out["minimum_observed_routing_dependence_blocks"] == 2
    assert out["routing_non_degenerate_under_all_unresolved_completions"] is True
    assert out["routing_measurement_complete"] is False
    assert out["prospective_routing_model_contract_frozen"] is False
    assert out["routing_model_ready"] is False
    assert out["public_retrieval_ceilings_frozen_for_current_unresolved_targets"] is True
    assert out["public_retrieval_ceiling_ledger"] == "data/BALANCE_PLANT_U3_EVIDENCE_CEILING_V1.csv"
    assert out["targeted_measurement_contract"] == "data/BALANCE_PLANT_U3_TARGETED_MEASUREMENT_SPEC_V2.json"
    assert out["targeted_measurement_targets"] == [
        "Monochoria australasica",
        "Monochoria cyanea",
        "Osbeckia chinensis",
        "Senna covesii",
    ]
    assert out["senna_covesii_routing_contract_frozen"] is True
    assert out["senna_covesii_shared_integrated_requires_equivalence"] is True
    assert out["prospective_expansion_queue"] == "data/BALANCE_PLANT_U3_ROUTING_EXPANSION_QUEUE_V1.csv"
    assert out["prospective_expansion_queue_exhausted"] is True
    assert out["n_prospective_expansion_blocks"] == 4
    assert out["n_prospective_expansion_evidence_ceiling_blocked"] == 4
    assert out["next_evidence_targets"] == [
        "collect_or_adjudicate_Senna_covesii_routing_under_U3MEAS_SENCOV_001",
        "collect_or_adjudicate_Osbeckia_conflict_under_U3MEAS_OSBCHI_001",
        "collect_or_adjudicate_Monochoria_pollination_under_frozen_exact_species_routes",
        "reopen_frozen_expansion_blocks_only_with_new_matching_stage_evidence",
    ]
    assert "selected under the frozen predictor-blind matching" in out["acquisition_guard"]
    assert "do not invent a minimum-n threshold post hoc" in out["model_readiness_rule"]
    assert out["sencov_estimability_contract"] == (
        "docs/BALANCE_PLANT_U3_SENCOV_ROUTING_ESTIMABILITY_V1.md"
    )
    assert out["sencov_estimability_targets_template"].endswith(
        "BALANCE_PLANT_U3_SENCOV_ROUTING_POWER_TARGETS_TEMPLATE_V1.json"
    )
    assert out["sencov_stage0_nuisance_template"].endswith(
        "BALANCE_PLANT_U3_SENCOV_STAGE0_NUISANCE_TEMPLATE_V1.json"
    )
    assert "prospective four-family expansion is exhausted" in out["model_readiness_rule"]

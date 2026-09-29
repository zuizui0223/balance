import json
from pathlib import Path

from balance_domain.plant_confirmatory import (
    build_receipt_screening_coverage,
    confirmatory_parameter_budget,
    load_plant_predictor_receipts,
    primary_module_opportunity,
    primary_spatial_exposure,
    primary_temporal_exposure,
)
from balance_domain.plant_macro import PRIMARY_ARCHITECTURE_CLASSES, primary_architecture_class


ROOT = Path(__file__).resolve().parents[1]
SPEC_V1 = ROOT / "data" / "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V1.json"
SPEC_V2 = ROOT / "data" / "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V2.json"
SPEC_V3 = ROOT / "data" / "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V3.json"
SPEC = ROOT / "data" / "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4.json"
TEMPLATE = ROOT / "data" / "BALANCE_PLANT_CONFIRMATORY_PREDICTOR_RECEIPT_TEMPLATE_V1.csv"
U1_FRAME = ROOT / "data" / "BALANCE_PLANT_U1_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U2_FRAME = ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"


def test_frozen_model_spec_matches_executable_primary_mapping():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    mapping = spec["primary_response"]["mapping"]
    assert set(mapping) == set(PRIMARY_ARCHITECTURE_CLASSES)
    for class_name, modes in mapping.items():
        assert set(modes) == set(PRIMARY_ARCHITECTURE_CLASSES[class_name])
        for mode in modes:
            assert primary_architecture_class(mode) == class_name


def test_frozen_primary_model_v4_has_universe_stratified_intercepts_and_no_fallback():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    assert spec["primary_model"]["no_outcome_dependent_fallback"] is True
    assert spec["primary_model"]["family"] == (
        "regularized_bayesian_multinomial_logit_with_universe_stratified_intercepts"
    )
    assert spec["primary_model"]["common_slopes_across_U2_U6"] is True
    assert spec["primary_fitting_universes"] == [
        "U2_BARRETT_2002",
        "U6_POLLEN_THEFT_HARGREAVES_2009",
    ]
    assert spec["registered_interaction_extension"]["id"] == "I1_MODULE_X_TIMING"


def test_v1_was_superseded_before_fit_by_parameter_budget():
    v1 = json.loads(SPEC_V1.read_text(encoding="utf-8"))
    assert v1["status"] == "SUPERSEDED_PRE_FIT_BY_V2_PARAMETER_BUDGET"
    assert v1["superseded_by"] == "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V2"


def test_v2_was_superseded_before_outcome_coding_by_spatial_support_audit():
    v2 = json.loads(SPEC_V2.read_text(encoding="utf-8"))
    assert v2["status"] == "SUPERSEDED_PRE_OUTCOME_BY_V3_SPATIAL_SUPPORT"
    assert v2["superseded_by"] == "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V3"


def test_v3_was_superseded_before_outcome_coding_by_universe_stratification():
    v3 = json.loads(SPEC_V3.read_text(encoding="utf-8"))
    assert v3["status"] == "SUPERSEDED_PRE_OUTCOME_BY_V4_UNIVERSE_STRATIFICATION"
    assert v3["superseded_by"] == "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4"


def test_v3_was_superseded_preoutcome_by_v4_universe_stratification():
    v3 = json.loads(SPEC_V3.read_text(encoding="utf-8"))
    assert v3["status"] == "SUPERSEDED_PRE_OUTCOME_BY_V4_UNIVERSE_STRATIFICATION"
    assert v3["superseded_by"] == "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4"


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



def _assert_outcome_blind_receipt_frame(path):
    rows = load_plant_predictor_receipts(path)
    assert len(rows) == 60
    assert len({row["cluster_id"] for row in rows}) == 20
    by_cluster = {}
    for row in rows:
        by_cluster.setdefault(row["cluster_id"], set()).add(row["predictor"])
        assert row["reported_value"] == "UNRESOLVED"
        assert row["evidence_type"] == "UNCLEAR"
        assert row["outcome_independence"] == "UNCERTAIN"
        assert row["adjudication_status"] == "SCREENED"
        assert row["source_id"]
        assert "architecture" not in row
        assert "conflict_status" not in row
    assert all(predictors == {
        "module_substrate",
        "conflict_timing_geometry",
        "conflict_spatial_geometry",
    } for predictors in by_cluster.values())


def test_u1_confirmatory_receipt_frame_is_frozen_outcome_blind():
    _assert_outcome_blind_receipt_frame(U1_FRAME)


def test_u2_predictor_screen_progress_is_outcome_independent_but_not_adjudicated():
    rows = load_plant_predictor_receipts(U2_FRAME)
    assert len(rows) == 60
    assert len({row["cluster_id"] for row in rows}) == 20
    assert all("architecture" not in row and "conflict_status" not in row for row in rows)

    coverage = build_receipt_screening_coverage(rows)
    assert coverage["by_predictor"]["module_substrate"]["n_outcome_independent_resolved"] == 8
    assert coverage["by_predictor"]["conflict_timing_geometry"]["n_outcome_independent_resolved"] == 8
    assert coverage["by_predictor"]["conflict_spatial_geometry"]["n_outcome_independent_resolved"] == 8
    assert coverage["n_complete_outcome_independent_clusters"] == 8
    assert coverage["complete_outcome_independent_clusters"] == [
        "Asclepias_exaltata",
        "Campsis_radicans",
        "Eichhornia_paniculata",
        "Epilobium_obcordatum",
        "Ipomopsis_aggregata",
        "Mimulus_aurantiacus",
        "Polemonium_viscosum",
        "Pontederia_sagittata",
    ]
    assert coverage["n_complete_adjudicated_clusters"] == 0
    assert coverage["promotion_rule"].startswith("SCREENED")



def test_v4_primary_predictor_contrast_mappings_match_executable_code():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    mapping = spec["primary_predictor_contrasts"]

    for coarse, raw_values in mapping["module_opportunity2"].items():
        assert all(primary_module_opportunity(raw) == coarse for raw in raw_values)
    for coarse, raw_values in mapping["temporal_exposure3"].items():
        assert all(primary_temporal_exposure(raw) == coarse for raw in raw_values)

    spatial = spec["secondary_predictor_contrast"]["spatial_exposure2"]
    for coarse in ("SAME_UNIT", "DISTRIBUTED"):
        assert all(primary_spatial_exposure(raw) == coarse for raw in spatial[coarse])


def test_v4_parameter_budget_is_frozen_before_outcome_coding():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    frozen = spec["parameter_budget_at_frozen_two_universes"]
    budget = confirmatory_parameter_budget()
    assert frozen["universe_intercepts"] == 6
    assert frozen["predictor_slope_coefficients"] == 9
    assert frozen["total_primary_coefficients"] == 15
    assert frozen["total_with_registered_interaction"] == 21
    assert budget["v4_universe_intercepts"] == 6
    assert budget["v4_slope_coefficients"] == 9
    assert budget["v4_total_primary_coefficients"] == 15
    assert budget["v4_total_with_interaction"] == 21


def test_v4_estimability_gate_guards_universe_and_predictor_confounding():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    gate = spec["estimability_gate"]
    assert gate["minimum_independent_dependence_blocks_per_response_class"] == 2
    assert gate["minimum_independent_dependence_blocks_per_primary_predictor_level"] == 2
    assert gate["minimum_rows_per_primary_sampling_universe"] == 2
    assert gate["both_primary_sampling_universes_must_be_present"] is True
    assert gate["primary_common_slope_design_matrix_must_be_full_rank"] is True
    assert gate["primary_universe_stratified_design_matrix_must_be_full_rank"] is True
    assert gate["failure_action"] == "DO_NOT_FIT_OR_DROP_TERMS_POST_HOC"


def test_v4_generality_hierarchy_is_preoutcome_and_timing_only_cross_universe():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    hierarchy = spec["claim_hierarchy"]
    assert hierarchy["cross_universe_replicated"]["contrast"] == (
        "temporal SIMULTANEOUS vs ORDERED_OR_ALTERNATING"
    )
    assert hierarchy["U2_anchored"]["contrasts"] == [
        "module SINGLE vs MODULAR",
        "temporal VARIABLE_CONTEXT contrasts",
    ]
    assert hierarchy["support_limited"]["contrast"] == "spatial SAME_UNIT vs DISTRIBUTED"

    spatial = spec["secondary_predictor_contrast"]["spatial_exposure2"]
    assert spatial["preoutcome_support"] == {"SAME_UNIT": 28, "DISTRIBUTED": 1}
    assert spatial["role"] == "secondary_descriptive_or_separate_sensitivity_only"



def test_v4_cross_universe_generality_is_reserved_for_replicated_timing_contrast():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    claim = spec["claim_hierarchy"]["cross_universe_replicated"]
    assert claim["contrast"] == "temporal SIMULTANEOUS vs ORDERED_OR_ALTERNATING"
    assert spec["claim_hierarchy"]["U2_anchored"]["contrasts"] == [
        "module SINGLE vs MODULAR",
        "temporal VARIABLE_CONTEXT contrasts",
    ]
    sensitivity = spec["temporal_generality_sensitivity"]
    assert sensitivity["id"] == "G1_UNIVERSE_X_ORDERED"
    assert sensitivity["additional_coefficients"] == 3
    assert sensitivity["total_coefficients"] == 18
    assert sensitivity["practical_interaction_margin_log_odds"] == 1

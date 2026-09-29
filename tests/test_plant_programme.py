from pathlib import Path

from balance_domain.plant_programme import build_plant_programme_map


ROOT = Path(__file__).resolve().parents[1]
U1 = ROOT / "data" / "BALANCE_PLANT_U1_SCREENING_PROVISIONAL_V1.csv"
U1_BLIND = ROOT / "data" / "BALANCE_PLANT_U1_BLIND_CONFLICT_SCREEN_V1.csv"
U1_PRODUCTION = ROOT / "data" / "BALANCE_PLANT_U1_PRODUCTION_BLIND_CONFLICT_SCREEN_V1.csv"
U2 = ROOT / "data" / "BALANCE_PLANT_U2_SCREENING_V1.csv"
U2_CONFLICT = ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv"
U3_CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
U3_UNIVERSE = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
U4 = ROOT / "data" / "BALANCE_PLANT_U4_CARNIVOROUS_CASES_V1.csv"
U6_FREEZE = ROOT / "data" / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"
U6_CODING = ROOT / "data" / "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv"
U6_ADJUDICATION = ROOT / "data" / "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv"
U6_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U6_DEPENDENCE = ROOT / "data" / "BALANCE_PLANT_U6_CROSS_UNIVERSE_DEPENDENCE_V1.csv"


def _readout():
    return build_plant_programme_map(
        u1_screening_path=U1,
        u2_screening_path=U2,
        u3_cases_path=U3_CASES,
        u3_universe_path=U3_UNIVERSE,
        u4_cases_path=U4,
        u1_blind_screen_path=U1_BLIND,
        u1_production_screen_path=U1_PRODUCTION,
        u2_conflict_screen_path=U2_CONFLICT,
        u6_freeze_path=U6_FREEZE,
        u6_coding_path=U6_CODING,
        u6_adjudication_path=U6_ADJUDICATION,
        u6_predictor_receipts_path=U6_RECEIPTS,
        u6_dependence_path=U6_DEPENDENCE,
    )


def test_programme_map_preserves_distinct_sampling_roles():
    out = _readout()
    roles = {x["sampling_role"] for x in out["lanes"].values()}
    assert len(roles) == 5
    assert out["pooled_prevalence_estimate"] is None
    assert out["primary_model_ready"] is False
    contract = out["primary_model_contract"]
    assert contract["specification"] == "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4"
    assert contract["response"] == "architecture_class4"
    assert contract["primary_universes"] == [
        "U2_BARRETT_2002",
        "U6_POLLEN_THEFT_HARGREAVES_2009",
    ]
    assert contract["external_validation_universes"] == [
        "U1_HAAS_LORTIE_2020",
    ]
    assert contract["fit_predictor_contrasts"] == [
        "module_opportunity2",
        "temporal_exposure3",
    ]
    assert contract["secondary_predictor_contrasts"] == [
        "spatial_exposure2",
    ]
    assert contract["maximum_main_fixed_coefficients"] == 15
    assert contract["universe_stratified_intercepts"] is True
    assert contract["predictor_receipts_required"] is True
    assert contract["outcome_dependent_fallback_allowed"] is False
    assert contract["u1_u3_u4_primary_denominator_allowed"] is False
    assert len(out["primary_model_blockers"]) == 5
    assert any("U6 independent double coding incomplete" in x for x in out["primary_model_blockers"])
    assert out["parallel_nonblocking_work"] == [
        "U1 independent coding as external specificity validation",
        "U3 matched/case-control measurements and controls",
        "U4 pollinator-prey mechanism stress test",
    ]


def test_u1_full47_source_screen_is_specificity_heavy_and_conflict_negative():
    u1 = _readout()["lanes"]["U1"]
    assert u1["n_records"] == 47
    assert u1["n_dependency_groups"] == 47
    assert u1["conflict_status_counts"] == {
        "ALIGNED_NO_CONFLICT": 1,
        "NO_DEMONSTRATED_CONFLICT": 46,
    }
    assert u1["conflict_status_counts"].get("POSITIVE", 0) == 0
    assert u1["strict_conflict_source_screen_complete"] is True
    assert u1["strict_conflict_positive_ids"] == []
    assert u1["strict_conflict_unresolved_ids"] == []

    provisional = u1["provisional_first20_macro_readout"]
    assert provisional["n_records"] == 20
    assert provisional["n_excluded"] == 13

def test_u2_uses_strict_conflict_ledger_not_stale_macro_status():
    u2 = _readout()["lanes"]["U2"]
    assert u2["n_records"] == 22
    assert u2["conflict_status_counts"] == {
        "NO_DEMONSTRATED_CONFLICT": 14,
        "POSITIVE": 8,
    }
    assert u2["strict_conflict_source_screen_complete"] is True
    provisional = u2["provisional_macro_readout"]
    assert provisional["n_records"] == 22

def test_u3_is_structural_positive_case_lane_not_prevalence_lane():
    u3 = _readout()["lanes"]["U3"]
    assert u3["n_source_resolved_cases"] == 6
    assert u3["n_direct_conflict_cases"] == 3
    assert u3["n_partial_conflict_cases"] == 3
    assert "prevalence" in u3["not_licensed"]


def test_u4_stress_test_contains_two_direct_positive_conflicts():
    u4 = _readout()["lanes"]["U4"]
    assert u4["n_species_cases"] == 10
    assert u4["n_positive_conflict"] == 2
    assert "SIGNAL_SEPARATION" in u4["architecture_modes_present"]



def test_u6_is_formal_conflict_first_lane_with_source_screened_predictors_only():
    u6 = _readout()["lanes"]["U6"]
    assert u6["n_records"] == 157
    assert u6["n_dependency_groups"] == 21
    assert u6["n_included_dependency_groups"] == 21
    assert u6["pass1_status"] == "PASS1_CLOSED_PASS2_CODING_OPEN"
    assert u6["pass2_coding_open"] is True
    assert u6["predictor_source_screen_complete_groups"] == 21
    assert u6["predictor_adjudicated_complete_groups"] == 0
    readiness = u6["evidence_readiness"]
    assert readiness["coding_complete"] is False
    assert readiness["adjudication_complete"] is False
    assert readiness["n_groups_with_three_adjudicated_independent_predictors"] == 0
    assert readiness["ready_for_combined_model_assembly"] is False

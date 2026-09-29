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
    )


def test_programme_map_preserves_distinct_sampling_roles():
    out = _readout()
    roles = {x["sampling_role"] for x in out["lanes"].values()}
    assert len(roles) == 4
    assert out["pooled_prevalence_estimate"] is None
    assert out["primary_model_ready"] is False
    contract = out["primary_model_contract"]
    assert contract["specification"] == "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V2"
    assert contract["response"] == "architecture_class4"
    assert contract["primary_universes"] == [
        "U1_HAAS_LORTIE_2020",
        "U2_BARRETT_2002",
        "U6_POLLEN_THEFT_HARGREAVES_2009",
    ]
    assert contract["fit_predictor_contrasts"] == [
        "module_opportunity2",
        "temporal_exposure3",
        "spatial_exposure2",
    ]
    assert contract["maximum_main_fixed_coefficients"] == 15
    assert contract["predictor_receipts_required"] is True
    assert contract["data_dependent_fallback_allowed"] is False
    assert contract["u3_u4_primary_denominator_allowed"] is False
    assert len(out["primary_model_blockers"]) == 6
    assert any("U6 independent double coding incomplete" in x for x in out["primary_model_blockers"])
    assert out["parallel_nonblocking_work"] == [
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

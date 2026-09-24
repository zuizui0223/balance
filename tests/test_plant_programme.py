from pathlib import Path

from balance_domain.plant_programme import build_plant_programme_map


ROOT = Path(__file__).resolve().parents[1]
U1 = ROOT / "data" / "BALANCE_PLANT_U1_SCREENING_PROVISIONAL_V1.csv"
U2 = ROOT / "data" / "BALANCE_PLANT_U2_SCREENING_V1.csv"
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
    )


def test_programme_map_preserves_distinct_sampling_roles():
    out = _readout()
    roles = {x["sampling_role"] for x in out["lanes"].values()}
    assert len(roles) == 4
    assert out["pooled_prevalence_estimate"] is None
    assert out["primary_model_ready"] is False


def test_u1_is_specificity_heavy_and_has_no_positive_conflict_in_provisional20():
    u1 = _readout()["lanes"]["U1"]
    assert u1["n_records"] == 20
    assert u1["conflict_status_counts"] == {
        "ALIGNED_NO_CONFLICT": 1,
        "NO_DEMONSTRATED_CONFLICT": 5,
        "UNRESOLVED": 14,
    }
    assert u1["conflict_status_counts"].get("POSITIVE", 0) == 0
    assert u1["n_excluded"] == 13


def test_u2_retains_positive_negative_and_unresolved_mechanism_calls():
    u2 = _readout()["lanes"]["U2"]
    assert u2["n_records"] == 22
    assert u2["conflict_status_counts"] == {
        "NO_DEMONSTRATED_CONFLICT": 2,
        "POSITIVE": 8,
        "UNRESOLVED": 12,
    }


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

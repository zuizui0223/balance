from pathlib import Path

from balance_domain.plant_estimability import class_support_from_rows, combined_class_support
from balance_domain.plant_macro import load_plant_macro_ledger


ROOT = Path(__file__).resolve().parents[1]
U1 = ROOT / "data" / "BALANCE_PLANT_U1_SCREENING_PROVISIONAL_V1.csv"
U2 = ROOT / "data" / "BALANCE_PLANT_U2_SCREENING_V1.csv"


def test_current_u1_first20_has_no_conflict_positive_primary_rows():
    out = class_support_from_rows(load_plant_macro_ledger(U1))
    assert out["n_records"] == 20
    assert out["n_conflict_positive"] == 0
    assert out["class_counts"] == {
        "SHARED": 0,
        "NONSTRUCTURAL_SEPARATION": 0,
        "STRUCTURAL_MODULE_DIVISION": 0,
        "MOSAIC": 0,
    }


def test_current_u2_screen_has_three_of_four_primary_classes_only():
    out = class_support_from_rows(load_plant_macro_ledger(U2))
    assert out["n_conflict_positive"] == 8
    assert out["class_counts"] == {
        "SHARED": 4,
        "NONSTRUCTURAL_SEPARATION": 3,
        "STRUCTURAL_MODULE_DIVISION": 0,
        "MOSAIC": 1,
    }
    assert out["missing_primary_classes"] == ["STRUCTURAL_MODULE_DIVISION"]
    assert out["all_primary_classes_present"] is False


def test_combined_first20_surface_is_not_four_class_fit_ready_and_does_not_recode():
    out = combined_class_support({
        "U1_FIRST20": load_plant_macro_ledger(U1),
        "U2": load_plant_macro_ledger(U2),
    })
    assert out["combined_screening_support"]["n_conflict_positive"] == 8
    assert out["combined_screening_support"]["missing_primary_classes"] == [
        "STRUCTURAL_MODULE_DIVISION"
    ]
    assert out["no_response_recoding_on_missing_class"] is True
    assert out["claim_ceiling"].startswith("screening_estimability")

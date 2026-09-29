from pathlib import Path

from balance_domain.plant_macro import load_plant_macro_ledger
from balance_domain.plant_universe_yield import build_estimand_yield_readout


ROOT = Path(__file__).resolve().parents[1]
U1 = ROOT / "data" / "BALANCE_PLANT_U1_SCREENING_PROVISIONAL_V1.csv"
U2 = ROOT / "data" / "BALANCE_PLANT_U2_SCREENING_PROVISIONAL_V1.csv"


def test_current_u1_u2_estimand_yield_readout_is_descriptive_only():
    readout = build_estimand_yield_readout(
        load_plant_macro_ledger(U1),
        load_plant_macro_ledger(U2),
    )

    assert readout["u1_broad_herbivory_pollination"]["n_records"] == 20
    assert readout["u1_broad_herbivory_pollination"]["n_conflict_positive"] == 0
    assert readout["u1_broad_herbivory_pollination"]["adjudication_status_counts"] == {
        "EXCLUDED": 13,
        "SCREENED": 7,
    }

    assert readout["u2_targeted_sexual_interference"]["n_records"] == 22
    assert readout["u2_targeted_sexual_interference"]["n_conflict_positive"] == 7
    assert readout["u2_targeted_sexual_interference"]["adjudication_status_counts"] == {
        "SCREENED": 22,
    }

    assert "not_a_natural_prevalence_comparison" in readout["forbidden_interpretation"]
    assert "pending_independent_coding" in readout["claim_ceiling"]


def test_u1_shared_coordinate_exclusions_remain_visible():
    readout = build_estimand_yield_readout(
        load_plant_macro_ledger(U1),
        load_plant_macro_ledger(U2),
    )
    assert readout["u1_broad_herbivory_pollination"]["exclusion_reason_counts"] == {
        "EXCLUDE_DIFFERENT_TRAITS_NO_SHARED_REPRODUCTIVE_COORDINATE": 13
    }


def test_u2_positive_architecture_signal_is_not_structural_only():
    readout = build_estimand_yield_readout(
        load_plant_macro_ledger(U1),
        load_plant_macro_ledger(U2),
    )
    modes = readout["u2_targeted_sexual_interference"]["architecture_mode_counts"]
    assert modes["SHARED_INTEGRATED"] >= 2
    assert modes["TEMPORAL_SEPARATION"] >= 1
    assert modes["SPATIAL_SEPARATION"] >= 1
    assert modes["TEMPORAL_AND_SPATIAL_SEPARATION"] >= 1

from pathlib import Path

from balance_domain.plant_macro import build_plant_macro_readout, load_plant_macro_ledger


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data" / "BALANCE_PLANT_MACRO_PILOT_V1.csv"


def test_plant_pilot_validates_and_stays_screening_only():
    rows = load_plant_macro_ledger(PILOT)
    assert len(rows) == 29
    assert all(r["adjudication_status"] == "SCREENED" for r in rows)
    assert all(r["primary_model_eligible"] == "false" for r in rows)


def test_plant_pilot_dependency_groups_prevent_context_pseudoreplication():
    readout = build_plant_macro_readout(PILOT)
    assert readout["n_records"] == 29
    assert readout["n_dependency_groups"] == 28


def test_plant_pilot_spans_all_required_architecture_modes():
    readout = build_plant_macro_readout(PILOT)
    modes = readout["architecture_mode_counts"]
    for mode in (
        "SHARED_INTEGRATED",
        "TEMPORAL_SEPARATION",
        "SPATIAL_SEPARATION",
        "TEMPORAL_AND_SPATIAL_SEPARATION",
        "WITHIN_FLOWER_DIVISION_OF_LABOUR",
        "AMONG_FLOWER_MODULE_DIVISION",
        "POLYMORPHIC_OR_MOSAIC",
        "UNRESOLVED",
    ):
        assert modes.get(mode, 0) > 0


def test_plant_pilot_retains_conflict_negative_and_aligned_controls():
    readout = build_plant_macro_readout(PILOT)
    conflict = readout["conflict_status_counts"]
    assert conflict["POSITIVE"] == 16
    assert conflict["NO_DEMONSTRATED_CONFLICT"] == 8
    assert conflict["ALIGNED_NO_CONFLICT"] == 1
    assert conflict["UNRESOLVED"] == 4


def test_architecture_is_not_called_resolution_for_all_rows():
    rows = load_plant_macro_ledger(PILOT)
    negative_architectures = {
        r["architecture_mode"]
        for r in rows
        if r["conflict_status"] != "POSITIVE"
    }
    assert "SHARED_INTEGRATED" in negative_architectures
    assert "SPATIAL_SEPARATION" in negative_architectures

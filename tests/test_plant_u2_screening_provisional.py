from pathlib import Path

from balance_domain.plant_macro import build_plant_macro_readout, load_plant_macro_ledger


ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "data" / "BALANCE_PLANT_U2_SCREENING_PROVISIONAL_V1.csv"


def test_u2_provisional_screen_validates_and_stays_nonconfirmatory():
    rows = load_plant_macro_ledger(SCREEN)
    assert len(rows) == 22
    assert all(r["adjudication_status"] == "SCREENED" for r in rows)
    assert all(r["primary_model_eligible"] == "false" for r in rows)


def test_u2_conflict_screen_is_conservative():
    readout = build_plant_macro_readout(SCREEN)
    assert readout["conflict_status_counts"] == {
        "NO_DEMONSTRATED_CONFLICT": 2,
        "POSITIVE": 7,
        "UNRESOLVED": 13,
    }


def test_u2_positive_conflict_systems_are_frozen_by_id():
    rows = load_plant_macro_ledger(SCREEN)
    positive = {
        r["dependency_group"]
        for r in rows
        if r["conflict_status"] == "POSITIVE"
    }
    assert positive == {
        "Campsis_radicans",
        "Asclepias_exaltata",
        "Mimulus_aurantiacus",
        "Polemonium_viscosum",
        "Eichhornia_paniculata",
        "Pontederia_sagittata",
        "Ipomopsis_aggregata",
    }


def test_u2_retains_direct_null_cases():
    rows = {r["dependency_group"]: r for r in load_plant_macro_ledger(SCREEN)}
    assert rows["Pontederia_cordata"]["conflict_status"] == "NO_DEMONSTRATED_CONFLICT"
    assert rows["Turnera_ulmifolia"]["conflict_status"] == "NO_DEMONSTRATED_CONFLICT"


def test_u2_positive_cases_span_nonstructural_architecture_modes():
    rows = [
        r
        for r in load_plant_macro_ledger(SCREEN)
        if r["conflict_status"] == "POSITIVE"
    ]
    modes = {r["architecture_mode"] for r in rows}
    assert {
        "SHARED_INTEGRATED",
        "TEMPORAL_SEPARATION",
        "SPATIAL_SEPARATION",
        "TEMPORAL_AND_SPATIAL_SEPARATION",
        "UNRESOLVED",
    } <= modes
    assert all(r["structural_module_division"] != "true" for r in rows)


def test_u2_architecture_does_not_imply_positive_conflict():
    rows = {r["dependency_group"]: r for r in load_plant_macro_ledger(SCREEN)}
    assert rows["Alpinia_kwangsiensis"]["architecture_mode"] == "TEMPORAL_AND_SPATIAL_SEPARATION"
    assert rows["Alpinia_kwangsiensis"]["conflict_status"] == "UNRESOLVED"
    for dep in (
        "Wachendorfia_paniculata",
        "Wachendorfia_brachyandra",
        "Wachendorfia_parviflora",
        "Wachendorfia_thyrsiflora",
    ):
        assert rows[dep]["architecture_mode"] == "POLYMORPHIC_OR_MOSAIC"
        assert rows[dep]["conflict_status"] == "UNRESOLVED"

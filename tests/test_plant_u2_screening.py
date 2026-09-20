from pathlib import Path

from balance_domain.plant_macro import build_plant_macro_readout, load_plant_macro_ledger


ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "data" / "BALANCE_PLANT_U2_SCREENING_V1.csv"


def test_u2_screening_ledger_validates_and_stays_nonconfirmatory():
    rows = load_plant_macro_ledger(SCREEN)
    assert len(rows) == 22
    assert len({r["dependency_group"] for r in rows}) == 22
    assert all(r["sampling_frame_id"] == "U2_BARRETT_2002" for r in rows)
    assert all(r["adjudication_status"] == "SCREENED" for r in rows)
    assert all(r["primary_model_eligible"] == "false" for r in rows)


def test_u2_screening_retains_positive_negative_and_unresolved_conflict_states():
    readout = build_plant_macro_readout(SCREEN)
    conflict = readout["conflict_status_counts"]
    assert conflict == {
        "NO_DEMONSTRATED_CONFLICT": 2,
        "POSITIVE": 8,
        "UNRESOLVED": 12,
    }


def test_u2_screening_does_not_force_polymorphisms_into_structural_binary():
    rows = load_plant_macro_ledger(SCREEN)
    polymorphic = [r for r in rows if r["architecture_mode"] == "POLYMORPHIC_OR_MOSAIC"]
    assert len(polymorphic) == 10
    assert all(r["structural_module_division"] == "unresolved" for r in polymorphic)


def test_u2_specificity_controls_are_preserved():
    rows = {r["dependency_group"]: r for r in load_plant_macro_ledger(SCREEN)}
    assert rows["Pontederia_cordata"]["conflict_status"] == "NO_DEMONSTRATED_CONFLICT"
    assert rows["Turnera_ulmifolia"]["conflict_status"] == "NO_DEMONSTRATED_CONFLICT"
    assert rows["Pontederia_cordata"]["primary_model_eligible"] == "false"
    assert rows["Turnera_ulmifolia"]["primary_model_eligible"] == "false"


def test_u2_direct_positive_cases_remain_screened_not_adjudicated():
    rows = {r["dependency_group"]: r for r in load_plant_macro_ledger(SCREEN)}
    for dep in (
        "Campsis_radicans",
        "Asclepias_exaltata",
        "Mimulus_aurantiacus",
        "Polemonium_viscosum",
        "Eichhornia_paniculata",
        "Pontederia_sagittata",
        "Epilobium_obcordatum",
        "Ipomopsis_aggregata",
    ):
        assert rows[dep]["conflict_status"] == "POSITIVE"
        assert rows[dep]["adjudication_status"] == "SCREENED"
        assert rows[dep]["primary_model_eligible"] == "false"


def test_u2_historical_heteranthery_is_not_promoted_from_morphology_alone():
    rows = {r["dependency_group"]: r for r in load_plant_macro_ledger(SCREEN)}
    for dep in ("Solanum_rostratum_historical", "Chamaecrista_fasciculata_historical"):
        assert rows[dep]["conflict_status"] == "UNRESOLVED"
        assert rows[dep]["architecture_mode"] == "UNRESOLVED"
        assert rows[dep]["evidence_quality"] == "LOW"


def test_u2_polemonium_retains_joint_spatiotemporal_architecture():
    rows = {r["dependency_group"]: r for r in load_plant_macro_ledger(SCREEN)}
    pole = rows["Polemonium_viscosum"]
    assert pole["conflict_status"] == "POSITIVE"
    assert pole["architecture_mode"] == "TEMPORAL_AND_SPATIAL_SEPARATION"
    assert pole["structural_module_division"] == "false"

from pathlib import Path

from balance_domain.plant_macro import build_plant_macro_readout, load_plant_macro_ledger
from balance_domain.plant_u1 import load_u1_source_resolution


ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "data" / "BALANCE_PLANT_U1_SCREENING_PROVISIONAL_V1.csv"
RESOLUTION = ROOT / "data" / "BALANCE_PLANT_U1_SOURCE_RESOLUTION_V1.csv"


def test_u1_provisional_screen_validates_and_stays_nonconfirmatory():
    rows = load_plant_macro_ledger(SCREEN)
    assert len(rows) == 20
    assert all(r["primary_model_eligible"] == "false" for r in rows)
    assert sum(r["adjudication_status"] == "SCREENED" for r in rows) == 7
    assert sum(r["adjudication_status"] == "EXCLUDED" for r in rows) == 13


def test_u1_provisional_screen_matches_the_source_ready_first20():
    screen = {r["dependency_group"] for r in load_plant_macro_ledger(SCREEN)}
    source = {r["dependency_group"] for r in load_u1_source_resolution(RESOLUTION)}
    assert screen == source
    assert len(screen) == 20


def test_u1_strict_shared_coordinate_gate_is_highly_selective():
    rows = load_plant_macro_ledger(SCREEN)
    excluded = [r for r in rows if r["adjudication_status"] == "EXCLUDED"]
    assert len(excluded) == 13
    assert all(
        r["exclusion_reason"] == "EXCLUDE_DIFFERENT_TRAITS_NO_SHARED_REPRODUCTIVE_COORDINATE"
        for r in excluded
    )
    assert all(r["architecture_mode"] == "NA" for r in excluded)
    assert all(r["structural_module_division"] == "na" for r in excluded)


def test_u1_provisional_conflict_screen_has_no_promoted_positive_case():
    readout = build_plant_macro_readout(SCREEN)
    assert readout["conflict_status_counts"] == {
        "ALIGNED_NO_CONFLICT": 1,
        "NO_DEMONSTRATED_CONFLICT": 5,
        "UNRESOLVED": 14,
    }


def test_u1_retains_aligned_and_no_conflict_specificity_cases():
    rows = {r["dependency_group"]: r for r in load_plant_macro_ledger(SCREEN)}
    assert rows["Castilleja_indivisa"]["conflict_status"] == "ALIGNED_NO_CONFLICT"
    for dep in (
        "Aechmea_pectinata",
        "Alstroemeria_ligtu_var_Simsii",
        "Bouvardia_ternifolia",
        "Centaurea_solstitialis",
        "Centrosema_virginianum",
    ):
        assert rows[dep]["conflict_status"] == "NO_DEMONSTRATED_CONFLICT"


def test_u1_cross_organ_interaction_examples_fail_s0_not_conflict_gate():
    rows = {r["dependency_group"]: r for r in load_plant_macro_ledger(SCREEN)}
    for dep in (
        "Alstroemeria_aurea",
        "Brassica_nigra",
        "Cucumis_melo",
        "Cucumis_sativus",
        "Cucurbita_moschata",
    ):
        assert rows[dep]["adjudication_status"] == "EXCLUDED"
        assert rows[dep]["architecture_mode"] == "NA"

from pathlib import Path

from balance_domain.plant_u3_controls import (
    build_u3_matched_control_readout,
    load_u3_matched_controls,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"


def test_real_u3_matched_control_registry_has_one_primary_record_per_case():
    rows = load_u3_matched_controls(PAIRS, CASES, U3)
    assert len(rows) == 6

    by_case = {r["case_taxon"]: r for r in rows}
    assert set(by_case) == {
        "Solanum rostratum",
        "Melastoma malabathricum",
        "Monochoria korsakowii",
        "Monochoria vaginalis",
        "Senna alata",
        "Senna bicapsularis",
    }

    expected_controls = {
        "Solanum rostratum": "Solanum lycocarpum",
        "Melastoma malabathricum": "Osbeckia chinensis",
        "Monochoria korsakowii": "Monochoria australasica",
        "Monochoria vaginalis": "Monochoria australasica",
        "Senna alata": "Senna spectabilis",
        "Senna bicapsularis": "Senna covesii",
    }
    statuses = {
        "Solanum rostratum": "ADJUDICATED",
        "Melastoma malabathricum": "ADJUDICATED",
        "Monochoria korsakowii": "SCREENED",
        "Monochoria vaginalis": "SCREENED",
        "Senna alata": "ADJUDICATED",
        "Senna bicapsularis": "ADJUDICATED",
    }
    for case, control in expected_controls.items():
        row = by_case[case]
        assert row["control_taxon"] == control
        assert row["pair_role"] == "PRIMARY"
        assert row["selection_status"] == statuses[case]
        assert row["predictor_blinding_status"] == "BLINDED"

    assert by_case["Solanum rostratum"]["animal_pollination_eligible"] is True
    assert by_case["Melastoma malabathricum"]["animal_pollination_eligible"] is True
    assert by_case["Monochoria korsakowii"]["animal_pollination_eligible"] is None
    assert by_case["Monochoria vaginalis"]["animal_pollination_eligible"] is None
    assert by_case["Senna alata"]["animal_pollination_eligible"] is True
    assert by_case["Senna alata"]["heteranthery_absence_confirmed"] is True
    assert by_case["Senna bicapsularis"]["animal_pollination_eligible"] is True
    assert by_case["Senna bicapsularis"]["heteranthery_absence_confirmed"] is True


def test_senna_alata_replacement_is_source_quality_selected_spectabilis():
    rows = load_u3_matched_controls(PAIRS, CASES, U3)
    row = next(r for r in rows if r["case_taxon"] == "Senna alata")
    assert row["control_taxon"] == "Senna spectabilis"
    assert row["selection_status"] == "ADJUDICATED"
    assert row["tie_break_used"] == "SOURCE_QUALITY"
    assert row["animal_pollination_eligible"] is True
    assert row["heteranthery_absence_confirmed"] is True


def test_melastoma_control_is_same_tribe_sister_lineage_not_fake_congener():
    rows = load_u3_matched_controls(PAIRS, CASES, U3)
    mel = next(r for r in rows if r["case_taxon"] == "Melastoma malabathricum")
    assert mel["control_taxon"] == "Osbeckia chinensis"
    assert mel["match_level"] == "SAME_TRIBE_SUBFAMILY"
    assert mel["tie_break_used"] == "PHYLOGENETIC_DISTANCE"
    assert "10.1002/tax.13349" in mel["phylogenetic_basis"]


def test_monochoria_shared_control_remains_explicitly_nonindependent():
    rows = load_u3_matched_controls(PAIRS, CASES, U3)
    by_case = {r["case_taxon"]: r for r in rows}
    assert by_case["Monochoria korsakowii"]["control_taxon"] == by_case[
        "Monochoria vaginalis"
    ]["control_taxon"]


def test_real_u3_matched_control_layer_has_only_monochoria_open():
    readout = build_u3_matched_control_readout(PAIRS, CASES, U3)
    assert readout["n_pairs"] == 6
    assert readout["n_registered_primary_pairs"] == 6
    assert readout["n_adjudicated_primary_pairs"] == 4
    assert readout["n_registered_case_taxa"] == 6
    assert readout["n_cases_with_registered_primary_control"] == 6
    assert readout["cases_without_registered_primary_control"] == []
    assert readout["screened_control_coverage_complete"] is True
    assert readout["n_cases_with_adjudicated_primary_control"] == 4
    assert set(readout["unmatched_case_taxa"]) == {
        "Monochoria korsakowii",
        "Monochoria vaginalis",
    }
    assert readout["case_control_layer_closed"] is False


def test_monochoria_pollination_eligibility_is_not_promoted_from_amegilla_territorial_record():
    rows = load_u3_matched_controls(PAIRS, CASES, U3)
    mon = [r for r in rows if r["control_taxon"] == "Monochoria australasica"]
    assert len(mon) == 2
    assert all(r["animal_pollination_eligible"] is None for r in mon)
    assert all(r["selection_status"] == "SCREENED" for r in mon)


def test_bicapsularis_replacement_is_source_quality_selected_covesii():
    rows = load_u3_matched_controls(PAIRS, CASES, U3)
    row = next(r for r in rows if r["case_taxon"] == "Senna bicapsularis")
    assert row["control_taxon"] == "Senna covesii"
    assert row["selection_status"] == "ADJUDICATED"
    assert row["tie_break_used"] == "SOURCE_QUALITY"
    assert row["animal_pollination_eligible"] is True
    assert row["heteranthery_absence_confirmed"] is True

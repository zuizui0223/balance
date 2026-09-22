from pathlib import Path

from balance_domain.plant_u3_controls import (
    build_u3_matched_control_readout,
    load_u3_matched_controls,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"


def test_real_u3_matched_control_registry_has_one_screened_primary_per_case():
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
        "Senna alata": "Senna surattensis",
        "Senna bicapsularis": "Senna surattensis",
    }
    for case, control in expected_controls.items():
        row = by_case[case]
        assert row["control_taxon"] == control
        assert row["pair_role"] == "PRIMARY"
        assert row["selection_status"] == "SCREENED"
        assert row["predictor_blinding_status"] == "BLINDED"
        assert row["animal_pollination_eligible"] is True
        assert row["heteranthery_absence_confirmed"] is True


def test_melastoma_control_is_same_tribe_sister_lineage_not_fake_congener():
    rows = load_u3_matched_controls(PAIRS, CASES, U3)
    mel = next(r for r in rows if r["case_taxon"] == "Melastoma malabathricum")
    assert mel["control_taxon"] == "Osbeckia chinensis"
    assert mel["match_level"] == "SAME_TRIBE_SUBFAMILY"
    assert mel["tie_break_used"] == "PHYLOGENETIC_DISTANCE"
    assert "10.1002/tax.13349" in mel["phylogenetic_basis"]


def test_shared_controls_remain_explicitly_nonindependent():
    rows = load_u3_matched_controls(PAIRS, CASES, U3)
    by_case = {r["case_taxon"]: r for r in rows}
    assert by_case["Monochoria korsakowii"]["control_taxon"] == by_case[
        "Monochoria vaginalis"
    ]["control_taxon"]
    assert by_case["Senna alata"]["control_taxon"] == by_case[
        "Senna bicapsularis"
    ]["control_taxon"]


def test_real_u3_matched_control_layer_has_full_screened_coverage_but_stays_open():
    readout = build_u3_matched_control_readout(PAIRS, CASES, U3)
    assert readout["n_pairs"] == 6
    assert readout["n_adjudicated_primary_pairs"] == 0
    assert readout["n_registered_case_taxa"] == 6
    assert readout["n_cases_with_adjudicated_primary_control"] == 0
    assert set(readout["unmatched_case_taxa"]) == {
        "Solanum rostratum",
        "Melastoma malabathricum",
        "Monochoria korsakowii",
        "Monochoria vaginalis",
        "Senna alata",
        "Senna bicapsularis",
    }
    assert readout["case_control_layer_closed"] is False

"""Source-anchored Solanum intervention ladders: reject statistical overclaims."""
import json

import pytest

from balance_domain.solanum_mechanical_gate import (
    SOURCE,
    build_solanum_mechanical_gate_evidence,
    source_receipts,
)


def test_published_three_study_programmes_are_not_three_evolutionary_transitions():
    report = build_solanum_mechanical_gate_evidence()
    assert report["study_programmes"] == 3
    assert report["species_distinct"] == 4
    assert report["independent_evolutionary_transition_replications"] == 0
    assert report["frozen_u3_and_v4_sample_counts_changed"] is False
    assert report["source_effects_newly_fitted"] == 0
    assert report["architecture_coder_rows_opened"] == 0


def test_2022_intervention_improved_mechanics_three_but_pollen_two():
    report = build_solanum_mechanical_gate_evidence()
    assert report["original_2022_species_with_positive_distal_velocity"] == 3
    assert report["original_2022_species_with_detected_pollen_release_gain"] == 2
    assert report["original_2022_species_with_nondetected_pollen_gain"] == 1
    by = {
        r["species"]: r
        for r in report["original_2022_treatment_stage_comparisons"]
    }
    assert set(by) == {
        "Solanum elaeagnifolium", "Solanum sisymbriifolium",
        "Solanum pyracanthos",
    }
    assert by["Solanum elaeagnifolium"][
        "experimental_2022_joined_minus_free_distal_velocity_mm_per_sec"
    ] == pytest.approx(110.047)
    assert by["Solanum sisymbriifolium"][
        "experimental_2022_joined_minus_free_distal_velocity_mm_per_sec"
    ] == pytest.approx(116.419)
    assert by["Solanum pyracanthos"][
        "experimental_2022_joined_minus_free_distal_velocity_mm_per_sec"
    ] == pytest.approx(63.273)
    assert by["Solanum elaeagnifolium"][
        "experimental_2022_joined_minus_free_sqrt_pollen_release"
    ] == pytest.approx(48.213)
    assert by["Solanum sisymbriifolium"][
        "experimental_2022_joined_minus_free_sqrt_pollen_release"
    ] == pytest.approx(38.313)
    assert by["Solanum pyracanthos"][
        "experimental_2022_joined_minus_free_sqrt_pollen_release"
    ] == pytest.approx(-12.332)
    assert by["Solanum pyracanthos"]["pollen_effect_original_p_report"] == "p=0.169"
    assert all(r["not_a_measure_of_paternal_fitness"] for r in by.values())


def test_2026_spectrum_amplitude_results_do_not_establish_zero_harmonic_effect():
    r = build_solanum_mechanical_gate_evidence()
    assert "0/2/4-harmonic" in r["2026_controlled_RMS_vs_harmonics"]
    pair = r["cross_experiment_same_species_probe"]
    assert pair["species"] == "Solanum pyracanthos"
    assert pair["identifies_saturation_or_pore_mechanism"] is False
    assert pair["identifies_cross_study_mediation"] is False
    assert "units" in pair["not_a_contradiction_because"]
    assert "do not interpret no detected effect as equivalent structures" in r[
        "inferences_prohibited"
    ]


def test_any_tampering_with_original_pollen_contrast_refused(tmp_path):
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    item = next(
        r for r in original["source_records"]
        if r["species"] == "Solanum pyracanthos"
        and r["stage"] == "FLOWER_ARCHITECTURE_TO_SOURCE_POLLEN_RELEASE"
    )
    item["estimated_contrast"] = 0.0
    path = tmp_path / "tampered.json"
    path.write_text(json.dumps(original), encoding="utf-8")
    with pytest.raises(ValueError, match="Table 3"):
        source_receipts(path)


def test_do_not_pretend_causal_mediation_or_new_2026_numbers(tmp_path):
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    item = next(
        r for r in original["source_records"]
        if r["programme"] == "SOLANUM_VIBRATION_SPECTRUM_2026"
        and r["stage"] == "CONTROLLED_INPUT_AMPLITUDE_TO_SOURCE_POLLEN_RELEASE"
    )
    item["numeric_effect_estimate"] = 5.0
    path = tmp_path / "fabricated_rms.json"
    path.write_text(json.dumps(original), encoding="utf-8")
    with pytest.raises(ValueError, match="numerical effects"):
        source_receipts(path)


def test_species_reuse_cannot_be_relabelled_as_independent_transition(tmp_path):
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    original["dependency_contract"][
        "papers_not_independent_evolutionary_transitions"
    ] = False
    path = tmp_path / "wrong_dependence.json"
    path.write_text(json.dumps(original), encoding="utf-8")
    with pytest.raises(ValueError, match="firewall"):
        source_receipts(path)


def test_original_sample_size_and_distal_units_are_immutable(tmp_path):
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    original["studies"][0]["n_buzz_measurements"] = 2400
    path = tmp_path / "wrong_denominator.json"
    path.write_text(json.dumps(original), encoding="utf-8")
    with pytest.raises(ValueError, match="nested buzz"):
        source_receipts(path)


def test_harmonics_nonsignificance_is_not_statistical_equivalence(tmp_path):
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    item = next(
        r for r in original["source_records"]
        if r["stage"] == "HARMONIC_CONTENT_TO_SOURCE_POLLEN_RELEASE"
    )
    item["direction"] = "PROVEN_NO_EFFECT"
    path = tmp_path / "equivalence_invented.json"
    path.write_text(json.dumps(original), encoding="utf-8")
    with pytest.raises(ValueError, match="qualitative source statement"):
        source_receipts(path)

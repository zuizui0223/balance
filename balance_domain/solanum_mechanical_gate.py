"""Original-study Solanum mechanical-gate evidence reconciliation.

Recomputes only published 2022 treatment model linear combinations; all
other observations are faithful source-reported classifications. No original
Dryad CSV is downloaded, no beta is re-fitted, and no cross-study biological
mediation, fitness, ancestry or BALANCE occupancy is estimated.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] /
          "data/BALANCE_SOLANUM_MECHANICAL_GATE_SOURCE_LADDER_20261120.json")
EXPECTED_PROGRAMMES = {
    "SOLANUM_ANTHER_CONE_2022": "10.1111/evo.14485",
    "SOLANUM_BUZZ_DURATION_2025": "10.1111/1365-2435.70189",
    "SOLANUM_VIBRATION_SPECTRUM_2026": "10.1242/jeb.253005",
}
VIBRATION = "FLOWER_ARCHITECTURE_TO_DISTAL_RMS_VELOCITY"
POLLEN = "FLOWER_ARCHITECTURE_TO_SOURCE_POLLEN_RELEASE"
SAME_SPECIES = "Solanum pyracanthos"
LOOSE = {"Solanum elaeagnifolium", "Solanum sisymbriifolium"}
EXP_2022 = set(LOOSE) | {SAME_SPECIES}


def source_receipts(path: Path = SOURCE) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema_version") != "BALANCE_SOLANUM_MECHANICAL_GATE_SOURCE_LADDER_V1":
        raise ValueError("Solanum source ladder schema changed")
    if obj.get("status") != "ORIGINAL_PUBLISHED_RESULTS_TRANSCRIPTION_NOT_ORIGINAL_DATA_REFIT":
        raise ValueError("This audit does not accept source-outcome refits")
    studies = obj["studies"]
    if len(studies) != 3:
        raise ValueError("Three, and only three, source programmes expected")
    if {x["programme"]: x["doi"] for x in studies} != EXPECTED_PROGRAMMES:
        raise ValueError("Source DOI/programme alignment changed")
    if any(s["n_independent_research_programmes"] != 1 or
           s["n_separate_evolutionary_transitions"] != 0 for s in studies):
        raise ValueError("Cannot count source studies as independent transitions")
    s2022 = next(x for x in studies if x["programme"] == "SOLANUM_ANTHER_CONE_2022")
    if s2022["n_buzz_measurements"] != 240:
        raise ValueError("Original 2022 total of nested buzz records changed")
    s2025 = next(x for x in studies if x["programme"] == "SOLANUM_BUZZ_DURATION_2025")
    if (s2025["n_flower_trials"], s2025["n_bees"], s2025["n_colonies"],
        s2025["n_buzz_measurements"]) != (80, 13, 1, 2101):
        raise ValueError("Original 2025 trial-bee-buzz hierarchy changed")
    s2026 = next(x for x in studies if x["programme"] == "SOLANUM_VIBRATION_SPECTRUM_2026")
    if "n_flower_trials" in s2026 or "n_bees" in s2026:
        raise ValueError("Do not invent 2026 sample size")
    dep = obj["dependency_contract"]
    required_true = (
        "solanum_pyracanthos_appears_in_both_2022_and_2026",
        "solanum_rostratum_already_in_frozen_BALANCE_U3",
        "papers_not_independent_evolutionary_transitions",
        "no_multinomial_architecture_outcomes_used",
        "no_genetic_paternity_or_architecture_cost_measured",
        "do_not_pool_2022_RMS_velocity_mm_s_with_2026_RMS_acceleration_m_s2",
        "do_not_use_2022_NULL_as_zero_effect_or_equivalence",
        "do_not_multiply_2022_and_2026_source_coefficients_into_mediation_estimate",
        "numerical_2026_contrast_unavailable_from_abstract",
        "no_2026_raw_csv_retrieved_in_this_audit",
    )
    if not all(dep.get(k) is True for k in required_true):
        raise ValueError("Biological evidence/dependence firewall is incomplete")

    rows = obj["source_records"]
    if len(rows) != 10 or len({
        (row["programme"], row["species"], row["stage"])
        for row in rows
    }) != 10:
        raise ValueError("Source interventions duplicated or missing")
    by_stage = {
        stage: {r["species"]: r for r in rows if r["stage"] == stage}
        for stage in (VIBRATION, POLLEN)
    }
    if set(by_stage[VIBRATION]) != EXP_2022 or set(by_stage[POLLEN]) != EXP_2022:
        raise ValueError("Complete three-species 2022 paired stage rows required")
    expected_values = {
        "Solanum elaeagnifolium": (63.273 + 46.774, -12.332 + 60.545, 9.38),
        "Solanum sisymbriifolium": (63.273 + 53.146, -12.332 + 50.645, 7.18),
        SAME_SPECIES: (63.273, -12.332, 8.915),
    }
    for species, (vib, pollen, pollen_se) in expected_values.items():
        velocity_row = by_stage[VIBRATION][species]
        pollen_row = by_stage[POLLEN][species]
        if velocity_row["programme"] != "SOLANUM_ANTHER_CONE_2022":
            raise ValueError("Wrong original study for anther intervention")
        if pollen_row["programme"] != "SOLANUM_ANTHER_CONE_2022":
            raise ValueError("Wrong original study for pollen release intervention")
        if velocity_row["outcome"] != "DISTAL_RMS_VELOCITY_MM_S":
            raise ValueError("2022 endpoint has incompatible vibrational unit")
        if pollen_row["outcome"] != "SQRT_POLLEN_GRAINS_PER_BUZZ":
            raise ValueError("2022 pollen effect is on square-root scale")
        if abs(velocity_row["estimated_contrast"] - vib) > 1e-8:
            raise ValueError("2022 vibration estimate does not match Table 2")
        if abs(pollen_row["estimated_contrast"] - pollen) > 1e-8:
            raise ValueError("2022 pollen contrast does not match Table 3")
        if abs(pollen_row["contrast_se"] - pollen_se) > 1e-8:
            raise ValueError("2022 pollen EMM SE does not match original report")
        if velocity_row["direction"] != "SIGNIFICANT_POSITIVE":
            raise ValueError("2022 original distal velocity direction changed")
        if species in LOOSE:
            if (velocity_row["architecture_baseline"] != "LOOSE_ANTHERS"
                or pollen_row["architecture_baseline"] != "LOOSE_ANTHERS"
                or pollen_row["direction"] != "SIGNIFICANT_POSITIVE"
                or pollen_row["p_report"] != "p<0.0001"):
                raise ValueError("Original loose-species intervention effects changed")
        else:
            if (velocity_row["architecture_baseline"] != "NATURALLY_COMPACT_UNJOINED"
                or pollen_row["architecture_baseline"] != "NATURALLY_COMPACT_UNJOINED"
                or pollen_row["direction"] != "NO_STATISTICALLY_DETECTED_CHANGE"
                or pollen_row["p_report"] != "p=0.169"):
                raise ValueError("Do not promote nonsignificance to equality")

    current = [r for r in rows if r["programme"] == "SOLANUM_VIBRATION_SPECTRUM_2026"]
    if (len(current) != 3 or {r["species"] for r in current} != {SAME_SPECIES}):
        raise ValueError("2026 single-species experimental scope changed")
    expected_2026 = {
        "CONTROLLED_INPUT_AMPLITUDE_TO_SOURCE_POLLEN_RELEASE": "POSITIVE_AMPLITUDE_EFFECT",
        "HARMONIC_CONTENT_TO_SOURCE_POLLEN_RELEASE": "NO_DETECTED_HARMONIC_EFFECT",
        "INPUT_VIBRATION_TO_DISTAL_ANTHER_VIBRATION": "WEAK_INPUT_DISTAL_CORRELATION",
    }
    if {r["stage"]: r["direction"] for r in current} != expected_2026:
        raise ValueError("2026 qualitative source statement changed")
    if any(r["numeric_effect_estimate"] is not None for r in current):
        raise ValueError("2026 numerical effects have not been independently sourced")
    return obj


def build_solanum_mechanical_gate_evidence(path: Path = SOURCE) -> dict:
    src = source_receipts(path)
    rows = src["source_records"]
    pairs = []
    for sp in sorted(EXP_2022):
        vib = next(r for r in rows if r["species"] == sp and r["stage"] == VIBRATION)
        pollen = next(r for r in rows if r["species"] == sp and r["stage"] == POLLEN)
        pairs.append({
            "species": sp,
            "baseline_architecture": vib["architecture_baseline"],
            "experimental_2022_joined_minus_free_distal_velocity_mm_per_sec": (
                vib["estimated_contrast"]
            ),
            "experimental_2022_joined_minus_free_sqrt_pollen_release": (
                pollen["estimated_contrast"]
            ),
            "pollen_effect_source_label": pollen["direction"],
            "pollen_effect_original_p_report": pollen["p_report"],
            "not_a_measure_of_paternal_fitness": True,
        })
    mechanical_count = sum(
        x["experimental_2022_joined_minus_free_distal_velocity_mm_per_sec"] > 0
        for x in pairs
    )
    functional_count = sum(
        x["pollen_effect_source_label"] == "SIGNIFICANT_POSITIVE" for x in pairs
    )
    if (mechanical_count, functional_count) != (3, 2):
        raise ValueError("Expected 3/3 vibration and 2/3 pollen source effects")

    different_inputs_same_species = {
        "species": SAME_SPECIES,
        "2022_joined_vs_free": "distal RMS velocity increased but source pollen release did not show a significant increase",
        "2026_input_RMS_levels": "pollen removal depended on RMS acceleration; no detectable effect of harmonics at the tested levels",
        "not_a_contradiction_because": (
            "2022 joined-vs-free architecture manipulation measured anther-tip "
            "velocity, while 2026 input stimulus RMS manipulation measured "
            "acceleration and pollen removal. Treatments, units, and available "
            "pollen contexts are not exchangeable."
        ),
        "identifies_saturation_or_pore_mechanism": False,
        "identifies_cross_study_mediation": False,
    }
    return {
        "analysis": "BALANCE_SOLANUM_PROXIMAL_MECHANICAL_GATE_V1",
        "status": "SOURCE_REPORTED_EFFECTS_ONLY_NOT_RAW_DATA_FITS",
        "study_programmes": len(src["studies"]),
        "species_distinct": src["dependency_contract"]["total_distinct_species_four"],
        "original_2022_treatment_stage_comparisons": pairs,
        "original_2022_species_with_positive_distal_velocity": mechanical_count,
        "original_2022_species_with_detected_pollen_release_gain": functional_count,
        "original_2022_species_with_nondetected_pollen_gain": len(pairs)-functional_count,
        "2025_observed_buzz_duration_to_pollen_release": (
            "authors reported positive time-dependent release, 0.027-0.036 "
            "of available pollen per cumulative buzzing second"
        ),
        "2026_controlled_RMS_vs_harmonics": (
            "input RMS amplitude predicts pollen removal; 0/2/4-harmonic "
            "treatments at 300 Hz did not show detectable additional release "
            "differences at tested RMS levels"
        ),
        "cross_experiment_same_species_probe": different_inputs_same_species,
        "independent_evolutionary_transition_replications": 0,
        "frozen_u3_and_v4_sample_counts_changed": False,
        "inferences_prohibited": [
            "do not pool velocity mm/s with acceleration m/s2",
            "do not infer a causal mediator from two separate papers",
            "do not interpret no detected effect as equivalent structures",
            "do not infer pollen collected on bee or donor paternity from anther release",
            "do not treat two source studies in same Solanum species as two evolutionary transitions",
            "do not back-infer BALANCE W_S W_D K or Phi from pollen release",
        ],
        "source_effects_newly_fitted": 0,
        "architecture_coder_rows_opened": 0,
    }

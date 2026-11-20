"""Published Solanum buzz-pollen model reproduction, without raw trial rows.

This module NEVER fits original bee observations. It re-evaluates the two
published exponential model coefficients on prospective buzzing durations,
and explicitly preserves source-vs-published-text discrepancies.
"""
from __future__ import annotations

import json
from math import exp, expm1, isfinite, log
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "data" / "BALANCE_SOLANUM_BUZZ_POLLEN_SOURCE_2025_V1.json"
DOI = "10.1111/1365-2435.70189"
ARCHIVE_DOI = "10.5061/dryad.kkwh70sh4"
TIMES_SECONDS = (0.0, 0.748, 1.0, 5.0, 10.0, 20.0, 30.0)


def source_readout(path: Path = SOURCE) -> dict:
    """Fail closed on changed original-paper identity or claim ceiling."""
    source = json.loads(path.read_text(encoding="utf-8"))
    if source.get("schema_version") != (
        "BALANCE_SOLANUM_ROSTRATUM_2025_BEHAVIOR_POLLEN_SOURCE_V1"
    ):
        raise ValueError("Unexpected Solanum source-audit schema")
    if source.get("status") != "PUBLISHED_MODEL_SOURCE_ONLY_NOT_RAW_DATA_REANALYSIS":
        raise ValueError("Refusing to classify this as a real-data refit")
    if source["publication"]["doi"] != DOI or source["archive"]["dryad_doi"] != ARCHIVE_DOI:
        raise ValueError("Primary publication/archive identity changed")
    if source["archive"]["source_file_bytes_retrieved"] is not False:
        raise ValueError("Publication-only source audit must not claim acquired microdata")
    if source["archive"]["original_csv_independently_refitted"] is not False:
        raise ValueError("Publication-only source audit must not claim new model fits")
    grain = source["biological_unit"]
    if (grain["observed_floral_trials"], grain["unique_bees"],
        grain["observed_buzzes"], grain["bumblebee_colonies"],
        grain["original_study_programmes"]) != (80, 13, 2101, 1, 1):
        raise ValueError("Original study dependence-grain receipt changed")
    if source["biological_inference_boundaries"]["no_male_genetic_paternity"] is not True:
        raise ValueError("Source cannot be upgraded to genetic paternity evidence")
    if source["biological_inference_boundaries"][
        "not_independent_evolutionary_lineage_from_prior_U3_S_rostratum"
    ] is not True:
        raise ValueError("Same-taxon U3 dependence must be preserved")
    m = source["published_models"]
    if (
        m["model1"]["rate_per_buzz_second"] != 0.027
        or m["model1"]["available_pollen_grains"] != 403314
        or m["bee_mixed"]["rate_per_buzz_second"] != 0.036
        or m["bee_mixed"]["table1_available_pollen_grains"] != 352284
        or m["bee_mixed"]["results_prose_available_pollen_grains"] != 352384
    ):
        raise ValueError("Published model-source numeric anchors changed")
    if (m["bee_mixed"]["results_prose_available_pollen_grains"]
        - m["bee_mixed"]["table1_available_pollen_grains"]) != 100:
        raise ValueError("Text/table A0 discrepancy must remain visible")
    return source


def pollen_release_curve(
    *, rate_per_buzz_second: float, cumulative_buzz_seconds: float,
    available_pollen_grains: float,
) -> dict[str, float]:
    """Compute conditional source-release curve; pollen grains not male fitness."""
    for name, value in (
        ("rate_per_buzz_second", rate_per_buzz_second),
        ("cumulative_buzz_seconds", cumulative_buzz_seconds),
        ("available_pollen_grains", available_pollen_grains),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a finite number")
        if not isfinite(value) or value < 0:
            raise ValueError(f"{name} must be nonnegative and finite")
    r = float(rate_per_buzz_second)
    t = float(cumulative_buzz_seconds)
    p = float(available_pollen_grains)
    if r <= 0 or p <= 0:
        raise ValueError("rate and available pollen must be strictly positive")
    remaining_fraction = exp(-r*t)
    released_fraction = -expm1(-r*t)
    if abs(remaining_fraction + released_fraction - 1) > 1e-12:
        raise ValueError("Source mass-balance identity failed")
    return {
        "cumulative_buzz_seconds": t,
        "available_pollen_start": p,
        "pollen_remaining_model": p*remaining_fraction,
        "pollen_released_model": p*released_fraction,
        "fraction_remaining": remaining_fraction,
        "fraction_released": released_fraction,
    }


def build_solanum_published_kinetics_audit(path: Path = SOURCE) -> dict:
    """Reproduce fitted-curve implications and uncertainty/provenance boundary."""
    s = source_readout(path)
    models = s["published_models"]
    rates = {
        "original_nonlinear_fit": {
            "r": models["model1"]["rate_per_buzz_second"],
            "A0": models["model1"]["available_pollen_grains"],
            "published_half_life": models["model1"]["paper_reported_half_life_seconds"],
        },
        "bee_mixed_log_linear_fit": {
            "r": models["bee_mixed"]["rate_per_buzz_second"],
            "A0": models["bee_mixed"]["table1_available_pollen_grains"],
            "published_half_life": models["bee_mixed"]["paper_reported_half_life_seconds"],
        },
    }
    results = {}
    for label, spec in rates.items():
        half_life = log(2)/spec["r"]
        if abs(half_life - spec["published_half_life"]) > 0.7:
            raise ValueError("Rounded published release-rate does not match half-life")
        results[label] = {
            "source_fitted_rate_per_buzz_second": spec["r"],
            "source_fitted_available_pollen_A0": spec["A0"],
            "half_life_using_rounded_r_seconds": half_life,
            "paper_reported_half_life_seconds": spec["published_half_life"],
            "predictions_at_prespecified_buzz_duration_seconds": [
                pollen_release_curve(
                    rate_per_buzz_second=spec["r"],
                    cumulative_buzz_seconds=t,
                    available_pollen_grains=spec["A0"],
                )
                for t in TIMES_SECONDS
            ],
        }
    return {
        "analysis": "BALANCE_SOLANUM_PUBLISHED_BUZZ_TO_POLLEN_SOURCE_V1",
        "status": "REEXPRESSION_OF_PUBLISHED_FITS_NOT_NEW_FIT",
        "published_online_date": s["publication"]["online_date"],
        "journal_issue_citation": s["publication"]["issue_citation"],
        "original_article_doi": DOI,
        "published_dataset_doi": ARCHIVE_DOI,
        "focal_plant": s["biological_unit"]["focal_plant"],
        "bee_species": s["biological_unit"]["focal_pollinator"],
        "sampling_grain": {
            "flowers": s["biological_unit"]["observed_floral_trials"],
            "bees": s["biological_unit"]["unique_bees"],
            "colonies": s["biological_unit"]["bumblebee_colonies"],
            "buzzes_nested_not_independent": s["biological_unit"]["observed_buzzes"],
            "independent_research_programmes": 1,
            "independent_evolutionary_transition_replications": 0,
        },
        "published_model_predictions": results,
        "original_mean_buzz_duration_seconds": s["published_observations"][
            "buzz_duration_mean_seconds"
        ],
        "text_table_pollen_A0_conflict": {
            "table1_A0": models["bee_mixed"]["table1_available_pollen_grains"],
            "results_prose_A0": models["bee_mixed"]["results_prose_available_pollen_grains"],
            "difference_grains": models["bee_mixed"]["prose_table_difference_grains"],
            "state": "SOURCE_DISCREPANCY_UNRESOLVED_NOT_SILENTLY_CORRECTED",
        },
        "pollen_available_fraction_alternative_assumptions": {
            "using_mean_control_total": models["model2a"]["available_fraction"],
            "using_maximum_pollen_remaining": models["model2b"]["available_fraction"],
            "different_denominators_not_a_statistical_confidence_interval": True,
        },
        "published_raw_data_reanalysed": False,
        "new_original_biological_effects_estimated": 0,
        "independent_species_level_replication_added_to_U3": False,
        "paternity_or_net_architecture_fitness_identified": False,
        "q_threshold_and_thief_order_tested": False,
        "claim_ceiling": (
            "published_buzz_to_source_pollen_kinetics_reexpressed_not_"
            "genetic_paternity_or_architecture_selection"
        ),
    }

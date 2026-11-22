"""Source-constrained pollen-stage re-expression of Vasquez-Castro et al. (2025).

All source numeric values here are *already published group summaries*.
We do not recreate individual donor trials, estimate new p values, treat
15 experiments as 60 independent observations or infer flower architecture
causes the between-species comparisons.

The product of the two source-reported percentages is explicitly only a
descriptive product of two rounded *means*, not an unbiased sample mean of
per-trial products.
"""
from __future__ import annotations

import json
from math import exp, isclose
from pathlib import Path

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "data" / "BALANCE_VASQUEZ_CASTRO_2025_FATES_SOURCE_V1.json"
)


def source_values(path: Path = SOURCE) -> dict:
    source = json.loads(path.read_text(encoding="utf-8"))
    if source.get("schema_version") != "BALANCE_VASQUEZ_CASTRO_2025_POLLEN_FATES_SOURCE_V1":
        raise ValueError("Unrecognized original-paper source receipt")
    if source.get("status") != "PUBLISHED_SOURCE_NUMBERS_VERIFIED_RAW_TRIAL_DATA_NOT_YET_FETCHED":
        raise ValueError("Publication-only receipt must not silently claim refit")
    if (
        source["article"]["doi"] != "10.26786/1920-7603(2025)836"
        or source["dataset"]["record_id"] != 17102653
        or source["dataset"]["raw_original_trials_retrieved"] is not False
    ):
        raise ValueError("Original source DOI, archive or data recovery status changed")
    if source["design"]["recipient_stigmas_total"] != 60:
        raise ValueError("Expected nested recipient count 60")
    if source["design"]["primary_replicate"] != "one donor-bee-to-four-recipient trial":
        raise ValueError("Trial-level experimental independence changed")
    if source["design"]["completed_donor_trials"] != {
        "Solanum rostratum": 6, "Solanum dulcamara": 9
    }:
        raise ValueError("Original two-species trial counts changed")
    expected = {
        "Solanum rostratum": (13.55, 62.99, 27.65, 8.54, 0.86),
        "Solanum dulcamara": (37.77, 19.07, 65.92, 14.01, 1.00),
    }
    for sp, values in expected.items():
        row = source["published_source_results"][sp]
        observed = (
            row["source_pollen_removal_as_pct_total"],
            row["percent_removed_to_ground"],
            row["percent_removed_to_basket"],
            row["percent_removed_left_on_body"],
            row["percent_removed_to_stigmas"],
        )
        if observed != values:
            raise ValueError("Original published denominator or species means changed")
    if not all(source["scientific_ceiling"].values()):
        raise ValueError("Reject publication evidence upgraded to unsupported architecture fitness")
    return source


def build_source_pollen_fates(path: Path = SOURCE) -> dict:
    src = source_values(path)
    rows = []
    for sp, row in src["published_source_results"].items():
        removal = row["source_pollen_removal_as_pct_total"]
        fate = {
            "ground": row["percent_removed_to_ground"],
            "basket": row["percent_removed_to_basket"],
            "body": row["percent_removed_left_on_body"],
            "stigmas": row["percent_removed_to_stigmas"],
        }
        total = sum(fate.values())
        if not isclose(total, 100, abs_tol=0.06):
            raise ValueError("Four published source fate proportions fail roundoff mass balance")
        rows.append({
            "species": sp, "independent_donor_trials": row["n_completed_trials"],
            "author_pollen_removed_pct_of_measured_production": removal,
            "fate_pct_of_removed": fate,
            "fate_pct_rounding_sum": total,
            "descriptive_product_of_two_group_means_pct_produced_to_stigmas": (
                removal * fate["stigmas"] / 100
            ),
            "product_warning": (
                "product of published rounded species means; NOT actual "
                "E[removed_i / produced_i * deposited_i / removed_i], "
                "not an independently measured per-trial effect"
            ),
        })
    r = next(x for x in rows if x["species"]=="Solanum rostratum")
    d = next(x for x in rows if x["species"]=="Solanum dulcamara")
    if len(rows)!=2 or r["independent_donor_trials"]+d["independent_donor_trials"]!=15:
        raise ValueError("Two species, 15 donor trials needed")
    # Model-based, not a measured extension to more recipient flowers.
    slope = src["author_tests"]["release_visit_receipt_slope"]["estimate_log_rate"]
    carryover = exp(slope)
    first4 = sum(carryover**i for i in range(4))
    first20 = sum(carryover**i for i in range(20))
    omitted_fraction_4_to_20 = 1-first4/first20
    if not 0.24 < omitted_fraction_4_to_20 < 0.28:
        raise ValueError("Published carryover extrapolation not reproducible")
    return {
        "analysis":"BALANCE_VASQUEZ_CASTRO_ORIGINAL_SOURCE_POLLEN_FATES_V1",
        "status":"PUBLISHED_ORIGINAL_SOURCE_RESULTS_REEXPRESSED_NOT_RAW_REANALYSIS",
        "article_doi":src["article"]["doi"],
        "zenodo_record_id":17102653,
        "n_independent_study_programmes":1,
        "n_donor_trials":15,
        "n_nested_recipient_stigmas_not_independent_trials":60,
        "species_fates":rows,
        "source_species_contrast_descriptive": {
            "ground_loss_rostratum_minus_dulcamara_pct_points": (
                r["fate_pct_of_removed"]["ground"]-d["fate_pct_of_removed"]["ground"]
            ),
            "basket_gain_dulcamara_minus_rostratum_pct_points": (
                d["fate_pct_of_removed"]["basket"]-r["fate_pct_of_removed"]["basket"]
            ),
            "stigma_PTE_dulcamara_minus_rostratum_pct_points": (
                d["fate_pct_of_removed"]["stigmas"]-r["fate_pct_of_removed"]["stigmas"]
            ),
            "donor_fraction_removed_dulcamara_over_rostratum": (
                d["author_pollen_removed_pct_of_measured_production"]/
                r["author_pollen_removed_pct_of_measured_production"]
            ),
            "descriptive_product_of_rounded_means_dulcamara_over_rostratum": (
                d["descriptive_product_of_two_group_means_pct_produced_to_stigmas"]/
                r["descriptive_product_of_two_group_means_pct_produced_to_stigmas"]
            ),
            "contrast_tested_on_original_trials_here":False
        },
        "published_source_tests":src["author_tests"],
        "model_based_carryover":{
            "source_per_recipient_log_rate":slope,
            "per_recipient_retention_ratio":carryover,
            "fraction_of_expected_first20_deposition_in_first4":first4/first20,
            "model_only_missing_fraction_if_only_four_recipients":omitted_fraction_4_to_20,
            "not_new_empirical_stigma_count_or_GLM_fitting":True
        },
        "original_zenodo_raw_csv_rows_analyzed":0,
        "male_genetic_paternity_identified":False,
        "flower_structure_randomized":False,
        "claim_ceiling":"source-backed between-species pollen-fate-route contrasts; neither original row-level reanalysis nor architectural fitness or paternity"
    }

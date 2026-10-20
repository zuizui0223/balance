"""A **published-statistics-only** alternative-mechanism audit for Clarkia.

Neither this module nor its tests download or regenerate raw Dryad data.
The outcome-selected Clarkia original paper provides one source programme.
BALANCE U3's Solanum rostratum case provides a separate pollen-fate
mechanism, not a matched phylogenetically independent meta-analysis.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RECEIPT="data/CLARKIA_KAY2020_PUBLISHED_STATISTIC_RECEIPTS_V1.json"
EXPECTED_IDS={
    "EVOL_BEE","EVOL_ANTHER_MOVEMENT","TIMING_11_SPECIES",
    "POLLEN_FATE_CYLINDRICA","POLLEN_FATE_TOTAL_COVARIATE",
    "MORPH_BEE_COLOUR","DOSE_EXPOSED_POLLEN","DOSE_EXPORTED_POLLEN",
    "DOSE_BEE_PROVISIONS","FIELD_TIMED_ANTHER_REMOVAL",
}
ALLOWED_PROMOTION = {
    "EVIDENCE_OF_TEMPORAL_POLLEN_PRESENTATION",
    "NO_DETECTED_EXCLUSIVE_POLLEN_ROLE_DIVISION",
    "EXPERIMENTAL_SOURCE_DOSING_EXPOSURE_CHANGED",
}
BLOCKED_PROMOTION = {
    "POLLEN_DOSING_CAUSALLY_INCREASED_STIGMA_DELIVERY_CONFIRMED",
    "BOTH_ANTHER_WHORLS_FUNCTIONALLY_EQUIVALENT_PROVED",
    "TRADEOFF_CAUSED_EVOLUTIONARY_ORIGIN_OF_TWO_ANTHER_TYPES",
    "HERITABLE_CONCURRENT_TWO_COORDINATE_MODULE_WAS_MEASURED",
    "INTERVENTION_TREATMENT_IDENTICAL_IN_FLOWER_AGE",
}


def analyze(path: Path=ROOT/RECEIPT) -> dict:
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema")!="BALANCE_CLARKIA_KAY2020_PUBLISHED_STATISTICS_V1" or data.get("provenance_status")!="PUBLISHED_ARTICLE_TEXT_NOT_RAW_DATA_REANALYSIS":
        raise ValueError("Published source provenance must remain unpromoted")
    if (data["source"]["paper_doi"],data["source"]["dataset_doi"])!=(
        "10.1098/rspb.2020.2593","10.5061/dryad.8cz8w9gmp"):
        raise ValueError("Paper/Dryad source identities changed")
    receipts=data.get("receipts")
    if not isinstance(receipts,list) or {r["id"] for r in receipts}!=EXPECTED_IDS or len(receipts)!=len(EXPECTED_IDS):
        raise ValueError("Ten unique published source comparisons are required")
    r={x["id"]:x["source_report"] for x in receipts}
    timing=r["TIMING_11_SPECIES"]
    if (timing["n_heterantherous"],timing["n_other"])!=(6,5):
        raise ValueError("Published anther-timing species denominator changed")
    if not (timing["p"]<.05 and r["POLLEN_FATE_CYLINDRICA"]["p"]>.05):
        raise ValueError("Published tests must not be reversed")
    doses=r["DOSE_EXPOSED_POLLEN"]
    delivery=r["DOSE_EXPORTED_POLLEN"]
    mass=r["DOSE_BEE_PROVISIONS"]
    if (delivery["dosing_arrays"],delivery["no_dosing_arrays"])!=(13,15):
        raise ValueError("Published greenhouse unit denominators changed")
    if not (delivery["p"]>.05 and mass["p"]>.05):
        raise ValueError("No scientific equivalence promotion from nonsignificance")
    ratio=doses["no_dose_mm"]/doses["dose_mm"]
    observed_stigma_ratio=math.exp(delivery["no_dosing_log_ratio"])
    return{
        "schema":"BALANCE_CLARKIA_PUBLISHED_COMPETING_FUNCTION_MECHANISMS_V1",
        "status":"ORIGINAL_ARTICLE_SUMMARY_NOT_REANALYZED_DATA",
        "source":{"paper_doi":data["source"]["paper_doi"],"dryad_doi":data["source"]["dataset_doi"]},
        "source_original_study_programmes":1,
        "published_compared_anther_timing_species":11,
        "published_timing_phylo_ANOVA_F":timing["F"],
        "published_timing_phylo_p":timing["p"],
        "published_no_detected_scopa_stigma_fate_difference_p":r["POLLEN_FATE_CYLINDRICA"]["p"],
        "pollen_dosing_experiment_arrays":{"dosing":13,"no_dosing":15},
        "published_exposed_pollen":{"dosing_mm":doses["dose_mm"],"no_dosing_mm":doses["no_dose_mm"],
                                    "no_dosing_over_dosing_ratio_computed":ratio,
                                    "original_F":doses["F"],"original_p_less_than":doses["p_upper_bound"]},
        "published_stigma_delivery":{"no_dosing_vs_dosing_log_ratio":delivery["no_dosing_log_ratio"],
                                     "exponentiated_published_log_coefficient":observed_stigma_ratio,
                                     "not_unconditionally_a_raw_count_ratio":True,
                                     "original_p":delivery["p"],
                                     "causal_effect_positive_certified":False,
                                     "strict_equivalence_certified":False},
        "published_corbicular_mass_mg":{"dosing":mass["dose_mg"],"no_dosing":mass["no_dose_mg"],"original_p":mass["p"]},
        "published_anther_movement_association_p":r["EVOL_ANTHER_MOVEMENT"]["p"],
        "published_bee_pollination_association_p":r["EVOL_BEE"]["p"],
        "interpretation_support":sorted(ALLOWED_PROMOTION),
        "prohibited_claims":sorted(BLOCKED_PROMOTION),
        "source_raw_2018_pollen_trial_missing_in_public_manifest":True,
        "raw_replicate_level_confidence_intervals_computed":False,
        "actual_developmental_origin_from_conflict_established":False,
        "difference_between_whorl_morphology_and_ecological_role_identified_by_source_as_nonbijective":True,
    }

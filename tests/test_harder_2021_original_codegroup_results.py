"""Pin actual 2021 orchid original-file source discrepancy and raw-code export.

Data are one original orchid pollen interference experiment. The Zenodo
mirror is not an independent study, 'Trial' codes are NOT known unique bees,
and no original paper 31-trial donor effect is newly refitted.
"""
import json
from pathlib import Path

import pytest


ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results"/"harder_2021"/"ORIGINAL_ORCHID_TRIAL_ADMISSION_RECEIPT_20261124.json"
OUT=ROOT/"results"/"harder_2021"/"ORIGINAL_ORCHID_32_GROUP_EXPORT_SENSITIVITY_20261124.json"


def source():
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def analysis():
    return json.loads(OUT.read_text(encoding="utf-8"))


def test_authenticated_2021_file_has_one_more_coded_trial_than_paper():
    src=source()
    assert src["status"]=="AUTHENTIC_SOURCE_SCHEMAS_VERIFIED_EXTRA_TRIAL_HOLD"
    assert src["bytes"]==8041
    assert src["sha256"]=="303428b859bcba4756ac78c4ffd4b42121a6efce5b0cd2cc2030834705f62cbc"
    assert src["md5"]=="650e40ae7ebb41bdfb333dcf63c63c71"
    assert src["source_recipient_rows"]==383
    assert src["independent_donor_visit_sequences"]==32  # original source code-groups, NOT verified independent bees
    assert src["original_treatment_trial_counts"]=={"Emasc":16,"Intact":16}
    assert src["published_reported_n_donor_trials"]==31
    assert src["trial_count_discrepancy_present"] is True
    assert src["source_trial_admission"]=="HOLD_UNEXPLAINED_EXTRA_INTACT_TRIAL"
    assert src["raw_data_effects_estimated"]==0
    assert src["provenance"]["artifact_id"]==14849769785


def test_original_trial_2_3_continuity_is_hypothesis_not_certified_donor():
    rows=source()["trial_identity_metadata_only"]
    assert len(rows)==32
    a=next(x for x in rows if x["treatment"]=="Emasc" and x["trial_id"]=="2")
    b=next(x for x in rows if x["treatment"]=="Emasc" and x["trial_id"]=="3")
    assert (a["visit_min"],a["visit_max"],a["recipient_rows"])==("1","10",10)
    assert (b["visit_min"],b["visit_max"],b["recipient_rows"])==("11","17",7)
    assert a["initial_massula_values"]==b["initial_massula_values"]==["201"]
    assert a["final_donor_pollinaria_values"]==b["final_donor_pollinaria_values"]==["0"]
    assert sum(x["n_distinct_final_pollinaria_values"]>1 for x in rows)==4
    assert sum(int(x["visit_min"])!=1 for x in rows)==1
    assert sum(x["recipient_rows"]<6 for x in rows)==2


def test_actual_code_groups_show_lower_pollen_export_with_competitors():
    x=analysis()
    assert x["source_sha256"]==source()["sha256"]
    assert x["status"]=="AUTHENTIC_ORIGINAL_SOURCE_32_CODE_GROUP_EXPLORATORY_DISCREPANCY_ANALYSIS"
    assert x["source_group_counts"]=={"Emasc":16,"Intact":16}
    base=x["source_coded_groups_mean_export_fraction"]
    assert base["emasculated_mean"]==pytest.approx(.5214915625069592)
    assert base["intact_mean"]==pytest.approx(.3930351223054467)
    assert base["intact_over_emasculated_mean_ratio"]==pytest.approx(.7536749404266762)
    assert base["intact_minus_emasculated_difference"]==pytest.approx(-.12845644020151248)
    merged=x["possible_contiguous_split_Emasc_2_3_merge"]["results_if_merged"]
    assert merged["n_emasculated_coded_groups"]==15
    assert merged["n_intact_coded_groups"]==16
    assert merged["intact_over_emasculated_mean_ratio"]==pytest.approx(.7065702566500089)
    assert x["claim_limits"]["no_unique_original_31_trial_mapping"] is True
    assert x["claim_limits"]["not_seed_paternity_or_male_genetic_success"] is True


def test_every_possible_intact_omission_preserves_direction_but_uncertainty_includes_zero():
    x=analysis()
    bounds=x["all_sixteen_possible_one_intact_group_omission_envelope"]
    assert bounds["n_scenarios"]==16
    assert bounds["n_effect_sign_in_original_paper_direction"]==16
    assert bounds["min_ratio"]==pytest.approx(.7071582459802837)
    assert bounds["max_ratio"]==pytest.approx(.8033850475941143)
    assert bounds["max_export_difference"]<0
    boot=x["original_coded_group_bootstrap"]
    assert boot["reps"]==20000
    assert boot["seed"]==20261124
    ci=boot["descriptive_95pct_intact_minus_emasculated_diff"]
    assert ci==pytest.approx([-.26844167064858526,.011764942748380974])
    assert ci[0]<0<ci[1]
    assert boot["not_a_sampling_CI_for_paper_31_trial_population"] is True
    assert x["original_group_anomalies"]["inconsistent_original_R_within_coded_group_count"]==4
    assert x["original_group_anomalies"]["cannot_compute_2021_doubled_transport_loss_from_this_table"] is True


def test_equal_recipient_window_still_requires_an_inclusion_guard():
    x=analysis()
    window=x["six_recipient_common_observed_window"]
    w=window["contrast"]
    assert w["n_emasculated_coded_groups"]==14
    assert w["n_intact_coded_groups"]==15
    assert w["intact_over_emasculated_mean_ratio"]==pytest.approx(.7219795626730864)
    assert window["excluded_ambiguous_or_short_code_groups"]==3
    assert x["provenance"]["actions_run"]==45241393794
    assert x["provenance"]["artifact_id"]==14851008003
    assert x["provenance"]["artifact_zip_sha256"]=="646fccc4ea5ca5aef8fdad6455ca8b0786f79bb841a63de342971a81fe119ade"

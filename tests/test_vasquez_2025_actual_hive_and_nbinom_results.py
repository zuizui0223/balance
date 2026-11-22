"""Regression guards for exact authentic Zenodo B1/B2 and nbinom2 source model.

No trial rows are reprinted or fabricated. Neither model is a new study.
"""
import json
from pathlib import Path

import pytest


ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"results"/"vasquez_2025"
HIVE=DIR/"ORIGINAL_HIVE_AND_TRIAL_INFLUENCE_20261122.json"
MODEL=DIR/"ORIGINAL_RECIPIENT_NBINOM_REPLAY_20261122.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hive_source_and_original_trial_deletion_results():
    x=load(HIVE)
    assert x["status"]=="ACTUAL_SOURCE_POSTOPEN_DESCRIPTIVE_HIVE_CHECK_NOT_CONFIRMATORY"
    assert x["n_source_trials"]==15
    assert x["n_hives"]==2
    assert x["source_sha256"]=="484ed52ac611dbc6dc1831320a6c54d314492e9830823edd8934690c35205b79"
    assert x["provenance"]["run_id"]==45030511028
    by={z["hive"]:z for z in x["within_hive_comparisons"]}
    assert set(by)=={"B1","B2"}
    assert (by["B1"]["n_dulcamara"],by["B1"]["n_rostratum"])==(5,5)
    assert (by["B2"]["n_dulcamara"],by["B2"]["n_rostratum"])==(4,1)
    assert by["B1"]["within_hive_dulcamara_minus_rostratum"][
        "source_to_four_stigmas_pct_of_production"
    ]==pytest.approx(0.2816905352285103)
    assert by["B2"]["within_hive_dulcamara_minus_rostratum"][
        "source_to_four_stigmas_pct_of_production"
    ]==pytest.approx(0.21942829496572466)
    leave=x["single_donor_deletion"]
    assert leave["n_source_trials_removed_one_at_a_time"]==15
    assert leave["n_differences_positive"]==15
    assert leave["min_end_to_end_dulcamara_minus_rostratum_pp"]==pytest.approx(.17782717948143062)
    assert leave["max_end_to_end_dulcamara_minus_rostratum_pp"]==pytest.approx(.2703804068318603)
    assert x["limits"]["two_hives_insufficient_for_population_cluster_inference"] is True
    assert x["limits"]["B2_rostratum_n1_no_species_replication_within_B2"] is True
    assert x["limits"]["species_not_randomized"] is True


def test_original_negative_binomial_model_is_replayed_not_independently_discovered():
    m=load(MODEL)
    assert m["status"]=="AUTHENTIC_ORIGINAL_ZENODO_NBINOM2_MODEL_REPLAY_SOURCE_AGREEMENT"
    assert m["source_doi"]=="10.26786/1920-7603(2025)836"
    assert m["raw_original_data_sha256"]=="484ed52ac611dbc6dc1831320a6c54d314492e9830823edd8934690c35205b79"
    assert (m["n_independent_donor_trials"],m["n_recipient_observations_nested_in_donors"])==(15,60)
    assert m["provenance"]["workflow_run_id"]==45030511028
    assert m["provenance"]["artifact_id"]==14757542712
    assert m["provenance"]["artifact_zip_sha256"]=="392765f8aefb76bf2d558f64745efbc0a21d8997420bb8d7580cb6aaa65d082e"
    f=m["replayed_model_comparison"]
    assert f["additive_AIC"]==pytest.approx(794.806984)
    assert f["species_by_recipient_AIC"]==pytest.approx(796.616746)
    assert f["interaction_minus_additive_AIC"]==pytest.approx(1.809762)
    assert f["replay_status"]=="SAME_DIRECTION_APPROX_ORIGINAL_NUMBERS"
    co={z["term"]:z for z in m["replayed_additive_coefficients"]}
    assert set(co)=={
        "recipient","flower_spS.rostratum",
        "log(duration_visit)","log(donor_released)"
    }
    expected={
        "recipient":(-.33917199,.09760693,.00051108943),
        "flower_spS.rostratum":(-.95382404,.30952719,.0020592471),
        "log(duration_visit)":(.26463433,.11031051,.016440157),
        "log(donor_released)":(.15484967,.15906799,.33031428)
    }
    for term,(beta,se,p) in expected.items():
        assert co[term]["estimate"]==pytest.approx(beta)
        assert co[term]["standard_error"]==pytest.approx(se)
        assert co[term]["p_value"]==pytest.approx(p)
    assert m["inference_ceiling"]["this_replays_existing_published_effects_not_independent_replication"] is True
    assert m["inference_ceiling"]["recipient_rows_not_independent_trials"] is True
    assert m["inference_ceiling"]["ground_basket_body_pollen_fates_unavailable_from_this_raw_file"] is True
    assert m["inference_ceiling"]["V4_blind_architecture_outcomes_unmodified"] is True

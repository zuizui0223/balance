"""Frozen original-Dryad findings guard against silent scientific promotion.

The true positive source replay is tested only by the GitHub Actions job after
both original file MD5s and all source row checks pass. No test here invents
a 'source-confirmed' dataset from fabricated input.
"""
import copy
import json
from pathlib import Path

import pytest

from scripts.verify_dalechampia_2015_source_freeze import validate_source_freeze

ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/"data/DALECHAMPIA_2015_EXACT_DRYAD_SENSITIVITY_FREEZE_V1.json"


def frozen():
    return json.loads(FREEZE.read_text(encoding="utf-8"))


def test_source_freeze_keeps_stage_specific_effects_separate():
    d=frozen()
    assert d["observed_seed_support"] == {
        "recorded_seed_rows":1221,
        "recorded_seed_masses":1220,
        "numeric_mass_under_20mg_count":117,
        "maternal_plants_with_any_seeds":37,
        "blossom_identities":142,
        "abortion_morphology_independently_verified":False,
    }
    gas=d["bract_gas_within_plant"]
    assert gas["n_plants"]==6
    assert gas["mean_green_minus_white"]==1.044868
    assert gas["plant_bootstrap_95"]==[0.766266,1.328367]
    assert d["scientific_ceiling"]["bract_labelled_carbon_transfer_verified"] is False
    assert d["scientific_ceiling"]["direct_structural_balance_identified"] is False
    assert d["paired_maternal_seed_mass"]["original_pelabon_2015_mixed_model_reproduced"] is False


def test_forged_frozen_source_receipt_and_no_original_data_never_claim_success():
    d=frozen()
    with pytest.raises(ValueError, match="SHA256"):
        validate_source_freeze(d, {}, b"not archived source data")
    bad=copy.deepcopy(d)
    bad["status"]="STRUCTURAL_BALANCE_IDENTIFIED"
    with pytest.raises(ValueError, match="not approved"):
        validate_source_freeze(bad, {}, b"not archived source data")


def test_reanalysis_is_frozen_as_nonconfirmatory_and_sensitive_to_sample_selection():
    d=frozen()
    effects=d["paired_maternal_seed_mass"]["contrasts"]
    assert effects["all_measured_masses"]["bag_minus_cont"]["n"] == 34
    assert effects["numeric_ge20_proxy_only"]["bag_minus_cont"]["n"] == 30
    assert effects["numeric_ge20_proxy_only"]["cut_minus_cont"]["mean"] == -0.013168
    assert effects["all_measured_masses"]["cut_minus_cont"]["mean"] == -1.255833
    assert effects["numeric_ge20_proxy_only"]["cut_minus_cont"]["ci95"][0] < 0
    assert effects["numeric_ge20_proxy_only"]["cut_minus_cont"]["ci95"][1] > 0
    assert d["paired_maternal_seed_mass"]["selection_bias_due_missing_or_threshold_proxies_possible"] is True


def test_source_file_digest_pins_are_complete_and_distinct_from_ci_models():
    d=frozen()
    assert len(d["original_source_file_sha256"]) == 2
    assert all(len(v)==64 for v in d["original_source_file_sha256"].values())
    assert len(d["exact_generated_receipt_sha256"]) == 64
    assert d["source_dataset_doi"]=="10.5061/dryad.nb675"
    assert d["scientific_ceiling"]["extra_biological_clusters"]==0

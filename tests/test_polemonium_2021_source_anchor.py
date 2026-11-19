"""Guard that external published results are not mistaken for model calibration."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = ROOT / "data" / "BALANCE_POLEMONIUM_2021_SOURCE_ONLY_ANCHOR_V1.json"


def test_original_source_anchor_is_one_published_study_not_raw_reanalysis():
    source = json.loads(ANCHOR.read_text(encoding="utf-8"))
    assert source["schema_version"] == "BALANCE_POLEMONIUM_FOLIOSISSIMUM_SOURCE_ANCHOR_V1"
    assert source["status"] == "PUBLICATION_REPORTED_RESULTS_ONLY_NOT_RAW_DATA_REANALYSIS"
    assert source["source"]["doi"] == "10.1093/aob/mcab050"
    assert source["source"]["number_of_independent_original_research_programmes"] == 1
    assert source["model_link"]["not_added_to_frozen_U6"] is True
    assert source["model_link"]["direct_architecture_worldline"] is False


def test_source_transcription_keeps_pollen_stock_deposition_and_seed_distinct():
    source = json.loads(ANCHOR.read_text(encoding="utf-8"))
    observed = source["published_results_descriptive"]
    assert observed["pollen_remaining_on_anthers_after_one_visit"][
        "muscid_fly_mean_grains"
    ] == 9700
    assert observed["pollen_remaining_on_anthers_after_one_visit"][
        "bumblebee_mean_grains"
    ] == 16900
    assert observed["pollen_deposited_on_stigma_per_single_visit"][
        "reported_test_p"
    ] == 0.189
    assert observed["hand_supplementation_2016"][
        "control_seeds_per_fruit_mean"
    ] == 5.5
    assert observed["hand_supplementation_2016"][
        "supplemented_seeds_per_fruit_mean"
    ] == 6.46
    assert "does not prove zero" in observed["neighbourhood_pollen_manipulation"][
        "warning"
    ]


def test_original_source_never_claims_a_calibrated_visitation_interaction():
    source = json.loads(ANCHOR.read_text(encoding="utf-8"))
    assert "No matched intervention" in source["model_link"]["causal_gate_not_measured"]
    assert source["model_link"]["source_timing_not_measured"].startswith("No controlled")
    assert "an actual odds ratio" in " ".join(source["model_link"]["do_not_infer"])

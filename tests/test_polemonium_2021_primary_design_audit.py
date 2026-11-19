"""Fail-closed checks of the publisher-reported 2015/2016 source design.

These numerical anchors are a manual source read. This is NOT an original
neighbourhood-row reanalysis or an independent source replication.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "BALANCE_POLEMONIUM_2021_PRIMARY_DESIGN_AUDIT_V1.json"


def original():
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def test_different_years_different_interventions_not_two_identical_replicates():
    d = original()
    assert d["schema_version"] == "BALANCE_POLEMONIUM_2021_PRIMARY_DESIGN_AUDIT_V1"
    assert d["status"] == "PUBLISHED_PRIMARY_ARTICLE_TEXT_READ_NOT_RAW_DATA"
    assert d["original_publication"]["doi"] == "10.1093/aob/mcab050"
    assert d["evidence"]["2015"]["source_neighbourhood_count"] == 4
    assert d["evidence"]["2016"]["source_neighbourhood_count"] == 10
    assert d["evidence"]["2015"]["hand_supplementation_factorial_present"] is False
    assert "rotated" in d["evidence"]["2016"]["source_removal"]


def test_2015_pollen_receipt_effect_is_not_silently_recoded_as_no_effect():
    report = original()["evidence"]["2015"]["neighbourhood_pollen_receipt_effect"]
    assert "32.2 percent lower" in report["female"]
    assert "28.9 percent lower" in report["hermaphrodite"]
    assert report["original_main_effect_test"] == "F(1,93)=4.20, p=0.04"


def test_original_2016_hand_and_source_interaction_are_distinct():
    d = original()["evidence"]["2016"]
    assert d["seed_per_fruit"]["original_control_mean"] == 5.5
    assert d["seed_per_fruit"]["hand_supplemented_mean"] == 6.46
    assert d["seed_per_fruit"]["hand_effect_test"] == "chi-square=13.07, p<0.001"
    assert (
        d["seed_per_fruit"]["pollen_reduction_x_hand_supplementation_interaction_test"]
        == "chi-square=0.083, p=0.773"
    )
    assert d["fruit_set"]["pollen_reduction_x_hand_supplementation_interaction_test"] == (
        "chi-square=0.33, p=0.568"
    )
    assert d["pollen_receipt"]["original_test"] == "chi-square=0.334, p>0.563"


def test_original_source_data_and_fitness_ceiling_are_explicit():
    d = original()
    assert d["data_recovery"]["exact_original_data_files_retrieved"] is False
    assert d["data_recovery"]["original_experimental_unit_data_refit"] is False
    assert d["data_recovery"]["original_row_level_data_repository_identified"] is False
    assert d["source_text_access"].startswith("Publisher HTML read")
    assert any("No study intervention independently randomized" in x
               for x in d["interpretation_constraints"])
    assert any("No donor genetic paternity" in x
               for x in d["interpretation_constraints"])
    assert "not_new_biological_effect_estimate" in d["claim_ceiling"]

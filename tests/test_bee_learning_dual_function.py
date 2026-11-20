"""Tests keep published results, paired bee grain, and source ceiling separate."""
import csv
import json

import pytest

from balance_domain.bee_learning_dual_function import (
    SOURCE,
    load_original_paired_csv,
    published_dual_function_audit,
    validate_publication_receipt,
)


def sample_rows():
    # Entirely SYNTHETIC fixtures. Never published Mayberry source observations.
    return [
        ["b1", "c1", "SOEL", "naive", 10, 10, 8],
        ["b1", "c1", "SOEL", "experienced", 10, 18, 4],
        ["b2", "c2", "SOEL", "naïve", 9, 12, 10],
        ["b2", "c2", "SOEL", "experienced", 9, 20, 3],
        ["b3", "c3", "PHCA", "naive", 7, 5, 4],
        ["b3", "c3", "PHCA", "experienced", 7, 7, 5],
    ]


def write(tmp_path, rows=None, header=None):
    path = tmp_path / "synthetic_not_published.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header or [
            "BeeID", "ColonyID", "Species", "Treatment", "NumVisits",
            "CorbPolperVis", "StigPolperVis",
        ])
        writer.writerows(sample_rows() if rows is None else rows)
    return path


def test_published_dual_function_asymmetric_evidence_and_species_interaction():
    report = published_dual_function_audit()
    assert report["status"] == "PUBLISHED_SOURCE_ONLY_NOT_ORIGINAL_RAW_DATA_REFIT"
    assert report["flower_species"] == 4
    assert report["collection_positive_percent_all_species"] == 4
    assert report["stigma_direction_positive_species"] == 2
    assert report["stigma_direction_negative_species"] == 2
    assert report["published_global_collection_change_percent"] == 22
    assert report["published_global_collection_p"] == pytest.approx(0.0017)
    assert report["published_global_stigma_p"] == pytest.approx(0.893)
    assert report["published_species_by_experience_stigma_interaction_p"] == pytest.approx(
        0.0040
    )
    assert report["published_species_by_experience_collection_interaction_p"] == pytest.approx(
        0.961
    )
    assert report["published_routine_by_species_by_experience_stigma_p"] == pytest.approx(
        0.00005
    )
    assert report["source_data_rows_accessed"] == 0
    assert report["new_published_effects_fitted_by_this_audit"] == 0


def test_same_species_2022_experiment_not_independent_phylogenetic_replicate():
    d = validate_publication_receipt()
    assert d["experiment"]["bees"] == "Bombus impatiens"
    assert d["experiment"]["same_bee_24h_order_confounded"] is True
    assert d["experiment"]["replicate_unit"] == "BEEID_WITHIN_COLONYID"
    assert d["source_claim_ceiling"][
        "same_species_S_elaeagnifolium_in_2022_anther_joining_study"
    ] is True
    assert d["source_claim_ceiling"]["stigma_deposition_proxy_not_measured_female_seed_fitness"]
    assert d["source_claim_ceiling"][
        "overall_stigma_nonsignificance_does_not_establish_equivalence"
    ] is True
    assert d["archived_data"]["raw_csv_retrieved"] is False


def test_species_percentages_are_reported_point_estimates_not_four_p_values():
    r = published_dual_function_audit()
    x = {z["dryad_species_code"]: z for z in r["species_source_point_estimates"]}
    assert {
        k: (
            v["published_collection_percent_change"],
            v["published_stigma_percent_change"],
        )
        for k, v in x.items()
    } == {
        "PHCA": (17, 18), "EXAF": (19, 28), "SOEL": (26, -49),
        "MIGU": (27, -6),
    }
    assert all(
        v["species_specific_effect_has_individual_significance"] == "UNRESOLVED"
        for v in x.values()
    )


def test_missing_original_csv_is_not_turned_into_fabricated_paired_effect(tmp_path):
    with pytest.raises(FileNotFoundError, match="not locally supplied"):
        load_original_paired_csv(tmp_path / "unavailable.csv")


def test_synthetic_pairing_is_by_colony_bee_within_species_not_individual_visit(tmp_path):
    report = load_original_paired_csv(write(tmp_path))
    assert report["status"] == "ORIGINAL_SOURCE_CSV_USER_SUPPLIED_PAIRED_DESCRIPTIVES"
    assert report["paired_bee_trial_count"] == 3
    assert report["unpaired_bee_count"] == 0
    by = {x["species_code"]: x for x in report["species_results"]}
    assert by["SOEL"]["n_paired_bees"] == 2
    assert by["SOEL"]["n_colonies_of_paired_bees"] == 2
    assert by["PHCA"]["n_paired_bees"] == 1
    assert by["SOEL"][
        "mean_within_bee_delta_log1p_pollen_basket_per_visit"
    ] > 0
    assert by["SOEL"][
        "mean_within_bee_delta_log1p_stigma_pollen_per_visit"
    ] < 0
    assert report["no_new_p_values_or_causal_paternity"] is True


def test_missing_naive_pair_is_explicitly_excluded_not_naively_joined(tmp_path):
    rows = sample_rows()
    rows.pop(1)
    report = load_original_paired_csv(write(tmp_path, rows=rows))
    assert report["paired_bee_trial_count"] == 2
    assert report["unpaired_bee_count"] == 1
    assert report["unpaired_bees_excluded_from_paired_summary"] is True


@pytest.mark.parametrize("operation,expected_error", [
    ("mismatch_visits", "matched visit counts"),
    ("duplicate_trial", "Duplicate bee trial"),
    ("cross_species", "reused across species"),
    ("negative_stigma", "invalid StigPolperVis"),
    ("nan_basket", "invalid CorbPolperVis"),
    ("missing_field", "canonical bee/colony"),
])
def test_synthetic_invalid_original_csv_does_not_produce_pseudo_replicates(
    tmp_path, operation, expected_error
):
    rows = sample_rows()
    head = None
    if operation == "mismatch_visits":
        rows[1][4] = 11
    elif operation == "duplicate_trial":
        rows += [rows[0].copy()]
    elif operation == "cross_species":
        rows[1][2] = "EXAF"
    elif operation == "negative_stigma":
        rows[0][6] = -1
    elif operation == "nan_basket":
        rows[0][5] = "nan"
    else:
        head = ["BeeID", "ColonyID", "Species", "Treatment", "NumVisits",
                "CorbPolperVis", "FAKE_STIGMA"]
    with pytest.raises(ValueError, match=expected_error):
        load_original_paired_csv(write(tmp_path, rows=rows, header=head))


def test_cannot_relabel_global_nonsignificance_as_significant_or_equivalence(tmp_path):
    d = json.loads(SOURCE.read_text(encoding="utf-8"))
    d["published_results"]["stigmatic_deposition_experience"]["overall_p"] = 0.001
    wrong = tmp_path / "fake_source.json"
    wrong.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(ValueError, match="Original paper global/interaction"):
        validate_publication_receipt(wrong)


def test_cannot_silently_assign_independent_2024_paternity(tmp_path):
    d = json.loads(SOURCE.read_text(encoding="utf-8"))
    d["source_claim_ceiling"]["no_genetically_assigned_donor_paternity"] = False
    wrong = tmp_path / "fake_source.json"
    wrong.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(ValueError, match="promoted to fitness"):
        validate_publication_receipt(wrong)


def test_documented_dryad_ERGU_alias_is_treated_as_MIGU_same_species(tmp_path):
    rows = sample_rows()
    rows[4][2] = "ERGU"
    rows[5][2] = "MIGU"
    # Both records must refer to the same bee's assigned Erythranthe taxon.
    report = load_original_paired_csv(write(tmp_path, rows=rows))
    assert report["paired_bee_trial_count"] == 3
    assert "MIGU" in {x["species_code"] for x in report["species_results"]}

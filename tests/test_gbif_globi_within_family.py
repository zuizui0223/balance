"""Actual GBIF and GloBI 48-species snapshots: family-conditional documentation.

This is a POST-OPEN observation-bias sensitivity, not an ecological field
trial or a randomized allocation of GloBI documentation among species.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from balance_domain.gbif_occurrence_effort import source_effort_audit_from_files
from balance_domain.gbif_globi_within_family import (
    EXPECTED, EXPECTED_MIXED, MANIFEST, SCHEMA,
    _rank2_with_ties, _reference_by_family,
    analyze_effort_family_rank_reference,
    analyze_effort_family_rank_from_source,
)
from scripts.audit_gbif_globi_within_family import write_readout

ROOT=Path(__file__).resolve().parents[1]


def source():
    return source_effort_audit_from_files(ROOT,ROOT/MANIFEST)


def test_source_verified_family_conditional_permutations_not_field_causation():
    readout=analyze_effort_family_rank_from_source(ROOT,ROOT/MANIFEST)
    assert readout["schema_version"]==SCHEMA
    assert readout["status"]=="POSTOPEN_PUBLIC_RECORD_DOCUMENTATION_BIAS_STRATIFIED_REFERENCE_NOT_CONFLICT"
    assert readout["all_original_source_species_retained"]==48
    assert readout["source_family_convenience_stratification_not_random_global_sample"] is True
    assert readout["within_family_label_exchangeability_is_hypothetical_unverified"] is True
    assert readout["primary_statistic_chosen_post_open_not_preregistered"] is True
    assert readout["GBIF_occurrences_are_public_indexed_records_not_effective_field_effort"] is True
    assert readout["GloBI_records_are_source_documentation_not_all_biotic_interactions"] is True
    assert readout["non_detected_GloBI_is_not_absence_of_real_interactions"] is True
    assert readout["no_direct_floral_fitness_or_functional_conflict_studied"] is True
    assert readout["structural_BALANCE_occupancy_identified"] is False
    assert readout["additional_independent_biological_clusters"]==0


def test_all_16_within_family_documented_undocumented_pairs_concordant():
    r=analyze_effort_family_rank_reference(source())
    stat=r["primary_indexed_occurrence_counts"]
    assert stat["GBIF_count_field"]=="gbif_occurrence_search_count"
    assert stat["n_informative_mixed_families"]==5
    assert stat["n_species_in_informative_families"]==20
    assert stat["n_distinct_documented_undocumented_family_pairs"]==16
    assert stat["n_pairs_documented_has_higher_GBIF_count"]==16
    assert stat["n_pairs_documented_has_lower_GBIF_count"]==0
    assert stat["n_pairs_tied_GBIF_count"]==0
    assert stat["all_informative_documented_vs_undocumented_pairs_higher"] is True
    mixed={x["family"]:x for x in stat["family_data"]
           if x["contributes_to_within_family_reference"]}
    assert {family:x["n_name_documented"] for family,x in mixed.items()}==EXPECTED_MIXED
    assert {family:x["pairwise_documented_higher"] for family,x in mixed.items()}=={
        "Fabaceae":3,"Rosaceae":3,"Rubiaceae":3,"Brassicaceae":4,"Ericaceae":3
    }
    assert all(x["pairwise_documented_lower"]==0 for x in mixed.values())
    assert {family for family,x in mixed.items()
            if x["all_four_sampled_species_same_genus"]}=={
                "Fabaceae","Rosaceae"
            }
    assert len(stat["family_data"])==12


def test_all_permutations_exact_and_reference_probabilities_are_postopen_only():
    a=analyze_effort_family_rank_reference(source())["primary_indexed_occurrence_counts"]
    assert a["observed_documented_rank_sum"]==48.0
    assert a["conditional_exchangeability_expected_rank_sum"]==40.0
    assert a["conditional_reference_assignments"]==1536
    assert a["upper_tail_assignments"]==1
    assert a["lower_tail_assignments"]==1536
    assert a["two_sided_absolute_deviation_assignments"]==2
    assert a["conditional_one_sided_upper_reference_fraction"]==pytest.approx(1/1536)
    assert a["conditional_two_sided_reference_fraction"]==pytest.approx(2/1536)
    assert a["not_randomized_labels_or_confirmatory_p_value"] is True
    assert a["statistic"].startswith("sum_twice_midrank")


def test_georeferenced_effort_has_the_same_source_documentation_perfect_order():
    result=analyze_effort_family_rank_reference(source())
    a=result["primary_indexed_occurrence_counts"]
    b=result["georeferenced_occurrence_counts_sensitivity"]
    for key in (
        "n_informative_mixed_families",
        "n_distinct_documented_undocumented_family_pairs",
        "n_pairs_documented_has_higher_GBIF_count",
        "observed_documented_rank_sum",
        "conditional_exchangeability_expected_rank_sum",
        "conditional_reference_assignments",
        "upper_tail_assignments",
        "two_sided_absolute_deviation_assignments",
    ):
        assert a[key]==b[key]
    assert b["GBIF_count_field"]=="gbif_occurrence_search_has_coordinates_count"


def test_reference_ties_use_midrank_and_do_not_fake_perfect_order():
    members=[
        {"gbif_species_key":11,"gbif_occurrence_search_count":0,"globi_name_recorded":False},
        {"gbif_species_key":12,"gbif_occurrence_search_count":5,"globi_name_recorded":True},
        {"gbif_species_key":13,"gbif_occurrence_search_count":5,"globi_name_recorded":False},
        {"gbif_species_key":14,"gbif_occurrence_search_count":10,"globi_name_recorded":True},
    ]
    field="gbif_occurrence_search_count"
    rank=_rank2_with_ties(members,field)
    assert rank=={11:2,12:5,13:5,14:8}
    sample=_reference_by_family({"synthetic":members},field)
    assert sample["n_pairs_documented_has_higher_GBIF_count"]==3
    assert sample["n_pairs_documented_has_lower_GBIF_count"]==0
    assert sample["n_pairs_tied_GBIF_count"]==1
    assert sample["all_informative_documented_vs_undocumented_pairs_higher"] is False
    assert sample["conditional_reference_assignments"]==6


def test_source_taxon_label_falsification_not_mistaken_for_real_interaction_change():
    d=source()
    d["species"][0]["globi_name_recorded"]=True
    with pytest.raises(ValueError,match="source label and row count inconsistent"):
        analyze_effort_family_rank_reference(d)
    d=source()
    row=next(r for r in d["species"] if r["globi_name_recorded"])
    row["globi_exact_target_name_relation_rows"]=0
    with pytest.raises(ValueError,match="source label and row count inconsistent"):
        analyze_effort_family_rank_reference(d)
    d=source()
    d["species"]=d["species"][:-1]
    with pytest.raises(ValueError,match="all 48 original source taxa"):
        analyze_effort_family_rank_reference(d)


def test_false_field_effort_and_balance_promotion_hold():
    d=source()
    d["GloBI_absence_is_not_ecological_interaction_absence"]=False
    with pytest.raises(ValueError,match="source ecological evidence boundary"):
        analyze_effort_family_rank_reference(d)
    d=source()
    d["fitness_impact_or_SCH_L_identified"]=True
    with pytest.raises(ValueError,match="source ecological evidence boundary"):
        analyze_effort_family_rank_reference(d)
    d=source()
    d["net_structural_BALANCE_occupancy_identified"]=True
    with pytest.raises(ValueError,match="source ecological evidence boundary"):
        analyze_effort_family_rank_reference(d)


def test_family_relabeling_observation_only_drift_rejected():
    d=source()
    original_true=next(r for r in d["species"] if r["globi_name_recorded"]
                       and r["family"]=="Rosaceae")
    original_false=next(r for r in d["species"] if not r["globi_name_recorded"]
                        and r["family"]=="Rosaceae")
    original_true["globi_name_recorded"]=False
    original_true["globi_exact_target_name_relation_rows"]=0
    original_false["globi_name_recorded"]=True
    original_false["globi_exact_target_name_relation_rows"]=1
    with pytest.raises(ValueError,match="conditional rank signal changed"):
        analyze_effort_family_rank_reference(d)


def test_readonly_verified_original_audit_runner(tmp_path):
    out=tmp_path/"family_rank_readout.json"
    report=write_readout(ROOT,ROOT/MANIFEST,out)
    assert report==json.loads(out.read_text(encoding="utf-8"))
    assert len(report["original_48_species_source_manifest_sha256"])==64
    with pytest.raises(ValueError,match="refuse to overwrite"):
        write_readout(ROOT,ROOT/MANIFEST,out)
    assert EXPECTED["n_conditional_assignments"]==1536

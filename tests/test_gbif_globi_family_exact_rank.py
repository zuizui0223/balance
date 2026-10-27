"""Real original-source GBIF/GloBI documentation bias, conditional on FAMILY.

These tests are based on 48 truly retrieved public taxon/occurrence documents,
NOT synthetic inferred flower conflict or RCT label randomization. We separately
test toy assignments for null support, ties, and original source tampering.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from balance_domain.gbif_globi_family_exact_rank import (
    SCHEMA,
    exact_family_label_reference,
    real_source_rank_audit,
)

ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/"data/BALANCE_GBIF_GLOBI_FAMILY_CONDITIONAL_RANK_FREEZE_V1.json"


def test_authentic_species_first_panel_has_perfect_family_specific_source_documentation_rank():
    readout=real_source_rank_audit(ROOT)
    assert readout["schema_version"]==SCHEMA
    assert readout["status"]=="SOURCE_VERIFIED_POSTOPEN_FAMILY_CONDITIONAL_REPORTING_BIAS_ASSOCIATION"
    assert readout["n_species"]==48
    assert readout["n_family_strata"]==12
    assert readout["n_GloBI_name_documented"]==16
    assert readout["n_GloBI_direct_GBIF_key_documented"]==2
    assert len(readout["source_manifests_sha256"])==2

    primary=readout["family_conditional_source_analyses"]["name_exact_all_occurrence"]
    assert primary["n_informative_mixed_documentation_families"]==5
    assert primary["n_within_family_documented_undocumented_pairs"]==16
    assert primary["observed_concordant_pairs_equivalent"]==16
    assert primary["max_concordant_pairs_equivalent"]==16
    assert primary["exact_conditional_label_assignments"]==1536
    assert primary["right_tail_arrangement_count"]==1
    assert primary["right_tail_conditional_p"]==pytest.approx(1/1536)
    assert primary["two_sided_doubled_tail_conditional_p"]==pytest.approx(2/1536)
    assert primary["all_informative_families_perfectly_rank_separated"] is True
    assert [(x["family"],x["n_GloBI_label_documented"]) for x in
            primary["family_detail_mixed_only"]]==[
                ("Brassicaceae",2),("Ericaceae",1),("Fabaceae",3),
                ("Rosaceae",1),("Rubiaceae",1)
            ]


def test_actual_coordinate_occurrence_measure_is_independent_count_source_not_replication():
    result=real_source_rank_audit(ROOT)
    coord=result["family_conditional_source_analyses"]["name_exact_georeferenced"]
    assert coord["n_informative_mixed_documentation_families"]==5
    assert coord["n_within_family_documented_undocumented_pairs"]==16
    assert coord["observed_concordant_pairs_equivalent"]==16
    assert coord["right_tail_conditional_p"]==pytest.approx(1/1536)
    assert coord["two_sided_doubled_tail_conditional_p"]==pytest.approx(2/1536)
    assert coord["post_open_exploratory_statistic_not_confirmatory"] is True
    assert coord["within_family_source_label_exchangeability_not_verified"] is True


def test_author_name_vs_direct_taxon_key_support_changes_identifiability():
    result=real_source_rank_audit(ROOT)
    strict=result["family_conditional_source_analyses"]["direct_GBIF_key_all_occurrence"]
    assert strict["n_documented_species_source_roster"]==2
    assert strict["n_informative_mixed_documentation_families"]==2
    assert strict["n_within_family_documented_undocumented_pairs"]==6
    assert strict["observed_concordant_pairs_equivalent"]==3
    assert strict["exact_conditional_label_assignments"]==16
    assert strict["right_tail_conditional_p"]==pytest.approx(10/16)
    assert strict["two_sided_doubled_tail_conditional_p"]==1.0
    assert strict["all_informative_families_perfectly_rank_separated"] is False
    assert result["name_vs_key_support_is_severely_different"] is True
    assert result["actual_pollinator_or_antagonist_fitness_not_measured"] is True
    assert result["new_independent_flora_selection_transition_or_BALANCE_worldline"] is False
    assert result["additional_independent_biological_clusters"]==0


def _synthetic_roster():
    # Fully artificial 48-species 12-family source opportunity labels,
    # used only to check exact conditional combinatorics and tie cases.
    rows=[]
    for f in range(12):
        for k in range(4):
            rows.append({
                "gbif_species_key":10000+4*f+k,
                "family":f"TEST_FAMILY_{f:02d}",
                "gbif_occurrence_search_count":4-k,
                "label":bool(f==0 and k==0),
            })
    return rows


def test_synthetic_one_family_significance_resolution_and_ties():
    rows=_synthetic_roster()
    r=exact_family_label_reference(rows,label_field="label",
                                  measure_field="gbif_occurrence_search_count")
    assert r["n_informative_mixed_documentation_families"]==1
    assert r["n_within_family_documented_undocumented_pairs"]==3
    assert r["observed_concordant_pairs_equivalent"]==3
    assert r["exact_conditional_label_assignments"]==4
    assert r["right_tail_conditional_p"]==.25
    assert r["two_sided_doubled_tail_conditional_p"]==.5
    # A GBIF occurrence count tie makes the exact rank event 2/4
    rows[1]["gbif_occurrence_search_count"]=4
    rt=exact_family_label_reference(rows,label_field="label",
                                   measure_field="gbif_occurrence_search_count")
    assert rt["observed_concordant_pairs_equivalent"]==2.5
    assert rt["right_tail_conditional_p"]==.5
    assert rt["all_informative_families_perfectly_rank_separated"] is False


def test_synthetic_false_absence_and_duplicate_source_species_rejected():
    rows=_synthetic_roster()
    bad=copy.deepcopy(rows)
    bad[0]["label"]=None
    with pytest.raises(ValueError,match="coverage label must be boolean"):
        exact_family_label_reference(bad,label_field="label",
                                     measure_field="gbif_occurrence_search_count")
    bad=copy.deepcopy(rows)
    bad[0]["gbif_species_key"]=bad[1]["gbif_species_key"]
    with pytest.raises(ValueError,match="missing/duplicated"):
        exact_family_label_reference(bad,label_field="label",
                                     measure_field="gbif_occurrence_search_count")
    bad=copy.deepcopy(rows)
    bad[0]["gbif_occurrence_search_count"]=-1
    with pytest.raises(ValueError,match="nonnegative"):
        exact_family_label_reference(bad,label_field="label",
                                     measure_field="gbif_occurrence_search_count")
    with pytest.raises(ValueError,match="frozen 48"):
        exact_family_label_reference(rows[:-1],label_field="label",
                                     measure_field="gbif_occurrence_search_count")


def test_frozen_real_public_48_species_fact_and_no_conflict_fabrication():
    d=json.loads(FREEZE.read_text(encoding="utf-8"))
    assert d["status"]=="POSTOPEN_REAL_PUBLIC_GBIF_AND_GLOBI_COVERAGE_ASSOCIATION_NOT_BIOLOGICAL_CONFLICT"
    assert d["frozen_species_frame"]=={
        "selected_species":48,"chosen_family_strata":12,"per_family":4,
    }
    assert d["original_record_count_test"]["n_pair_concordant"]==16
    assert d["original_record_count_test"]["exact_conditional_arrangements"]==1536
    assert d["original_record_count_test"]["one_sided_conditional_exchangeable_label_probability"]==pytest.approx(1/1536)
    assert d["direct_GBIF_key_sensitivity"]["n_pair_concordant"]==3
    assert d["direct_GBIF_key_sensitivity"]["one_sided_right_tail_conditional_p"]==pytest.approx(.625)
    assert d["original_record_count_test"]["source_by_family_selection_not_randomized"] is True
    assert d["design_and_inference_limits"]["families_not_random_angiosperm_sample"] is True
    assert d["design_and_inference_limits"]["strict_structural_BALANCE_occupancy_identified"] is False
    assert d["design_and_inference_limits"]["additional_independent_biological_clusters"]==0

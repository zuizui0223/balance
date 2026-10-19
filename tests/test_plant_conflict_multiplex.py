"""Exact-source ecology multiplex stress tests. No new biological outcomes."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from balance_domain.plant_conflict_multiplex import (
    ALIAS, EXPECTED_OVERLAPS, REQUIRED_FILES, SCHEMA,
    _verified_anchor_registry, analyze_flower_multiplex,
    analyze_multiplex_sources,
)
from balance_domain.plant_macro import load_plant_macro_ledger
from balance_domain.plant_u2_screen import load_u2_conflict_screen
from scripts.audit_plant_conflict_multiplex import source_multiplex_receipt

ROOT=Path(__file__).resolve().parents[1]


def files():
    return {path:ROOT/path for path in REQUIRED_FILES}


def data():
    p=files()
    return (
        load_u2_conflict_screen(p[REQUIRED_FILES[0]]),
        load_plant_macro_ledger(p[REQUIRED_FILES[1]]),
        load_plant_macro_ledger(p[REQUIRED_FILES[2]]),
        json.loads(p[REQUIRED_FILES[3]].read_text(encoding="utf-8")),
    )


def test_four_source_overlaps_preserve_whole_nonexchangeable_universes():
    out=analyze_multiplex_sources(files())
    assert out["schema_version"]==SCHEMA
    assert out["status"]=="FOUR_SOURCE_SCREENED_SPECIES_MULTIPLEX_EXAMPLES_NOT_PREVALENCE"
    assert out["total_source_screened_records"]==51
    assert out["n_distinct_source_dependency_groups"]==46
    assert out["n_u2_strict_sexual_interference_source_species"]==22
    assert out["n_outcome_enriched_plant_pilot_rows"]==29
    assert out["n_distinct_species_dependency_groups_in_pilot"]==28
    assert out["n_cross_source_species_overlaps"]==4
    assert {r["dependency_group"] for r in out["source_cases"]}==EXPECTED_OVERLAPS
    assert out["n_source_dual_positive_distinct_architecture_cases"]==1
    assert out["n_source_status_asymmetric_or_unresolved_cases"]==3
    assert out["source_sample_outcome_blind"] is False
    assert out["source_pair_outcomes_and_contexts_nonexchangeable"] is True
    assert out["independent_double_coding_completed"] is False
    assert out["structural_BALANCE_occupancy_identified"] is False
    assert out["additional_independent_biological_clusters"]==0
    assert len(out["original_source_sha256"])==4


def test_same_species_has_two_direct_positive_conflicts_but_different_organs():
    r=analyze_multiplex_sources(files())
    s={x["dependency_group"]:x for x in r["source_cases"]}
    pole=s["Polemonium_viscosum"]
    assert pole["u2_conflict_status"]=="POSITIVE"
    assert pole["pilot_conflict_status"]=="POSITIVE"
    assert pole["u2_architecture_mode"]=="TEMPORAL_AND_SPATIAL_SEPARATION"
    assert pole["pilot_architecture_mode"]=="SHARED_INTEGRATED"
    assert pole["both_source_positive_different_architecture"] is True
    assert pole["u2_structure_tested"]!=pole["pilot_structure_tested"]
    assert pole["recorded_studies_have_identical_function_pair_and_structural_coordinate"] is False
    assert pole["causal_change_in_architecture_between_studies_established"] is False
    old,new=pole["source_anchor_publications"]
    assert old["quantified_source_values"]=={
        "year_one_self_precedence_hours":24,
        "first_year_compatible_pollen_germination_reduction_percent":32,
        "first_year_seed_set_reduction_percent":40,
    }
    assert new["quantified_source_values"]=={
        "genetic_corolla_length_flare_correlation":0.70,
    }
    assert pole["net_structural_BALANCE_identified"] is False


def test_narcissus_lab_potential_vs_field_realized_interference_is_not_zero_cost():
    r=analyze_multiplex_sources(files())
    n=next(x for x in r["source_cases"]
           if x["dependency_group"]=="Narcissus_assoanus")
    assert n["u2_conflict_status"]=="NO_DEMONSTRATED_CONFLICT"
    assert n["pilot_conflict_status"]=="POSITIVE"
    early,late=n["source_anchor_publications"]
    assert early["doi"]=="10.1046/j.1365-2540.2000.00651.x"
    assert late["quantified_source_values"]=={
        "simultaneous_self_cross_vs_cross_seed_reduction_percent":20,
        "prior_self_24h_then_cross_seed_reduction_percent":60,
    }
    assert late["field_status"]=="NO_DETECTED_MATERNAL_OR_PATERNAL_FITNESS_EFFECT"
    assert late["morph_specific_functional_avoidance"]=={
        "long_styled":"PROTANDRY_REDUCED_EARLY_STIGMA_RECEPTIVITY",
        "short_styled":"HERKOGAMY_SPATIAL_STIGMA_ANTHER_SEPARATION",
    }
    assert n["same_population_year_and_field_environment_established"] is False
    assert n["new_independent_biological_cluster"] is False


def test_historical_solanum_and_unresolved_ipomopsis_not_false_absences():
    cases={
        x["dependency_group"]:x
        for x in analyze_multiplex_sources(files())["source_cases"]
    }
    sol=cases["Solanum_rostratum"]
    assert ALIAS=={"Solanum_rostratum_historical":"Solanum_rostratum"}
    assert sol["u2_conflict_status"]=="NO_DEMONSTRATED_CONFLICT"
    assert sol["u2_architecture_mode"]=="UNRESOLVED"
    assert sol["pilot_conflict_status"]=="POSITIVE"
    assert sol["pilot_architecture_mode"]=="WITHIN_FLOWER_DIVISION_OF_LABOUR"
    assert sol["source_anchor_publications"][0]["id"]=="Todd_1882_American_Naturalist"
    assert sol["source_anchor_publications"][1]["doi"]=="10.1111/j.1420-9101.2009.01693.x"
    ip=cases["Ipomopsis_aggregata"]
    assert ip["u2_conflict_status"]=="POSITIVE"
    assert ip["pilot_conflict_status"]=="UNRESOLVED"
    assert ip["source_anchor_publications"][0]["doi"]=="10.1002/j.1537-2197.1991.tb14511.x"
    assert all(v["net_structural_BALANCE_identified"] is False
               for v in (sol,ip))


def test_no_selected_subset_faux_macro_prevalence_allowed():
    a,b,c,reg=data()
    with pytest.raises(ValueError,match="22\\+22\\+29"):
        analyze_flower_multiplex(a,b,c[:-1],reg)
    broken=copy.deepcopy(c)
    for row in broken:
        if row["system_taxon"]=="Polemonium viscosum":
            row["architecture_mode"]="SEPARATE_MODULES"
    with pytest.raises(ValueError,match="source status or architecture altered"):
        analyze_flower_multiplex(a,b,broken,reg)
    broken=copy.deepcopy(c)
    for row in broken:
        row["primary_model_eligible"]="true"
    with pytest.raises(ValueError,match="confirmatory denominator"):
        analyze_flower_multiplex(a,b,broken,reg)


def test_source_anchor_frozen_printed_numbers_and_external_meta_false():
    a,b,c,reg=data()
    modified=copy.deepcopy(reg)
    modified["cases"][1]["source_anchors"][0]["quantified_source_values"][
        "first_year_seed_set_reduction_percent"]=55
    with pytest.raises(ValueError,match="original printed effect anchors changed"):
        analyze_flower_multiplex(a,b,c,modified)
    modified=copy.deepcopy(reg)
    modified["independent_double_adjudication_complete"]=True
    with pytest.raises(ValueError,match="cross-source experiment"):
        _verified_anchor_registry(modified)
    modified=copy.deepcopy(reg)
    modified["direct_structural_BALANCE_occupancy_identified"]=True
    with pytest.raises(ValueError,match="cross-source experiment"):
        _verified_anchor_registry(modified)
    modified=copy.deepcopy(reg)
    modified["new_independent_biological_clusters"]=4
    with pytest.raises(ValueError,match="cross-source experiment"):
        _verified_anchor_registry(modified)
    modified=copy.deepcopy(reg)
    modified["cases"][0]["source_anchors"][0]["doi"]="invented DOI"
    with pytest.raises(ValueError,match="original source anchor"):
        _verified_anchor_registry(modified)


def test_source_conflict_and_architecture_ledger_synchronization():
    u2,source,pilot,reg=data()
    broken=copy.deepcopy(source)
    for row in broken:
        if row["dependency_group"]=="Polemonium_viscosum":
            row["conflict_status"]="NO_DEMONSTRATED_CONFLICT"
    with pytest.raises(ValueError,match="strict conflict source versus architecture"):
        analyze_flower_multiplex(u2,broken,pilot,reg)
    broken=copy.deepcopy(source)
    for row in broken:
        if row["dependency_group"]=="Polemonium_viscosum":
            row["system_taxon"]="Unrelated species"
    with pytest.raises(ValueError,match="species identity label mismatch"):
        analyze_flower_multiplex(u2,broken,pilot,reg)


def test_historical_alias_is_explicit_and_not_fuzzy_name_merging():
    u2,source,pilot,reg=data()
    broken=copy.deepcopy(u2)
    for row in broken:
        if row["dependency_group"]=="Solanum_rostratum_historical":
            row["dependency_group"]="Solanum_lycocarpum_historical"
    with pytest.raises(ValueError,match="overlap of U2 complete review"):
        analyze_flower_multiplex(broken,source,pilot,reg)
    broken=copy.deepcopy(pilot)
    for row in broken:
        if row["dependency_group"]=="Solanum_rostratum":
            row["dependency_group"]="Solanum_rostratum_historical"
    with pytest.raises(ValueError,match="only valid in U2"):
        analyze_flower_multiplex(u2,source,broken,reg)


def test_source_sha256_receipt_no_overwrite(tmp_path):
    out=tmp_path/"readout.json"
    result=source_multiplex_receipt(ROOT,out)
    assert json.loads(out.read_text(encoding="utf-8"))==result
    for key,value in result["original_source_sha256"].items():
        assert hashlib.sha256((ROOT/key).read_bytes()).hexdigest()==value
    with pytest.raises(ValueError,match="refuse to overwrite"):
        source_multiplex_receipt(ROOT,out)

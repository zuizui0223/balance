"""Source-review overlap is a biological specificity result, not prevalence.

The two reviews intentionally screen different function pairs; the 69 row
denominators are NOT exchangeable randomized samples of flowering plants.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from balance_domain.plant_cross_frame_conflict import (
    REGISTERED_OVERLAP,REQUIRED_SOURCE_PATHS,SCHEMA,
    analyze_cross_frame_rows,analyze_cross_frame_sources,
)
from balance_domain.plant_u1_screen import load_u1_blind_screen
from balance_domain.plant_u1_production_screen import load_u1_production_blind_screen
from balance_domain.plant_u2_screen import load_u2_conflict_screen
from balance_domain.plant_macro import load_plant_macro_ledger
from scripts.audit_plant_cross_frame_conflict import build_receipt

ROOT=Path(__file__).resolve().parents[1]


def paths():
    return {p:ROOT/p for p in REQUIRED_SOURCE_PATHS}


def fixture_rows():
    src=paths()
    return (
        load_u1_blind_screen(src[REQUIRED_SOURCE_PATHS[0]])+
        load_u1_production_blind_screen(src[REQUIRED_SOURCE_PATHS[1]]),
        load_u2_conflict_screen(src[REQUIRED_SOURCE_PATHS[2]]),
        load_plant_macro_ledger(src[REQUIRED_SOURCE_PATHS[3]]),
    )


def test_two_review_universes_are_complete_and_no_prevalence_is_inferred():
    r=analyze_cross_frame_sources(paths())
    assert r["schema_version"]==SCHEMA
    assert r["status"]=="SCREENED_PAIR_SPECIFIC_CONFLICT_HETEROGENEITY_NOT_CONFIRMATORY"
    assert r["n_source_scope_records_across_frames"]==69
    assert r["n_distinct_dependency_groups_across_frames"]==67
    assert r["n_shared_species_between_frames"]==2
    assert r["screened_review_frames"]["U1"]["source_screen_conflict_status_counts"]=={
        "NO_DEMONSTRATED_CONFLICT":46,"ALIGNED_NO_CONFLICT":1
    }
    assert r["screened_review_frames"]["U2"]["source_screen_conflict_status_counts"]=={
        "POSITIVE":8,"NO_DEMONSTRATED_CONFLICT":14
    }
    assert r["nonexchangeable_review_sampling_frames"] is True
    assert r["positive_source_screen_not_independently_adjudicated"] is True
    assert r["do_not_fisher_exact_test_U1_versus_U2"] is True
    assert r["not_natural_prevalence_or_survey_inclusion_probability"] is True
    assert r["not_net_structural_architecture_fitness_or_BALANCE_occupancy"] is True
    assert r["new_independent_biological_clusters"]==0
    assert len(r["original_screening_source_sha256"])==4
    assert all(len(v)==64 for v in r["original_screening_source_sha256"].values())


def test_same_species_has_mechanism_specific_conflict_evidence_not_temporal_shift():
    r=analyze_cross_frame_sources(paths())
    match={x["dependency_group"]:x for x in r["shared_species_mechanism_specific_contrasts"]}
    assert set(match)==REGISTERED_OVERLAP=={
        "Mimulus_aurantiacus","Ipomopsis_aggregata"
    }
    for v in match.values():
        assert v["u1_conflict_status"]=="NO_DEMONSTRATED_CONFLICT"
        assert v["u2_conflict_status"]=="POSITIVE"
        assert v["same_functions_or_trait_coordinate_measured"] is False
        assert v["same_population_year_or_experimental_context_established"] is False
        assert v["absence_of_U1_conflict_proven"] is False
        assert v["new_biological_cluster_created"] is False
        assert v["u1_source_basis"] and v["u2_source_basis"]
    assert match["Mimulus_aurantiacus"]["u2_resolved_architecture_mode"]=="SPATIAL_SEPARATION"
    assert match["Ipomopsis_aggregata"]["u2_resolved_architecture_mode"]=="SHARED_INTEGRATED"


def test_direct_sexual_interference_can_coexist_with_integrated_flower():
    r=analyze_cross_frame_sources(paths())["screened_review_frames"]["U2"]
    assert r["n_demonstrated_same_coordinate_conflicts"]==8
    assert r["positive_conflict_primary_architecture_classes"]=={
        "SHARED":4,"NONSTRUCTURAL_SEPARATION":3,"MOSAIC":1
    }
    assert r["n_source_positive_resolved_architecture"]==7
    assert r["n_source_positive_unresolved_mosaic_architecture"]==1
    # Nine negative U2 rows nevertheless have visually complex mosaic
    # morphology; that does NOT demonstrate nonexistence of conflict.
    assert r["screened_no_demonstrated_conflict_architecture_mode_counts"][
        "POLYMORPHIC_OR_MOSAIC"
    ]==9
    assert r["adjudication_status"]=="SCREENED"


def test_u2_conflict_and_architecture_different_underlying_source_fail():
    u1,u2,modes=fixture_rows()
    bad=copy.deepcopy(modes)
    i=next(i for i,x in enumerate(bad) if x["dependency_group"]=="Mimulus_aurantiacus")
    bad[i]["conflict_status"]="NO_DEMONSTRATED_CONFLICT"
    with pytest.raises(ValueError,match="source disagreement"):
        analyze_cross_frame_rows(u1,u2,bad)
    bad=copy.deepcopy(modes)
    bad[i]["architecture_mode"]="SHARED_INTEGRATED"
    with pytest.raises(ValueError,match="distribution changed"):
        analyze_cross_frame_rows(u1,u2,bad)


def test_source_frame_completeness_and_collision_fail_closed():
    u1,u2,modes=fixture_rows()
    with pytest.raises(ValueError,match="frozen 47"):
        analyze_cross_frame_rows(u1[:-1],u2,modes)
    bad=copy.deepcopy(u1)
    bad[1]["dependency_group"]=bad[0]["dependency_group"]
    with pytest.raises(ValueError,match="duplicate dependency"):
        analyze_cross_frame_rows(bad,u2,modes)
    bad=copy.deepcopy(u1)
    bad[0]["architecture_status"]="IDENTIFIED"
    with pytest.raises(ValueError,match="does NOT identify architecture"):
        analyze_cross_frame_rows(bad,u2,modes)


def test_source_specificity_is_not_negation_or_general_species_conflict():
    u1,u2,modes=fixture_rows()
    bad=copy.deepcopy(u1)
    ix=next(i for i,x in enumerate(bad) if x["dependency_group"]=="Ipomopsis_aggregata")
    bad[ix]["conflict_status"]="POSITIVE"
    with pytest.raises(ValueError,match="frozen U1"):
        analyze_cross_frame_rows(bad,u2,modes)
    bad=copy.deepcopy(modes)
    bad[0]["adjudication_status"]="ADJUDICATED"
    with pytest.raises(ValueError,match="remains SCREENED"):
        analyze_cross_frame_rows(u1,u2,bad)


def test_no_new_artificial_cluster_or_fractional_meta_effect(tmp_path):
    out=tmp_path/"cross_frame.json"
    result=build_receipt(ROOT,out)
    assert json.loads(out.read_text(encoding="utf-8"))==result
    for path,raw_digest in result["original_screening_source_sha256"].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==raw_digest
    with pytest.raises(ValueError,match="refusing overwrite"):
        build_receipt(ROOT,out)

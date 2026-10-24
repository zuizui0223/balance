"""Real public GBIF occurrence snapshots vs selected GloBI source coverage.

Tests analyze 48 ACTUALLY acquired independent species-first source records.
Source counts and documentation associations do not demonstrate herbivory,
pollination fitness, ecological absence, or a structural BALANCE region.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from balance_domain.gbif_occurrence_effort import (
    SCHEMA, READOUT,
    audit_effort_and_GloBI,
    git_blob_sha1,
    source_effort_audit_from_files,
)
from scripts.audit_gbif_occurrence_effort import write_source_readout

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"data/BALANCE_GBIF_OCCURRENCE_EFFORT_48_SOURCE_MANIFEST_V1.json"


def originals():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    selected=json.loads((ROOT/manifest["original_GBIF_selected_manifest_path"]).read_text())
    network=json.loads((ROOT/manifest["original_GloBI_static_coverage_path"]).read_text())
    batch={v["path"]:(ROOT/v["path"]).read_bytes() for v in manifest["source_batch_paths"]}
    return manifest,selected,network,batch


def test_actual_48_species_independent_GBIF_effort_audit():
    v=source_effort_audit_from_files(ROOT,MANIFEST)
    assert v["schema_version"]==READOUT
    assert v["status"]=="ACTUAL_OCCURRENCE_DOCUMENTATION_EFFORT_ASSOCIATION_NOT_FITNESS"
    a=v["source_source_aggregate"]
    assert a=={
        "n_species":48,
        "n_families":12,
        "n_with_any_GBIF_occurrence":45,
        "total_GBIF_indexed_occurrences":20131,
        "total_GBIF_occurrences_with_coordinates":13049,
        "n_with_GloBI_exact_target_name":16,
        "n_without_GloBI_exact_target_name":32,
        "n_without_GloBI_but_with_GBIF_records":29,
        "median_GBIF_occurrences_GloBI_documented":701,
        "median_GBIF_occurrences_GloBI_undocumented":6.5,
        "n_families_with_both_GloBI_documented_and_not":5,
        "n_families_with_higher_documented_median_GBIF_occurrences":5,
        "n_GloBI_documented_among_family_top_two_GBIF_counts":11,
        "n_GloBI_documented_among_family_bottom_two_GBIF_counts":5,
    }
    assert len(v["species"])==48
    assert len(v["family_strata"])==12
    assert len(v["source_batch_sha256"])==12
    assert len(v["effort_source_manifest_sha256"])==64
    assert v["pollinator_antagonist_conflict_not_identified"] is True
    assert v["fitness_impact_or_SCH_L_identified"] is False
    assert v["net_structural_BALANCE_occupancy_identified"] is False
    assert v["additional_independent_biological_clusters"]==0


def test_rare_plant_is_not_all_interaction_absence_and_search_index_field_zero_is_not_effort():
    v=source_effort_audit_from_files(ROOT,MANIFEST)
    by={x["species"]:x for x in v["species"]}
    assert by["Solanum asperolanatum"]["gbif_occurrence_search_count"]==4244
    assert by["Solanum asperolanatum"]["gbif_occurrence_search_has_coordinates_count"]==2372
    assert by["Solanum asperolanatum"]["globi_exact_target_name_relation_rows"]==103
    assert by["Oryza barthii"]["gbif_occurrence_search_count"]==4551
    assert by["Oryza barthii"]["gbif_occurrence_search_has_coordinates_count"]==3719
    assert by["Chrysanthemum bizarre"]["gbif_occurrence_search_count"]==0
    assert all(r["GBIF_species_search_numOccurrences_field"]==0 for r in v["species"])
    assert sum(x["globi_name_recorded"] for x in v["species"])==16
    assert sum(x["globi_exact_target_name_relation_rows"] for x in v["species"])==188
    assert v["GloBI_absence_is_not_ecological_interaction_absence"] is True


def test_within_family_descriptive_effort_rank_and_five_mixed_strata():
    v=source_effort_audit_from_files(ROOT,MANIFEST)
    fam=v["family_strata"]
    mixed=[x for x in fam if 0<x["n_GloBI_name_documented"]<4]
    assert {x["family"] for x in mixed}=={
        "Fabaceae","Rosaceae","Rubiaceae","Brassicaceae","Ericaceae"
    }
    assert all(x["documented_greater_than_undocumented_median"] is True
               for x in mixed)
    assert sum(x["top_two_occurrence_species_with_GloBI"] for x in fam)==11
    assert sum(x["bottom_two_occurrence_species_with_GloBI"] for x in fam)==5
    assert sum(x["GBIF_occurrence_count_total"] for x in fam)==20131
    assert v["family_median_comparison_is_not_causal_or_exchangeable"] is True


def test_original_public_response_blob_and_source_taxon_order_are_locked():
    m,s,c,b=originals()
    assert m["schema_version"]==SCHEMA
    assert len(m["source_batch_paths"])==12
    assert git_blob_sha1((ROOT/m["original_GBIF_selected_manifest_path"]).read_bytes())==m[
        "original_GBIF_selected_manifest_git_blob_sha1"
    ]
    for r in m["source_batch_paths"]:
        assert git_blob_sha1(b[r["path"]])==r["git_blob_sha1"]
    assert len({r["gbif_species_key"] for r in s["species"]})==48


def test_wrong_species_and_source_blob_are_rejected_instead_of_mutated():
    m,s,c,b=originals()
    corrupt=copy.deepcopy(b)
    first=m["source_batch_paths"][0]["path"]
    corrupt[first]=corrupt[first].replace(b'"count":',b'"new_count":',1)
    with pytest.raises(ValueError,match="original GBIF occurrence source text changed"):
        audit_effort_and_GloBI(m,s,c,corrupt)
    other=copy.deepcopy(s)
    other["species"][0],other["species"][1]=other["species"][1],other["species"][0]
    with pytest.raises(ValueError,match="frozen species-first position"):
        audit_effort_and_GloBI(m,other,c,b)
    nofile=dict(b);nofile.pop(first)
    with pytest.raises(ValueError,match="all twelve"):
        audit_effort_and_GloBI(m,s,c,nofile)


def test_original_gbif_response_coordinates_cannot_exceed_total():
    m,s,c,b=originals()
    corrupt=dict(b)
    path=m["source_batch_paths"][0]["path"]
    dat=json.loads(corrupt[path])
    original=dat["records"][0]
    original["with_coordinates"]["count"]=original["total"]["count"]+1
    raw=json.loads(original["with_coordinates"]["original_source_text"])
    raw["count"]=original["with_coordinates"]["count"]
    original["with_coordinates"]["original_source_text"]=json.dumps(raw)
    corrupt[path]=(json.dumps(dat,indent=2)+"\n").encode()
    other=copy.deepcopy(m)
    other["source_batch_paths"][0]["git_blob_sha1"]=git_blob_sha1(corrupt[path])
    with pytest.raises(ValueError,match="georeferenced GBIF occurrence count"):
        audit_effort_and_GloBI(other,s,c,corrupt)


def test_cross_date_bias_and_fake_ecological_promotion_rejected():
    m,s,c,b=originals()
    invalid=copy.deepcopy(m)
    invalid["gbif_snapshot_date"]="2026-10-19"
    with pytest.raises(ValueError,match="different dated"):
        audit_effort_and_GloBI(invalid,s,c,b)
    invalid=copy.deepcopy(m)
    invalid["sampling_and_ecological_claim_limits"][
        "strict_structural_BALANCE_occupancy_identified"]=True
    with pytest.raises(ValueError,match="do not measure structural BALANCE"):
        audit_effort_and_GloBI(invalid,s,c,b)
    invalid=copy.deepcopy(m)
    invalid["sampling_and_ecological_claim_limits"][
        "unrecorded_GloBI_interaction_not_biological_absence"]=False
    with pytest.raises(ValueError,match="source taxonomy and inference limits"):
        audit_effort_and_GloBI(invalid,s,c,b)


def test_unmodified_output_no_overwrite_or_secret_source_join(tmp_path):
    out1=tmp_path/"effort.json"
    out2=tmp_path/"effort.csv"
    result=write_source_readout(ROOT,MANIFEST,out1,out2)
    assert result==json.loads(out1.read_text(encoding="utf-8"))
    lines=out2.read_text(encoding="utf-8").splitlines()
    assert len(lines)==49
    assert all("structural" not in line.lower() for line in lines)
    with pytest.raises(ValueError,match="destination exists"):
        write_source_readout(ROOT,MANIFEST,out1,out2)
    assert result["source_GBIF_date"]=="2026-10-24"
    assert result["source_GloBI_date"]=="2026-10-19"

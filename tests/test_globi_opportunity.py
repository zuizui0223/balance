"""Real archived public GloBI relation dataset test; NO fitness/selection conflict."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from balance_domain.globi_opportunity import (
    COLS, FROZEN, READOUT_SCHEMA,
    _csv_records, _git_blob_sha1,
    summarize_globi_opportunity_snapshot, summarize_globi_files,
)
from scripts.audit_globi_opportunity_pilot import build_pilot_receipt

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"data/BALANCE_GLOBI_OPPORTUNITY_SOURCE_SNAPSHOT_V1.json"


def dataset():
    v=json.loads(CONTRACT.read_text(encoding="utf-8"))
    rows={t["snapshot_path"]:(ROOT/t["snapshot_path"]).read_bytes()
          for t in v["taxa"]}
    return v,rows


def test_real_public_gloBI_source_coverage_is_taxonomy_limited_not_conflict():
    r=summarize_globi_files(ROOT,CONTRACT)
    assert r["schema_version"]==READOUT_SCHEMA
    assert r["status"]=="ARCHIVED_PUBLIC_GLOBI_INTERACTION_OPPORTUNITY_NOT_FITNESS_CONFLICT"
    assert r["n_source_selected_plant_queries"]==4
    assert r["total_original_snapshot_relation_rows"]==254
    assert r["total_strict_exact_target_taxon_rows"]==96
    assert r["total_mismatched_target_taxon_rows"]==158
    assert r["Solanum_rostratum_Dunal_verified_interaction_records"] is None
    assert r["snapshot_not_unbiased_flora_population"] is True
    assert r["interaction_opportunity_is_not_direct_conflict_or_fitness"] is True
    assert r["strict_structural_BALANCE_occupancy_identified"] is False
    assert r["added_independent_biological_clusters"]==0
    assert len(r["source_contract_sha256"])==64


def test_unchanged_source_interaction_types_preserve_actual_relations_not_visits_as_success():
    data=summarize_globi_files(ROOT,CONTRACT)
    r={v["taxon"]:v for v in data["source_relations_by_focal_plant"]}
    assert r["Polemonium viscosum"]["total_source_snapshot_relations"]==30
    assert r["Polemonium viscosum"]["strict_exact_target_species_relations"]==28
    assert r["Polemonium viscosum"]["strict_exact_taxon_relation_class_counts"]["pollinates"]==7
    assert r["Polemonium viscosum"]["strict_exact_taxon_relation_class_counts"]["visitsFlowersOf"]==2
    assert r["Narcissus assoanus"]["strict_exact_target_species_relations"]==2
    assert r["Narcissus assoanus"]["strict_exact_taxon_relation_class_counts"]=={
        "pathogenOf":1,"visits":1
    }
    assert r["Ipomopsis aggregata"]["total_source_snapshot_relations"]==126
    assert r["Ipomopsis aggregata"]["strict_exact_target_species_relations"]==66
    assert r["Ipomopsis aggregata"]["strict_exact_taxon_relation_class_counts"]["pollinates"]==8
    assert r["Ipomopsis aggregata"]["strict_exact_taxon_relation_class_counts"]["visitsFlowersOf"]==16
    assert r["Ipomopsis aggregata"]["target_side_taxonomy_mismatched_relations"]==60
    assert all(x["could_infer_SCH_opposing_selection"] is False for x in r.values())
    assert all(x["source_relation_is_independently_verified_plant_fitness"] is False for x in r.values())
    assert all(x["source_taxonomic_rank_species_only_verified"] is False for x in r.values())


def test_solanum_homonym_forbidden_to_autoresolve_even_96_query_rows():
    spec,bytes_by_path=dataset()
    result=summarize_globi_opportunity_snapshot(spec,bytes_by_path)
    sol=next(v for v in result["source_relations_by_focal_plant"]
             if v["taxon"]=="Solanum rostratum")
    assert sol["total_source_snapshot_relations"]==96
    assert sol["strict_exact_target_species_relations"]==0
    assert sol["target_side_mismatch_names_with_counts"]=={
        "Solanum angustifolium":96
    }
    assert sol["focal_identification_status"]=="NO_AUTO_RESOLUTION_AMBIGUOUS_HOMONYM"
    assert result["Solanum_rostratum_Dunal_verified_interaction_records"] is None
    assert "cannot infer biological absence" in result["why_not_zero"]


def test_original_api_text_blob_hashes_are_frozen_and_read_only():
    spec,raw=dataset()
    for row in spec["taxa"]:
        path=row["snapshot_path"]
        assert _git_blob_sha1(raw[path])==row["git_blob_sha1"]
        parsed=_csv_records(raw[path])
        assert len(parsed)==row["expected_total_rows"]
        assert tuple(parsed[0])==COLS
    assert sum(x["expected_exact_target_rows"] for x in spec["taxa"])==96
    assert sum(x["expected_other_target_rows"] for x in spec["taxa"])==158


def test_tampering_snapshot_and_contract_closes_counts():
    spec,raw=dataset()
    path=spec["taxa"][0]["snapshot_path"]
    changed=dict(raw)
    changed[path]=changed[path].replace(b"Bombus",b"Dombus",1)
    with pytest.raises(ValueError,match="source snapshot changed"):
        summarize_globi_opportunity_snapshot(spec,changed)
    changed=dict(raw)
    del changed[path]
    with pytest.raises(ValueError,match="all four original source"):
        summarize_globi_opportunity_snapshot(spec,changed)
    reg=copy.deepcopy(spec)
    reg["taxa"][0]["expected_exact_target_rows"]=30
    with pytest.raises(ValueError,match="frozen raw/strict"):
        summarize_globi_opportunity_snapshot(reg,raw)
    reg=copy.deepcopy(spec)
    reg["source_name_matches_outside_target_side_do_not_count_as_target_query_matches"]=False
    with pytest.raises(ValueError,match="source-side target"):
        summarize_globi_opportunity_snapshot(reg,raw)


def test_no_public_relation_can_be_relabelled_as_positive_selection_or_balance():
    spec,raw=dataset()
    for field,value in (
        ("empirical_direct_SCH_conflict_identified",True),
        ("net_architecture_BALANCE_occupancy_identified",True),
        ("novel_independent_biological_clusters_added",1),
        ("no_interaction_means_absence_of_ecological_agent",True),
        ("source_species_richness_from_aggregated_higher_taxon_rows_identified",True),
    ):
        d=copy.deepcopy(spec)
        d[field]=value
        with pytest.raises(ValueError,match="source inference boundary"):
            summarize_globi_opportunity_snapshot(d,raw)


def test_runner_pins_source_and_cannot_overwrite(tmp_path):
    dest=tmp_path/"globi_opportunity.json"
    result=build_pilot_receipt(ROOT,CONTRACT,dest)
    assert result==json.loads(dest.read_text(encoding="utf-8"))
    assert result["total_original_snapshot_relation_rows"]==254
    with pytest.raises(ValueError,match="cannot overwrite"):
        build_pilot_receipt(ROOT,CONTRACT,dest)
    spec,_=dataset()
    assert spec["source_method"].startswith("TinyFish public page text extraction")
    assert spec["api_nonversioned_and_live_queries_unstable"] is True
    assert spec["retrieval_date"]=="2026-10-19"

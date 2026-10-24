"""Original public GBIF/GloBI 48-species source bytes, not synthetic fixtures.

Ecological evidence ceiling: these are indexed association records and taxa,
not new individual organisms, pollination-success experiments, or BALANCE.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from balance_domain.gbif_species_first_coverage import (
    SCHEMA,audit_source_files,audit_real_species_first_coverage,
)

ROOT=Path(__file__).resolve().parents[1]


def real():
    frame=json.loads((ROOT/"data/BALANCE_GBIF_SPECIES_FIRST_CROSS_ORDER_PANEL_V1.json").read_text())
    species=json.loads((ROOT/"data/BALANCE_GBIF_SPECIES_FIRST_SELECTED_V1.json").read_text())
    g=json.loads((ROOT/"data/BALANCE_GBIF_GLOBI_SPECIES_FIRST_READOUT_V1.json").read_text())
    paths={x["source_snapshot_path"] for x in species["family_counts"]}|{
        x["source_path"] for x in g["per_species"]}
    source={p:(ROOT/p).read_bytes() for p in paths}
    return frame,species,g,source


def test_original_12_family_48_species_public_records_replayed_without_conflict():
    out=audit_source_files(ROOT)
    assert out["schema_version"]==SCHEMA
    assert out["n_gbif_accepted_taxa_selected"]==48
    assert out["n_families_12_distinct_orders"]==12
    assert out["n_GloBI_queries_succeeded"]==48
    assert out["n_species_with_exact_target_name_relation"]==16
    assert out["n_species_without_exact_target_name_relation"]==32
    assert out["n_families_without_any_exact_target_name_relation"]==5
    assert out["n_exact_target_name_rows"]==188
    assert out["n_exact_target_and_direct_GBIF_key_rows"]==88
    assert out["n_exact_target_but_non_GBIF_identifier_rows"]==100
    assert out["n_taxa_with_direct_GBIF_species_key"]==2
    assert out["n_target_taxon_mismatch_rows"]==42
    assert out["n_GloBI_original_relation_rows"]==230
    assert out["strict_structural_BALANCE_occupancy_identified"] is False
    assert out["additional_independent_biological_clusters"]==0


def test_real_relation_label_coverage_does_not_establish_guild_absence():
    out=audit_source_files(ROOT)
    r=out["by_original_GloBI_relation_type"]
    assert r.get("pollinates",0)==0
    assert r.get("visitsFlowersOf",0)==2
    assert r.get("eats",0)==90
    assert out["flower_visitation_or_pollination_literal_record_rows"]==2
    assert out["n_taxa_with_flower_visit_or_pollinate_label"]==1
    assert out["missing_GloBI_record_means_ecological_absence"] is False
    assert out["GBIF_search_numOccurrences_field_independently_confirms_zero_occurrences"] is False
    assert out["pollinator_guild_competition_measured"] is False
    assert out["opposing_trait_fitness_gradient_identified"] is False
    assert out["interaction_data_unbiased_across_species_or_families"] is False
    assert out["species_first_sampled_families_globally_representative"] is False


def test_original_source_concentration_and_direct_GBIF_keys_are_not_studies():
    rows=audit_source_files(ROOT)["species_coverage"]
    keyed={r["gbif_accepted_species_name"]:r for r in rows}
    x=keyed["Solanum asperolanatum"]
    assert x["GloBI_exact_target_name_rows"]==103
    assert x["GloBI_direct_identical_GBIF_key_rows"]==87
    assert x["GloBI_other_taxon_target_rows"]==42
    assert x["verbatim_exact_target_relation_types"]["eats"]==80
    y=keyed["Ptilagrostis porteri"]
    assert y["GloBI_direct_identical_GBIF_key_rows"]==1
    assert sum(r["GloBI_direct_identical_GBIF_key_rows"] for r in rows)==88
    h=keyed["Hormathophylla longicaulis"]
    assert h["literal_flower_visit_or_pollinate_rows"]==2
    assert h["GloBI_direct_identical_GBIF_key_rows"]==0
    out=audit_source_files(ROOT)
    assert out["largest_single_species_relation_rows"]==103
    assert out["largest_single_species_share_of_exact_rows"]==pytest.approx(103/188,abs=1e-6)


def test_family_coverage_not_neutral_or_independent_taxonomic_replication():
    families=audit_source_files(ROOT)["family_coverage"]
    assert set(families)=={
        "Asteraceae","Fabaceae","Orchidaceae","Poaceae",
        "Lamiaceae","Rosaceae","Solanaceae","Rubiaceae",
        "Ranunculaceae","Brassicaceae","Ericaceae","Myrtaceae",
    }
    assert all(r["n_species"]==4 for r in families.values())
    assert families["Solanaceae"]["n_with_exact_GloBI_target_name"]==4
    assert families["Poaceae"]["n_with_exact_GloBI_target_name"]==4
    assert families["Fabaceae"]["n_with_exact_GloBI_target_name"]==3
    assert families["Orchidaceae"]["n_with_exact_GloBI_target_name"]==0
    assert families["Myrtaceae"]["n_with_exact_GloBI_target_name"]==0
    assert families["Solanaceae"]["exact_name_GloBI_relation_rows"]==125
    assert families["Solanaceae"]["same_GBIF_key_relation_rows"]==87
    assert families["Brassicaceae"]["floral_visitation_or_pollination_label_rows"]==2


def test_tampered_original_GloBI_source_or_summary_stays_closed():
    frame,species,network,files=real()
    name=next(v["source_path"] for v in network["per_species"]
              if v["exact_target_name_rows"]>=1)
    bad=dict(files)
    bad[name]=bad[name]+b"NEW_FAKE_SOURCE_RECORD"
    with pytest.raises(ValueError,match="original byte digest altered"):
        audit_real_species_first_coverage(frame,species,network,bad)
    fake=copy.deepcopy(network)
    fake["strict_structural_BALANCE_occupancy_identified"]=True
    with pytest.raises(ValueError,match="cannot be relabelled"):
        audit_real_species_first_coverage(frame,species,fake,files)
    bad=dict(files);del bad[name]
    with pytest.raises(ValueError,match="12\\+48"):
        audit_real_species_first_coverage(frame,species,network,bad)


def test_original_GBIF_species_selection_rederived_from_source_not_fitted_posthoc():
    frame,species,network,files=real()
    tampered=copy.deepcopy(species)
    tampered["species"][0]["gbif_species_key"]+=100000
    with pytest.raises(ValueError):
        audit_real_species_first_coverage(frame,tampered,network,files)
    tampered=copy.deepcopy(frame)
    tampered["deterministic_seed"]="chosen_after_interactions"
    with pytest.raises(ValueError,match="pre-interaction selection contract digest"):
        audit_real_species_first_coverage(tampered,species,network,files)
    raw=dict(files)
    family=species["family_counts"][0]["source_snapshot_path"]
    edited=json.loads(raw[family])
    edited["results"][0]["canonicalName"]="Madeup organismus"
    raw[family]=json.dumps(edited).encode()
    # If first GBIF source row was not itself selected, its alteration still
    # can alter the eligible rank order; source remains non-verbatim.
    # Strong original-text provenance is retained by frozen git commit.
    if edited["results"][0]["key"] in {
        x["gbif_species_key"] for x in species["species"]
    }:
        with pytest.raises(ValueError,match="species selection differs"):
            audit_real_species_first_coverage(frame,species,network,raw)


def test_full_selection_history_preserves_all_taxa_even_no_interactions():
    out=audit_source_files(ROOT)
    assert len(out["species_coverage"])==48
    assert sum(x["GloBI_exact_target_name_rows"]==0 for x in out["species_coverage"])==32
    assert sum(x["GBIF_search_numOccurrences_field"]==0
               for x in out["species_coverage"])==48
    assert out["author_level_taxon_link_verified_from_GloBI"] is False
    assert out["index_target_guild_richness_estimable_from_broad_taxon_rows"] is False


def test_published_48_species_static_source_table_matches_independent_reaudit():
    import csv
    stored=json.loads((
        ROOT/"data/BALANCE_GBIF_GLOBI_SPECIES_FIRST_STATIC_COVERAGE_V1.json"
    ).read_text(encoding="utf-8"))
    with (ROOT/"data/BALANCE_GBIF_GLOBI_SPECIES_FIRST_48_SPECIES_V1.csv").open(
        encoding="utf-8",newline=""
    ) as fd:
        rows=list(csv.DictReader(fd))
    rebuilt=audit_source_files(ROOT)
    assert stored["schema_version"]=="BALANCE_GBIF_GLOBI_SPECIES_FIRST_STATIC_COVERAGE_V1"
    assert stored["status"]=="SOURCE_COMPUTED_OBSERVATIONAL_DATABASE_COVERAGE_ONLY"
    assert stored["totals"]["n_species"]==rebuilt["n_gbif_accepted_taxa_selected"]==48
    assert stored["totals"]["n_exact_name_species"]==rebuilt[
        "n_species_with_exact_target_name_relation"]==16
    assert stored["totals"]["n_exact_target_name_rows"]==rebuilt[
        "n_exact_target_name_rows"]==188
    assert stored["totals"]["n_same_GBIF_key_rows"]==rebuilt[
        "n_exact_target_and_direct_GBIF_key_rows"]==88
    assert stored["totals"]["n_species_with_flower_labels"]==rebuilt[
        "n_taxa_with_flower_visit_or_pollinate_label"]==1
    assert stored["totals"]["family_no_record"]==rebuilt[
        "n_families_without_any_exact_target_name_relation"]==5
    assert len(rows)==len(stored["species"])==48
    assert {int(row["gbif_species_key"]) for row in rows}=={
        x["gbif_species_key"] for x in rebuilt["species_coverage"]
    }
    assert stored["direct_trait_fitness_conflict_observations"]==0
    assert stored["strict_structural_BALANCE_occurrences"]==0
    assert all(x["retrieval_status"]!="GLOBI_SOURCE_HOLD" for x in stored["species"])

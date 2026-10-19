"""Source-backed GloBI interaction OPPORTUNITY pilot with strict taxon checks.

This is genuinely retrieved external public database information, but:
- 4 taxa chosen from prior informative botanical papers, NOT a random
  angiosperm denominator or a study of interaction prevalence.
- GloBI query expansion may resolve homonyms/other taxa. NEVER count those
  records for the requested focal target species without a verified
  authorship/accepted-concept crosswalk.
- source taxa include broad ranks, ambiguous names, and repeated interaction
  classes; no independent agent-species counts are inferred.
- "pollinates" and "visitsFlowersOf" are verbatim public interaction labels,
  NOT measured pollination success or the functional conflict L>0.
- Live GloBI search responses change over time. Stored text is a dated
  source snapshot, not an API release and not original network raw bytes.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

SCHEMA="BALANCE_GLOBI_OPPORTUNITY_SOURCE_SNAPSHOT_V1"
READOUT_SCHEMA="BALANCE_GLOBI_OPPORTUNITY_STRICT_TAXON_READOUT_V1"
COLS=(
    "source_taxon_external_id","source_taxon_name","source_taxon_path",
    "source_specimen_occurrence_id","source_specimen_institution_code",
    "source_specimen_collection_code","source_specimen_catalog_number",
    "source_specimen_life_stage","source_specimen_basis_of_record",
    "interaction_type","target_taxon_external_id","target_taxon_name",
    "target_taxon_path","target_specimen_occurrence_id",
    "target_specimen_institution_code","target_specimen_collection_code",
    "target_specimen_catalog_number","target_specimen_life_stage",
    "target_specimen_basis_of_record","latitude","longitude",
    "study_title",
)
FROZEN={
    "Polemonium viscosum":(30,28,{"pollinates":7,"visitsFlowersOf":2}),
    "Narcissus assoanus":(2,2,{"visits":1,"pathogenOf":1}),
    "Solanum rostratum":(96,0,{}),
    "Ipomopsis aggregata":(126,66,{"pollinates":8,"visitsFlowersOf":16}),
}
SOURCE_PROVENANCE_KEY="source_taxon_name"
TARGET_PROVENANCE_KEY="target_taxon_name"


def _git_blob_sha1(raw:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()


def _csv_records(raw:bytes)->list[dict[str,str]]:
    try:
        txt=raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("GloBI textual source snapshot must be UTF-8") from exc
    r=csv.DictReader(io.StringIO(txt))
    if tuple(r.fieldnames or ())!=COLS:
        raise ValueError("GloBI public API source field order/schema differs from snapshot")
    rows=list(r)
    if not rows:
        raise ValueError("GloBI source snapshot empty (do not infer zero interactions)")
    for n,row in enumerate(rows,start=2):
        if None in row or any(v is None for v in row.values()):
            raise ValueError(f"GloBI CSV source row {n} malformed")
        if not row["interaction_type"]:
            raise ValueError(f"GloBI source row {n} missing relation type")
    return rows


def _contract(spec:dict)->list[dict]:
    if not isinstance(spec,dict) or spec.get("schema_version")!=SCHEMA:
        raise ValueError("versioned GloBI source opportunity contract required")
    if spec.get("status")!="LIVE_PUBLIC_GLOBI_INTERACTION_TEXT_SNAPSHOT_NO_CONFLICT_DATA":
        raise ValueError("source opportunity evidence cannot be promoted into fitness")
    if spec.get("retrieval_date")!="2026-10-19":
        raise ValueError("source snapshot retrieval date changed")
    if spec.get("api_nonversioned_and_live_queries_unstable") is not True:
        raise ValueError("GloBI public API queries are not pinned immutable releases")
    if spec.get("source_name_matches_outside_target_side_do_not_count_as_target_query_matches") is not True:
        raise ValueError("source-side target name is not a target-side match")
    for key,val in (
        ("text_extraction_is_not_original_http_binary_archive",True),
        ("all_taxon_name_mismatches_retained_for_audit",True),
        ("no_interaction_means_absence_of_ecological_agent",False),
        ("source_species_richness_from_aggregated_higher_taxon_rows_identified",False),
        ("empirical_direct_SCH_conflict_identified",False),
        ("net_architecture_BALANCE_occupancy_identified",False),
        ("novel_independent_biological_clusters_added",0),
    ):
        observed=spec.get(key)
        if (observed is not val if isinstance(val,bool) else
            type(observed) is not int or observed != val):
            raise ValueError(f"GloBI source inference boundary changed: {key}")
    taxa=spec.get("taxa")
    if not isinstance(taxa,list) or len(taxa)!=4 or (
        {t.get("focal_query_taxon") for t in taxa}!=set(FROZEN)
    ):
        raise ValueError("four registered source-selected species required")
    for t in taxa:
        name=t["focal_query_taxon"]
        a,b,_=FROZEN[name]
        if t.get("expected_total_rows")!=a or t.get("expected_exact_target_rows")!=b or (
            t.get("expected_other_target_rows")!=a-b
        ):
            raise ValueError("GloBI frozen raw/strict species support drifted")
        if t.get("git_blob_sha1") is None or len(t["git_blob_sha1"])!=40:
            raise ValueError("source Git blob SHA1 must be frozen")
        if t.get("source_query_url")!=(
            "https://api.globalbioticinteractions.org/interaction.csv?targetTaxon="
            +name.replace(" ","%20")+"&limit=500"
        ):
            raise ValueError("registered GloBI query changed")
    so=spec.get("solanum_taxonomic_homonym_audit",{})
    if (so.get("query_name")!="Solanum rostratum" or
        so.get("focal_accepted_name")!="Solanum rostratum Dunal" or
        so.get("distinct_synonym_status")!="SYNONYM_OF_SOLANUM_ANGUSTIFOLIUM_MILL" or
        so.get("api_reported_target_name")!="Solanum angustifolium" or
        so.get("original_target_authorship_returned_by_GloBI") is not False or
        so.get("target_records_automatically_assigned_to_focal_rostratum_Dunal") !=0):
        raise ValueError("Solanum homonym author ambiguity must remain HOLD")
    return taxa


def summarize_globi_opportunity_snapshot(
    contract:dict,snapshots:dict[str,bytes],
)->dict:
    """Only exact target-TAXON-SIDE records can enter opportunity readout."""
    taxa=_contract(contract)
    if set(snapshots)!={t["snapshot_path"] for t in taxa}:
        raise ValueError("must provide all four original source snapshot paths")
    results=[]
    for t in taxa:
        path=t["snapshot_path"]
        raw=snapshots[path]
        if type(raw) is not bytes or _git_blob_sha1(raw)!=t["git_blob_sha1"]:
            raise ValueError(f"GloBI source snapshot changed: {path}")
        rows=_csv_records(raw)
        taxon=t["focal_query_taxon"]
        exact=[r for r in rows if r["target_taxon_name"]==taxon]
        rejected=[r for r in rows if r["target_taxon_name"]!=taxon]
        if len(rows)!=t["expected_total_rows"] or len(exact)!=t["expected_exact_target_rows"]:
            raise ValueError("original source count or target-side taxon matching drifted")
        raw_types=Counter(r["interaction_type"] for r in rows)
        exact_types=Counter(r["interaction_type"] for r in exact)
        wrong_targets=Counter(r["target_taxon_name"] for r in rejected)
        if taxon=="Solanum rostratum" and wrong_targets!={"Solanum angustifolium":96}:
            raise ValueError("Solanum author-homonym mismatch pattern changed")
        for key,value in FROZEN[taxon][2].items():
            if exact_types[key]!=value:
                raise ValueError(f"original {taxon} relation-class count changed for {key}")
        results.append({
            "taxon":taxon,
            "source_query_url":t["source_query_url"],
            "text_snapshot_git_blob_sha1":t["git_blob_sha1"],
            "text_snapshot_sha256":hashlib.sha256(raw).hexdigest(),
            "total_source_snapshot_relations":len(rows),
            "strict_exact_target_species_relations":len(exact),
            "target_side_taxonomy_mismatched_relations":len(rejected),
            "source_taxon_name_on_target_side_only":True,
            "strict_exact_taxon_relation_class_counts":dict(sorted(exact_types.items())),
            "all_raw_source_relation_class_counts":dict(sorted(raw_types.items())),
            "target_side_mismatch_names_with_counts":dict(sorted(wrong_targets.items())),
            "source_taxonomic_rank_species_only_verified":False,
            "source_relation_is_independently_verified_plant_fitness":False,
            "animal_agent_identified_by_original_voucher_or_experiment":False,
            "no_known_relation_is_proof_of_absence":False,
            "focal_identification_status":(
                "NO_AUTO_RESOLUTION_AMBIGUOUS_HOMONYM" if taxon=="Solanum rostratum"
                else "STRICT_TARGET_NAME_MATCH_ONLY_NOT_AUTHOR_VERIFIED"
            ),
            "could_infer_SCH_opposing_selection":False,
        })
    if sum(r["total_source_snapshot_relations"] for r in results)!=254:
        raise ValueError("four-source public GloBI opportunity snapshot coverage drifted")
    return {
        "schema_version":READOUT_SCHEMA,
        "status":"ARCHIVED_PUBLIC_GLOBI_INTERACTION_OPPORTUNITY_NOT_FITNESS_CONFLICT",
        "snapshot_date":"2026-10-19",
        "source_api":"https://api.globalbioticinteractions.org/interaction.csv",
        "study_frame":"four previously outcome-selected botanical cases, NOT sampled species first",
        "n_source_selected_plant_queries":4,
        "total_original_snapshot_relation_rows":sum(x["total_source_snapshot_relations"] for x in results),
        "total_strict_exact_target_taxon_rows":sum(x["strict_exact_target_species_relations"] for x in results),
        "total_mismatched_target_taxon_rows":sum(x["target_side_taxonomy_mismatched_relations"] for x in results),
        "Solanum_rostratum_Dunal_verified_interaction_records":None,
        "why_not_zero":"GloBI returned only Solanum angustifolium under ambiguous rostratum homonym; cannot infer biological absence",
        "source_relations_by_focal_plant":results,
        "source_query_service_live_unversioned":True,
        "archived_text_snapshots_reproducible":True,
        "snapshot_not_unbiased_flora_population":True,
        "interaction_opportunity_is_not_direct_conflict_or_fitness":True,
        "cross_source_observations_not_independent_biological_replication":True,
        "strict_structural_BALANCE_occupancy_identified":False,
        "added_independent_biological_clusters":0,
        "claim_ceiling":"public recorded biotic relation opportunity and severe taxonomy/coverage bias only; no pair-specific opposing fitness gradients",
    }


def summarize_globi_files(root:Path,contract_path:Path)->dict:
    d=contract_path.read_bytes()
    spec=json.loads(d)
    files={t["snapshot_path"]:(root/t["snapshot_path"]).read_bytes()
           for t in _contract(spec)}
    out=summarize_globi_opportunity_snapshot(spec,files)
    out["source_contract_sha256"]=hashlib.sha256(d).hexdigest()
    return out

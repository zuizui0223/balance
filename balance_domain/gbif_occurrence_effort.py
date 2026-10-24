"""Independent GBIF occurrence RECORD COVERAGE vs GloBI documentation.

The plant names and GBIF taxon keys were selected in a species-first panel
before checking any GloBI source. This audit adds actual GBIF occurrence/search
counts, *not* the misleading numOccurrences field in species/search.
Counts come from text snapshots retrieved five days after the GloBI snapshot.

Neither indexed GBIF occurrences nor the presence of GloBI interaction rows
is an experimentally measured reproductive functional trade-off. The 12
plant-family strata are selected convenience strata, not a representative
flora, and the comparison is descriptive, not causal or phylogenetically
adjusted. A GBIF taxonomy key search may include subspecific taxon records.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
from statistics import median

SCHEMA = "BALANCE_GBIF_OCCURRENCE_EFFORT_48_SOURCE_MANIFEST_V1"
BATCH_SCHEMA = "BALANCE_GBIF_OCCURRENCE_EFFORT_SOURCE_BATCH_V1"
READOUT = "BALANCE_GBIF_OCCURRENCE_EFFORT_GLOBI_COVERAGE_V1"
EXPECTED_DATE = "2026-10-24"
GLOBI_DATE = "2026-10-19"
EXPECTED_N = 48
SOURCE_BATCH_COUNT = 12


def git_blob_sha1(raw: bytes) -> str:
    if type(raw) is not bytes:
        raise ValueError("archived public source file bytes required")
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def _natural_int(value, label):
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be an unaltered nonnegative source integer")
    return value


def _gbif_occurrence_response(raw_text: str, url: str, expected_count: int) -> int:
    if not isinstance(raw_text,str) or not raw_text:
        raise ValueError("original GBIF occurrence response text missing")
    try:
        source=json.loads(raw_text)
    except (ValueError, TypeError) as exc:
        raise ValueError("GBIF original occurrence response not valid JSON") from exc
    if (not isinstance(source,dict) or
        source.get("limit")!=0 or source.get("offset")!=0 or
        type(source.get("endOfRecords")) is not bool or
        source.get("results")!=[] or source.get("facets")!=[] or
        type(source.get("count")) is not int or
        source["count"]!=expected_count):
        raise ValueError(f"original occurrence/search count or query contract drifted: {url}")
    return source["count"]


def _freeze_contract(freeze: dict) -> dict:
    if (not isinstance(freeze,dict) or freeze.get("schema_version")!=SCHEMA
        or freeze.get("status")!=
        "REAL_GBIF_OCCURRENCE_SEARCH_COUNTS_POST_OPEN_DESCRIPTIVE_NOT_CONFLICT"):
        raise ValueError("source effort manifest schema or evidence status differs")
    if freeze.get("gbif_snapshot_date")!=EXPECTED_DATE or (
        freeze.get("globi_snapshot_date")!=GLOBI_DATE
    ):
        raise ValueError("GBIF and GloBI source snapshots are different dated retrievals")
    for k in (
        "original_species_sampling_selected_before_interactions",
        "source_frame_species_first",
        "family_strata_are_convenience_selected",
        "public_web_text_extraction_not_original_HTTP_bytes",
        "live_GBIF_occurrence_index_not_pinned_release",
        "GBIF_occurrence_counts_include_matched_descendant_taxa",
        "original_GBIF_species_search_numOccurrences_is_not_occurrence_search_count",
        "record_effort_proxy_not_direct_plant_interaction_evidence",
        "original_denominator_never_reselected_after_GloBI",
    ):
        if freeze.get(k) is not True:
            raise ValueError(f"source survey limitation or design missing: {k}")
    if freeze.get("source_api")!="https://api.gbif.org/v1/occurrence/search":
        raise ValueError("official GBIF occurrence/source endpoint changed")
    for path,blob in (
        ("original_GBIF_selected_manifest_path",
         "original_GBIF_selected_manifest_git_blob_sha1"),
        ("original_GloBI_static_coverage_path",
         "original_GloBI_static_coverage_git_blob_sha1"),
    ):
        if not (isinstance(freeze.get(path),str)
                and isinstance(freeze.get(blob),str)
                and len(freeze[blob])==40):
            raise ValueError("registered source manifest and blob hash missing")
    b=freeze.get("source_batch_paths")
    if not isinstance(b,list) or len(b)!=SOURCE_BATCH_COUNT:
        raise ValueError("exact twelve archived original source batches required")
    for i,item in enumerate(b,1):
        name=f"data/external/gbif/{EXPECTED_DATE}/occurrence_effort_batch_{i:02d}.json"
        if (not isinstance(item,dict) or item.get("path")!=name or
            not isinstance(item.get("git_blob_sha1"),str) or
            len(item["git_blob_sha1"])!=40 or
            item.get("expected_records")!=4):
            raise ValueError("GBIF original source batch path/shape drifted")
    limits=freeze.get("sampling_and_ecological_claim_limits")
    if not isinstance(limits,dict) or set(limits)!={
        "no_same_coordinate_competing_fitness_gradients_measured",
        "index_occurrence_count_not_true_sampling_effort_denominator",
        "cross_date_comparison_not_simultaneously_indexed",
        "unrecorded_GloBI_interaction_not_biological_absence",
        "ecological_association_not_causal_evidence_effort",
        "no_phylogenetic_or_guild_prevalence_inferred",
        "strict_structural_BALANCE_occupancy_identified",
        "additional_independent_biological_clusters",
    }:
        raise ValueError("source claim ceiling missing")
    for k,v in limits.items():
        if k=="additional_independent_biological_clusters":
            if type(v) is not int or v!=0:
                raise ValueError("occurrence data cannot add biological experiment clusters")
        elif k=="strict_structural_BALANCE_occupancy_identified":
            if v is not False:
                raise ValueError("indexed records do not measure structural BALANCE")
        elif v is not True:
            raise ValueError("source taxonomy and inference limits must remain explicit")
    return freeze


def audit_effort_and_GloBI(
    contract: dict, selected: dict, coverage: dict,
    original_batch_bytes: dict[str, bytes],
) -> dict:
    """Exact 48 source-linked taxa, no GloBI absence -> ecological absence."""
    _freeze_contract(contract)
    chosen=selected.get("species")
    data=coverage.get("species")
    if not isinstance(chosen,list) or len(chosen)!=48:
        raise ValueError("original GBIF outcome-independent denominator changed")
    if not isinstance(data,list) or len(data)!=48 or (
        coverage.get("totals",{}).get("n_species")!=48 or
        coverage["totals"].get("n_exact_name_species")!=16):
        raise ValueError("original GloBI name-qualified denominator changed")
    if selected.get("schema_version")!="BALANCE_GBIF_SPECIES_FIRST_SELECTED_V1" or (
        coverage.get("schema_version")!=
        "BALANCE_GBIF_GLOBI_SPECIES_FIRST_STATIC_COVERAGE_V1"
    ):
        raise ValueError("original 48-species source scope not matched")
    cov={s["gbif_species_key"]:s for s in data}
    if len(cov)!=48 or (
        {s["gbif_species_key"] for s in chosen}!=set(cov)
    ):
        raise ValueError("GBIF/GloBI species IDs changed")
    if any(s.get("GBIF_numOccurrences_field")!=0 for s in chosen):
        raise ValueError("original taxonomy search fields no longer match source")

    files=contract["source_batch_paths"]
    if set(original_batch_bytes)!={f["path"] for f in files}:
        raise ValueError("all twelve exact original GBIF source batches required")
    recorded=[]
    for i,item in enumerate(files):
        raw=original_batch_bytes[item["path"]]
        if git_blob_sha1(raw)!=item["git_blob_sha1"]:
            raise ValueError("original GBIF occurrence source text changed")
        try:
            document=json.loads(raw)
        except (ValueError,UnicodeError) as exc:
            raise ValueError("original source count batch not valid JSON") from exc
        if (document.get("schema_version")!=BATCH_SCHEMA or
            document.get("batch_index")!=i+1 or
            document.get("retrieval_date")!=EXPECTED_DATE or
            document.get("source_kind")!=
            "OFFICIAL_GBIF_OCCURRENCE_SEARCH_COUNTS_TEXT_EXTRACTED_NOT_HTTP_BYTES" or
            document.get("n_selected_taxa")!=4 or
            document.get("original_species_selection_untouched") is not True
        ):
            raise ValueError("GBIF occurrence batch format changed")
        src=document.get("records")
        if not isinstance(src,list) or len(src)!=4:
            raise ValueError("GBIF occurrence batch source records missing")
        for j,r in enumerate(src):
            pos=i*4+j
            original=chosen[pos]
            key=original["gbif_species_key"]
            if not (r.get("gbif_species_key")==key and
                    r.get("gbif_species_name")==original["canonical_name"]
                    and r.get("gbif_family")==original["family"]):
                raise ValueError("source occurrence taxon not in frozen species-first position")
            count_rows=[]
            for field,suffix in (
                ("total", "&limit=0"),
                ("with_coordinates", "&hasCoordinate=true&limit=0"),
            ):
                q=r[field]
                base="https://api.gbif.org/v1/occurrence/search?taxonKey="+str(key)
                url=base+suffix
                if not isinstance(q,dict) or q.get("requested_url")!=url:
                    raise ValueError("original GBIF taxonKey, coordinate flag or source endpoint changed")
                source_count=_natural_int(q.get("count"),field)
                verified=_gbif_occurrence_response(
                    q.get("original_source_text"),url,source_count
                )
                count_rows.append(verified)
            total,geo=count_rows
            if geo>total:
                raise ValueError("georeferenced GBIF occurrence count cannot exceed total")
            from_globi=cov[key]
            if from_globi["species"]!=original["canonical_name"] or (
                from_globi["family"]!=original["family"]
            ):
                raise ValueError("sampled GBIF occurrence and GloBI taxonomy mismatch")
            records=_natural_int(from_globi.get("exact_GloBI_target_name_rows"),
                                 "original GloBI name-matched row count")
            recorded.append({
                "gbif_species_key":key,
                "species":original["canonical_name"],
                "family":original["family"],
                "order":original["order"],
                "gbif_occurrence_search_count":total,
                "gbif_occurrence_search_has_coordinates_count":geo,
                "globi_exact_target_name_relation_rows":records,
                "globi_name_recorded":records>0,
                "GBIF_species_search_numOccurrences_field":0,
                "GBIF_occurrence_count_is_effort_proxy_not_true_abundance":True,
                "no_GloBI_records_not_interaction_absence":True,
            })
    if len(recorded)!=EXPECTED_N or len({
        x["gbif_species_key"] for x in recorded
    })!=EXPECTED_N:
        raise ValueError("GBIF occurrence effort study denominator duplicated")

    with_glo=[x for x in recorded if x["globi_name_recorded"]]
    without=[x for x in recorded if not x["globi_name_recorded"]]
    family=defaultdict(list)
    for r in recorded:
        family[r["family"]].append(r)
    if len(family)!=12 or any(len(v)!=4 for v in family.values()):
        raise ValueError("original cross-order family strata did not remain intact")
    family_profiles=[]
    matched_family=0
    higher_family_median=0
    highest_two=0
    lowest_two=0
    for name,rr in sorted(family.items()):
        rank=sorted(rr,key=lambda x:(
            -x["gbif_occurrence_search_count"], x["gbif_species_key"]
        ))
        top=sum(x["globi_name_recorded"] for x in rank[:2])
        low=sum(x["globi_name_recorded"] for x in rank[2:])
        highest_two+=top
        lowest_two+=low
        pos=[x["gbif_occurrence_search_count"] for x in rr
             if x["globi_name_recorded"]]
        neg=[x["gbif_occurrence_search_count"] for x in rr
             if not x["globi_name_recorded"]]
        compar=bool(pos and neg)
        if compar:
            matched_family+=1
        higher=bool(compar and median(pos)>median(neg))
        higher_family_median+=higher
        family_profiles.append({
            "family":name,
            "n_species":4,
            "n_GloBI_name_documented":len(pos),
            "n_with_gbif_occurrences":sum(
                x["gbif_occurrence_search_count"]>0 for x in rr
            ),
            "GBIF_occurrence_count_total":sum(
                x["gbif_occurrence_search_count"] for x in rr
            ),
            "within_family_GloBI_documented_median_occurrence":(
                median(pos) if pos else None
            ),
            "within_family_GloBI_undocumented_median_occurrence":(
                median(neg) if neg else None
            ),
            "documented_greater_than_undocumented_median":(
                higher if compar else None
            ),
            "top_two_occurrence_species_with_GloBI":top,
            "bottom_two_occurrence_species_with_GloBI":low,
        })

    aggregated={
        "n_species":len(recorded),
        "n_families":len(family),
        "n_with_any_GBIF_occurrence":sum(x["gbif_occurrence_search_count"]>0
                                         for x in recorded),
        "total_GBIF_indexed_occurrences":sum(x["gbif_occurrence_search_count"]
                                             for x in recorded),
        "total_GBIF_occurrences_with_coordinates":sum(
            x["gbif_occurrence_search_has_coordinates_count"] for x in recorded
        ),
        "n_with_GloBI_exact_target_name":len(with_glo),
        "n_without_GloBI_exact_target_name":len(without),
        "n_without_GloBI_but_with_GBIF_records":sum(
            x["gbif_occurrence_search_count"]>0 for x in without
        ),
        "median_GBIF_occurrences_GloBI_documented":median(
            x["gbif_occurrence_search_count"] for x in with_glo
        ),
        "median_GBIF_occurrences_GloBI_undocumented":median(
            x["gbif_occurrence_search_count"] for x in without
        ),
        "n_families_with_both_GloBI_documented_and_not":matched_family,
        "n_families_with_higher_documented_median_GBIF_occurrences":higher_family_median,
        "n_GloBI_documented_among_family_top_two_GBIF_counts":highest_two,
        "n_GloBI_documented_among_family_bottom_two_GBIF_counts":lowest_two,
    }
    if aggregated != contract.get("observed_aggregate_verification"):
        raise ValueError("actual GBIF indexed records no longer match source-frozen descriptive facts")

    return {
        "schema_version":READOUT,
        "status":"ACTUAL_OCCURRENCE_DOCUMENTATION_EFFORT_ASSOCIATION_NOT_FITNESS",
        "source_GBIF_date":EXPECTED_DATE,
        "source_GloBI_date":GLOBI_DATE,
        "n_species_first_selected":48,
        "source_source_aggregate":aggregated,
        "species":recorded,
        "family_strata":family_profiles,
        "family_median_comparison_is_not_causal_or_exchangeable":True,
        "GBIF_count_includes_indexed_occurrences_not_unique_effort_or_abundance":True,
        "cross_date_and_taxonomic_index_limitations":True,
        "source_taxa_not_globally_representative":True,
        "GloBI_absence_is_not_ecological_interaction_absence":True,
        "pollinator_antagonist_conflict_not_identified":True,
        "fitness_impact_or_SCH_L_identified":False,
        "net_structural_BALANCE_occupancy_identified":False,
        "additional_independent_biological_clusters":0,
        "ecological_interpretation":(
            "GloBI database relation documentation correlates strongly with "
            "GBIF indexed occurrence counts among preselected taxonomic names, "
            "including within some preselected families, but this is "
            "observational *reporting coverage*, not a pollinator selection "
            "or ecological conflict gradient."
        ),
    }


def source_effort_audit_from_files(root: Path,manifest_path:Path)->dict:
    raw=manifest_path.read_bytes()
    m=json.loads(raw)
    _freeze_contract(m)
    chosen_path=root/m["original_GBIF_selected_manifest_path"]
    globi_path=root/m["original_GloBI_static_coverage_path"]
    chosen_bytes=chosen_path.read_bytes()
    globi_bytes=globi_path.read_bytes()
    if git_blob_sha1(chosen_bytes)!=m["original_GBIF_selected_manifest_git_blob_sha1"]:
        raise ValueError("original frozen GBIF taxon sampling contract changed")
    if git_blob_sha1(globi_bytes)!=m["original_GloBI_static_coverage_git_blob_sha1"]:
        raise ValueError("original 2026-10-19 GloBI documentation summary changed")
    sources={x["path"]:(root/x["path"]).read_bytes()
             for x in m["source_batch_paths"]}
    result=audit_effort_and_GloBI(
        m,json.loads(chosen_bytes),json.loads(globi_bytes),sources
    )
    result["effort_source_manifest_sha256"]=hashlib.sha256(raw).hexdigest()
    result["source_batch_sha256"]={
        p:hashlib.sha256(b).hexdigest() for p,b in sorted(sources.items())
    }
    return result

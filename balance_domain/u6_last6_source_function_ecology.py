"""Final six original U6 source-ecology observations, STRICTLY NON-CODER.

This extends the first-six and next-six original-study ecology extraction
lanes. It never opens, completes, or imputes the 42 independent architecture
A/B rows or frozen V4 outcomes. Admission is based only on the original
frozen source timing labels, NOT architecture or source result attractiveness.

The separate unmerged first-six clock exploration is not read as though it
were canonical main-branch source data. Its 3 extra taxa appear in a
specifically labelled cross-branch bookkeeping count only.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from .u6_next6_source_function_ecology import (
    ROOT, FREEZE, PACKET, PREDICTORS, PILOT, NEXT6,
    DEPENDENCE, CODER, analyze as prior_audit,
)

LAST6="data/BALANCE_U6_LAST6_SOURCE_FUNCTION_ECOLOGY_V1.csv"
IMPORTED_CLOCK="data/BALANCE_U6_IMPORTED_FIRST6_CLOCK_ONLY_THREE_V1.json"
CLOCK_SOURCE_SHA="d0e3bca8906fa46214b20973ac0d72a0cbe8dddf"
LANE="LAST_SIX_LEXICOGRAPHIC_SIMULTANEOUS_AFTER_PRIOR_SOURCE_LANES"
FROZEN_EXPECTED={
    "Nothofagus_pumilio","Passiflora_foetida","Prockia_crucis",
    "Pseudobombax_ellipticum","Theobroma_cacao","Zea_mays",
}
SOURCE_LOCI={
    "DESTRUCTIVE_WIND_POLLINATED_FLOWER_HARVEST",
    "SOURCE_ANTHER_POLLEN_AND_STIGMA_CONTACT_DIFFER",
    "SOURCE_ANTHER_POLLEN_SOLE_FLORAL_REWARD",
    "NIGHT_DAY_VISITOR_RESOURCE_USE",
    "SOURCE_ANTHER_POLLEN_TAKEN_WITHOUT_STIGMA_CONTACT",
    "WIND_DISPERSED_POLLEN_AS_DIET_OF_PREDATORY_BEETLES",
}
EVIDENCE_CEILINGS={
    "Nothofagus_pumilio","Prockia_crucis",
    "Pseudobombax_ellipticum","Zea_mays",
}


def _read(path: Path) -> tuple[list[dict[str,str]],str]:
    raw=path.read_bytes()
    with path.open(encoding="utf-8-sig",newline="") as stream:
        rdr=csv.DictReader(stream)
        keys=rdr.fieldnames or []
        if len(keys)!=len(set(keys)):
            raise ValueError("Original source column names not unique")
        rows=list(rdr)
    if not rows or any(None in x for x in rows):
        raise ValueError("Incomplete or malformed original-source table")
    return rows,hashlib.sha256(raw).hexdigest()


def analyze(base: Path=ROOT) -> dict[str,Any]:
    prior=prior_audit(base)
    if prior["additional_six_source_extracted"]!=6 or prior["distinct_main_branch_source_observation_groups"]!=12:
        raise ValueError("Prior source-only six+six coverage no longer valid")
    original=json.loads((base/FREEZE).read_text(encoding="utf-8"))
    names=original["included_dependency_groups"]
    if len(names)!=21 or len(set(names))!=21:
        raise ValueError("Frozen original denominator changed")
    all_taxa=set(names)

    recs,receipt_hash=_read(base/PREDICTORS)
    if len(recs)!=63:
        raise ValueError("Original original source predictor count changed")
    times={}
    for item in recs:
        if (item["predictor"]=="conflict_timing_geometry" and
            item["adjudication_status"]=="SCREENED" and
            item["outcome_independence"]=="TRUE"):
            if item["cluster_id"] in times:
                raise ValueError("Duplicate source timing")
            times[item["cluster_id"]]=item["reported_value"]
    if len(times)!=21:
        raise ValueError("Unadjudicated source times changed")
    concurrent=sorted(k for k,t in times.items() if t=="SIMULTANEOUS")
    sequential=sorted(k for k,t in times.items() if t=="SEQUENTIAL_WITHIN_UNIT")
    if len(concurrent)!=18 or len(sequential)!=3:
        raise ValueError("Original source timing denominator or statuses changed")
    last_names=set(concurrent[12:])
    if last_names!=FROZEN_EXPECTED:
        raise ValueError("Last-six original-source selection has shifted")

    admitted,packet_hash=_read(base/PACKET)
    admission={row["dependency_group"]:row for row in admitted}
    if set(admission)!=all_taxa:
        raise ValueError("Original source packet membership changed")
    sources,source_hash=_read(base/LAST6)
    by={}
    for row in sources:
        taxon=row["dependency_group"]
        if taxon in by or taxon not in last_names:
            raise ValueError("Last-six source selection not fixed/blinded")
        if row["selection_lane"]!=LANE:
            raise ValueError("Source result selected under incorrect protocol")
        if row["admission_reference_id"]!=admission[taxon]["source_reference_ids"]:
            raise ValueError("Original admission reference reattributed")
        if row["functional_location"] not in SOURCE_LOCI:
            raise ValueError("Source loss location unrecognized")
        if not all(row.get(key,"") for key in (
            "source_primary_url","source_secondary_url","source_access_class",
            "ecological_mechanism","source_observation_ecology",
            "source_reported_effect","missing_for_formal_architecture_coding",
            "source_adjudication_status",
        )):
            raise ValueError("Source evidence or missingness explanation absent")
        if not (row["source_primary_url"].startswith("https://") and
                row["source_secondary_url"].startswith("https://")):
            raise ValueError("Original-source URLs must be HTTPS source locators")
        if row["formal_u6_architecture_assigned"]!="NOT_ASSIGNED_BY_EXTRACTOR":
            raise ValueError("Original-source extractor may not fill CODER_A/B architecture")
        if row["independent_coder_authorship"]!="NO_AI_EXTRACTOR_NOT_CODER_A_OR_B":
            raise ValueError("Independent architecture coder authorship cannot be claimed")
        by[taxon]=row
    if len(by)!=6 or set(by)!=last_names:
        raise ValueError("Exactly final six preselected original-source groups required")
    if {key for key,row in by.items() if
            row["source_adjudication_status"].startswith("EVIDENCE_CEILING")}!=EVIDENCE_CEILINGS:
        raise ValueError("Primary-source evidence ceilings changed")
    zea=by["Zea_mays"]
    if (zea["functional_location"]!="WIND_DISPERSED_POLLEN_AS_DIET_OF_PREDATORY_BEETLES"
            or "ADMISSION_ELIGIBILITY_REVIEW_REQUIRED" not in zea["source_adjudication_status"]):
        raise ValueError("Zea predatory beetle pollen-diet/admission distinction not preserved")
    if by["Nothofagus_pumilio"]["functional_location"]!="DESTRUCTIVE_WIND_POLLINATED_FLOWER_HARVEST":
        raise ValueError("Parakeet destructive flower consumption misclassified")
    if by["Passiflora_foetida"]["ecological_mechanism"]!="POLLEN_COLLECTOR_WITHOUT_STIGMA_CONTACT_VERSUS_EFFECTIVE_NECTAR_VISITOR":
        raise ValueError("Pollen and nectar robber behavioural routes confounded")
    if by["Theobroma_cacao"]["admission_reference_id"]!="U6_REF_153;U6_REF_155":
        raise ValueError("One cacao taxon has two references; not two independent replicates")

    old_names=set(prior["new_selected_source_groups"])
    original_source_pilot,prior_hash=_read(base/PILOT)
    old_pilot={r["dependency_group"] for r in original_source_pilot}
    if len(original_source_pilot)!=6 or len(old_pilot)!=6:
        raise ValueError("Original pilot altered")
    main_taxa=last_names|old_names|old_pilot
    if len(main_taxa)!=18:
        raise ValueError("Last six overlap earlier main source ecology studies")
    cross_branch=last_names|old_names|set(sequential)|set(concurrent[:6])
    if len(cross_branch)!=21:
        raise ValueError("Cross-branch provisional source coverage does not reach 21")
    # Branch-dependent 3 other source taxa are kept as an UNMERGED
    # literature-extraction bookkeeping item, not as present-row records.
    source_research_lacking_on_stacked_branch=sorted(all_taxa-main_taxa)
    if source_research_lacking_on_stacked_branch!=concurrent[3:6]:
        raise ValueError("Unmerged original first-six clock branch identity changed")

    # Reuse (without re-adjudicating) the three prior FIRST-SIX source notes
    # already authored on another still-unmerged branch. Their source blob
    # identity remains immutable; this transfer is a source-extractor copy,
    # *not* a first or second blinded architectural code.
    clock_blob=(base/IMPORTED_CLOCK).read_bytes()
    imported=json.loads(clock_blob.decode("utf-8"))
    expected_clock=set(source_research_lacking_on_stacked_branch)
    entries=imported.get("original_evidence_notes")
    if (imported.get("schema")!="BALANCE_U6_IMPORTED_ORIGINAL_FIRST6_CLOCK_THREE_V1"
            or imported.get("status")!="SOURCE_NOTES_COPIED_FROM_UNMERGED_OLDER_DRAFT_NOT_BLINDED_ARCHITECTURE"
            or imported.get("original_blob_sha")!=CLOCK_SOURCE_SHA
            or imported.get("source_rows_copied")!=3
            or imported.get("formal_u6_architecture_assigned") is not False
            or imported.get("independent_coder_A_or_B") is not False
            or imported.get("V4_architecture_results_opened") is not False
            or not isinstance(entries,list) or len(entries)!=3
            or {x["dependency_group"] for x in entries}!=expected_clock):
        raise ValueError("Original three clock-source notes cannot be misread as independent V4 coding")
    for entry in entries:
        if (not entry.get("source_records")
                or not entry.get("observed_components")
                or not entry.get("clock_axes")
                or not entry.get("unresolved")):
            raise ValueError("Transferred original source context is incomplete")
        if any(
            not row.get("url","").startswith("https://")
            or not row.get("observation")
            for row in entry["source_records"]
        ):
            raise ValueError("Transferred source locator or biological notes unavailable")
    combined_names=main_taxa|expected_clock
    if combined_names!=all_taxa or len(combined_names)!=21:
        raise ValueError("Source-only co-located ecology denominator not 21")

    dep,dep_hash=_read(base/DEPENDENCE)
    depmap={r["u6_dependency_group"]:r for r in dep}
    if len(depmap)!=21:
        raise ValueError("Taxonomic dependency ledger changed")
    coder,coder_hash=_read(base/CODER)
    if len(coder)!=42 or {r["dependency_group"] for r in coder}!=all_taxa:
        raise ValueError("Frozen double coder template membership changed")
    if any(r["coding_status"]!="UNSTARTED" or
           r["architecture_mode"]!="UNRESOLVED" or
           r["module_substrate"]!="UNRESOLVED" or
           r["conflict_timing_geometry"]!="UNRESOLVED" or
           r["conflict_spatial_geometry"]!="UNRESOLVED" for r in coder):
        raise ValueError("Independent architecture/predictor coder results are NOT opened")
    for name in ("Impatiens_capensis","Melastoma_affine"):
        if depmap[name]["analysis_action"] not in {"SHARED_SPECIES_BLOCK","SHARED_TAXON_CONCEPT_BLOCK"}:
            raise ValueError("Cross-review accepted taxon overlap was discarded")
    return {
        "schema":"BALANCE_U6_FINAL6_ORIGINAL_SOURCE_FUNCTION_ECOLOGY_V1",
        "status":"ALL_21_PROVISIONAL_ACROSS_BRANCHES_NO_INDEPENDENT_CODING",
        "frozen_taxon_groups":21,
        "original_source_timing":{"simultaneous":len(concurrent),"sequential":len(sequential)},
        "final_six_original_source_selected":sorted(last_names),
        "added_new_original_source_notes":len(by),
        "main_plus_stacked_ecology_taxa":len(main_taxa),
        "main_plus_stacked_groups_not_in_this_branch":source_research_lacking_on_stacked_branch,
        "cross_branch_provisional_distinct_source_taxa":len(cross_branch),
        "cross_branch_provisional_not_canonical":True,
        "co_located_source_ecology_taxa":len(combined_names),
        "imported_old_source_only_clock_taxa":sorted(expected_clock),
        "imported_old_source_blob_sha":CLOCK_SOURCE_SHA,
        "imported_old_clock_is_nonadjudicating":True,
        "combined_source_evidence_biological_replicates_not_counted":True,
        "public_original_or_primary_abstract_evidence_ceiling_taxa":sorted(EVIDENCE_CEILINGS),
        "original_studies_collapsed_by_taxon":True,
        "zeamays_pollen_predator_food_without_plant_fitness_source_review_required":True,
        "known_pollen_stage_types":dict(sorted(Counter(r["functional_location"] for r in sources).items())),
        "source_sha256":{LAST6:source_hash,IMPORTED_CLOCK:hashlib.sha256(clock_blob).hexdigest(),
                         FREEZE:hashlib.sha256((base/FREEZE).read_bytes()).hexdigest(),
                         PREDICTORS:receipt_hash,PACKET:packet_hash,PILOT:prior_hash,
                         DEPENDENCE:dep_hash,CODER:coder_hash},
        "original_independent_coder_slots":len(coder),
        "independently_completed_architecture_slots":0,
        "original_V4_confirmatory_architecture_opened":False,
        "original_source_inclusion_modified":False,
        "same_coordinate_causal_tradeoff_loss_measured":False,
        "genetically_evolved_new_module_origins_demonstrated":False,
        "new_observation_records":sorted(sources,key=lambda x:x["dependency_group"]),
    }

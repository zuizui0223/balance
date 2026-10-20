"""Pre-outcome, source-only BALANCE U6 support and accepted-taxon audit.

All 21 U6 admission groups were defined by evidence of pollen theft BEFORE
architecture outcome coding (Hargreaves et al. 2009 review). This module
does not import, parse, or inspect U6 architecture codes other than checking
that the frozen double-coder worksheets are entirely UNSTARTED/UNRESOLVED.
It never opens BALANCE V4 outcome data or changes the Pass-1 freeze.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
FREEZE="data/BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"
SOURCE="data/BALANCE_PLANT_U6_PASS2_SOURCE_RECOVERY_FRAME_V1.csv"
PREDICTORS="data/BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
DEPENDENCE="data/BALANCE_PLANT_U6_CROSS_UNIVERSE_DEPENDENCE_V1.csv"
TAXON="data/BALANCE_U6_PREOUTCOME_TAXON_OVERLAP_SOURCE_V1.csv"
CODERS="data/BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv"

REGISTERED_PREDICTORS=(
    "module_substrate","conflict_timing_geometry","conflict_spatial_geometry"
)
OUTCOME_FIELDS=("architecture_mode",)
EXPECTED_SEQ={"Clusia_arrudae","Crescentia_alata","Tolmiea_menziesii"}
REQUIRED_ALIASES={"Impatiens_capensis","Melastoma_affine"}


def _read(base: Path, rel: str) -> tuple[list[dict[str,str]],str]:
    raw=(base/rel).read_bytes()
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if not rows or len(rows[0])!=len(set(rows[0])):
        raise ValueError("Invalid source table schema: "+rel)
    if any(None in row for row in rows):
        raise ValueError("Malformed source table: "+rel)
    return rows,hashlib.sha256(raw).hexdigest()


def _counts(rows: list[dict[str,str]],field: str) -> dict[str,int]:
    return dict(sorted(Counter(x[field] for x in rows).items()))


def analyze(base: Path=ROOT) -> dict[str, Any]:
    blob=(base/FREEZE).read_bytes()
    freeze=json.loads(blob.decode("utf-8"))
    if (freeze.get("schema_version")!="BALANCE_PLANT_U6_PASS1_FREEZE_V1"
            or freeze.get("status")!="PASS1_CLOSED_PASS2_CODING_OPEN"
            or freeze.get("pass1_contract",{}).get("architecture_used_for_admission") is not False):
        raise ValueError("U6 architecture-blind Pass-1 freeze changed")
    universe=freeze.get("included_dependency_groups")
    if len(universe)!=21 or len(set(universe))!=21:
        raise ValueError("Frozen U6 21-group admission changed")
    groups=set(universe)

    source,source_hash=_read(base,SOURCE)
    if (len(source)!=21 or {r["dependency_group"] for r in source}!=groups
            or any(r["packet_status"]!="FROZEN" for r in source)):
        raise ValueError("Frozen U6 generic source recovery frame changed")
    valid_recovery={"RESOLVED","EVIDENCE_CEILING"}
    if any(r["source_recovery_status"] not in valid_recovery for r in source):
        raise ValueError("Unexpected U6 source recovery adjudication status")

    predictors,predict_hash=_read(base,PREDICTORS)
    by_group:dict[str,dict[str,str]]=defaultdict(dict)
    if len(predictors)!=63:
        raise ValueError("Expected 63 source-screened predictor receipts")
    for r in predictors:
        group=r.get("cluster_id","")
        pred=r.get("predictor","")
        if (group not in groups or pred not in REGISTERED_PREDICTORS
                or pred in by_group[group]
                or r.get("outcome_independence")!="TRUE"
                or r.get("adjudication_status")!="SCREENED"):
            raise ValueError("U6 63 predictor receipts are not independently screened and unique")
        by_group[group][pred]=r["reported_value"]
    if set(by_group)!=groups or any(
        set(x)!=set(REGISTERED_PREDICTORS) for x in by_group.values()
    ):
        raise ValueError("Each admitted U6 group requires exactly three predictor receipts")
    by_pred={
        p:dict(sorted(Counter(v[p] for v in by_group.values()).items()))
        for p in REGISTERED_PREDICTORS
    }
    if (by_pred["module_substrate"]!={"SINGLE_OR_CONTINUOUS":21}
            or by_pred["conflict_spatial_geometry"]!={"SAME_UNIT":21}
            or by_pred["conflict_timing_geometry"]!={"SEQUENTIAL_WITHIN_UNIT":3,"SIMULTANEOUS":18}):
        raise ValueError("Frozen U6 predictor class support changed")
    sequential={g for g,v in by_group.items()
                if v["conflict_timing_geometry"]=="SEQUENTIAL_WITHIN_UNIT"}
    if sequential!=EXPECTED_SEQ:
        raise ValueError("Sequential source conflict groups changed")

    dependence,dep_hash=_read(base,DEPENDENCE)
    if len(dependence)!=21 or {x["u6_dependency_group"] for x in dependence}!=groups:
        raise ValueError("U6 taxon and cross-universe dependency map changed")
    bydep={x["u6_dependency_group"]:x for x in dependence}
    expected={
        "Impatiens_capensis":("U1","U1_024","SHARED_SPECIES_BLOCK"),
        "Melastoma_affine":("U3","U3_PAIR_MELMA_001","SHARED_TAXON_CONCEPT_BLOCK"),
    }
    for name,(frame,rec,action) in expected.items():
        d=bydep[name]
        if (d["overlap_universe"],d["overlap_record_id"],d["analysis_action"])!=(frame,rec,action):
            raise ValueError("Existing canonical U6 source taxon overlap changed")
    if any(x["analysis_action"]!="U6_ONLY" for x in dependence
           if x["u6_dependency_group"] not in expected):
        raise ValueError("Unexpected additional U6 dependence requires taxonomic review")

    taxa,taxon_hash=_read(base,TAXON)
    if len(taxa)!=2 or {r["u6_dependency_group"] for r in taxa}!=REQUIRED_ALIASES:
        raise ValueError("Taxonomic overlap source overlay must contain exactly 2 groups")
    for row in taxa:
        d=bydep[row["u6_dependency_group"]]
        if (row["overlap_universe"],row["overlap_record_id"])!=(
            d["overlap_universe"],d["overlap_record_id"]
        ):
            raise ValueError("Taxon-concept overlay cannot override canonical source map")
        if (row["biological_populations_identical"]!="NOT_TESTED"
                or not row["authority_url"].startswith("https://")):
            raise ValueError("Taxonomic overlap cannot imply confirmed population identity")
    m=next(x for x in taxa if x["u6_dependency_group"]=="Melastoma_affine")
    if (m["overlap_level"]!="POWO_ACCEPTED_SPECIES_CONCEPT"
            or m["accepted_taxon_concept"]!="Melastoma malabathricum subsp. malabathricum"
            or m["other_universe_taxon_name"]!="Melastoma malabathricum L."):
        raise ValueError("POWO accepted-name synonym overlay changed without review")

    coder,coder_hash=_read(base,CODERS)
    if len(coder)!=42 or {r["dependency_group"] for r in coder}!=groups:
        raise ValueError("U6 independent double coder frame identity changed")
    pairs=defaultdict(set)
    for row in coder:
        pairs[row["dependency_group"]].add(row["coder_id"])
        if (row["architecture_mode"]!="UNRESOLVED"
                or row["coding_status"]!="UNSTARTED"):
            raise ValueError("This pre-outcome audit must not open/relabel independent architecture results")
        for field in REGISTERED_PREDICTORS:
            if row[field]!="UNRESOLVED":
                raise ValueError("Unadjudicated coder predictors must remain blinded")
    if any(ids!={"CODER_A","CODER_B"} for ids in pairs.values()):
        raise ValueError("U6 must retain both independent coders per taxon")
    if freeze["pass1_contract"]["n_anchor_review_references"]!=157:
        raise ValueError("Frozen reference cohort changed")
    outcomes=freeze["candidate_reference_outcomes"]
    if tuple(len(outcomes[k]) for k in (
            "included_reference_ids","excluded_reference_ids",
            "retained_unresolved_reference_ids"))!=(21,3,9):
        raise ValueError("U6 frozen candidate-reference statuses changed")
    # This supports estimating only a *possible future* timing/architecture
    # contrast, conditional on completed independent outcome adjudication.
    # The source-time predictor itself also awaits independent adjudication.
    return {
        "schema":"BALANCE_U6_PREOUTCOME_SUPPORT_TAXON_DEPENDENCE_V1",
        "status":"FROZEN_SOURCE_SUPPORT_ONLY_ZERO_ARCHITECTURE_RECEIPTS",
        "source_sha256":{
            FREEZE:hashlib.sha256(blob).hexdigest(),
            SOURCE:source_hash,PREDICTORS:predict_hash,
            DEPENDENCE:dep_hash,TAXON:taxon_hash,CODERS:coder_hash,
        },
        "anchor_reference_universe":157,
        "candidate_reference_outcomes":{
            "include":21,"exclude":3,"retained_unresolved":9,
        },
        "admitted_conflict_first_dependency_groups":len(groups),
        "source_recovery_statuses":_counts(source,"source_recovery_status"),
        "source_predictor_receipts":len(predictors),
        "source_predictor_statuses":_counts(predictors,"adjudication_status"),
        "source_predicted_geometry":by_pred,
        "source_sequential_exposure_groups":sorted(sequential),
        "predictor_source_opportunity":{
            "module_substrate_observed_distinct_source_classes":len(by_pred["module_substrate"]),
            "timing_observed_distinct_source_classes":len(by_pred["conflict_timing_geometry"]),
            "spatial_observed_distinct_source_classes":len(by_pred["conflict_spatial_geometry"]),
            "within_u6_module_substrate_contrast_identifiable":False,
            "within_u6_spatial_placement_contrast_identifiable":False,
            "timing_future_contrast_possible_with_only_three_ordered_groups":True,
            "timing_architecture_effect_currently_identified":False,
            "source_timing_is_not_measured_joint_function_C":True,
            "external_staggered_pollinator_visit_is_not_developmental_pollen_dosing":True,
        },
        "frozen_taxon_dependency_actions":_counts(dependence,"analysis_action"),
        "taxon_concept_overlay":{
            "exact_species_overlap_with_U1":["Impatiens_capensis"],
            "accepted_species_concept_overlap_with_U3":["Melastoma_affine"],
            "POWO_url":m["authority_url"],
            "same_biological_population_verified":False,
            "conservative_u6_only_groups":19,
            "cannot_claim_u6_u3_zero_overlap":True,
        },
        "double_coder_architecture_receipts":{
            "frozen_coder_rows":42,
            "source_coding_status":_counts(coder,"coding_status"),
            "source_architecture_labels":_counts(coder,"architecture_mode"),
            "independently_adjudicated_architecture_groups":0,
        },
        "qualified_u6_structure_effects":0,
        "registered_primary_V4_outcomes_accessed":False,
        "frozen_pass1_file_or_taxon_map_modified":False,
        "ecological_functional_new_module_origin_established":False,
        "disallowed_promotions":[
            "U6 selected review cases as global pollen-theft or modularity prevalence",
            "Melastoma accepted species concept as two phylogenetic independent units",
            "POWO accepted-name identity as evidence of matching sample populations",
            "18/3 source timing tags as quantified concurrent conflicting function optima",
            "source-pool SINGLE as physically unmodularized flower",
            "SCREENED predictors as independently ADJUDICATED",
            "UNSTARTED coded architecture rows as biological SHARED outcomes",
            "U6 temporal coding as pollen-dosing developmental regulation",
            "post-outcome insertion of heteranthery-selected U3 cases into U6",
            "costed structural payoff, heritable origin, or causal role differentiation",
        ],
    }

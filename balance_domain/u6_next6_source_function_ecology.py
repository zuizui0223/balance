"""U6 second six source-ecology observations without confirmatory coding.

The registered Pass-1 (21 groups) and original predictor SOURCE timing codes
determine case admission before reading any architecture outcome. Three
sequential groups + first three alphabetic concurrent were in the main
six-source pilot; a separate older first-six-clock branch supplied concurrent
ranks 1-6; this lane *only* adds concurrent ranks 7-12.

All notes are study-author abstracts/published summaries. Do not use this
post-outcome investigator literature extraction as CODER_A or CODER_B, or
inject the new notes into the frozen independent blind source packets.
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
PACKET="data/BALANCE_PLANT_U6_PASS2_SOURCE_PACKET_V1.csv"
PREDICTORS="data/BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
DEPENDENCE="data/BALANCE_PLANT_U6_CROSS_UNIVERSE_DEPENDENCE_V1.csv"
CODER="data/BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv"
PILOT="data/BALANCE_U6_ORIGINAL_SOURCE_ECOLOGY_PILOT_V1.csv"
NEXT6="data/BALANCE_U6_NEXT6_SOURCE_FUNCTION_ECOLOGY_V1.csv"

ALLOWED_LOCATIONS={
    "POLLEN_AT_FLOWER_ANTHER_TO_STIGMA_TRANSPORT",
    "PRE_DEPOSITION_ANTHER_POLLEN_CONSUMED_BY_THRIPS",
    "ANTHER_POLLEN_REMOVAL_AND_SEX_PHASE_SPECIFIC_VISITOR_CONTACT",
    "PRE_DEPOSITION_ANTHER_POLLEN_CONSUMED_BY_FLOWER_MITES",
    "ANTHER_REMOVAL_VERSUS_STIGMA_DEPOSITION_BEHAVIOUR_DEPENDENT",
    "POST_DEPOSITION_STIGMA_POLLEN_REMOVAL",
}
EXPECTED_NEXT6={
    "Campomanesia_pubescens","Echium_plantagineum",
    "Grevillea_barklyana","Hamelia_patens",
    "Impatiens_capensis","Melastoma_affine",
}
EXPECTED_EVIDENCE_CEILING={"Hamelia_patens"}
EXPECTED_ALIAS={"Impatiens_capensis":"SHARED_SPECIES_BLOCK",
                "Melastoma_affine":"SHARED_TAXON_CONCEPT_BLOCK"}
LANE="AFTER_ALREADY_RECORDED_FIRST_SIX_SIMULTANEOUS_NEXT_SIX_LEXICAL"
FROZEN_FIRST6_PREVIOUS_DRAFT="exploration/u6-source-mechanism-clocks-20261021"


def _csv(base: Path, relative: str) -> tuple[list[dict[str,str]],str]:
    raw=(base/relative).read_bytes()
    with (base/relative).open(encoding="utf-8-sig",newline="") as h:
        rd=csv.DictReader(h)
        if not rd.fieldnames or len(set(rd.fieldnames))!=len(rd.fieldnames):
            raise ValueError(f"Malformed source columns {relative}")
        rows=list(rd)
    if not rows or any(None in row for row in rows):
        raise ValueError(f"Malformed or empty source rows {relative}")
    return rows,hashlib.sha256(raw).hexdigest()


def _unique(rows: list[dict[str,str]],column: str) -> dict[str,dict[str,str]]:
    result={}
    for row in rows:
        key=row.get(column,"")
        if not key or key in result:
            raise ValueError(f"Duplicate/missing source key {column}")
        result[key]=row
    return result


def analyze(base: Path=ROOT) -> dict[str,Any]:
    data=(base/FREEZE).read_bytes()
    frozen=json.loads(data.decode("utf-8"))
    if (frozen.get("schema_version")!="BALANCE_PLANT_U6_PASS1_FREEZE_V1"
            or frozen.get("status")!="PASS1_CLOSED_PASS2_CODING_OPEN"
            or frozen.get("pass1_contract",{}).get("architecture_used_for_admission") is not False):
        raise ValueError("Architecture-blind U6 Pass1 frozen cohort changed")
    groups=frozen.get("included_dependency_groups")
    if len(groups)!=21 or len(set(groups))!=21:
        raise ValueError("U6 denominator must remain 21 source-selected taxa")
    universe=set(groups)
    packet,p_sha=_csv(base,PACKET)
    pack=_unique(packet,"dependency_group")
    if set(pack)!=universe or len(packet)!=21:
        raise ValueError("Original U6 source packet identities changed")
    predictors,pred_sha=_csv(base,PREDICTORS)
    if len(predictors)!=63:
        raise ValueError("U6 source predictor receipt count changed")
    temporal={}
    for r in predictors:
        if r["cluster_id"] not in universe or r["adjudication_status"]!="SCREENED" or r["outcome_independence"]!="TRUE":
            raise ValueError("Original outcome-blind predictor status changed")
        if r["predictor"]=="conflict_timing_geometry":
            if r["cluster_id"] in temporal or r["reported_value"] not in {"SIMULTANEOUS","SEQUENTIAL_WITHIN_UNIT"}:
                raise ValueError("Bad or duplicate original source timing")
            temporal[r["cluster_id"]]=r["reported_value"]
    if len(temporal)!=21:
        raise ValueError("One timing screening receipt required per frozen group")
    sequential=sorted(g for g,v in temporal.items() if v=="SEQUENTIAL_WITHIN_UNIT")
    concurrent=sorted(g for g,v in temporal.items() if v=="SIMULTANEOUS")
    if len(sequential)!=3 or len(concurrent)!=18:
        raise ValueError("Frozen U6 timing predictor frequencies changed")

    expected=set(concurrent[6:12])
    if expected!=EXPECTED_NEXT6:
        raise ValueError("Prior concurrent first-six plus next-six lexical selection changed")
    previous_pilot,pilot_sha=_csv(base,PILOT)
    recorded=_unique(previous_pilot,"dependency_group")
    known_prior=set(sequential+concurrent[:3])
    if set(recorded)!=known_prior or len(recorded)!=6 or known_prior & expected:
        raise ValueError("Previous six-source pilot/selection changed")
    for row in recorded.values():
        if (row["formal_u6_architecture_assigned"]!="NOT_ASSIGNED_BY_EXTRACTOR"
                or row["independent_coder_authorship"]!="NO_AI_EXTRACTOR_NOT_CODER_A_OR_B"):
            raise ValueError("Original ecological source pilot has been promoted to coder")

    recent,r_sha=_csv(base,NEXT6)
    new=_unique(recent,"dependency_group")
    if set(new)!=expected or len(new)!=6:
        raise ValueError("Next-six outcome-blind source selection changed")
    dependence,dep_sha=_csv(base,DEPENDENCE)
    dep=_unique(dependence,"u6_dependency_group")
    if set(dep)!=universe:
        raise ValueError("Source dependency map changed")
    seen={}
    for name,row in new.items():
        if row["selection_rule"]!=LANE:
            raise ValueError("Outcome-independent selection rule changed")
        if row["admission_ref"]!=pack[name]["source_reference_ids"]:
            raise ValueError("Admission original source reference mismatch")
        if not row["source_primary_url"].startswith("https://"):
            raise ValueError("No source identity for ecological observation")
        if not row["source_secondary_url"].startswith("https://"):
            raise ValueError("No explicit supplement/source limitation URL")
        if row["functional_location"] not in ALLOWED_LOCATIONS:
            raise ValueError("Unrecognized observed ecological resource location")
        if row["formal_u6_architecture_assigned"]!="NOT_ASSIGNED_BY_EXTRACTOR":
            raise ValueError("Ecological extraction cannot be a four-class coder")
        if row["independent_coder_authorship"]!="NO_AI_EXTRACTOR_NOT_CODER_A_OR_B":
            raise ValueError("Source extractor cannot impersonate independent blind coder")
        for field in ("source_type","ecological_mechanism","original_observation",
                      "numeric_scope","main_uncertainty","extra_evidence","source_adjudication"):
            if not row.get(field):
                raise ValueError("Source ecology needs source/uncertainty receipt for "+name)
        seen[name]=row
    flagged={n for n in seen if "EVIDENCE_CEILING" in seen[n]["source_adjudication"]}
    if flagged!=EXPECTED_EVIDENCE_CEILING:
        raise ValueError("Original Hamelia numerical source access ceiling removed")
    if seen["Melastoma_affine"]["functional_location"]!="POST_DEPOSITION_STIGMA_POLLEN_REMOVAL":
        raise ValueError("Gross/Mackay stigma deposition-phase locus must not be mislabelled anther theft")
    if (seen["Echium_plantagineum"]["admission_ref"]!=
            pack["Actinidia_deliciosa"]["source_reference_ids"]):
        raise ValueError("Kirk 1987 source cannot become two independent source programmes")
    for n,action in EXPECTED_ALIAS.items():
        if dep[n]["analysis_action"]!=action:
            raise ValueError("Existing U1/U3 shared taxon dependence cannot be omitted")

    coders,c_sha=_csv(base,CODER)
    if len(coders)!=42 or {r["dependency_group"] for r in coders}!=universe:
        raise ValueError("Two independent U6 coding slots per group must exist")
    a_b=defaultdict(set)
    for row in coders:
        a_b[row["dependency_group"]].add(row["coder_id"])
        if row["coding_status"]!="UNSTARTED" or row["architecture_mode"]!="UNRESOLVED":
            raise ValueError("No coded U6 architecture outcomes may be imported into this source audit")
        if any(row[k]!="UNRESOLVED" for k in (
                "module_substrate","conflict_timing_geometry","conflict_spatial_geometry")):
            raise ValueError("No independent source predictor adjudications completed")
    if any(ids!={"CODER_A","CODER_B"} for ids in a_b.values()):
        raise ValueError("Frozen independent double-coding identities changed")

    # Twenty-one frozen taxa: original six in main, this newly extracted six,
    # and the prior first-six-clock project branch. The branch is not merged
    # and its output is not imported as formal coder evidence.
    extracted_main=set(recorded)|expected
    exploratory_cross_draft=set(sequential)|set(concurrent[:6])|expected
    if len(extracted_main)!=12 or len(exploratory_cross_draft)!=15:
        raise ValueError("Source selection ledger overlaps unexpectedly")
    by_reference=defaultdict(set)
    for name in extracted_main:
        for ref in pack[name]["source_reference_ids"].split(";"):
            by_reference[ref].add(name)
    shared={ref:sorted(items) for ref,items in by_reference.items() if len(items)>1}
    if shared!={"U6_REF_078":["Actinidia_deliciosa","Echium_plantagineum"]}:
        raise ValueError("Shared Kirk source identity not accounted for")
    return {
        "schema":"BALANCE_U6_NEXT6_ORIGINAL_SOURCE_ECOLOGY_V1",
        "status":"SIX_ADDITIONAL_SOURCE_OBSERVATIONS_NOT_INDEPENDENT_ARCHITECTURE_CODING",
        "frozen_admitted_u6_taxa":21,
        "frozen_source_timing":{"sequential":len(sequential),"simultaneous":len(concurrent)},
        "new_selection_rule":LANE,
        "new_selected_source_groups":sorted(expected),
        "original_six_main_covered":len(recorded),
        "additional_six_source_extracted":len(new),
        "distinct_main_branch_source_observation_groups":len(extracted_main),
        "distinct_main_branch_unextracted":21-len(extracted_main),
        "provisional_cross_branch_selected_total":len(exploratory_cross_draft),
        "cross_branch_remaining_unextracted":21-len(exploratory_cross_draft),
        "cross_branch_clock_source_branch":FROZEN_FIRST6_PREVIOUS_DRAFT,
        "cross_branch_results_not_formally_merged":True,
        "admission_source_id_reused_across_taxa":shared,
        "source_location_types":dict(sorted(Counter(r["functional_location"] for r in recent).items())),
        "post_deposition_stigma_pollen_removal_taxa":["Melastoma_affine"],
        "primary_1995_hamelia_effect_not_read_or_recomputed":True,
        "original_full_text_or_raw_table_not_recovered_for_every_source":True,
        "source_known_taxonomic_dependence":{
            n:dep[n]["analysis_action"] for n in sorted(EXPECTED_ALIAS)
        },
        "source_rows":sorted(recent,key=lambda x:x["dependency_group"]),
        "source_sha256":{
            FREEZE:hashlib.sha256(data).hexdigest(),PACKET:p_sha,
            PREDICTORS:pred_sha,PILOT:pilot_sha,NEXT6:r_sha,
            DEPENDENCE:dep_sha,CODER:c_sha,
        },
        "independent_coder_architecture_labels_added":0,
        "independent_coder_forms_modified":False,
        "v4_outcome_file_opened":False,
        "same_coordinate_conflict_loss_identified":False,
        "historical_evolutionary_origins_estimated":False,
        "source_extraction_does_not_estimate_population_prevalence":True,
    }

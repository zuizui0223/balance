"""Original-source ecological evidence pilot, NEVER independent architecture coding.

Six taxa were selected without morphology: the complete three frozen U6
SEQUENTIAL_WITHIN_UNIT groups plus the lexically first three of eighteen
SIMULTANEOUS groups. This script has no reader/import for the independent
A/B architecture worksheet or BALANCE V4 confirmatory response.

Original abstract-level descriptive observations in the six-row CSV are
exploratory SOURCE_EXTRACTOR notes, not two independent coder adjudications.
A/B must remain blind to this pilot until their registered coding is locked.
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
RECOVERY="data/BALANCE_PLANT_U6_PASS2_SOURCE_RECOVERY_FRAME_V1.csv"
DEPENDENCE="data/BALANCE_PLANT_U6_CROSS_UNIVERSE_DEPENDENCE_V1.csv"
PILOT="data/BALANCE_U6_ORIGINAL_SOURCE_ECOLOGY_PILOT_V1.csv"

LANE="ALL_THREE_SEQUENTIAL_PLUS_FIRST_THREE_SIMULTANEOUS_ALPHABETIC_BY_FROZEN_U6_GROUP"
ALLOWED_TIME={"SIMULTANEOUS","SEQUENTIAL_WITHIN_UNIT"}
ALLOWED_STUDY_SOURCE={
    "PUBLISHER_ORIGINAL_ABSTRACT",
    "ORIGINAL_AUTHOR_ABSTRACT_INDEXED_BY_AGRIS",
    "AUTHOR_ORIGINAL_ABSTRACT_REPRODUCED_IN_INSTITUTIONAL_RECORD",
    "PUBLISHER_ORIGINAL_ABSTRACT_PLUS_INDEPENDENT_ORIGINAL_2002_ARTICLE",
    "INSTITUTIONAL_ORIGINAL_AUTHOR_ABSTRACT",
    "ORIGINAL_STUDY_ABSTRACT_REPRODUCED_BY_BIBLIOGRAPHIC_INDEX",
}
FORBIDDEN_RESULT_MARKERS=(
    "FORMAL_ARCHITECTURE_ASSIGNED",
    "CODER_A","CODER_B","ADJUDICATED",
)
EXPECTED_ORIGINAL_SELECTION={
    "Clusia_arrudae","Crescentia_alata","Tolmiea_menziesii",
    "Actinidia_deliciosa","Amomum_subulatum","Aphelandra_golfodulcensis",
}


def _load(base:Path,rel:str)->tuple[list[dict[str,str]],str]:
    raw=(base/rel).read_bytes()
    with (base/rel).open(encoding="utf-8-sig",newline="") as h:
        reader=csv.DictReader(h)
        fields=reader.fieldnames or []
        if len(fields)!=len(set(fields)):
            raise ValueError("duplicate original input columns: "+rel)
        rows=list(reader)
    if not rows or any(None in row for row in rows):
        raise ValueError("empty or malformed source table "+rel)
    return rows,hashlib.sha256(raw).hexdigest()


def _unique(rows, key,source):
    names=[row[key] for row in rows]
    if any(not name for name in names) or len(names)!=len(set(names)):
        raise ValueError("duplicate/missing "+source+" source identity")
    return {row[key]:row for row in rows}


def analyze(base:Path=ROOT)->dict[str,Any]:
    raw=(base/FREEZE).read_bytes()
    freeze=json.loads(raw.decode("utf-8"))
    if (freeze.get("schema_version")!="BALANCE_PLANT_U6_PASS1_FREEZE_V1"
            or freeze.get("status")!="PASS1_CLOSED_PASS2_CODING_OPEN"
            or freeze.get("pass1_contract",{}).get("architecture_used_for_admission") is not False):
        raise ValueError("U6 frozen architecture-blind source contract changed")
    universe=freeze["included_dependency_groups"]
    if len(universe)!=21 or len(set(universe))!=21:
        raise ValueError("original U6 sample denominator changed")
    groups=set(universe)

    packet,p_sha=_load(base,PACKET)
    packet_by=_unique(packet,"dependency_group","source packet")
    recovery,r_sha=_load(base,RECOVERY)
    recovery_by=_unique(recovery,"dependency_group","source recovery")
    depend,d_sha=_load(base,DEPENDENCE)
    depend_by=_unique(depend,"u6_dependency_group","source dependence")
    if any(set(d)!=groups or len(d)!=21
           for d in (packet_by,recovery_by,depend_by)):
        raise ValueError("frozen source reference/recovery/dependence records changed")
    if any(row["packet_status"]!="FROZEN" or row["source_recovery_status"]
           not in {"RESOLVED","EVIDENCE_CEILING"} for row in recovery):
        raise ValueError("source recovery is not frozen or must retain evidence ceiling")

    predicates,pred_sha=_load(base,PREDICTORS)
    timing={}
    module={}
    spatial=set()
    for x in predicates:
        group=x["cluster_id"]
        if group not in groups or x["adjudication_status"]!="SCREENED":
            raise ValueError("source predictor row changed/unadjudicated geometry corrupted")
        if x["outcome_independence"]!="TRUE":
            raise ValueError("outcome-dependent original predictor discovered")
        key=x["predictor"]
        if key=="conflict_timing_geometry":
            if group in timing or x["reported_value"] not in ALLOWED_TIME:
                raise ValueError("source timing predictor changed")
            timing[group]=x["reported_value"]
        elif key=="module_substrate":
            if group in module or x["reported_value"]!="SINGLE_OR_CONTINUOUS":
                raise ValueError("source pollen pool changed")
            module[group]=x["reported_value"]
        elif key=="conflict_spatial_geometry":
            if x["reported_value"]!="SAME_UNIT" or group in spatial:
                raise ValueError("source spatial geometry changed or duplicate source group")
            spatial.add(group)
        else:
            raise ValueError("unrecognized original source predictor")
    if len(predicates)!=63 or set(timing)!=groups or set(module)!=groups or spatial!=groups:
        raise ValueError("three source predictors per each frozen group required")
    sequential=sorted(k for k,v in timing.items() if v=="SEQUENTIAL_WITHIN_UNIT")
    concurrent=sorted(k for k,v in timing.items() if v=="SIMULTANEOUS")
    if len(sequential)!=3 or len(concurrent)!=18:
        raise ValueError("frozen timing source split changed")
    selected=set(sequential+concurrent[:3])
    if selected!=EXPECTED_ORIGINAL_SELECTION:
        raise ValueError("outcome-independent pilot selection changed")

    pilot,pilot_sha=_load(base,PILOT)
    by=_unique(pilot,"dependency_group","source pilot")
    if len(pilot)!=6 or set(by)!=selected:
        raise ValueError("original source extractor six selected groups changed")
    for name,row in by.items():
        if row["selection_lane"]!=LANE:
            raise ValueError("source sample selection was changed after observations")
        if row["admission_reference_id"]!=packet_by[name]["source_reference_ids"]:
            raise ValueError("source observation does not match original review admission")
        if not row["primary_source_url"].startswith("https://"):
            raise ValueError("missing exact original source locator")
        if (row["source_access_class"] not in ALLOWED_STUDY_SOURCE
                or not row["source_observation_ecology"]
                or not row["source_observation_structure"]
                or not row["source_observation_timing"]
                or not row["source_reported_effect"]
                or not row["missing_for_formal_architecture_coding"]):
            raise ValueError("observation lacks source or missingness status")
        if row["formal_u6_architecture_assigned"]!="NOT_ASSIGNED_BY_EXTRACTOR":
            raise ValueError("source observation extractor cannot act as independent architecture coder")
        if row["independent_coder_authorship"]!="NO_AI_EXTRACTOR_NOT_CODER_A_OR_B":
            raise ValueError("source extractor cannot impersonate independent coder A or B")
        if row["provisional_ecological_interpretation"].startswith(FORBIDDEN_RESULT_MARKERS):
            raise ValueError("source ecological note cannot masquerade as frozen outcome")

    by_reference=defaultdict(set)
    for name in universe:
        for reference_id in packet_by[name]["source_reference_ids"].split(";"):
            if not reference_id.startswith("U6_REF_"):
                raise ValueError("registered U6 source-reference identifier invalid")
            by_reference[reference_id].add(name)
    shared_source_programmes={
        k:sorted(v) for k,v in by_reference.items() if len(v)>1
    }
    if shared_source_programmes!={"U6_REF_078":[
        "Actinidia_deliciosa","Echium_plantagineum"
    ]}:
        raise ValueError("Original U6 primary study reuse across source taxa changed")

    all_rows=[]
    for name in universe:
        src=recovery_by[name]
        rec=by.get(name)
        all_rows.append({
            "dependency_group":name,
            "original_source_ref":packet_by[name]["source_reference_ids"],
            "original_primary_source_bibliography":packet_by[name]["primary_source_basis"],
            "source_recovery_status":src["source_recovery_status"],
            "original_timing_exposure_code":timing[name],
            "original_source_pollen_pool":module[name],
            "cross_universe_action":depend_by[name]["analysis_action"],
            "independent_A_B_coding_performed_by_this_audit":False,
            "observation_literature_extracted_by_pilot":rec is not None,
            "ecological_observation":rec["source_observation_ecology"] if rec else None,
            "floral_observation":rec["source_observation_structure"] if rec else None,
            "functional_time_observation":rec["source_observation_timing"] if rec else None,
            "reported_source_effect":rec["source_reported_effect"] if rec else None,
            "source_locator":rec["primary_source_url"] if rec else None,
            "source_limitations":rec["missing_for_formal_architecture_coding"] if rec else None,
        })

    cases=Counter(row["provisional_ecological_interpretation"] for row in pilot)
    recovered_status=Counter(r["source_recovery_status"] for r in recovery)
    return {
        "schema":"BALANCE_U6_FROZEN_SOURCE_FUNCTIONAL_ECOLOGY_EXTRACTION_PILOT_V1",
        "status":"SIX_ORIGINAL_ABSTRACT_SOURCE_OBSERVATIONS_NOT_ARCHITECTURE_ADJUDICATION",
        "sampling_rule":LANE,
        "source_sha256":{
            FREEZE:hashlib.sha256(raw).hexdigest(),
            PACKET:p_sha,RECOVERY:r_sha,
            PREDICTORS:pred_sha,DEPENDENCE:d_sha,PILOT:pilot_sha,
        },
        "admitted_groups":21,
        "original_source_recovery_statuses":dict(sorted(recovered_status.items())),
        "source_timing_groups":{"simultaneous":len(concurrent),"sequential":len(sequential)},
        "pilot_selected_groups":sorted(selected),
        "selected_timing_counts":{
            "SEQUENTIAL_WITHIN_UNIT":len(sequential),
            "SIMULTANEOUS":len(concurrent[:3]),
        },
        "original_abstract_observations_extracted":len(pilot),
        "distinct_admission_source_reference_ids":len(by_reference),
        "shared_original_source_reference_between_taxa":shared_source_programmes,
        "taxa_with_shared_original_source_reference_are_not_independent_studies":True,
        "not_yet_extracted":21-len(pilot),
        "provisional_ecological_mechanisms_described_not_as_natural_rates":dict(sorted(cases.items())),
        "analysis_rows":all_rows,
        "independent_A_B_architecture_labels_written":0,
        "sealed_V4_architecture_outcome_opened":False,
        "source_abstract_sufficient_to_prove_new_heritable_module":False,
        "historical_evolutionary_causality_established":False,
        "source_packet_for_blind_independent_A_B_unchanged":True,
        "warning":"EXTRACTOR_NOT_A_BLINDED_CODER: keep this pilot away from independent A/B raters until labels are locked.",
    }

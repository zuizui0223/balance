"""Source-excerpt clock evidence for the FIRST SIX frozen U6 pollen-theft taxa.

This is a new *researcher source-review* surface. It is NOT one of the two
independent human coders, not an adjudicated predictor receipt, and not a
confirmatory U6 architecture outcome. Source retrieval was frozen before
any anatomical observations in the U6 screening frame. No taxa are
selected because of an interesting phenotypic outcome.

A source-time tag ('SIMULTANEOUS' pollen fate vs retained/exported fate)
is not automatically equal to within-day visitor order, floral sexual
phase, multi-day floret opening, or cross-individual sex organization.
"""
from __future__ import annotations

import csv
from collections import Counter
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
FREEZE="data/BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"
PACKET="data/BALANCE_PLANT_U6_PASS2_SOURCE_PACKET_V1.csv"
RECOVERY="data/BALANCE_PLANT_U6_PASS2_SOURCE_RECOVERY_FRAME_V1.csv"
ORIGINAL_CODER="data/BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv"
OBS="data/BALANCE_U6_FIRST6_ORIGINAL_PHENOMENOLOGY_V1.json"
EXPECTED_TAXA=(
    "Actinidia_deliciosa","Amomum_subulatum",
    "Aphelandra_golfodulcensis","Banksia_menziesii",
    "Bromelia_antiacantha","Campanula_americana",
)
APPROVED_LEVELS={
    "ORIGINAL_ABSTRACT_AND_INDEPENDENT_FLORAL_ANATOMY",
    "ORIGINAL_STUDY_OPEN_REPOSITORY_ABSTRACT",
    "PRIMARY_PAPER_IDENTITY_SECONDARY_PUBLIC_ABSTRACT_SUMMARY",
    "ORIGINAL_STUDY_PUBLIC_ABSTRACT",
    "TWO_DISTINCT_ORIGINAL_STUDY_ABSTRACTS",
}
APPROVED_URL_HOSTS={
    "doi.org","pubmed.ncbi.nlm.nih.gov",
    "repository.ias.ac.in",
}
DOI_SOURCE_TYPES={
    "PUBLISHED_ORIGINAL_ABSTRACT",
    "PUBLISHED_ORIGINAL_ARTICLE_TEXT",
    "ORIGINAL_PAPER_PUBLIC_REPOSITORY_ABSTRACT",
    "PRIMARY_PAPER_WITH_SECONDARY_PUBLIC_SUMMARY",
    "ORIGINAL_PAPER_PUBLIC_ABSTRACT",
    "ORIGINAL_PAPER_PUBLIC_HTML_METHODS",
}
FORBIDDEN_OUTPUT_KEYS={
    "architecture_mode","module_substrate",
    "conflict_timing_geometry","conflict_spatial_geometry",
    "coder_id","coding_status","R","K","Phi",
}


def _csv(base:Path,path:str) -> tuple[list[dict[str,str]],str]:
    raw=(base/path).read_bytes()
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if not rows or len(set(rows[0]))!=len(rows[0]) or any(None in r for r in rows):
        raise ValueError("Invalid frozen U6 CSV: "+path)
    return rows,hashlib.sha256(raw).hexdigest()


def _freeze(base:Path) -> tuple[list[str],str]:
    raw=(base/FREEZE).read_bytes()
    src=json.loads(raw.decode("utf-8"))
    groups=src.get("included_dependency_groups")
    if (src.get("status")!="PASS1_CLOSED_PASS2_CODING_OPEN"
        or src.get("pass1_contract",{}).get("architecture_used_for_admission") is not False
        or not isinstance(groups,list) or len(groups)!=21 or len(set(groups))!=21
        or tuple(groups[:6])!=EXPECTED_TAXA):
        raise ValueError("First-six outcome-independent selection order has changed")
    return groups,hashlib.sha256(raw).hexdigest()


def _no_outcome_keys(value:Any) -> None:
    if isinstance(value,dict):
        if set(value).intersection(FORBIDDEN_OUTPUT_KEYS):
            raise ValueError("Source phenomenology cannot insert frozen architecture or predictor result")
        for x in value.values():
            _no_outcome_keys(x)
    elif isinstance(value,list):
        for x in value:
            _no_outcome_keys(x)


def analyze(base:Path=ROOT) -> dict[str,Any]:
    groups,freeze_hash=_freeze(base)
    packet,packet_hash=_csv(base,PACKET)
    recovery,recovery_hash=_csv(base,RECOVERY)
    coder,coder_hash=_csv(base,ORIGINAL_CODER)
    if (
        len(packet)!=21 or len(recovery)!=21 or
        [r["dependency_group"] for r in packet]!=groups or
        {r["dependency_group"] for r in recovery}!=set(groups) or
        any(r["packet_status"]!="FROZEN" for r in recovery)
    ):
        raise ValueError("Original frozen source packet/recovery denominators changed")
    if (len(coder)!=42 or {r["dependency_group"] for r in coder}!=set(groups)
        or any(r["coding_status"]!="UNSTARTED"
               or r["architecture_mode"]!="UNRESOLVED" for r in coder)):
        raise ValueError("This surface must never open U6 independent coder outcomes")
    for row in coder:
        if any(row[f]!="UNRESOLVED" for f in (
                "module_substrate","conflict_timing_geometry",
                "conflict_spatial_geometry"
        )):
            raise ValueError("Protected double coder predictor state changed")
    for group in groups:
        members={r["coder_id"] for r in coder if r["dependency_group"]==group}
        if members!={"CODER_A","CODER_B"}:
            raise ValueError("Missing or duplicated independent frozen coder identity")
    raw=(base/OBS).read_bytes()
    obs=json.loads(raw.decode("utf-8"))
    if obs.get("schema")!="BALANCE_U6_FIRST6_ORIGINAL_PHENOMENOLOGY_V1":
        raise ValueError("Original evidence overlay has wrong schema")
    _no_outcome_keys(obs)
    items=obs.get("first_six",[])
    if len(items)!=6 or tuple(x["dependency_group"] for x in items)!=EXPECTED_TAXA:
        raise ValueError("Outcome-blind first six cannot be reordered or replaced")
    if obs.get("status")!="PUBLIC_ORIGINAL_ABSTRACT_LEVEL_EVIDENCE_NOT_INDEPENDENT_CODER":
        raise ValueError("Do not promote original literature review to independent coder")
    rec={r["dependency_group"]:r for r in recovery}
    ids={r["dependency_group"]:r["source_reference_ids"] for r in packet}
    clock=Counter(); components=Counter(); observed=[]
    by_evidence=Counter(); source_programme_count=0
    for row in items:
        group=row["dependency_group"]
        if row["evidence_status"] not in APPROVED_LEVELS:
            raise ValueError("Unregistered article/abstract evidence status")
        evidence=row["source_records"]
        if not evidence or not row["unresolved"]:
            raise ValueError("No original source record or missing causal ceiling")
        if len({x["source_id"] for x in evidence})!=len(evidence):
            raise ValueError("Duplicate source-specific evidence within a taxon")
        for source in evidence:
            host=urlparse(source["url"]).netloc.lower()
            if host not in APPROVED_URL_HOSTS or source["type"] not in DOI_SOURCE_TYPES:
                raise ValueError("Source paper URL or evidence category not admitted")
            if not source["observation"] or not source["context"]:
                raise ValueError("Published source observation needs exact context")
        if row["source_contexts_not_matched"] != (len(evidence)>1):
            raise ValueError("Multiple study programmes cannot be treated as same experiment")
        clock.update(set(row["clock_axes"]))
        components.update(set(row["observed_components"]))
        by_evidence[row["evidence_status"]]+=1
        source_programme_count+=len(evidence)
        observed.append({
            "taxon":group.replace("_"," "),
            "frozen_dependency_group":group,
            "frozen_u6_reference_id":ids[group],
            "original_source_recovery_status":rec[group]["source_recovery_status"],
            "observed_anatomy_or_activity":row["observed_components"],
            "distinct_clock_axes":row["clock_axes"],
            "independent_source_programmes":len(evidence),
            "different_studies_not_a_matched_experiment":row["source_contexts_not_matched"],
            "original_source_receipts":evidence,
            "unidentified_evolutionary_claims":row["unresolved"],
            "not_an_independent_adjudicator":True,
            "not_a_structural_module_outcome":True,
        })
    if observed[2]["original_source_recovery_status"]!="EVIDENCE_CEILING":
        raise ValueError("Aphelandra source recovery ceiling cannot be auto-promoted")
    if [x["original_source_recovery_status"] for x in observed].count("RESOLVED")!=5:
        raise ValueError("Original 5/1 source recovery identity changed")
    if (sum(1 for x in observed if x["different_studies_not_a_matched_experiment"])!=2
        or sum(x["independent_source_programmes"] for x in observed)!=8):
        raise ValueError("Original source programme/context counts changed")
    return{
        "schema":"BALANCE_U6_FIRST6_MULTI_CLOCK_OBSERVATION_V1",
        "status":"SOURCE_REVIEW_ONLY_DOES_NOT_COMPLETE_ANY_U6_CODER_ROW",
        "selection":"ALPHABETICALLY_FROZEN_FIRST_SIX_NO_OUTCOME_BASED_REPLACEMENT",
        "original_frozen_admitted_groups":len(groups),
        "source_reviewed_initial_groups":len(observed),
        "source_review_remaining_groups_unreviewed":len(groups)-len(observed),
        "source_recovery_states":dict(sorted(Counter(
            x["original_source_recovery_status"] for x in observed).items()
        )),
        "source_programmes_evaluated":source_programme_count,
        "source_contexts_not_matched_count":2,
        "source_level_count":dict(sorted(by_evidence.items())),
        "clock_axes_species_presence_counts":dict(sorted(clock.items())),
        "observed_biological_components_species_presence_counts":dict(sorted(components.items())),
        "source_observation_rows":observed,
        "source_input_sha256":{
            FREEZE:freeze_hash,PACKET:packet_hash,
            RECOVERY:recovery_hash,ORIGINAL_CODER:coder_hash,
            OBS:hashlib.sha256(raw).hexdigest(),
        },
        "frozen_human_coder_rows_left_untouched":42,
        "independent_adjudicated_architecture_groups":0,
        "qualifying_structural_origin_effects":0,
        "common_fitness_shared_plastic_module_comparator":False,
        "no_causal_history_of_new_modules_inferred":True,
        "frozen_v4_outcome_file_read":False,
        "source_timing_tag_is_not_substituted_for_any_of_these_clocks":True,
        "data_statement":(
            "Only publicly described phenomena from first-six original-source reports;"
            " not outcome coding, natural frequency, same-plant genotype response,"
            " genetically dated origin, independent source replication or estimated Phi."
        ),
    }

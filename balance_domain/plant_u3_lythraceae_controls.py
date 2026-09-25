"""Fail-closed prospective Lythraceae control search for Lagerstroemia indica."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

FIELDS = (
    "candidate_id","case_taxon","candidate_control","candidate_role",
    "taxonomic_relation","heteranthery_absence_status","animal_pollination_status",
    "phylogenetic_proximity_status","closest_eligible_search_status",
    "selection_status","source_id","blocker","notes",
)
ROLE = {"NEAR_RELATIVE","FAMILY_LEVEL_CANDIDATE"}
GATE = {"PASS","OPEN","FAIL"}
STATUS = {"OPEN","SCREENED","REJECTED"}
EXPECTED = {
    "Lagerstroemia guilinensis","Lagerstroemia excelsa","Lagerstroemia glabra",
    "Lagerstroemia subcostata","Lagerstroemia parviflora",
    "Lagerstroemia speciosa","Lagerstroemia macrocarpa",
}

def load_u3_lythraceae_control_search(path: Path) -> list[dict[str,str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader=csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 Lythraceae control-search columns must match canonical order")
        rows=list(reader)
    if {r["candidate_control"] for r in rows} != EXPECTED:
        raise ValueError("U3 Lythraceae search must retain the frozen candidate set")
    seen=set()
    for n,row in enumerate(rows,start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside Lythraceae search schema")
        clean={k:(v or "").strip() for k,v in row.items()}
        if clean["candidate_id"] in seen:
            raise ValueError(f"duplicate candidate_id {clean['candidate_id']!r}")
        seen.add(clean["candidate_id"])
        if clean["case_taxon"] != "Lagerstroemia indica":
            raise ValueError(f"row {n} wrong prospective case taxon")
        if clean["candidate_role"] not in ROLE:
            raise ValueError(f"row {n} invalid candidate role")
        for field in (
            "heteranthery_absence_status","animal_pollination_status",
            "phylogenetic_proximity_status","closest_eligible_search_status",
        ):
            if clean[field] not in GATE:
                raise ValueError(f"row {n} invalid {field}")
        if clean["selection_status"] not in STATUS:
            raise ValueError(f"row {n} invalid selection status")
        if clean["selection_status"] == "REJECTED":
            if "FAIL" not in tuple(clean[f] for f in (
                "heteranthery_absence_status","animal_pollination_status",
                "phylogenetic_proximity_status","closest_eligible_search_status",
            )):
                raise ValueError(f"row {n} REJECTED candidate requires a failed gate")
        elif clean["selection_status"] == "OPEN":
            gates=tuple(clean[f] for f in (
                "heteranthery_absence_status","animal_pollination_status",
                "phylogenetic_proximity_status","closest_eligible_search_status",
            ))
            if "FAIL" in gates or "OPEN" not in gates:
                raise ValueError(f"row {n} OPEN candidate requires open and no failed gates")
        if not clean["source_id"] or not clean["blocker"]:
            raise ValueError(f"row {n} source and blocker must be frozen")
        row.update(clean)

    near=[r for r in rows if r["candidate_role"]=="NEAR_RELATIVE"]
    if not near or any(r["selection_status"]!="REJECTED" for r in near):
        raise ValueError("all frozen close Lythraceae candidates must remain rejected")
    if any(r["heteranthery_absence_status"]!="FAIL" for r in near):
        raise ValueError("close Lagerstroemia candidates are rejected by the absence gate")

    family=[r for r in rows if r["candidate_role"]=="FAMILY_LEVEL_CANDIDATE"]
    if {r["candidate_control"] for r in family} != {
        "Lagerstroemia parviflora","Lagerstroemia speciosa","Lagerstroemia macrocarpa"
    }:
        raise ValueError("retain all three frozen monomorphic family-level candidates")
    if any(r["heteranthery_absence_status"]!="PASS" for r in family):
        raise ValueError("family-level candidates must pass negative morphology")
    spec=next(r for r in rows if r["candidate_control"]=="Lagerstroemia speciosa")
    if spec["animal_pollination_status"]!="PASS":
        raise ValueError("L. speciosa has source-secure effective bee pollination")
    par=next(r for r in rows if r["candidate_control"]=="Lagerstroemia parviflora")
    if par["phylogenetic_proximity_status"]!="OPEN":
        raise ValueError("L. parviflora is unsampled on the common modern phylogenetic surface")
    if any(r["selection_status"]!="OPEN" for r in family):
        raise ValueError("no monomorphic control may be promoted while ranking remains open")
    return rows

def build_u3_lythraceae_control_search_readout(path: Path) -> dict:
    rows=load_u3_lythraceae_control_search(path)
    near=[r for r in rows if r["candidate_role"]=="NEAR_RELATIVE"]
    family=[r for r in rows if r["candidate_role"]=="FAMILY_LEVEL_CANDIDATE"]
    return {
        "analysis":"balance_u3_lythraceae_prospective_control_search",
        "n_candidates":len(rows),
        "status_counts":dict(sorted(Counter(r["selection_status"] for r in rows).items())),
        "n_close_candidates_rejected_by_absence_gate":sum(
            r["heteranthery_absence_status"]=="FAIL" for r in near
        ),
        "monomorphic_family_level_candidates":sorted(r["candidate_control"] for r in family),
        "family_level_candidates_with_animal_pollination_pass":sorted(
            r["candidate_control"] for r in family if r["animal_pollination_status"]=="PASS"
        ),
        "control_selected":False,
        "search_closed":False,
        "blocker":"MONOMORPHIC_L_PARVIFLORA_COMMON_PHYLOGENETIC_RANKING_AND_EFFECTIVE_POLLINATION_OPEN",
        "claim_ceiling":"blinded_control_candidate_search_only_not_control_selection_not_conflict_extraction_not_routing_architecture",
    }

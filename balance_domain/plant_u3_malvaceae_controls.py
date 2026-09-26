"""Fail-closed prospective Malvaceae control search for Mollia lepidota."""
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
ROLE={"RESOLVED_CONGENER","UNRESOLVED_CONGENER","GENUS_REMAINDER"}
GATE={"PASS","OPEN","FAIL"}
STATUS={"OPEN","SCREENED","REJECTED"}
EXPECTED_RESOLVED={"Mollia speciosa","Mollia gracilis","Mollia tomentosa","Mollia longifolia"}
EXPECTED_OPEN={"Mollia trimera","Mollia spp. unresolved accepted remainder"}

def load_u3_malvaceae_control_search(path: Path) -> list[dict[str,str]]:
    with path.open(encoding="utf-8",newline="") as handle:
        reader=csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 Malvaceae control-search columns must match canonical order")
        rows=list(reader)
    if {r["candidate_control"] for r in rows} != EXPECTED_RESOLVED|EXPECTED_OPEN:
        raise ValueError("U3 Malvaceae search must retain the frozen congeneric receipts")
    seen=set()
    for n,row in enumerate(rows,start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside Malvaceae search schema")
        clean={k:(v or "").strip() for k,v in row.items()}
        if clean["candidate_id"] in seen:
            raise ValueError(f"duplicate candidate_id {clean['candidate_id']!r}")
        seen.add(clean["candidate_id"])
        if clean["case_taxon"]!="Mollia lepidota":
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
        gates=tuple(clean[f] for f in (
            "heteranthery_absence_status","animal_pollination_status",
            "phylogenetic_proximity_status","closest_eligible_search_status",
        ))
        if clean["selection_status"]=="REJECTED":
            if "FAIL" not in gates:
                raise ValueError(f"row {n} rejected candidate requires a failed gate")
        elif clean["selection_status"]=="OPEN":
            if "FAIL" in gates or "OPEN" not in gates:
                raise ValueError(f"row {n} open candidate requires open and no failed gates")
        if not clean["source_id"] or not clean["blocker"]:
            raise ValueError(f"row {n} source and blocker must be frozen")
        row.update(clean)

    resolved=[r for r in rows if r["candidate_role"]=="RESOLVED_CONGENER"]
    if {r["candidate_control"] for r in resolved} != EXPECTED_RESOLVED:
        raise ValueError("retain the four source-resolved close congener morphology receipts")
    if any(r["heteranthery_absence_status"]!="FAIL" or r["selection_status"]!="REJECTED" for r in resolved):
        raise ValueError("source-resolved close Mollia congeners must remain morphology failures")

    trimera=next(r for r in rows if r["candidate_control"]=="Mollia trimera")
    if trimera["selection_status"]!="OPEN":
        raise ValueError("M. trimera must remain open under the divergent-floral-plan evidence ceiling")
    if trimera["heteranthery_absence_status"]!="OPEN" or trimera["phylogenetic_proximity_status"]!="OPEN":
        raise ValueError("M. trimera morphology and intrageneric ranking must remain open")

    remainder=next(r for r in rows if r["candidate_role"]=="GENUS_REMAINDER")
    if remainder["selection_status"]!="OPEN":
        raise ValueError("unresolved accepted Mollia remainder must stay open")
    return rows

def build_u3_malvaceae_control_search_readout(path: Path) -> dict:
    rows=load_u3_malvaceae_control_search(path)
    resolved=[r for r in rows if r["candidate_role"]=="RESOLVED_CONGENER"]
    open_rows=[r for r in rows if r["selection_status"]=="OPEN"]
    return {
        "analysis":"balance_u3_malvaceae_prospective_control_search",
        "n_receipts":len(rows),
        "status_counts":dict(sorted(Counter(r["selection_status"] for r in rows).items())),
        "n_resolved_congener_morphology_failures":sum(
            r["heteranthery_absence_status"]=="FAIL" for r in resolved
        ),
        "open_congeneric_surfaces":sorted(r["candidate_control"] for r in open_rows),
        "control_selected":False,
        "search_closed":False,
        "blocker":"MOLLIA_DIVERGENT_AND_REMAINDER_SPECIES_MORPHOLOGY_PLUS_INTRAGENERIC_PHYLOGENY_OPEN",
        "claim_ceiling":"blinded_control_candidate_search_only_not_control_selection_not_conflict_extraction_not_routing_architecture",
    }

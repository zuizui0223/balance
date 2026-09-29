"""Fail-closed candidate-control audit for the prospective Diascia block."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

FIELDS=(
    "candidate_id","case_taxon","candidate_control","proximity_status",
    "heteranthery_absence_status","animal_pollination_status",
    "closest_eligible_status","decision","source_id","notes",
)
GATE={"PASS","OPEN","FAIL"}
DECISION={"OPEN","REJECTED"}

def load_diascia_control_audit(path:Path)->list[dict[str,str]]:
    with path.open(encoding="utf-8",newline="") as handle:
        reader=csv.DictReader(handle)
        if tuple(reader.fieldnames or ())!=FIELDS:
            raise ValueError("Diascia control audit columns must match canonical order")
        rows=list(reader)
    if not rows:
        raise ValueError("Diascia control audit must not be empty")
    seen=set()
    for n,row in enumerate(rows,start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside Diascia audit schema")
        row.update({k:(v or "").strip() for k,v in row.items()})
        if row["candidate_id"] in seen or not row["candidate_id"]:
            raise ValueError(f"row {n} candidate_id must be unique and frozen")
        seen.add(row["candidate_id"])
        if row["case_taxon"]!="Diascia anastrepta":
            raise ValueError(f"row {n} wrong Diascia case")
        for field in ("proximity_status","heteranthery_absence_status","animal_pollination_status","closest_eligible_status"):
            if row[field] not in GATE:
                raise ValueError(f"row {n} invalid {field}")
        if row["decision"] not in DECISION:
            raise ValueError(f"row {n} invalid decision")
        gates=[row[f] for f in ("proximity_status","heteranthery_absence_status","animal_pollination_status","closest_eligible_status")]
        if row["decision"]=="REJECTED" and "FAIL" not in gates:
            raise ValueError(f"row {n} rejected candidate requires a failed gate")
        if row["decision"]=="OPEN":
            if "FAIL" in gates or "OPEN" not in gates:
                raise ValueError(f"row {n} open candidate requires open but no failed gates")
        if not row["source_id"] or not row["notes"]:
            raise ValueError(f"row {n} source and notes must be frozen")
    return rows

def build_diascia_control_audit(path:Path)->dict:
    rows=load_diascia_control_audit(path)
    decisions=Counter(r["decision"] for r in rows)
    open_rows=[r for r in rows if r["decision"]=="OPEN"]
    return {
        "analysis":"balance_u3_diascia_control_audit",
        "n_candidates":len(rows),
        "decision_counts":dict(sorted(decisions.items())),
        "open_candidates":sorted(r["candidate_control"] for r in open_rows),
        "n_biologically_eligible_but_closest_open":sum(
            r["heteranthery_absence_status"]=="PASS"
            and r["animal_pollination_status"]=="PASS"
            and r["closest_eligible_status"]=="OPEN"
            for r in rows
        ),
        "control_selected":False,
        "evidence_ceiling_blocked":True,
        "blocker":"CLOSEST_ELIGIBLE_CONGENER_RANKING_NOT_SOURCE_CLOSED",
        "claim_ceiling":"matching_stage_candidate_audit_only_not_control_selection_not_routing_outcome",
    }

"""Frozen public-evidence ceilings for unresolved U3 measurements.

A frozen ceiling means that the registered public-source audit has not recovered
qualifying evidence for the target. It does not prove that the biology is absent
or that no unpublished/new source exists. It prevents repeated retrieval from
being mistaken for unresolved design work.
"""
from __future__ import annotations

import csv
from pathlib import Path


FIELDS = (
    "target_id",
    "taxon",
    "evidence_target",
    "registered_gate",
    "audit_date",
    "search_languages",
    "source_ids",
    "best_available_evidence",
    "qualifying_direct_evidence",
    "status",
    "next_action",
    "notes",
)

EXPECTED_TARGETS = {
    "U3_EC_MON_AUS_POLLINATION",
    "U3_EC_MON_CYA_POLLINATION",
    "U3_EC_OSB_CHI_CONFLICT",
    "U3_EC_SEN_COV_ROUTING",
    "U3_EC_COC_TET_POLLINATION",
}
STATUS = {"PUBLIC_RETRIEVAL_CEILING_FROZEN_UNRESOLVED"}
NEXT_ACTION = {
    "NEW_DIRECT_PRIMARY_OR_FIELD_EVIDENCE_REQUIRED",
    "NEW_DIRECT_PRIMARY_OR_EMPIRICAL_EVIDENCE_REQUIRED",
    "NEW_DIRECT_PRIMARY_OR_EMPIRICAL_ROUTING_EVIDENCE_REQUIRED",
}


def load_u3_evidence_ceilings(path: Path) -> list[dict[str, str | bool]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 evidence-ceiling columns must match canonical order")
        rows = list(reader)

    if {r["target_id"] for r in rows} != EXPECTED_TARGETS:
        raise ValueError("U3 evidence-ceiling ledger must contain exactly the five frozen targets")

    out: list[dict[str, str | bool]] = []
    seen: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U3 evidence-ceiling schema")
        clean = {k: (v or "").strip() for k, v in row.items()}
        target = clean["target_id"]
        if target in seen:
            raise ValueError(f"duplicate evidence-ceiling target {target!r}")
        seen.add(target)
        for field in FIELDS:
            if field not in {"notes"} and not clean[field]:
                raise ValueError(f"row {n} {field} must be frozen")
        q = clean["qualifying_direct_evidence"].casefold()
        if q not in {"true", "false"}:
            raise ValueError(f"row {n} qualifying_direct_evidence must be true/false")
        if q != "false":
            raise ValueError(f"row {n} frozen unresolved ceiling cannot claim qualifying evidence")
        if clean["status"] not in STATUS:
            raise ValueError(f"row {n} invalid evidence-ceiling status")
        if clean["next_action"] not in NEXT_ACTION:
            raise ValueError(f"row {n} invalid next_action")
        out.append({**clean, "qualifying_direct_evidence": False})
    return out


def build_u3_evidence_ceiling_readout(path: Path) -> dict:
    rows = load_u3_evidence_ceilings(path)
    return {
        "analysis": "balance_plant_u3_public_evidence_ceiling",
        "n_targets": len(rows),
        "n_frozen_unresolved": len(rows),
        "n_qualifying_direct_evidence": 0,
        "public_retrieval_ceiling_frozen": True,
        "retrieval_open": False,
        "taxa_requiring_new_direct_or_empirical_evidence": sorted(
            {str(r["taxon"]) for r in rows}
        ),
        "targets": sorted(str(r["target_id"]) for r in rows),
        "claim_ceiling": (
            "registered_public_retrieval_ceiling_only_not_biological_absence_"
            "not_exhaustive_global_literature_proof_not_measurement_completion"
        ),
    }

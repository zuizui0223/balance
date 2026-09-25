"""Fail-closed evidence ceilings for the remaining U3 empirical gates."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "ceiling_id",
    "taxon",
    "gate",
    "strongest_evidence_status",
    "search_scope_status",
    "decision",
    "missing_evidence",
    "source_id",
    "notes",
)

EXPECTED = {
    "U3CEIL_MONAUS_001": (
        "Monochoria australasica",
        "DIRECT_SPECIES_LEVEL_EFFECTIVE_ANIMAL_POLLINATION",
    ),
    "U3CEIL_MONCYA_001": (
        "Monochoria cyanea",
        "DIRECT_SPECIES_LEVEL_EFFECTIVE_ANIMAL_POLLINATION",
    ),
    "U3CEIL_OSBCHI_001": (
        "Osbeckia chinensis",
        "CONTROL_POLLEN_FATE_CONFLICT",
    ),
}

SEARCH_STATUS = {
    "PUBLIC_LITERATURE_SEARCHED_NO_DIRECT_RECEIPT",
    "PUBLIC_LITERATURE_SEARCHED_NO_MATCHED_FATE_RECEIPT",
}
DECISION = {"OPEN", "PASS"}


def load_u3_evidence_ceiling(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 evidence-ceiling columns must match canonical order")
        rows = list(reader)

    if len(rows) != len(EXPECTED):
        raise ValueError("U3 evidence-ceiling ledger must contain exactly three registered targets")

    seen = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U3 evidence-ceiling schema")
        clean = {k: (v or "").strip() for k, v in row.items()}
        row.update(clean)
        ceiling_id = row["ceiling_id"]
        if ceiling_id not in EXPECTED or ceiling_id in seen:
            raise ValueError(f"row {n} ceiling_id must be unique and registered")
        seen.add(ceiling_id)

        expected_taxon, expected_gate = EXPECTED[ceiling_id]
        if row["taxon"] != expected_taxon or row["gate"] != expected_gate:
            raise ValueError(f"row {n} target identity disagrees with frozen ceiling")
        if row["search_scope_status"] not in SEARCH_STATUS:
            raise ValueError(f"row {n} invalid search_scope_status")
        if row["decision"] not in DECISION:
            raise ValueError(f"row {n} invalid decision")
        if not row["strongest_evidence_status"] or not row["source_id"]:
            raise ValueError(f"row {n} evidence provenance must be frozen")

        if row["decision"] == "OPEN":
            if not row["missing_evidence"]:
                raise ValueError(f"row {n} OPEN ceiling requires explicit missing evidence")
            if "NO_" not in row["search_scope_status"]:
                raise ValueError(f"row {n} OPEN ceiling requires a fail-closed search status")
        else:
            if row["missing_evidence"]:
                raise ValueError(f"row {n} PASS ceiling cannot retain missing evidence")
    return rows


def build_u3_evidence_ceiling_readout(path: Path) -> dict:
    rows = load_u3_evidence_ceiling(path)
    decisions = Counter(r["decision"] for r in rows)
    open_rows = [r for r in rows if r["decision"] == "OPEN"]
    return {
        "analysis": "balance_plant_u3_evidence_ceiling",
        "n_targets": len(rows),
        "decision_counts": dict(sorted(decisions.items())),
        "open_taxa": sorted(r["taxon"] for r in open_rows),
        "open_gates": {
            r["taxon"]: r["gate"] for r in sorted(open_rows, key=lambda x: x["taxon"])
        },
        "evidence_ceiling_closed": not open_rows,
        "claim_ceiling": (
            "search_ceiling_and_missing_evidence_receipts_only_"
            "not_negative_biological_evidence_not_effect_estimate"
        ),
    }

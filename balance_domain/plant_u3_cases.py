"""Species-level source-resolved case candidates for U3 heteranthery."""
from __future__ import annotations

import csv
from pathlib import Path

from .plant_u3 import load_u3_universe


FIELDS = (
    "case_id",
    "family",
    "case_taxon",
    "primary_source_id",
    "primary_source_doi",
    "evidence_class",
    "direct_pollen_fate_conflict_evidence",
    "heteranthery_confirmed",
    "case_status",
    "matched_control_status",
    "notes",
)

DIRECT = {"true", "partial", "false"}
HET = {"true"}
CASE_STATUS = {"SOURCE_RESOLVED_NOT_MATCHED", "MATCHED_CONTROL_REGISTERED", "REJECTED"}
CONTROL_STATUS = {"CONTROL_NOT_REGISTERED", "CONTROL_REGISTERED"}


def load_u3_case_candidates(case_path: Path, universe_path: Path) -> list[dict[str, str]]:
    universe = load_u3_universe(universe_path)
    allowed_families = {r["family"] for r in universe}

    with case_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 case-candidate columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("U3 case-candidate registry must contain at least one case")

    ids = set()
    taxa = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U3 case schema")
        for field in FIELDS[:-1]:
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"row {n} {field} must be frozen")
        if row["case_id"] in ids:
            raise ValueError(f"duplicate U3 case_id {row['case_id']!r}")
        ids.add(row["case_id"])
        if row["case_taxon"] in taxa:
            raise ValueError(f"duplicate U3 case taxon {row['case_taxon']!r}")
        taxa.add(row["case_taxon"])
        if row["family"] not in allowed_families:
            raise ValueError(f"row {n} family is absent from the 16-family U3 universe")
        if row["direct_pollen_fate_conflict_evidence"] not in DIRECT:
            raise ValueError(f"row {n} invalid direct conflict evidence class")
        if row["heteranthery_confirmed"] not in HET:
            raise ValueError(f"row {n} U3 case requires confirmed heteranthery")
        if row["case_status"] not in CASE_STATUS:
            raise ValueError(f"row {n} invalid case_status")
        if row["matched_control_status"] not in CONTROL_STATUS:
            raise ValueError(f"row {n} invalid matched_control_status")
        if (
            row["case_status"] == "SOURCE_RESOLVED_NOT_MATCHED"
            and row["matched_control_status"] != "CONTROL_NOT_REGISTERED"
        ):
            raise ValueError(f"row {n} unmatched case cannot claim a registered control")
        if (
            row["case_status"] == "MATCHED_CONTROL_REGISTERED"
            and row["matched_control_status"] != "CONTROL_REGISTERED"
        ):
            raise ValueError(f"row {n} matched case requires CONTROL_REGISTERED")

    return rows


def build_u3_case_readout(case_path: Path, universe_path: Path) -> dict:
    rows = load_u3_case_candidates(case_path, universe_path)
    return {
        "analysis": "balance_plant_u3_species_case_candidates",
        "n_source_resolved_cases": len(rows),
        "n_families_represented": len({r["family"] for r in rows}),
        "n_direct_conflict_cases": sum(
            r["direct_pollen_fate_conflict_evidence"] == "true" for r in rows
        ),
        "n_partial_conflict_cases": sum(
            r["direct_pollen_fate_conflict_evidence"] == "partial" for r in rows
        ),
        "n_matched_control_cases": sum(
            r["matched_control_status"] == "CONTROL_REGISTERED" for r in rows
        ),
        "confirmatory_case_control_ready": all(
            r["matched_control_status"] == "CONTROL_REGISTERED" for r in rows
        ),
        "claim_ceiling": (
            "source_resolved_heteranthery_cases_only_not_case_control_"
            "not_prevalence_not_historical_causation"
        ),
    }

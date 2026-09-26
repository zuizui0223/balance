"""Fail-closed matched-control receipts for U3 heteranthery cases."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .plant_u3_cases import load_u3_case_candidates


FIELDS = (
    "pair_id",
    "pair_role",
    "case_family",
    "case_taxon",
    "case_source_id",
    "control_taxon",
    "control_source_id",
    "match_level",
    "phylogenetic_basis",
    "animal_pollination_eligible",
    "heteranthery_absence_confirmed",
    "selection_status",
    "tie_break_used",
    "predictor_blinding_status",
    "notes",
)

PAIR_ROLE = {"PRIMARY", "SENSITIVITY"}
MATCH_LEVEL = {"CONGENERIC", "SAME_TRIBE_SUBFAMILY", "SAME_FAMILY"}
SELECTION_STATUS = {"SCREENED", "ADJUDICATED", "REJECTED"}
TIE_BREAK = {"NONE", "PHYLOGENETIC_DISTANCE", "SOURCE_QUALITY", "LEXICOGRAPHIC_TAXON"}
BLINDING = {"BLINDED", "UNBLINDED", "UNCERTAIN"}


def _tri_bool(value: str, field: str, row: int) -> bool | None:
    v = value.strip().casefold()
    if v not in {"true", "false", "unresolved"}:
        raise ValueError(
            f"row {row} {field} must be literal true, false, or unresolved"
        )
    if v == "unresolved":
        return None
    return v == "true"


def load_u3_matched_controls(
    path: Path,
    case_path: Path,
    universe_path: Path,
) -> list[dict]:
    cases = load_u3_case_candidates(case_path, universe_path)
    case_by_taxon = {r["case_taxon"]: r for r in cases}

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 matched-control columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("U3 matched-control ledger must contain at least one pair")

    pair_ids: set[str] = set()
    primary_cases: set[str] = set()
    out: list[dict] = []

    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U3 matched-control schema")
        clean = dict(row)
        for field in (
            "pair_id", "pair_role", "case_family", "case_taxon", "case_source_id",
            "control_taxon", "control_source_id", "match_level", "phylogenetic_basis",
            "selection_status", "tie_break_used", "predictor_blinding_status",
        ):
            if not isinstance(clean.get(field), str) or not clean[field].strip():
                raise ValueError(f"row {n} {field} must be frozen")

        if clean["pair_id"] in pair_ids:
            raise ValueError(f"duplicate pair_id {clean['pair_id']!r}")
        pair_ids.add(clean["pair_id"])

        if clean["case_taxon"] not in case_by_taxon:
            raise ValueError(f"row {n} case taxon is absent from U3 case registry")
        case = case_by_taxon[clean["case_taxon"]]
        if clean["case_family"] != case["family"]:
            raise ValueError(f"row {n} case family disagrees with U3 case registry")
        if clean["case_source_id"] != case["primary_source_id"]:
            raise ValueError(f"row {n} case source disagrees with U3 case registry")
        if clean["case_taxon"] == clean["control_taxon"]:
            raise ValueError(f"row {n} case and control taxon must differ")

        if clean["pair_role"] not in PAIR_ROLE:
            raise ValueError(f"row {n} invalid pair_role")
        if clean["match_level"] not in MATCH_LEVEL:
            raise ValueError(f"row {n} invalid match_level")
        if clean["selection_status"] not in SELECTION_STATUS:
            raise ValueError(f"row {n} invalid selection_status")
        if clean["tie_break_used"] not in TIE_BREAK:
            raise ValueError(f"row {n} invalid tie_break_used")
        if clean["predictor_blinding_status"] not in BLINDING:
            raise ValueError(f"row {n} invalid predictor_blinding_status")

        clean["animal_pollination_eligible"] = _tri_bool(
            clean["animal_pollination_eligible"], "animal_pollination_eligible", n
        )
        heteranthery = clean["heteranthery_absence_confirmed"].strip().casefold()
        if heteranthery not in {"true", "false"}:
            raise ValueError(
                f"row {n} heteranthery_absence_confirmed must be literal true or false"
            )
        clean["heteranthery_absence_confirmed"] = heteranthery == "true"

        if clean["pair_role"] == "PRIMARY":
            if clean["case_taxon"] in primary_cases:
                raise ValueError(
                    f"case {clean['case_taxon']!r} has more than one PRIMARY control"
                )
            primary_cases.add(clean["case_taxon"])

        if clean["selection_status"] == "ADJUDICATED":
            if not clean["animal_pollination_eligible"]:
                raise ValueError(f"row {n} adjudicated control must pass animal-pollination eligibility")
            if not clean["heteranthery_absence_confirmed"]:
                raise ValueError(f"row {n} adjudicated control requires confirmed heteranthery absence")
            if clean["predictor_blinding_status"] != "BLINDED":
                raise ValueError(
                    f"row {n} adjudicated control must have been selected before predictor extraction"
                )

        clean["notes"] = (row.get("notes") or "").strip()
        out.append(clean)

    return out


def build_u3_matched_control_readout(
    path: Path,
    case_path: Path,
    universe_path: Path,
) -> dict:
    rows = load_u3_matched_controls(path, case_path, universe_path)
    primary = [r for r in rows if r["pair_role"] == "PRIMARY"]
    registered_primary = [
        r for r in primary if r["selection_status"] in {"SCREENED", "ADJUDICATED"}
    ]
    adjudicated_primary = [
        r for r in primary if r["selection_status"] == "ADJUDICATED"
    ]
    registered_cases = load_u3_case_candidates(case_path, universe_path)
    all_case_taxa = {r["case_taxon"] for r in registered_cases}
    candidate_case_taxa = {r["case_taxon"] for r in registered_primary}
    closed_case_taxa = {r["case_taxon"] for r in adjudicated_primary}
    return {
        "analysis": "balance_plant_u3_matched_control_readout",
        "n_pairs": len(rows),
        "pair_role_counts": dict(sorted(Counter(r["pair_role"] for r in rows).items())),
        "n_registered_primary_pairs": len(registered_primary),
        "n_adjudicated_primary_pairs": len(adjudicated_primary),
        "n_registered_case_taxa": len(all_case_taxa),
        "n_cases_with_registered_primary_control": len(candidate_case_taxa),
        "cases_without_registered_primary_control": sorted(
            all_case_taxa - candidate_case_taxa
        ),
        "screened_control_coverage_complete": all_case_taxa == candidate_case_taxa,
        "n_cases_with_adjudicated_primary_control": len(closed_case_taxa),
        "unmatched_case_taxa": sorted(all_case_taxa - closed_case_taxa),
        "case_control_layer_closed": all_case_taxa == closed_case_taxa,
        "claim_ceiling": (
            "matched_case_control_selection_receipts_only_"
            "not_effect_estimate_not_prevalence_not_historical_causation"
        ),
    }

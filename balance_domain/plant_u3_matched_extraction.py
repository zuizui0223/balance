"""Matched predictor extraction for adjudicated U3 case-control pairs."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .plant_u3_adjudication import load_u3_control_adjudication


FIELDS = (
    "pair_id",
    "taxon_role",
    "taxon",
    "architecture_mode",
    "module_substrate",
    "pollen_fate_conflict_status",
    "conflict_evidence_class",
    "animal_pollination_status",
    "source_id",
    "extraction_status",
    "notes",
)

ROLE = {"CASE", "CONTROL"}
ARCHITECTURE = {
    "WITHIN_FLOWER_DIVISION_OF_LABOUR",
    "AMONG_FLOWER_MODULE_DIVISION",
    "SHARED_INTEGRATED",
    "TEMPORAL_SEPARATION",
    "SPATIAL_SEPARATION",
    "TEMPORAL_AND_SPATIAL_SEPARATION",
    "POLYMORPHIC_OR_MOSAIC",
    "UNRESOLVED",
}
MODULE = {
    "SERIAL_WITHIN_FLOWER",
    "REPEATED_FLOWERS",
    "SINGLE_OR_CONTINUOUS",
    "PREEXISTING_SEPARATE_ORGANS",
    "MULTILEVEL",
    "UNRESOLVED",
}
CONFLICT = {"POSITIVE", "NO_DEMONSTRATED_CONFLICT", "UNRESOLVED"}
POLLINATION = {"CONFIRMED", "UNRESOLVED"}
EXTRACTION = {"EXTRACTED", "PENDING"}


def load_u3_matched_extraction(
    path: Path,
    adjudication_path: Path,
    pair_path: Path,
    case_path: Path,
    universe_path: Path,
) -> list[dict[str, str]]:
    adjudication = load_u3_control_adjudication(
        adjudication_path, pair_path, case_path, universe_path
    )
    passed = {
        r["pair_id"]: r for r in adjudication if r["decision"] == "PASS"
    }

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 matched extraction columns must match canonical order")
        rows = list(reader)

    grouped: dict[str, dict[str, dict[str, str]]] = {}
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U3 matched extraction schema")
        clean = {k: (v or "").strip() for k, v in row.items()}
        pair_id = clean["pair_id"]
        if pair_id not in passed:
            raise ValueError(
                f"row {n} extraction is allowed only for PASS-adjudicated pair {pair_id!r}"
            )
        if clean["taxon_role"] not in ROLE:
            raise ValueError(f"row {n} invalid taxon_role")
        if clean["architecture_mode"] not in ARCHITECTURE:
            raise ValueError(f"row {n} invalid architecture_mode")
        if clean["module_substrate"] not in MODULE:
            raise ValueError(f"row {n} invalid module_substrate")
        if clean["pollen_fate_conflict_status"] not in CONFLICT:
            raise ValueError(f"row {n} invalid pollen_fate_conflict_status")
        if clean["animal_pollination_status"] not in POLLINATION:
            raise ValueError(f"row {n} invalid animal_pollination_status")
        if clean["extraction_status"] not in EXTRACTION:
            raise ValueError(f"row {n} invalid extraction_status")
        if not clean["taxon"] or not clean["source_id"] or not clean["conflict_evidence_class"]:
            raise ValueError(f"row {n} source and taxon fields must be frozen")

        group = grouped.setdefault(pair_id, {})
        if clean["taxon_role"] in group:
            raise ValueError(
                f"pair {pair_id!r} has duplicate {clean['taxon_role']} extraction"
            )
        group[clean["taxon_role"]] = clean

    if set(grouped) != set(passed):
        raise ValueError(
            "U3 matched extraction must cover every PASS-adjudicated pair exactly"
        )

    out: list[dict[str, str]] = []
    for pair_id, roles in sorted(grouped.items()):
        if set(roles) != ROLE:
            raise ValueError(f"pair {pair_id!r} requires exactly CASE and CONTROL rows")

        adj = passed[pair_id]
        if roles["CASE"]["taxon"] != adj["case_taxon"]:
            raise ValueError(f"pair {pair_id!r} case taxon disagrees with adjudication")
        if roles["CONTROL"]["taxon"] != adj["control_taxon"]:
            raise ValueError(f"pair {pair_id!r} control taxon disagrees with adjudication")

        if roles["CASE"]["architecture_mode"] != "WITHIN_FLOWER_DIVISION_OF_LABOUR":
            raise ValueError(
                f"pair {pair_id!r} case architecture must be within-flower division"
            )

        # A nonheterantherous control is not assumed to be globally integrated.
        # It may use another conflict-resolution architecture (for example,
        # among-flower sex-function partitioning) or remain unresolved.
        out.extend((roles["CASE"], roles["CONTROL"]))

    return out


def build_u3_matched_extraction_readout(
    path: Path,
    adjudication_path: Path,
    pair_path: Path,
    case_path: Path,
    universe_path: Path,
) -> dict:
    rows = load_u3_matched_extraction(
        path, adjudication_path, pair_path, case_path, universe_path
    )
    controls = [r for r in rows if r["taxon_role"] == "CONTROL"]
    cases = [r for r in rows if r["taxon_role"] == "CASE"]
    return {
        "analysis": "balance_plant_u3_matched_extraction",
        "n_pairs": len(cases),
        "case_conflict_status_counts": dict(
            sorted(Counter(r["pollen_fate_conflict_status"] for r in cases).items())
        ),
        "control_conflict_status_counts": dict(
            sorted(Counter(r["pollen_fate_conflict_status"] for r in controls).items())
        ),
        "control_architecture_mode_counts": dict(
            sorted(Counter(r["architecture_mode"] for r in controls).items())
        ),
        "control_module_substrate_counts": dict(
            sorted(Counter(r["module_substrate"] for r in controls).items())
        ),
        "n_controls_with_resolved_architecture": sum(
            r["architecture_mode"] != "UNRESOLVED" for r in controls
        ),
        "n_controls_with_resolved_conflict": sum(
            r["pollen_fate_conflict_status"] in {"POSITIVE", "NO_DEMONSTRATED_CONFLICT"}
            for r in controls
        ),
        "matched_conflict_estimand_ready": all(
            r["pollen_fate_conflict_status"] != "UNRESOLVED" for r in controls
        ),
        "claim_ceiling": (
            "matched_source_extraction_only_no_effect_estimate_"
            "until_control_conflict_evidence_is_resolved"
        ),
    }

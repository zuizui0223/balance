"""Cross-surface contract for U3 representative coverage versus Table-S1 provenance."""
from __future__ import annotations

import json
from pathlib import Path

from .plant_u3 import load_u3_universe
from .plant_u3_representative_candidates import build_u3_representative_candidate_readout


ARCHIVAL_FAMILIES = {"Malvaceae", "Bixaceae", "Scrophulariaceae"}
EXPECTED_CANONICAL = {
    "Malvaceae": ("Mollia lepidota", "SOURCE_RESOLVED_INDEPENDENTLY"),
    "Bixaceae": ("Amoreuxia wrightii", "SOURCE_RESOLVED_INDEPENDENTLY"),
    "Scrophulariaceae": (
        "Verbascum phoeniceum",
        "SOURCE_RESOLVED_INDEPENDENTLY_POST_REVIEW",
    ),
}


def load_u3_representative_resolution(
    resolution_path: Path,
    universe_path: Path,
    candidate_path: Path,
) -> dict:
    payload = json.loads(resolution_path.read_text(encoding="utf-8"))
    if payload.get("analysis") != "balance_plant_u3_representative_resolution_v3":
        raise ValueError("U3 representative-resolution analysis id drifted")
    if payload.get("review_doi") != "10.1111/j.1469-8137.2010.03430.x":
        raise ValueError("U3 representative-resolution review DOI drifted")

    universe = load_u3_universe(universe_path)
    if any(
        row["representative_taxa_status"] == "TABLE_S1_REPRESENTATIVE_PENDING"
        for row in universe
    ):
        raise ValueError("canonical U3 representative coverage cannot contain pending rows")

    if payload.get("resolved_family_representatives") != 16:
        raise ValueError("U3 representative resolution must report 16 resolved families")
    if payload.get("pending_independent_representative_families") != []:
        raise ValueError("independent representative coverage must be closed")
    if payload.get("canonical_representative_coverage_closed") is not True:
        raise ValueError("canonical representative coverage must be explicitly closed")

    archival = set(payload.get("exact_table_s1_identity_unrecovered_families", []))
    if archival != ARCHIVAL_FAMILIES:
        raise ValueError("exact Table-S1 archival-open family set drifted")
    if payload.get("exact_table_s1_identity_closed") is not False:
        raise ValueError("exact Table-S1 identity must remain explicitly open")
    if payload.get("exact_table_s1_identity_blocks_current_u3_analysis") is not False:
        raise ValueError("archival Table-S1 identity must not be a current U3 analysis gate")

    by_family = {row["family"]: row for row in universe}
    resolutions = payload.get("resolutions")
    if not isinstance(resolutions, dict):
        raise ValueError("resolution payload requires family resolutions")

    for family, (taxon, status) in EXPECTED_CANONICAL.items():
        row = by_family[family]
        if row["representative_taxa"] != taxon:
            raise ValueError(f"{family} canonical representative drifted")
        if row["representative_taxa_status"] != status:
            raise ValueError(f"{family} canonical representative provenance drifted")
        rec = resolutions.get(family)
        if not isinstance(rec, dict):
            raise ValueError(f"{family} missing from representative-resolution receipt")
        if rec.get("representative") != taxon or rec.get("status") != status:
            raise ValueError(f"{family} resolution receipt disagrees with canonical universe")
        if rec.get("table_s1_identity_claim") is not False:
            raise ValueError(f"{family} must not claim exact Table-S1 identity")

    candidate = build_u3_representative_candidate_readout(candidate_path)
    if set(candidate["open_families"]) != ARCHIVAL_FAMILIES:
        raise ValueError("archival candidate search must remain open for the three exact Table-S1 identities")

    return payload


def build_u3_representative_resolution_readout(
    resolution_path: Path,
    universe_path: Path,
    candidate_path: Path,
) -> dict:
    payload = load_u3_representative_resolution(
        resolution_path, universe_path, candidate_path
    )
    return {
        "analysis": "balance_u3_representative_resolution_contract",
        "canonical_representative_coverage_closed": True,
        "n_canonical_representative_families": 16,
        "exact_table_s1_identity_closed": False,
        "exact_table_s1_identity_unrecovered_families": sorted(ARCHIVAL_FAMILIES),
        "exact_table_s1_identity_blocks_current_u3_analysis": False,
        "claim_ceiling": payload["claim_ceiling"],
    }

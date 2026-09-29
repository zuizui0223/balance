"""Production-source identity map for U1 taxa outside the reliability first-20."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .plant_u1 import load_u1_universe


FIELDS = (
    "universe_record_id",
    "dependency_group",
    "taxon_raw",
    "figshare_article_ids",
    "analysis_rows",
    "source_identity_status",
    "source_content_status",
    "mapping_basis",
    "notes",
)

EXPECTED_IDS = {f"U1_{i:03d}" for i in range(21, 48)}
IDENTITY_STATUS = "MAPPED_PRIMARY_FROM_REVIEW_DATA"
MAPPING_BASIS = "DIRECT_FIGSHARE_ANALYSIS_STUDY_JOIN"
CONTENT_STATUS = {"CONTENT_RETRIEVAL_PENDING", "SOURCE_READY_PRIMARY"}


def load_u1_production_source_map(path: Path, universe_path: Path) -> list[dict[str, str]]:
    universe = load_u1_universe(universe_path)
    universe_by_id = {r["universe_record_id"]: r for r in universe}

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U1 production-source columns must match canonical order")
        rows = list(reader)

    if len(rows) != len(EXPECTED_IDS):
        raise ValueError("U1 production-source map must contain exactly U1_021..U1_047")

    seen = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U1 production-source schema")
        clean = {k: (v or "").strip() for k, v in row.items()}
        row.update(clean)
        uid = clean["universe_record_id"]
        if uid not in EXPECTED_IDS or uid in seen:
            raise ValueError(f"row {n} universe_record_id must be unique within U1_021..U1_047")
        seen.add(uid)
        canonical = universe_by_id.get(uid)
        if canonical is None:
            raise ValueError(f"row {n} source map references absent U1 record")
        if clean["dependency_group"] != canonical["dependency_group"]:
            raise ValueError(f"row {n} dependency_group disagrees with U1 universe")
        if clean["taxon_raw"] != canonical["taxon_raw"]:
            raise ValueError(f"row {n} taxon_raw disagrees with U1 universe")
        if clean["source_identity_status"] != IDENTITY_STATUS:
            raise ValueError(f"row {n} source identity must come from direct review data")
        if clean["source_content_status"] not in CONTENT_STATUS:
            raise ValueError(f"row {n} invalid source_content_status")
        if clean["mapping_basis"] != MAPPING_BASIS:
            raise ValueError(f"row {n} mapping_basis must remain frozen")
        ids = clean["figshare_article_ids"].split(";")
        if not ids or any(not x.isdigit() for x in ids) or len(ids) != len(set(ids)):
            raise ValueError(f"row {n} figshare_article_ids must be unique numeric IDs")
        try:
            analysis_rows = int(clean["analysis_rows"])
        except ValueError as exc:
            raise ValueError(f"row {n} analysis_rows must be integer") from exc
        if analysis_rows <= 0:
            raise ValueError(f"row {n} analysis_rows must be positive")
        expected_universe_status = (
            "RESOLVED_PRIMARY"
            if clean["source_content_status"] == "SOURCE_READY_PRIMARY"
            else "MAPPED_PRIMARY_CONTENT_PENDING"
        )
        if canonical["primary_source_status"] != expected_universe_status:
            raise ValueError(
                f"row {n} U1 universe source status disagrees with production-source map"
            )

    if seen != EXPECTED_IDS:
        raise ValueError("U1 production-source map does not cover U1_021..U1_047 exactly")
    return rows


def build_u1_production_source_readout(path: Path, universe_path: Path) -> dict:
    rows = load_u1_production_source_map(path, universe_path)
    content = Counter(r["source_content_status"] for r in rows)
    multi = sorted(
        r["taxon_raw"] for r in rows if ";" in r["figshare_article_ids"]
    )
    return {
        "analysis": "balance_plant_u1_production_source_map_v1",
        "n_mapped_taxa": len(rows),
        "n_source_ready_primary": content.get("SOURCE_READY_PRIMARY", 0),
        "n_content_retrieval_pending": content.get("CONTENT_RETRIEVAL_PENDING", 0),
        "multi_study_taxa": multi,
        "all_source_identities_mapped": len(rows) == 27,
        "all_source_content_ready": content.get("CONTENT_RETRIEVAL_PENDING", 0) == 0,
        "claim_ceiling": (
            "review_primary_study_identity_mapping_only_"
            "content_pending_rows_not_ready_for_production_coding"
        ),
    }

"""Fail-closed registry for targeted U1 structural-class recovery."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "queue_id",
    "universe_record_id",
    "dependency_group",
    "primary_source",
    "priority",
    "architecture_opportunity",
    "current_conflict_state",
    "current_architecture_state",
    "targeted_question",
    "promotion_gate",
    "queue_status",
    "claim_ceiling",
    "notes",
)

PRIORITIES = {"HIGH", "MEDIUM_HIGH", "MEDIUM", "SPECIFICITY"}
QUEUE_STATUS = {"TARGETED_FULL_TEXT_ADJUDICATION"}
CLAIM_CEILING = {"DISCOVERY_QUEUE_ONLY_NO_PRIMARY_MODEL_PROMOTION"}
UNADJUDICATED = {"UNADJUDICATED"}


def load_u1_structural_recovery_queue(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U1 structural-recovery queue columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("U1 structural-recovery queue must contain at least one candidate")

    seen_queue: set[str] = set()
    seen_universe: set[str] = set()
    out: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside canonical schema")
        clean = {key: (row.get(key) or "").strip() for key in FIELDS}
        for key in FIELDS:
            if not clean[key]:
                raise ValueError(f"row {row_number} {key} must be non-empty")

        if clean["queue_id"] in seen_queue:
            raise ValueError(f"duplicate queue_id {clean['queue_id']!r}")
        seen_queue.add(clean["queue_id"])

        if clean["universe_record_id"] in seen_universe:
            raise ValueError(
                f"duplicate universe_record_id {clean['universe_record_id']!r}"
            )
        seen_universe.add(clean["universe_record_id"])

        if clean["priority"] not in PRIORITIES:
            raise ValueError(f"row {row_number} invalid priority")
        if clean["queue_status"] not in QUEUE_STATUS:
            raise ValueError(f"row {row_number} invalid queue_status")
        if clean["claim_ceiling"] not in CLAIM_CEILING:
            raise ValueError(f"row {row_number} invalid claim_ceiling")
        if clean["current_conflict_state"] not in UNADJUDICATED:
            raise ValueError(
                f"row {row_number} queue cannot pre-adjudicate conflict state"
            )
        if clean["current_architecture_state"] not in UNADJUDICATED:
            raise ValueError(
                f"row {row_number} queue cannot pre-adjudicate architecture state"
            )
        if not clean["universe_record_id"].startswith("U1_"):
            raise ValueError(f"row {row_number} must originate in the frozen U1 universe")

        out.append(clean)

    return out


def build_u1_structural_recovery_readout(path: Path) -> dict:
    rows = load_u1_structural_recovery_queue(path)
    return {
        "analysis": "balance_u1_structural_class_recovery_queue",
        "n_candidates": len(rows),
        "priority_counts": dict(sorted(Counter(r["priority"] for r in rows).items())),
        "universe_record_ids": [r["universe_record_id"] for r in rows],
        "all_conflict_states_unadjudicated": all(
            r["current_conflict_state"] == "UNADJUDICATED" for r in rows
        ),
        "all_architecture_states_unadjudicated": all(
            r["current_architecture_state"] == "UNADJUDICATED" for r in rows
        ),
        "primary_model_promotion_allowed": False,
        "claim_ceiling": "targeted_retrieval_queue_only_not_confirmatory_evidence",
    }



SCREEN_FIELDS = (
    "queue_id",
    "universe_record_id",
    "dependency_group",
    "screen_status",
    "conflict_receipt",
    "routing_receipt",
    "promotion_decision",
    "reason_code",
    "source_basis",
    "claim_ceiling",
    "notes",
)

SCREEN_STATUS = {"SOURCE_SCREEN_COMPLETE"}
PROMOTION_DECISIONS = {"DO_NOT_PROMOTE_CURRENT_SOURCE"}
SCREEN_CLAIM_CEILING = {"SOURCE_SCREEN_ONLY_NOT_INDEPENDENT_ADJUDICATION"}


def load_u1_structural_recovery_screen(path: Path) -> list[dict[str, str]]:
    """Load source-screen decisions without allowing confirmatory promotion."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != SCREEN_FIELDS:
            raise ValueError("U1 structural-recovery screen columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("U1 structural-recovery screen must contain at least one row")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside canonical schema")
        clean = {key: (row.get(key) or "").strip() for key in SCREEN_FIELDS}
        for key in SCREEN_FIELDS:
            if not clean[key]:
                raise ValueError(f"row {row_number} {key} must be non-empty")

        if clean["queue_id"] in seen:
            raise ValueError(f"duplicate queue_id {clean['queue_id']!r}")
        seen.add(clean["queue_id"])

        if clean["screen_status"] not in SCREEN_STATUS:
            raise ValueError(f"row {row_number} invalid screen_status")
        if clean["promotion_decision"] not in PROMOTION_DECISIONS:
            raise ValueError(
                f"row {row_number} source screen cannot promote a candidate"
            )
        if clean["claim_ceiling"] not in SCREEN_CLAIM_CEILING:
            raise ValueError(f"row {row_number} invalid screen claim ceiling")
        if clean["conflict_receipt"] == "POSITIVE":
            raise ValueError(
                f"row {row_number} source screen cannot independently adjudicate conflict"
            )

        out.append(clean)

    return out


def build_u1_structural_recovery_screen_readout(path: Path) -> dict:
    rows = load_u1_structural_recovery_screen(path)
    return {
        "analysis": "balance_u1_structural_recovery_source_screen",
        "n_screened": len(rows),
        "n_promoted": sum(
            r["promotion_decision"] != "DO_NOT_PROMOTE_CURRENT_SOURCE" for r in rows
        ),
        "reason_code_counts": dict(
            sorted(Counter(r["reason_code"] for r in rows).items())
        ),
        "all_source_screen_only": all(
            r["claim_ceiling"] == "SOURCE_SCREEN_ONLY_NOT_INDEPENDENT_ADJUDICATION"
            for r in rows
        ),
        "primary_model_promotion_allowed": False,
    }

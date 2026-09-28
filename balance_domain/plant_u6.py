"""Blinded reconstruction contract for the BALANCE U6 pollen-theft universe."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


FIELDS = (
    "reference_id",
    "reference_citation",
    "reference_year",
    "reference_type_status",
    "plant_taxon_raw",
    "dependency_group",
    "primary_source_status",
    "inclusion_status",
    "exclusion_reason",
    "classification_basis",
    "notes",
)

FORBIDDEN_PASS1_FIELDS = {
    "architecture_mode",
    "heteranthery_status",
    "dichogamy_status",
    "herkogamy_status",
    "poricidal_anther_status",
    "module_substrate",
    "conflict_timing_geometry",
    "conflict_spatial_geometry",
}

REFERENCE_STATUS = {
    "EMPIRICAL_POLLEN_THEFT_CANDIDATE",
    "EMPIRICAL_BUT_NOT_POLLEN_THEFT",
    "REVIEW_OR_THEORY",
    "NONPLANT_OR_METHODS",
    "UNRESOLVED",
}
INCLUSION_STATUS = {"INCLUDE", "EXCLUDE", "UNRESOLVED"}
PRIMARY_SOURCE_STATUS = {"RESOLVED", "UNRESOLVED", "NOT_REQUIRED"}


def load_u6_anchor(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "BALANCE_PLANT_U6_REVIEW_ANCHOR_V1":
        raise ValueError("U6 anchor schema mismatch")
    forbidden = set(data.get("forbidden_during_pass1", []))
    if forbidden != FORBIDDEN_PASS1_FIELDS:
        raise ValueError("U6 Pass-1 forbidden-field contract drifted")
    if data.get("primary_model_admission") != (
        "FORBIDDEN_UNTIL_PASS2_INDEPENDENT_CODING_AND_DEPENDENCE_AUDIT"
    ):
        raise ValueError("U6 primary-model admission must remain closed")
    return data


def load_u6_reference_classification(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        if fields != FIELDS:
            extras = set(fields) & FORBIDDEN_PASS1_FIELDS
            if extras:
                raise ValueError(
                    f"U6 Pass-1 classification contains forbidden architecture fields: {sorted(extras)}"
                )
            raise ValueError("U6 reference classification columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("U6 reference classification must contain at least one row")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside canonical schema")
        clean = {key: (row.get(key) or "").strip() for key in FIELDS}
        if not clean["reference_id"] or not clean["reference_citation"]:
            raise ValueError(f"row {row_number} reference identity must be non-empty")
        if clean["reference_id"] in seen:
            raise ValueError(f"duplicate U6 reference_id {clean['reference_id']!r}")
        seen.add(clean["reference_id"])

        if clean["reference_type_status"] not in REFERENCE_STATUS:
            raise ValueError(f"row {row_number} invalid reference_type_status")
        if clean["primary_source_status"] not in PRIMARY_SOURCE_STATUS:
            raise ValueError(f"row {row_number} invalid primary_source_status")
        if clean["inclusion_status"] not in INCLUSION_STATUS:
            raise ValueError(f"row {row_number} invalid inclusion_status")
        if clean["classification_basis"] != "ANCHOR_REVIEW_REFERENCE_CLASSIFICATION":
            raise ValueError(f"row {row_number} invalid classification_basis")
        out.append(clean)
    return out



def build_u6_reference_readout(path: Path) -> dict:
    """Summarize Pass-1 reconstruction progress without opening architecture fields."""
    rows = load_u6_reference_classification(path)
    status_counts = Counter(r["reference_type_status"] for r in rows)
    inclusion_counts = Counter(r["inclusion_status"] for r in rows)
    candidate_ids = [
        r["reference_id"]
        for r in rows
        if r["reference_type_status"] == "EMPIRICAL_POLLEN_THEFT_CANDIDATE"
    ]
    included = [r["reference_id"] for r in rows if r["inclusion_status"] == "INCLUDE"]
    return {
        "analysis": "balance_plant_u6_pass1_reference_reconstruction",
        "n_references": len(rows),
        "reference_status_counts": dict(sorted(status_counts.items())),
        "inclusion_status_counts": dict(sorted(inclusion_counts.items())),
        "pollen_theft_candidate_reference_ids": candidate_ids,
        "included_reference_ids": included,
        "n_included": len(included),
        "architecture_fields_open": False,
        "pass2_open": False,
        "claim_ceiling": "pass1_reference_reconstruction_only",
    }



def build_u6_multi_batch_readout(paths: list[Path]) -> dict:
    """Combine frozen Pass-1 batches while enforcing unique ordered reference IDs."""
    if not paths:
        raise ValueError("U6 multi-batch readout requires at least one batch")

    rows: list[dict[str, str]] = []
    for path in paths:
        rows.extend(load_u6_reference_classification(path))

    ids = [row["reference_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("U6 Pass-1 batches contain duplicate reference IDs")

    def _number(reference_id: str) -> int:
        prefix = "U6_REF_"
        if not reference_id.startswith(prefix):
            raise ValueError(f"invalid U6 reference_id {reference_id!r}")
        try:
            return int(reference_id[len(prefix):])
        except ValueError as exc:
            raise ValueError(f"invalid U6 reference_id {reference_id!r}") from exc

    numbers = [_number(reference_id) for reference_id in ids]
    if numbers != list(range(numbers[0], numbers[0] + len(numbers))):
        raise ValueError("U6 Pass-1 batch reference IDs must be consecutive in supplied order")

    status_counts = Counter(row["reference_type_status"] for row in rows)
    inclusion_counts = Counter(row["inclusion_status"] for row in rows)
    candidates = [
        row["reference_id"]
        for row in rows
        if row["reference_type_status"] == "EMPIRICAL_POLLEN_THEFT_CANDIDATE"
    ]
    return {
        "analysis": "balance_plant_u6_pass1_multibatch_reconstruction",
        "n_references": len(rows),
        "first_reference_id": ids[0],
        "last_reference_id": ids[-1],
        "reference_status_counts": dict(sorted(status_counts.items())),
        "inclusion_status_counts": dict(sorted(inclusion_counts.items())),
        "pollen_theft_candidate_reference_ids": candidates,
        "n_candidates": len(candidates),
        "n_included": sum(row["inclusion_status"] == "INCLUDE" for row in rows),
        "architecture_fields_open": False,
        "pass2_open": False,
        "claim_ceiling": "pass1_reference_reconstruction_only",
    }



CANDIDATE_FIELDS = (
    "adjudication_id",
    "reference_id",
    "plant_taxon",
    "dependency_group",
    "primary_source_status",
    "qualifying_receipt",
    "decision",
    "reason_code",
    "source_basis",
    "notes",
)

QUALIFYING_RECEIPTS = {
    "DIRECT_REMOVAL_LOW_DEPOSITION",
    "DIRECT_REMOVAL_FITNESS_COST",
    "DIRECT_CONSUMPTION_AVAILABLE_POLLEN_LOSS",
    "DIRECT_POLLEN_ROBBING_NO_POLLINATION",
    "NONE",
    "UNRESOLVED",
}
CANDIDATE_DECISIONS = {"INCLUDE", "EXCLUDE", "RETAIN_UNRESOLVED"}
CANDIDATE_PRIMARY_STATUS = {"RESOLVED", "PARTIAL", "UNRESOLVED"}


def load_u6_candidate_adjudication(path: Path) -> list[dict[str, str]]:
    """Load taxon-level candidate decisions while keeping Pass-2 architecture closed."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        if fields != CANDIDATE_FIELDS:
            extras = set(fields) & FORBIDDEN_PASS1_FIELDS
            if extras:
                raise ValueError(
                    f"U6 candidate adjudication contains forbidden architecture fields: {sorted(extras)}"
                )
            raise ValueError("U6 candidate adjudication columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("U6 candidate adjudication must contain at least one row")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside canonical schema")
        clean = {key: (row.get(key) or "").strip() for key in CANDIDATE_FIELDS}
        for key in CANDIDATE_FIELDS:
            if not clean[key]:
                raise ValueError(f"row {row_number} {key} must be non-empty")

        if clean["adjudication_id"] in seen:
            raise ValueError(f"duplicate adjudication_id {clean['adjudication_id']!r}")
        seen.add(clean["adjudication_id"])
        if not clean["reference_id"].startswith("U6_REF_"):
            raise ValueError(f"row {row_number} invalid reference_id")
        if clean["primary_source_status"] not in CANDIDATE_PRIMARY_STATUS:
            raise ValueError(f"row {row_number} invalid primary_source_status")
        if clean["qualifying_receipt"] not in QUALIFYING_RECEIPTS:
            raise ValueError(f"row {row_number} invalid qualifying_receipt")
        if clean["decision"] not in CANDIDATE_DECISIONS:
            raise ValueError(f"row {row_number} invalid decision")

        if clean["decision"] == "INCLUDE":
            if clean["primary_source_status"] != "RESOLVED":
                raise ValueError(f"row {row_number} INCLUDE requires RESOLVED primary source")
            if clean["qualifying_receipt"] in {"NONE", "UNRESOLVED"}:
                raise ValueError(f"row {row_number} INCLUDE requires a qualifying receipt")
            if clean["plant_taxon"] == "UNRESOLVED" or clean["dependency_group"] == "UNRESOLVED":
                raise ValueError(f"row {row_number} INCLUDE requires frozen taxon/dependency group")

        if clean["decision"] == "EXCLUDE" and clean["reason_code"] == "UNRESOLVED":
            raise ValueError(f"row {row_number} EXCLUDE requires a frozen reason")
        out.append(clean)

    return out


def build_u6_candidate_adjudication_readout(path: Path) -> dict:
    rows = load_u6_candidate_adjudication(path)
    decision_counts = Counter(row["decision"] for row in rows)
    included = [row for row in rows if row["decision"] == "INCLUDE"]
    dependencies = sorted({row["dependency_group"] for row in included})
    return {
        "analysis": "balance_plant_u6_candidate_primary_source_adjudication",
        "n_adjudication_rows": len(rows),
        "decision_counts": dict(sorted(decision_counts.items())),
        "n_included_rows": len(included),
        "n_included_dependency_groups": len(dependencies),
        "included_dependency_groups": dependencies,
        "pass2_open": False,
        "architecture_fields_open": False,
        "claim_ceiling": "pass1_candidate_adjudication_only",
    }



def build_u6_pass1_freeze(
    reference_paths: list[Path],
    adjudication_paths: list[Path],
) -> dict:
    """Close U6 Pass 1 only after the conflict-first universe is fully reconstructed.

    RETAIN_UNRESOLVED is explicit evidence-ceiling missingness and is not silently
    promoted or replaced. Pass 2 opens only for dependency groups supported by at
    least one INCLUDE adjudication.
    """
    if not reference_paths or not adjudication_paths:
        raise ValueError("U6 Pass-1 freeze requires reference and adjudication paths")

    references: list[dict[str, str]] = []
    for path in reference_paths:
        references.extend(load_u6_reference_classification(path))

    reference_ids = [row["reference_id"] for row in references]
    expected_ids = [f"U6_REF_{i:03d}" for i in range(1, 158)]
    if reference_ids != expected_ids:
        raise ValueError("U6 Pass-1 freeze requires the complete ordered 157-reference universe")
    if any(row["reference_type_status"] == "UNRESOLVED" for row in references):
        raise ValueError("U6 Pass-1 freeze cannot retain unresolved reference classifications")

    candidate_ids = {
        row["reference_id"]
        for row in references
        if row["reference_type_status"] == "EMPIRICAL_POLLEN_THEFT_CANDIDATE"
    }

    adjudications: list[dict[str, str]] = []
    for path in adjudication_paths:
        adjudications.extend(load_u6_candidate_adjudication(path))

    adjudicated_ids = {row["reference_id"] for row in adjudications}
    missing = sorted(candidate_ids - adjudicated_ids)
    extra = sorted(adjudicated_ids - candidate_ids)
    if missing:
        raise ValueError(f"U6 candidate references lack adjudication: {missing}")
    if extra:
        raise ValueError(f"U6 adjudication exists for non-candidate references: {extra}")

    by_reference: dict[str, list[dict[str, str]]] = {}
    for row in adjudications:
        by_reference.setdefault(row["reference_id"], []).append(row)

    included_reference_ids: list[str] = []
    excluded_reference_ids: list[str] = []
    retained_unresolved_reference_ids: list[str] = []
    for reference_id in sorted(candidate_ids):
        decisions = {row["decision"] for row in by_reference[reference_id]}
        if "INCLUDE" in decisions:
            included_reference_ids.append(reference_id)
        elif "RETAIN_UNRESOLVED" in decisions:
            retained_unresolved_reference_ids.append(reference_id)
        elif decisions == {"EXCLUDE"}:
            excluded_reference_ids.append(reference_id)
        else:
            raise ValueError(
                f"U6 candidate {reference_id!r} has an unsupported decision mixture: "
                f"{sorted(decisions)}"
            )

    included_rows = [row for row in adjudications if row["decision"] == "INCLUDE"]
    included_dependency_groups = sorted({row["dependency_group"] for row in included_rows})
    if not included_dependency_groups:
        raise ValueError("U6 Pass-1 freeze produced no included dependency groups")

    source_refs_by_dependency: dict[str, list[str]] = {}
    for row in included_rows:
        source_refs_by_dependency.setdefault(row["dependency_group"], []).append(
            row["reference_id"]
        )
    source_refs_by_dependency = {
        group: sorted(set(reference_ids))
        for group, reference_ids in sorted(source_refs_by_dependency.items())
    }

    return {
        "analysis": "balance_plant_u6_pass1_freeze",
        "status": "PASS1_CLOSED_PASS2_CODING_OPEN",
        "n_references": len(references),
        "n_candidate_references": len(candidate_ids),
        "n_candidate_adjudication_rows": len(adjudications),
        "n_included_reference_ids": len(included_reference_ids),
        "n_excluded_reference_ids": len(excluded_reference_ids),
        "n_retained_unresolved_reference_ids": len(retained_unresolved_reference_ids),
        "included_reference_ids": included_reference_ids,
        "excluded_reference_ids": excluded_reference_ids,
        "retained_unresolved_reference_ids": retained_unresolved_reference_ids,
        "n_included_dependency_groups": len(included_dependency_groups),
        "included_dependency_groups": included_dependency_groups,
        "source_reference_ids_by_dependency_group": source_refs_by_dependency,
        "architecture_used_for_pass1_admission": False,
        "pass2_open": True,
        "primary_model_admission": False,
        "claim_ceiling": (
            "pass1_conflict_first_universe_closed_pass2_architecture_coding_open_"
            "not_confirmatory_model_ready"
        ),
    }

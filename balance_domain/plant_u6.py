"""Blinded reconstruction contract for the BALANCE U6 pollen-theft universe."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from .plant_macro import MODULE_SUBSTRATE, RESOLUTION, SPATIAL, TIMING


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
        "status": "PASS1_CLOSED_PASS2_SOURCE_RECOVERY_OPEN",
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
        "pass2_source_recovery_open": True,
        "pass2_coding_open": False,
        "primary_model_admission": False,
        "claim_ceiling": (
            "pass1_conflict_first_universe_closed_pass2_source_recovery_open_"
            "architecture_coding_locked_not_confirmatory_model_ready"
        ),
    }



PASS1_FREEZE_SCHEMA = "BALANCE_PLANT_U6_PASS1_FREEZE_V1"


def load_u6_pass1_freeze_manifest(path: Path) -> dict:
    """Load the frozen U6 Pass-1 manifest and keep confirmatory admission closed."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != PASS1_FREEZE_SCHEMA:
        raise ValueError("U6 Pass-1 freeze manifest schema mismatch")
    if data.get("status") != "PASS1_CLOSED_PASS2_SOURCE_RECOVERY_OPEN":
        raise ValueError("U6 Pass-1 freeze manifest must declare Pass 1 closed and source recovery open")
    contract = data.get("pass1_contract", {})
    if contract.get("n_anchor_review_references") != 157:
        raise ValueError("U6 Pass-1 freeze must retain all 157 anchor references")
    if contract.get("n_unresolved_reference_classifications") != 0:
        raise ValueError("U6 Pass-1 freeze cannot retain unresolved reference classifications")
    if contract.get("architecture_used_for_admission") is not False:
        raise ValueError("U6 Pass-1 admission must remain architecture-blind")
    if data.get("pass2", {}).get("source_recovery_open") is not True:
        raise ValueError("U6 Pass-1 freeze must explicitly open Pass-2 source recovery")
    if data.get("pass2", {}).get("coding_open") is not False:
        raise ValueError("U6 Pass-2 coding must remain closed until the source packet is frozen")
    if data.get("pass2", {}).get("primary_model_admission") is not False:
        raise ValueError("U6 Pass-1 freeze cannot directly license the primary model")

    groups = data.get("included_dependency_groups")
    if not isinstance(groups, list) or not groups:
        raise ValueError("U6 Pass-1 freeze requires included dependency groups")
    if groups != sorted(set(groups)):
        raise ValueError("U6 included dependency groups must be unique and sorted")

    source_map = data.get("source_reference_ids_by_dependency_group")
    if not isinstance(source_map, dict) or set(source_map) != set(groups):
        raise ValueError("U6 source-reference map must cover every included dependency group")
    return data


def validate_u6_pass1_freeze_manifest(
    manifest_path: Path,
    reference_paths: list[Path],
    adjudication_paths: list[Path],
) -> dict:
    """Require the frozen manifest to equal the executable Pass-1 reconstruction."""
    manifest = load_u6_pass1_freeze_manifest(manifest_path)
    live = build_u6_pass1_freeze(reference_paths, adjudication_paths)

    for key in (
        "included_reference_ids",
        "excluded_reference_ids",
        "retained_unresolved_reference_ids",
    ):
        expected = manifest["candidate_reference_outcomes"][key]
        if expected != live[key]:
            raise ValueError(f"U6 Pass-1 freeze manifest drift for {key}")

    if manifest["included_dependency_groups"] != live["included_dependency_groups"]:
        raise ValueError("U6 Pass-1 freeze manifest dependency groups drifted")
    if (
        manifest["source_reference_ids_by_dependency_group"]
        != live["source_reference_ids_by_dependency_group"]
    ):
        raise ValueError("U6 Pass-1 freeze source-reference mapping drifted")
    return live


PASS2_FIELDS = (
    "dependency_group",
    "source_reference_ids",
    "coder_id",
    "architecture_mode",
    "module_substrate",
    "conflict_timing_geometry",
    "conflict_spatial_geometry",
    "coding_status",
    "notes",
)

PASS2_CODING_STATUS = {"UNSTARTED", "CODED"}


def load_u6_pass2_double_coding(path: Path, freeze_manifest_path: Path) -> list[dict[str, str]]:
    """Load U6 Pass-2 architecture/predictor coding only for frozen Pass-1 groups."""
    manifest = load_u6_pass1_freeze_manifest(freeze_manifest_path)
    expected_groups = set(manifest["included_dependency_groups"])
    source_map = manifest["source_reference_ids_by_dependency_group"]

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != PASS2_FIELDS:
            raise ValueError("U6 Pass-2 coding columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("U6 Pass-2 coding worksheet must contain rows")

    grouped: dict[str, list[dict[str, str]]] = {}
    coder_ids: set[str] = set()
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside U6 Pass-2 schema")
        clean = {key: (row.get(key) or "").strip() for key in PASS2_FIELDS}
        for key in PASS2_FIELDS[:-1]:
            if not clean[key]:
                raise ValueError(f"row {row_number} {key} must be non-empty")

        group = clean["dependency_group"]
        if group not in expected_groups:
            raise ValueError(f"row {row_number} non-frozen U6 dependency group {group!r}")
        expected_sources = ";".join(source_map[group])
        if clean["source_reference_ids"] != expected_sources:
            raise ValueError(f"row {row_number} source references disagree with Pass-1 freeze")

        key = (group, clean["coder_id"])
        if key in seen:
            raise ValueError(f"duplicate U6 Pass-2 group/coder pair {key!r}")
        seen.add(key)
        coder_ids.add(clean["coder_id"])
        grouped.setdefault(group, []).append(clean)

        if clean["architecture_mode"] not in RESOLUTION - {"NA"}:
            raise ValueError(f"row {row_number} invalid architecture_mode")
        if clean["module_substrate"] not in MODULE_SUBSTRATE:
            raise ValueError(f"row {row_number} invalid module_substrate")
        if clean["conflict_timing_geometry"] not in TIMING:
            raise ValueError(f"row {row_number} invalid conflict_timing_geometry")
        if clean["conflict_spatial_geometry"] not in SPATIAL:
            raise ValueError(f"row {row_number} invalid conflict_spatial_geometry")
        if clean["coding_status"] not in PASS2_CODING_STATUS:
            raise ValueError(f"row {row_number} invalid coding_status")

        if manifest["pass2"].get("coding_open") is not True:
            if clean["coding_status"] != "UNSTARTED":
                raise ValueError(
                    f"row {row_number} U6 Pass-2 coding is locked until source recovery freezes"
                )

        if clean["coding_status"] == "UNSTARTED":
            if any(
                clean[field] != "UNRESOLVED"
                for field in (
                    "architecture_mode",
                    "module_substrate",
                    "conflict_timing_geometry",
                    "conflict_spatial_geometry",
                )
            ):
                raise ValueError(
                    f"row {row_number} UNSTARTED coding must remain entirely UNRESOLVED"
                )
        clean["notes"] = (row.get("notes") or "").strip()
        out.append(clean)

    if len(coder_ids) != 2:
        raise ValueError("U6 Pass-2 worksheet requires exactly two independent coder IDs")
    if set(grouped) != expected_groups:
        raise ValueError("U6 Pass-2 worksheet must cover every frozen dependency group")
    if any(len(rows) != 2 for rows in grouped.values()):
        raise ValueError("each U6 Pass-2 dependency group requires exactly two coder rows")
    return out



U6_DEPENDENCE_FIELDS = (
    "u6_dependency_group",
    "overlap_universe",
    "overlap_record_id",
    "dependence_block",
    "analysis_action",
    "notes",
)

U6_ANALYSIS_ACTIONS = {"U6_ONLY", "SHARED_SPECIES_BLOCK", "SHARED_TAXON_CONCEPT_BLOCK"}


def load_u6_cross_universe_dependence(path: Path, freeze_manifest_path: Path) -> list[dict[str, str]]:
    """Validate one dependence row for every frozen U6 dependency group."""
    manifest = load_u6_pass1_freeze_manifest(freeze_manifest_path)
    expected_groups = set(manifest["included_dependency_groups"])

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != U6_DEPENDENCE_FIELDS:
            raise ValueError("U6 dependence columns must match canonical order")
        rows = list(reader)

    if len(rows) != len(expected_groups):
        raise ValueError("U6 dependence map must contain exactly one row per frozen group")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside U6 dependence schema")
        clean = {key: (row.get(key) or "").strip() for key in U6_DEPENDENCE_FIELDS}
        for key in U6_DEPENDENCE_FIELDS:
            if not clean[key]:
                raise ValueError(f"row {row_number} {key} must be non-empty")
        group = clean["u6_dependency_group"]
        if group not in expected_groups:
            raise ValueError(f"row {row_number} non-frozen U6 dependency group {group!r}")
        if group in seen:
            raise ValueError(f"duplicate U6 dependence group {group!r}")
        seen.add(group)
        if clean["analysis_action"] not in U6_ANALYSIS_ACTIONS:
            raise ValueError(f"row {row_number} invalid analysis_action")
        if clean["analysis_action"] in {"SHARED_SPECIES_BLOCK", "SHARED_TAXON_CONCEPT_BLOCK"}:
            if clean["overlap_universe"] == "NONE" or clean["overlap_record_id"] == "NONE":
                raise ValueError(f"row {row_number} shared species block requires overlap identity")
        if clean["analysis_action"] == "U6_ONLY":
            if clean["overlap_universe"] != "NONE" or clean["overlap_record_id"] != "NONE":
                raise ValueError(f"row {row_number} U6_ONLY cannot declare external overlap")
        out.append(clean)

    if seen != expected_groups:
        raise ValueError("U6 dependence map does not cover the frozen dependency groups")
    return out



U6_SOURCE_RECOVERY_FIELDS = (
    "dependency_group",
    "admission_reference_ids",
    "query_pollination_biology",
    "query_floral_morphology",
    "query_pollen_transfer",
    "source_recovery_status",
    "supplemental_primary_source_ids",
    "packet_status",
    "notes",
)

U6_SOURCE_RECOVERY_STATUS = {"PENDING", "RESOLVED", "EVIDENCE_CEILING"}
U6_SOURCE_PACKET_STATUS = {"OPEN", "FROZEN"}
U6_FORBIDDEN_QUERY_TERMS = {
    "heteranthery",
    "dichogamy",
    "herkogamy",
    "division of labour",
    "division of labor",
    "structural module division",
    "shared integrated",
    "temporal separation",
    "spatial separation",
    "signal separation",
    "polymorphic or mosaic",
    "poricidal",
}


def load_u6_pass2_source_recovery(path: Path, freeze_manifest_path: Path) -> list[dict[str, str]]:
    """Validate generic architecture-blind source recovery before Pass-2 coding."""
    manifest = load_u6_pass1_freeze_manifest(freeze_manifest_path)
    expected_groups = set(manifest["included_dependency_groups"])
    source_map = manifest["source_reference_ids_by_dependency_group"]

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != U6_SOURCE_RECOVERY_FIELDS:
            raise ValueError("U6 Pass-2 source-recovery columns must match canonical order")
        rows = list(reader)

    if len(rows) != len(expected_groups):
        raise ValueError("U6 source-recovery frame must contain one row per frozen group")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside U6 source-recovery schema")
        clean = {key: (row.get(key) or "").strip() for key in U6_SOURCE_RECOVERY_FIELDS}
        for key in U6_SOURCE_RECOVERY_FIELDS:
            if not clean[key]:
                raise ValueError(f"row {row_number} {key} must be non-empty")

        group = clean["dependency_group"]
        if group not in expected_groups:
            raise ValueError(f"row {row_number} non-frozen U6 source-recovery group {group!r}")
        if group in seen:
            raise ValueError(f"duplicate U6 source-recovery group {group!r}")
        seen.add(group)

        expected_refs = ";".join(source_map[group])
        if clean["admission_reference_ids"] != expected_refs:
            raise ValueError(f"row {row_number} admission references disagree with Pass-1 freeze")

        query_text = " ".join(
            clean[field].casefold()
            for field in (
                "query_pollination_biology",
                "query_floral_morphology",
                "query_pollen_transfer",
            )
        )
        leaked = sorted(term for term in U6_FORBIDDEN_QUERY_TERMS if term in query_text)
        if leaked:
            raise ValueError(
                f"row {row_number} source-recovery query leaks architecture categories: {leaked}"
            )

        if clean["source_recovery_status"] not in U6_SOURCE_RECOVERY_STATUS:
            raise ValueError(f"row {row_number} invalid source_recovery_status")
        if clean["packet_status"] not in U6_SOURCE_PACKET_STATUS:
            raise ValueError(f"row {row_number} invalid packet_status")

        if clean["source_recovery_status"] == "PENDING":
            if clean["supplemental_primary_source_ids"] != "UNRESOLVED":
                raise ValueError(
                    f"row {row_number} pending source recovery must retain UNRESOLVED sources"
                )
            if clean["packet_status"] != "OPEN":
                raise ValueError(f"row {row_number} pending source recovery cannot be frozen")

        if clean["packet_status"] == "FROZEN" and clean["source_recovery_status"] == "PENDING":
            raise ValueError(f"row {row_number} frozen packet cannot remain pending")
        out.append(clean)

    if seen != expected_groups:
        raise ValueError("U6 source-recovery frame does not cover frozen dependency groups")
    return out


def u6_source_packet_ready(rows: list[dict[str, str]]) -> bool:
    """Return True only when every frozen group has a closed source-recovery decision."""
    return bool(rows) and all(
        row["source_recovery_status"] in {"RESOLVED", "EVIDENCE_CEILING"}
        and row["packet_status"] == "FROZEN"
        for row in rows
    )

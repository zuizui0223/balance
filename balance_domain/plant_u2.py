"""Guards for the Barrett-2002 sexual-interference discovery universe."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .plant_macro_agreement import (
    FIELDS as WORKSHEET_FIELDS,
    build_agreement_report_from_rows,
)
from .plant_macro import CONFLICT, MODULE_SUBSTRATE, RESOLUTION, SPATIAL, TIMING


FIELDS = (
    "universe_record_id",
    "universe_id",
    "dependency_group",
    "taxon_raw",
    "review_reference",
    "primary_source_id",
    "primary_source_doi",
    "evidence_family",
    "screening_status",
    "source_resolution_status",
    "notes",
)

COVERAGE_FIELDS = (
    "reference_id",
    "citation_short",
    "reference_class",
    "dependency_groups",
    "coverage_status",
    "notes",
)


SAMPLE_FIELDS = (
    "sample_order",
    "universe_record_id",
    "dependency_group",
    "taxon_raw",
    "selection_rule",
    "source_resolution_status",
    "double_code_status",
)

SOURCE_PACKET_FIELDS = (
    "sample_order",
    "universe_record_id",
    "dependency_group",
    "taxon_raw",
    "primary_source_id",
    "primary_source_doi",
    "coder_instruction",
)

SCREENING = {"UNSCREENED", "SCREENED", "ADJUDICATED", "EXCLUDED"}
SOURCE = {"RESOLVED_PRIMARY", "TAXON_RESOLUTION_PENDING", "SOURCE_RESOLUTION_PENDING"}
REFERENCE_CLASS = {
    "TAXON_EMPIRICAL",
    "SYNTHESIS_REVIEW",
    "THEORY_GENERAL",
    "HISTORICAL_SYNTHESIS",
    "BROAD_COMPARATIVE_DATASET",
}
COVERAGE_STATUS = {"MAPPED", "NO_NEW_GROUP_REQUIRED", "PENDING"}

EXPECTED_GROUPS = 22
EXPECTED_REFERENCES = 37
EXPECTED_DOUBLE_CODE_SAMPLE = 20
FROZEN_DOUBLE_CODE_SELECTION_RULE = "FIRST_20_DEPENDENCY_GROUPS_BY_FROZEN_U2_RECORD_ID"


def load_u2_universe(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U2 universe columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_GROUPS:
        raise ValueError(
            f"U2 universe must contain {EXPECTED_GROUPS} registered dependency groups"
        )

    ids: set[str] = set()
    deps: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U2 schema")
        for field in (
            "universe_record_id",
            "universe_id",
            "dependency_group",
            "taxon_raw",
            "review_reference",
            "primary_source_id",
            "evidence_family",
            "screening_status",
            "source_resolution_status",
        ):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"row {n} {field} must be frozen")

        if row["universe_id"] != "U2_BARRETT_2002":
            raise ValueError(f"row {n} has wrong U2 universe_id")
        if row["screening_status"] not in SCREENING:
            raise ValueError(f"row {n} invalid screening_status")
        if row["source_resolution_status"] not in SOURCE:
            raise ValueError(f"row {n} invalid source_resolution_status")
        if row["universe_record_id"] in ids:
            raise ValueError(f"duplicate U2 record id {row['universe_record_id']!r}")
        ids.add(row["universe_record_id"])

        if row["dependency_group"] in deps:
            raise ValueError(
                f"duplicate U2 dependency_group {row['dependency_group']!r}: "
                "merge repeated studies instead of counting bibliographic replication"
            )
        deps.add(row["dependency_group"])

        if row["source_resolution_status"] == "TAXON_RESOLUTION_PENDING":
            if "spp." not in row["taxon_raw"] and "program" not in row["dependency_group"].lower():
                raise ValueError(
                    f"row {n} taxon-resolution-pending record must visibly preserve non-species grain"
                )

    return rows


def load_u2_reference_coverage(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != COVERAGE_FIELDS:
            raise ValueError("U2 reference-coverage columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_REFERENCES:
        raise ValueError(
            f"Barrett 2002 reference coverage must contain all {EXPECTED_REFERENCES} references"
        )

    ids: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"coverage row {n} has fields outside schema")
        for field in ("reference_id", "citation_short", "reference_class", "coverage_status"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"coverage row {n} {field} must be frozen")
        if row["reference_id"] in ids:
            raise ValueError(f"duplicate Barrett reference id {row['reference_id']!r}")
        ids.add(row["reference_id"])
        if row["reference_class"] not in REFERENCE_CLASS:
            raise ValueError(f"coverage row {n} invalid reference_class")
        if row["coverage_status"] not in COVERAGE_STATUS:
            raise ValueError(f"coverage row {n} invalid coverage_status")

        if row["reference_class"] == "TAXON_EMPIRICAL":
            if row["coverage_status"] != "MAPPED":
                raise ValueError(
                    f"coverage row {n} taxon-empirical reference must be MAPPED"
                )
            if not row["dependency_groups"].strip():
                raise ValueError(
                    f"coverage row {n} taxon-empirical reference requires dependency groups"
                )
        else:
            if row["coverage_status"] == "MAPPED" and not row["dependency_groups"].strip():
                raise ValueError(
                    f"coverage row {n} mapped non-empirical reference needs explicit group mapping"
                )
    return rows


def validate_u2_reference_handoff(
    universe_rows: list[dict[str, str]],
    coverage_rows: list[dict[str, str]],
) -> dict:
    deps = {r["dependency_group"] for r in universe_rows}
    mapped_empirical: set[str] = set()

    for row in coverage_rows:
        if row["reference_class"] != "TAXON_EMPIRICAL":
            continue
        for dep in (x.strip() for x in row["dependency_groups"].split(";")):
            if dep not in deps:
                raise ValueError(
                    f"Barrett reference {row['reference_id']} maps to absent U2 group {dep!r}"
                )
            mapped_empirical.add(dep)

    # Every dependency group in this review-defined universe must have at least one
    # taxon-specific empirical citation in the review coverage ledger.
    unmapped_groups = sorted(deps - mapped_empirical)
    if unmapped_groups:
        raise ValueError(
            "U2 dependency groups lack taxon-specific Barrett reference mapping: "
            + ", ".join(unmapped_groups)
        )

    pending = [r["reference_id"] for r in coverage_rows if r["coverage_status"] == "PENDING"]
    unresolved_sources = [
        r["dependency_group"]
        for r in universe_rows
        if r["source_resolution_status"] != "RESOLVED_PRIMARY"
    ]

    return {
        "analysis": "balance_plant_u2_reference_handoff",
        "n_registered_dependency_groups": len(universe_rows),
        "n_barrett_references": len(coverage_rows),
        "n_taxon_empirical_references": sum(
            r["reference_class"] == "TAXON_EMPIRICAL" for r in coverage_rows
        ),
        "n_mapped_empirical_dependency_groups": len(mapped_empirical),
        "n_pending_reference_classifications": len(pending),
        "pending_reference_ids": sorted(pending),
        "n_unresolved_primary_sources": len(unresolved_sources),
        "unresolved_dependency_groups": sorted(unresolved_sources),
        "review_reference_coverage_closed": not pending,
        "species_source_resolution_closed": not unresolved_sources,
        "discovery_universe_source_closed": not pending and not unresolved_sources,
        "claim_ceiling": (
            "barrett_reference_coverage_and_species_source_resolution_only_"
            "not_conflict_status_not_architecture_mode_not_confirmatory"
        ),
    }


def build_u2_readout_from_rows(rows: list[dict[str, str]]) -> dict:
    source = Counter(r["source_resolution_status"] for r in rows)
    families = Counter(r["evidence_family"] for r in rows)
    screening = Counter(r["screening_status"] for r in rows)
    return {
        "analysis": "balance_plant_u2_review_universe",
        "n_registered_dependency_groups": len(rows),
        "source_resolution_counts": dict(sorted(source.items())),
        "evidence_family_counts": dict(sorted(families.items())),
        "screening_status_counts": dict(sorted(screening.items())),
        "n_species_level_source_resolved": sum(
            r["source_resolution_status"] == "RESOLVED_PRIMARY"
            and "spp." not in r["taxon_raw"]
            for r in rows
        ),
        "n_taxon_resolution_pending": source.get("TAXON_RESOLUTION_PENDING", 0),
        "claim_ceiling": (
            "review_defined_discovery_universe_only_"
            "not_conflict_positive_not_architecture_resolution_not_confirmatory"
        ),
    }


def build_u2_readout(path: Path) -> dict:
    return build_u2_readout_from_rows(load_u2_universe(path))


def build_u2_reference_handoff(universe_path: Path, coverage_path: Path) -> dict:
    return validate_u2_reference_handoff(
        load_u2_universe(universe_path),
        load_u2_reference_coverage(coverage_path),
    )


def load_u2_double_code_sample(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != SAMPLE_FIELDS:
            raise ValueError("U2 double-code sample columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_DOUBLE_CODE_SAMPLE:
        raise ValueError(
            f"U2 double-code sample must contain {EXPECTED_DOUBLE_CODE_SAMPLE} groups"
        )
    orders = [int(r["sample_order"]) for r in rows]
    if orders != list(range(1, EXPECTED_DOUBLE_CODE_SAMPLE + 1)):
        raise ValueError("U2 sample_order must be exactly 1..20")
    if len({r["universe_record_id"] for r in rows}) != len(rows):
        raise ValueError("U2 double-code sample record IDs must be unique")
    if not all(r["double_code_status"] == "READY_FOR_INDEPENDENT_DOUBLE_CODING" for r in rows):
        raise ValueError("every U2 sampled group must be source-ready before coding")
    if not all(r["selection_rule"] == FROZEN_DOUBLE_CODE_SELECTION_RULE for r in rows):
        raise ValueError("U2 double-code sample must follow the preregistered record-ID rule")
    return rows


def load_u2_source_packet(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != SOURCE_PACKET_FIELDS:
            raise ValueError("U2 source-packet columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_DOUBLE_CODE_SAMPLE:
        raise ValueError(
            f"U2 source packet must contain {EXPECTED_DOUBLE_CODE_SAMPLE} groups"
        )
    for n, row in enumerate(rows, start=2):
        if row["coder_instruction"] != (
            "CODE_FROM_PRIMARY_SOURCE_ONLY_DO_NOT_USE_U2_EVIDENCE_FAMILY_OR_REVIEW_NOTES"
        ):
            raise ValueError(f"source-packet row {n} has wrong blinding instruction")
    return rows



def load_u2_blank_worksheet(path: Path) -> list[dict[str, str]]:
    """Validate the frozen two-coder U2 worksheet before independent coding."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != WORKSHEET_FIELDS:
            raise ValueError("U2 worksheet columns must match agreement schema")
        rows = list(reader)

    if len(rows) != EXPECTED_DOUBLE_CODE_SAMPLE * 2:
        raise ValueError("U2 worksheet must contain exactly two coder rows per sampled group")

    grouped: dict[str, set[str]] = {}
    for n, row in enumerate(rows, start=2):
        cluster = (row.get("cluster_id") or "").strip()
        coder = (row.get("coder_id") or "").strip()
        if not cluster or coder not in {"CODER_A", "CODER_B"}:
            raise ValueError(f"U2 worksheet row {n} invalid cluster/coder identity")
        grouped.setdefault(cluster, set()).add(coder)
        for field in WORKSHEET_FIELDS[2:]:
            if (row.get(field) or "").strip():
                raise ValueError(
                    f"U2 worksheet row {n} must be blank before independent coding"
                )

    if len(grouped) != EXPECTED_DOUBLE_CODE_SAMPLE:
        raise ValueError("U2 worksheet must contain exactly 20 dependency groups")
    if any(coders != {"CODER_A", "CODER_B"} for coders in grouped.values()):
        raise ValueError("every U2 worksheet group requires CODER_A and CODER_B")
    return rows


def validate_u2_double_code_handoff(
    universe_rows: list[dict[str, str]],
    sample_rows: list[dict[str, str]],
    packet_rows: list[dict[str, str]],
    worksheet_rows: list[dict[str, str]] | None = None,
) -> dict:
    by_id = {r["universe_record_id"]: r for r in universe_rows}
    expected = sorted(
        universe_rows,
        key=lambda r: r["universe_record_id"],
    )[:EXPECTED_DOUBLE_CODE_SAMPLE]

    if [r["universe_record_id"] for r in sample_rows] != [
        r["universe_record_id"] for r in expected
    ]:
        raise ValueError("U2 sample no longer matches preregistered record-ID selection rule")

    packet_by_id = {r["universe_record_id"]: r for r in packet_rows}
    for sample in sample_rows:
        uid = sample["universe_record_id"]
        if uid not in by_id or uid not in packet_by_id:
            raise ValueError(f"U2 sampled record {uid!r} missing from handoff")
        universe = by_id[uid]
        packet = packet_by_id[uid]
        for field in ("dependency_group", "taxon_raw"):
            if sample[field] != universe[field] or sample[field] != packet[field]:
                raise ValueError(f"U2 handoff mismatch for {uid!r} field {field}")
        if universe["source_resolution_status"] != "RESOLVED_PRIMARY":
            raise ValueError(f"U2 sampled record {uid!r} is not source-resolved")
        if sample["source_resolution_status"] != "RESOLVED_PRIMARY":
            raise ValueError(f"U2 sample status drift for {uid!r}")
        if packet["primary_source_id"] != universe["primary_source_id"]:
            raise ValueError(f"U2 blinded source packet source drift for {uid!r}")

    worksheet_groups = None
    if worksheet_rows is not None:
        worksheet_groups = {row["cluster_id"] for row in worksheet_rows}
        expected_groups = {row["dependency_group"] for row in sample_rows}
        if worksheet_groups != expected_groups:
            raise ValueError("U2 worksheet groups do not match frozen double-code sample")

    return {
        "analysis": "balance_plant_u2_double_code_handoff",
        "n_universe_groups": len(universe_rows),
        "n_sampled_groups": len(sample_rows),
        "n_source_packet_groups": len(packet_rows),
        "n_blank_worksheet_rows": (
            len(worksheet_rows) if worksheet_rows is not None else None
        ),
        "all_sampled_sources_resolved": True,
        "selection_rule_closed": True,
        "source_packet_blinded_to_review_evidence_family": True,
        "two_independent_coder_slots_per_group": (
            worksheet_rows is not None and len(worksheet_rows) == EXPECTED_DOUBLE_CODE_SAMPLE * 2
        ),
        "independent_double_coding_ready": True,
        "claim_ceiling": (
            "source_closed_blinded_coder_assignment_only_"
            "not_conflict_status_not_architecture_mode_not_adjudicated"
        ),
    }


def build_u2_double_code_handoff(
    universe_path: Path,
    sample_path: Path,
    packet_path: Path,
    worksheet_path: Path | None = None,
) -> dict:
    return validate_u2_double_code_handoff(
        load_u2_universe(universe_path),
        load_u2_double_code_sample(sample_path),
        load_u2_source_packet(packet_path),
        (
            load_u2_blank_worksheet(worksheet_path)
            if worksheet_path is not None
            else None
        ),
    )



U2_ADJUDICATION_FIELDS = (
    "cluster_id",
    "conflict_status",
    "architecture_mode",
    "module_substrate",
    "conflict_timing_geometry",
    "conflict_spatial_geometry",
    "adjudication_status",
    "adjudication_basis",
    "notes",
)

U2_ADJUDICATION_STATUS = {"PENDING", "ADJUDICATED"}


def load_u2_adjudication(
    path: Path,
    sample_rows: list[dict[str, str]],
    coding_rows: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Validate one adjudication row per frozen U2 reliability group.

    PENDING rows remain fully unresolved. ADJUDICATED rows are allowed only after
    exactly two completed coder rows exist for that group.
    """
    expected_groups = {row["dependency_group"] for row in sample_rows}
    if len(expected_groups) != EXPECTED_DOUBLE_CODE_SAMPLE:
        raise ValueError("U2 adjudication requires the frozen 20-group sample")

    coding_by_group: dict[str, list[dict[str, str]]] = {}
    if coding_rows is not None:
        for row in coding_rows:
            coding_by_group.setdefault(row["cluster_id"], []).append(row)
        if set(coding_by_group) != expected_groups:
            raise ValueError("U2 completed coding groups must exactly match the frozen reliability sample")

    agreement_repair_required = False
    if coding_rows is not None:
        agreement = build_agreement_report_from_rows(coding_rows)
        agreement_repair_required = any(
            stats["codebook_repair_trigger"]
            for stats in agreement["fields"].values()
        )

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != U2_ADJUDICATION_FIELDS:
            raise ValueError("U2 adjudication columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_DOUBLE_CODE_SAMPLE:
        raise ValueError("U2 adjudication requires exactly 20 rows")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U2 adjudication schema")
        clean = {key: (row.get(key) or "").strip() for key in U2_ADJUDICATION_FIELDS}
        for key in U2_ADJUDICATION_FIELDS[:-1]:
            if not clean[key]:
                raise ValueError(f"row {n} {key} must be non-empty")

        group = clean["cluster_id"]
        if group not in expected_groups:
            raise ValueError(f"row {n} non-frozen U2 adjudication group {group!r}")
        if group in seen:
            raise ValueError(f"duplicate U2 adjudication group {group!r}")
        seen.add(group)

        if clean["conflict_status"] not in CONFLICT:
            raise ValueError(f"row {n} invalid conflict_status")
        if clean["architecture_mode"] not in RESOLUTION:
            raise ValueError(f"row {n} invalid architecture_mode")
        if clean["module_substrate"] not in MODULE_SUBSTRATE:
            raise ValueError(f"row {n} invalid module_substrate")
        if clean["conflict_timing_geometry"] not in TIMING:
            raise ValueError(f"row {n} invalid conflict_timing_geometry")
        if clean["conflict_spatial_geometry"] not in SPATIAL:
            raise ValueError(f"row {n} invalid conflict_spatial_geometry")
        if clean["adjudication_status"] not in U2_ADJUDICATION_STATUS:
            raise ValueError(f"row {n} invalid adjudication_status")

        coded_fields = (
            "conflict_status",
            "architecture_mode",
            "module_substrate",
            "conflict_timing_geometry",
            "conflict_spatial_geometry",
        )
        if clean["adjudication_status"] == "PENDING":
            if clean["adjudication_basis"] != "AWAITING_INDEPENDENT_DOUBLE_CODING":
                raise ValueError(f"row {n} pending adjudication basis drifted")
            if any(clean[field] != "UNRESOLVED" for field in coded_fields):
                raise ValueError(f"row {n} pending adjudication must remain unresolved")
        else:
            if agreement_repair_required:
                raise ValueError(
                    f"row {n} cannot adjudicate before codebook repair/recode closes"
                )
            pair = coding_by_group.get(group, [])
            if len(pair) != 2:
                raise ValueError(
                    f"row {n} cannot adjudicate before two completed coder rows exist"
                )
            if {item["coder_id"] for item in pair} != {"CODER_A", "CODER_B"}:
                raise ValueError(f"row {n} adjudication requires CODER_A and CODER_B")
            if any(
                not (item.get(field) or "").strip()
                for item in pair
                for field in WORKSHEET_FIELDS[2:-1]
            ):
                raise ValueError(
                    f"row {n} cannot adjudicate while coder fields are incomplete"
                )
            pair_by_coder = {item["coder_id"]: item for item in pair}
            disagreements = [
                field for field in coded_fields
                if pair_by_coder["CODER_A"][field]
                != pair_by_coder["CODER_B"][field]
            ]
            expected_basis = (
                "SOURCE_REVIEW_OF_DISAGREEMENTS"
                if disagreements
                else "CODER_CONSENSUS"
            )
            if clean["adjudication_basis"] != expected_basis:
                raise ValueError(
                    f"row {n} adjudication_basis must be {expected_basis!r}"
                )
            for field in coded_fields:
                a_value = pair_by_coder["CODER_A"][field]
                b_value = pair_by_coder["CODER_B"][field]
                if a_value == b_value and clean[field] != a_value:
                    raise ValueError(
                        f"row {n} cannot override coder consensus for {field}"
                    )
            if not clean["notes"]:
                raise ValueError(f"row {n} adjudicated row requires notes")

        clean["notes"] = (row.get("notes") or "").strip()
        out.append(clean)

    if seen != expected_groups:
        raise ValueError("U2 adjudication does not cover the frozen sample groups")
    return out

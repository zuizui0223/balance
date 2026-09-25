"""Blinded independent-coder handoff for the frozen U1 first-20 sample."""
from __future__ import annotations

import csv
from pathlib import Path

from .plant_macro_agreement import FIELDS as WORKSHEET_FIELDS
from .plant_u1 import (
    load_u1_sample,
    load_u1_source_resolution,
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

EXPECTED_SAMPLE = 20
INSTRUCTION = (
    "CODE_FROM_PRIMARY_SOURCE_ONLY_"
    "DO_NOT_USE_U1_SCREENING_OR_SOURCE_EVIDENCE_NOTES"
)


def load_u1_source_packet(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != SOURCE_PACKET_FIELDS:
            raise ValueError("U1 source-packet columns must match canonical order")
        rows = list(reader)

    if len(rows) != EXPECTED_SAMPLE:
        raise ValueError("U1 source packet must contain exactly 20 groups")
    orders = [int(r["sample_order"]) for r in rows]
    if orders != list(range(1, EXPECTED_SAMPLE + 1)):
        raise ValueError("U1 source packet sample_order must be exactly 1..20")

    for n, row in enumerate(rows, start=2):
        if row["coder_instruction"] != INSTRUCTION:
            raise ValueError(f"U1 source-packet row {n} has wrong blinding instruction")
        for field in (
            "universe_record_id",
            "dependency_group",
            "taxon_raw",
            "primary_source_id",
        ):
            if not row[field].strip():
                raise ValueError(f"U1 source-packet row {n} {field} must be frozen")
    return rows


def load_u1_blank_worksheet(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != WORKSHEET_FIELDS:
            raise ValueError("U1 worksheet columns must match agreement schema")
        rows = list(reader)

    if len(rows) != EXPECTED_SAMPLE * 2:
        raise ValueError("U1 worksheet must contain exactly two coder rows per sample group")

    grouped: dict[str, set[str]] = {}
    for n, row in enumerate(rows, start=2):
        cluster = row["cluster_id"].strip()
        coder = row["coder_id"].strip()
        if not cluster or coder not in {"CODER_A", "CODER_B"}:
            raise ValueError(f"U1 worksheet row {n} invalid cluster/coder identity")
        grouped.setdefault(cluster, set()).add(coder)
        for field in WORKSHEET_FIELDS[2:]:
            if (row.get(field) or "").strip():
                raise ValueError(f"U1 worksheet row {n} must be blank before independent coding")
    if len(grouped) != EXPECTED_SAMPLE:
        raise ValueError("U1 worksheet must contain exactly 20 dependency groups")
    if any(coders != {"CODER_A", "CODER_B"} for coders in grouped.values()):
        raise ValueError("every U1 worksheet group requires CODER_A and CODER_B")
    return rows


def validate_u1_double_code_handoff(
    sample_rows: list[dict[str, str]],
    resolution_rows: list[dict[str, str]],
    packet_rows: list[dict[str, str]],
    worksheet_rows: list[dict[str, str]],
) -> dict:
    if len(sample_rows) != EXPECTED_SAMPLE or len(resolution_rows) != EXPECTED_SAMPLE:
        raise ValueError("U1 double-code handoff requires the frozen 20-row sample")

    resolution_by_id = {r["universe_record_id"]: r for r in resolution_rows}
    packet_by_id = {r["universe_record_id"]: r for r in packet_rows}

    expected_groups = set()
    for sample in sample_rows:
        uid = sample["universe_record_id"]
        if uid not in resolution_by_id or uid not in packet_by_id:
            raise ValueError(f"U1 sampled record {uid!r} missing from source handoff")
        resolution = resolution_by_id[uid]
        packet = packet_by_id[uid]
        for field in ("dependency_group", "taxon_raw"):
            if sample[field] != resolution[field] or sample[field] != packet[field]:
                raise ValueError(f"U1 handoff mismatch for {uid!r} field {field}")
        if sample["primary_source_status"] != "RESOLVED_PRIMARY":
            raise ValueError(f"U1 sample {uid!r} is not source-resolved")
        if resolution["source_status"] != "RESOLVED_PRIMARY":
            raise ValueError(f"U1 resolution {uid!r} is not primary-source resolved")
        if packet["primary_source_id"] != resolution["primary_citation"]:
            raise ValueError(f"U1 source packet citation drift for {uid!r}")
        if packet["primary_source_doi"] != resolution["doi"]:
            raise ValueError(f"U1 source packet DOI drift for {uid!r}")
        expected_groups.add(sample["dependency_group"])

    worksheet_groups = {r["cluster_id"] for r in worksheet_rows}
    if worksheet_groups != expected_groups:
        raise ValueError("U1 worksheet groups do not match the frozen first-20 sample")

    return {
        "analysis": "balance_plant_u1_double_code_handoff",
        "n_sampled_groups": len(sample_rows),
        "n_source_packet_groups": len(packet_rows),
        "n_blank_worksheet_rows": len(worksheet_rows),
        "all_sampled_sources_resolved": True,
        "source_packet_excludes_screening_and_evidence_surface": True,
        "two_independent_coder_slots_per_group": True,
        "independent_double_coding_ready": True,
        "claim_ceiling": (
            "source_closed_blinded_coder_assignment_only_"
            "not_conflict_status_not_architecture_mode_not_adjudicated"
        ),
    }


def build_u1_double_code_handoff(
    sample_path: Path,
    resolution_path: Path,
    packet_path: Path,
    worksheet_path: Path,
) -> dict:
    return validate_u1_double_code_handoff(
        load_u1_sample(sample_path),
        load_u1_source_resolution(resolution_path),
        load_u1_source_packet(packet_path),
        load_u1_blank_worksheet(worksheet_path),
    )

"""Assemble licensed U2/U6 rows for BALANCE plant confirmatory model V4.

This module performs no biological inference. It only joins independently adjudicated
surfaces and refuses to assemble a row when conflict, architecture, predictor-independence,
source provenance, or dependence identity is incomplete or inconsistent.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .plant_confirmatory import (
    PREDICTORS,
    adjudicated_independent_plant_values,
    load_plant_predictor_receipts,
)
from .plant_macro import primary_architecture_class
from .plant_macro_agreement import load_double_coding
from .plant_u2 import (
    load_u2_adjudication,
    load_u2_double_code_sample,
    load_u2_source_packet,
)
from .plant_u6 import (
    load_u6_cross_universe_dependence,
    load_u6_frozen_source_packet,
    load_u6_pass2_adjudication,
    load_u6_pass2_double_coding,
)
from .plant_model_assembly import validate_model_assembly_rows


U2_UNIVERSE = "U2_BARRETT_2002"
U6_UNIVERSE = "U6_POLLEN_THEFT_HARGREAVES_2009"

U2_CONFLICT_FAMILY = "SEXUAL_INTERFERENCE"
U6_CONFLICT_FAMILY = "POLLEN_REWARD_GAMETE"


def _licensed_predictors(
    receipts: list[dict[str, str]],
) -> dict[tuple[str, str], str]:
    return adjudicated_independent_plant_values(receipts)


def _require_predictor_match(
    *,
    group: str,
    adjudication: dict[str, str],
    licensed: dict[tuple[str, str], str],
) -> None:
    for predictor in PREDICTORS:
        receipt_value = licensed.get((group, predictor))
        if receipt_value is None:
            raise ValueError(
                f"{group!r} lacks an adjudicated outcome-independent receipt for {predictor}"
            )
        if adjudication[predictor] != receipt_value:
            raise ValueError(
                f"{group!r} adjudication/receipt mismatch for {predictor}: "
                f"{adjudication[predictor]!r} != {receipt_value!r}"
            )


def build_u2_licensed_rows(
    *,
    adjudication_rows: list[dict[str, str]],
    predictor_receipts: list[dict[str, str]],
    source_packet_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Build U2 model rows from final adjudication and independent predictor receipts."""
    licensed = _licensed_predictors(predictor_receipts)
    sources = {row["dependency_group"]: row for row in source_packet_rows}

    if len(adjudication_rows) != 20:
        raise ValueError("U2 final assembly requires all 20 frozen reliability adjudication rows")
    if any(row["adjudication_status"] != "ADJUDICATED" for row in adjudication_rows):
        raise ValueError("U2 final assembly cannot omit pending adjudication rows")
    if set(sources) != {row["cluster_id"] for row in adjudication_rows}:
        raise ValueError("U2 source packet and final adjudication groups disagree")

    out: list[dict[str, str]] = []
    for row in adjudication_rows:
        if row["adjudication_status"] != "ADJUDICATED":
            continue
        if row["conflict_status"] != "POSITIVE":
            continue

        group = row["cluster_id"]
        if group not in sources:
            raise ValueError(f"U2 adjudicated positive group {group!r} lacks source packet row")
        if row["architecture_mode"] == "UNRESOLVED":
            raise ValueError(f"U2 positive group {group!r} has unresolved architecture")
        for predictor in PREDICTORS:
            if row[predictor] == "UNRESOLVED":
                raise ValueError(f"U2 positive group {group!r} has unresolved {predictor}")

        _require_predictor_match(
            group=group,
            adjudication=row,
            licensed=licensed,
        )

        source = sources[group]
        doi = source.get("primary_source_doi", "").strip()
        source_basis = source["primary_source_id"].strip()
        if doi:
            source_basis += f" | DOI {doi}"

        assembled = {
            "analysis_row_id": f"U2::{group}",
            "universe_id": U2_UNIVERSE,
            "dependency_group": group,
            "dependence_block": f"U2::{group}",
            "system_taxon": source["taxon_raw"].strip(),
            "conflict_family": U2_CONFLICT_FAMILY,
            "conflict_receipt_status": "ADJUDICATED_POSITIVE",
            "architecture_mode": row["architecture_mode"],
            "module_substrate": row["module_substrate"],
            "conflict_timing_geometry": row["conflict_timing_geometry"],
            "conflict_spatial_geometry": row["conflict_spatial_geometry"],
            "architecture_adjudication_status": "ADJUDICATED",
            "predictor_receipt_status": "THREE_ADJUDICATED_OUTCOME_INDEPENDENT",
            "source_basis": source_basis,
            "claim_ceiling": (
                "U2_adjudicated_conflict_positive_routing_row_not_causal_transition"
            ),
        }
        # Fail immediately if the assembled row violates the current V4 contract.
        validate_model_assembly_rows([assembled])
        out.append(assembled)

    return sorted(out, key=lambda row: row["dependency_group"])


def build_u6_licensed_rows(
    *,
    adjudication_rows: list[dict[str, str]],
    predictor_receipts: list[dict[str, str]],
    dependence_rows: list[dict[str, str]],
    frozen_source_packet_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Build U6 model rows from conflict-first admission plus final Pass-2 adjudication."""
    licensed = _licensed_predictors(predictor_receipts)
    dependence = {row["u6_dependency_group"]: row for row in dependence_rows}
    sources = {row["dependency_group"]: row for row in frozen_source_packet_rows}

    expected_groups = set(dependence)
    if set(sources) != expected_groups:
        raise ValueError("U6 dependence and frozen source-packet groups disagree")

    if len(adjudication_rows) != len(expected_groups):
        raise ValueError("U6 final assembly requires one adjudication row per frozen group")
    if {row["dependency_group"] for row in adjudication_rows} != expected_groups:
        raise ValueError("U6 adjudication groups disagree with frozen dependence map")
    if any(row["adjudication_status"] != "ADJUDICATED" for row in adjudication_rows):
        raise ValueError("U6 final assembly cannot omit pending adjudication rows")

    adjudicated = {
        row["dependency_group"]: row
        for row in adjudication_rows
    }

    out: list[dict[str, str]] = []
    for group in sorted(adjudicated):
        row = adjudicated[group]
        if group not in expected_groups:
            raise ValueError(f"U6 adjudicated group {group!r} is not in frozen dependence map")
        if row["architecture_mode"] == "UNRESOLVED":
            raise ValueError(f"U6 group {group!r} has unresolved architecture")
        for predictor in PREDICTORS:
            if row[predictor] == "UNRESOLVED":
                raise ValueError(f"U6 group {group!r} has unresolved {predictor}")

        _require_predictor_match(
            group=group,
            adjudication=row,
            licensed=licensed,
        )

        dep = dependence[group]
        source = sources[group]
        source_parts = [source["admission_primary_source_basis"].strip()]
        supplemental = source["supplemental_primary_source_ids"].strip()
        if supplemental not in {
            "NONE_AFTER_REGISTERED_GENERIC_SEARCH",
            "NONE_ADMISSION_SOURCE_SUFFICIENT",
        }:
            source_parts.append(supplemental)

        assembled = {
            "analysis_row_id": f"U6::{group}",
            "universe_id": U6_UNIVERSE,
            "dependency_group": group,
            "dependence_block": dep["dependence_block"],
            "system_taxon": source["plant_taxon"].replace("_", " ").strip(),
            "conflict_family": U6_CONFLICT_FAMILY,
            "conflict_receipt_status": "ADJUDICATED_POSITIVE",
            "architecture_mode": row["architecture_mode"],
            "module_substrate": row["module_substrate"],
            "conflict_timing_geometry": row["conflict_timing_geometry"],
            "conflict_spatial_geometry": row["conflict_spatial_geometry"],
            "architecture_adjudication_status": "ADJUDICATED",
            "predictor_receipt_status": "THREE_ADJUDICATED_OUTCOME_INDEPENDENT",
            "source_basis": " | ".join(source_parts),
            "claim_ceiling": (
                "U6_conflict_first_adjudicated_routing_row_not_causal_transition"
            ),
        }
        validate_model_assembly_rows([assembled])
        out.append(assembled)

    return out


def build_v4_licensed_assembly(
    *,
    u2_adjudication_rows: list[dict[str, str]],
    u2_predictor_receipts: list[dict[str, str]],
    u2_source_packet_rows: list[dict[str, str]],
    u6_adjudication_rows: list[dict[str, str]],
    u6_predictor_receipts: list[dict[str, str]],
    u6_dependence_rows: list[dict[str, str]],
    u6_frozen_source_packet_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Join licensed U2 and U6 rows and revalidate the combined V4 assembly surface."""
    rows = build_u2_licensed_rows(
        adjudication_rows=u2_adjudication_rows,
        predictor_receipts=u2_predictor_receipts,
        source_packet_rows=u2_source_packet_rows,
    )
    rows += build_u6_licensed_rows(
        adjudication_rows=u6_adjudication_rows,
        predictor_receipts=u6_predictor_receipts,
        dependence_rows=u6_dependence_rows,
        frozen_source_packet_rows=u6_frozen_source_packet_rows,
    )
    if not rows:
        raise ValueError("no licensed U2/U6 rows are available for V4 assembly")
    return validate_model_assembly_rows(rows)



def build_v4_licensed_assembly_from_files(
    *,
    u2_sample_path: Path,
    u2_coding_path: Path,
    u2_adjudication_path: Path,
    u2_predictor_receipts_path: Path,
    u2_source_packet_path: Path,
    u6_freeze_path: Path,
    u6_coding_path: Path,
    u6_adjudication_path: Path,
    u6_predictor_receipts_path: Path,
    u6_dependence_path: Path,
    u6_source_recovery_path: Path,
    u6_frozen_source_packet_path: Path,
) -> list[dict[str, str]]:
    """Load canonical frozen surfaces and assemble V4 rows only after all gates close."""
    u2_sample = load_u2_double_code_sample(u2_sample_path)
    u2_coding = load_double_coding(u2_coding_path)
    if {row["coder_id"] for row in u2_coding} != {"CODER_A", "CODER_B"}:
        raise ValueError("U2 completed coding must preserve frozen CODER_A/CODER_B IDs")
    if {row["cluster_id"] for row in u2_coding} != {
        row["dependency_group"] for row in u2_sample
    }:
        raise ValueError("U2 completed coding groups disagree with frozen sample")

    u2_adjudication = load_u2_adjudication(
        u2_adjudication_path,
        u2_sample,
        u2_coding,
    )
    u2_receipts = load_plant_predictor_receipts(u2_predictor_receipts_path)
    u2_sources = load_u2_source_packet(u2_source_packet_path)

    u6_coding = load_u6_pass2_double_coding(u6_coding_path, u6_freeze_path)
    if any(row["coding_status"] != "CODED" for row in u6_coding):
        raise ValueError("U6 completed coding worksheet still contains UNSTARTED rows")
    u6_adjudication = load_u6_pass2_adjudication(
        u6_adjudication_path,
        u6_freeze_path,
        u6_coding,
    )
    u6_receipts = load_plant_predictor_receipts(u6_predictor_receipts_path)
    u6_dependence = load_u6_cross_universe_dependence(
        u6_dependence_path,
        u6_freeze_path,
    )
    u6_sources = load_u6_frozen_source_packet(
        u6_frozen_source_packet_path,
        u6_freeze_path,
        u6_source_recovery_path,
    )

    return build_v4_licensed_assembly(
        u2_adjudication_rows=u2_adjudication,
        u2_predictor_receipts=u2_receipts,
        u2_source_packet_rows=u2_sources,
        u6_adjudication_rows=u6_adjudication,
        u6_predictor_receipts=u6_receipts,
        u6_dependence_rows=u6_dependence,
        u6_frozen_source_packet_rows=u6_sources,
    )

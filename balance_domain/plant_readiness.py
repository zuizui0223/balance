"""Programme-wide readiness audit for BALANCE plant confirmatory model v4."""
from __future__ import annotations

from pathlib import Path

from .plant_confirmatory import (
    build_receipt_screening_coverage,
    load_plant_predictor_receipts,
)
from .plant_u1_full_screen import build_u1_full47_conflict_screen
from .plant_u1_double_code import load_u1_blank_worksheet
from .plant_u2 import load_u2_blank_worksheet
from .plant_u2_screen import build_u2_conflict_screen_readout
from .plant_u6 import (
    build_u6_evidence_readiness,
    load_u6_cross_universe_dependence,
    load_u6_pass1_freeze_manifest,
    load_u6_pass2_adjudication,
    load_u6_pass2_double_coding,
)


def build_plant_v4_readiness(
    *,
    u1_first20_conflict_path: Path,
    u1_production27_conflict_path: Path,
    u1_worksheet_path: Path,
    u2_conflict_path: Path,
    u2_worksheet_path: Path,
    u2_predictor_receipts_path: Path,
    u6_freeze_path: Path,
    u6_worksheet_path: Path,
    u6_adjudication_path: Path,
    u6_predictor_receipts_path: Path,
    u6_dependence_path: Path,
) -> dict:
    """Return the current gate state without inferring any missing human coding."""
    u1 = build_u1_full47_conflict_screen(
        u1_first20_conflict_path,
        u1_production27_conflict_path,
    )
    u1_worksheet = load_u1_blank_worksheet(u1_worksheet_path)

    u2 = build_u2_conflict_screen_readout(u2_conflict_path)
    u2_worksheet = load_u2_blank_worksheet(u2_worksheet_path)
    u2_receipts = load_plant_predictor_receipts(u2_predictor_receipts_path)
    u2_receipt_coverage = build_receipt_screening_coverage(u2_receipts)

    u6_manifest = load_u6_pass1_freeze_manifest(u6_freeze_path)
    u6_coding = load_u6_pass2_double_coding(u6_worksheet_path, u6_freeze_path)
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
    u6_readiness = build_u6_evidence_readiness(
        u6_coding,
        u6_adjudication,
        u6_receipts,
        u6_dependence,
    )

    u1_coding_started = any(
        any((row.get(field) or "").strip() for field in (
            "conflict_status",
            "architecture_mode",
            "module_substrate",
            "conflict_timing_geometry",
            "conflict_spatial_geometry",
        ))
        for row in u1_worksheet
    )
    u2_coding_started = any(
        any((row.get(field) or "").strip() for field in (
            "conflict_status",
            "architecture_mode",
            "module_substrate",
            "conflict_timing_geometry",
            "conflict_spatial_geometry",
        ))
        for row in u2_worksheet
    )

    machine_complete = {
        "u1_full47_source_screen": (
            u1["n_records"] == 47
            and u1["n_unresolved_candidate"] == 0
        ),
        "u2_full22_source_screen": (
            u2["n_dependency_groups"] == 22
            and u2["n_unresolved_candidate"] == 0
        ),
        "u2_positive_predictor_source_screen": (
            u2_receipt_coverage["n_complete_outcome_independent_clusters"] == 8
        ),
        "u6_pass1_conflict_first_freeze": (
            u6_manifest["pass1_contract"]["n_anchor_review_references"] == 157
            and len(u6_manifest["included_dependency_groups"]) == 21
        ),
        "u6_predictor_source_screen": (
            build_receipt_screening_coverage(u6_receipts)[
                "n_complete_outcome_independent_clusters"
            ] == 21
        ),
        "u6_cross_universe_dependence": len(u6_dependence) == 21,
    }

    primary_human_open = {
        "u2_independent_double_coding": not u2_coding_started,
        "u6_independent_double_coding": not u6_readiness["coding_complete"],
        "u6_post_coding_adjudication": not u6_readiness["adjudication_complete"],
        "u2_predictor_independent_adjudication": (
            u2_receipt_coverage["n_complete_adjudicated_clusters"] < 8
        ),
        "u6_predictor_independent_adjudication": (
            u6_readiness[
                "n_groups_with_three_adjudicated_independent_predictors"
            ] < 21
        ),
    }
    external_validation_open = {
        "u1_independent_double_coding": not u1_coding_started,
    }

    blockers = [name for name, is_open in primary_human_open.items() if is_open]

    return {
        "analysis": "balance_plant_v4_programme_readiness",
        "model_specification": "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4",
        "machine_complete": machine_complete,
        "all_machine_preparation_complete": all(machine_complete.values()),
        "primary_human_open_gates": primary_human_open,
        "external_validation_open_gates": external_validation_open,
        "open_gate_names": blockers,
        "primary_model_assembly_ready": False,
        "v4_estimability_ready_to_evaluate": False,
        "v3_estimability_ready_to_evaluate": False,
        "reason": (
            "U2/U6 independent coding/adjudication gates remain open; V4 model assembly "
            "and estimability must wait for adjudicated outcomes and predictor receipts"
        ),
        "source_screen_summary": {
            "U1": {
                "n_groups": u1["n_dependency_groups"],
                "n_positive": u1["n_positive_conflict"],
                "n_unresolved": u1["n_unresolved_candidate"],
            },
            "U2": {
                "n_groups": u2["n_dependency_groups"],
                "n_positive": u2["n_positive_conflict"],
                "n_unresolved": u2["n_unresolved_candidate"],
            },
            "U6": {
                "n_groups": len(u6_manifest["included_dependency_groups"]),
                "architecture_coding_complete": u6_readiness["coding_complete"],
            },
        },
        "claim_ceiling": "programme_readiness_only_not_biological_effect",
    }



def build_plant_v3_readiness(**kwargs) -> dict:
    """Backward-compatible alias for the superseded V3 readiness entrypoint."""
    return build_plant_v4_readiness(**kwargs)

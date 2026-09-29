"""Programme-wide readiness audit for BALANCE plant confirmatory model v4."""
from __future__ import annotations

from pathlib import Path

from .plant_confirmatory import (
    build_receipt_screening_coverage,
    load_plant_predictor_receipts,
)
from .plant_u1_full_screen import build_u1_full47_conflict_screen
from .plant_macro_agreement import load_double_coding
from .plant_u1 import load_u1_sample
from .plant_u1_double_code import load_u1_adjudication, load_u1_blank_worksheet
from .plant_u2 import (
    load_u2_adjudication,
    load_u2_blank_worksheet,
    load_u2_double_code_sample,
)
from .plant_u2_screen import build_u2_conflict_screen_readout
from .plant_preoutcome_generality import build_preoutcome_generality_audit


PRIMARY_MACHINE_GATES = (
    "u2_full22_source_screen",
    "u2_positive_predictor_source_screen",
    "u6_pass1_conflict_first_freeze",
    "u6_predictor_source_screen",
    "u6_cross_universe_dependence",
)
EXTERNAL_VALIDATION_MACHINE_GATES = ("u1_full47_source_screen",)


def _machine_gate_complete(
    machine_complete: dict[str, bool],
    required_gates: tuple[str, ...],
) -> bool:
    missing = [gate for gate in required_gates if gate not in machine_complete]
    if missing:
        raise ValueError(
            "machine readiness is missing required gates: " + ", ".join(missing)
        )
    return all(machine_complete[gate] for gate in required_gates)


def _load_two_coder_stage(path: Path, blank_loader) -> tuple[str, list[dict[str, str]]]:
    """Return UNSTARTED or COMPLETE; partial or relabeled coder IDs fail closed."""
    try:
        rows = blank_loader(path)
        return "UNSTARTED", rows
    except ValueError as blank_error:
        try:
            rows = load_double_coding(path)
        except ValueError as coded_error:
            raise ValueError(
                "double-coding worksheet is neither valid blank nor fully completed: "
                f"blank={blank_error}; completed={coded_error}"
            ) from coded_error
        coder_ids = {row["coder_id"] for row in rows}
        if coder_ids != {"CODER_A", "CODER_B"}:
            raise ValueError(
                "completed double-coding worksheet must preserve CODER_A/CODER_B IDs"
            )
        return "COMPLETE", rows


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
    u1_sample_path: Path,
    u1_worksheet_path: Path,
    u1_adjudication_path: Path,
    u2_conflict_path: Path,
    u2_sample_path: Path,
    u2_worksheet_path: Path,
    u2_adjudication_path: Path,
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
    u1_sample = load_u1_sample(u1_sample_path)
    u1_coding_stage, u1_worksheet = _load_two_coder_stage(
        u1_worksheet_path,
        load_u1_blank_worksheet,
    )
    u1_adjudication = load_u1_adjudication(
        u1_adjudication_path,
        u1_sample,
        u1_worksheet if u1_coding_stage == "COMPLETE" else None,
    )

    u2 = build_u2_conflict_screen_readout(u2_conflict_path)
    u2_sample = load_u2_double_code_sample(u2_sample_path)
    u2_coding_stage, u2_worksheet = _load_two_coder_stage(
        u2_worksheet_path,
        load_u2_blank_worksheet,
    )
    u2_adjudication = load_u2_adjudication(
        u2_adjudication_path,
        u2_sample,
        u2_worksheet if u2_coding_stage == "COMPLETE" else None,
    )
    u2_receipts = load_plant_predictor_receipts(u2_predictor_receipts_path)
    u2_receipt_coverage = build_receipt_screening_coverage(u2_receipts)

    preoutcome_generality = build_preoutcome_generality_audit(
        u2_conflict_path,
        u2_predictor_receipts_path,
        u6_predictor_receipts_path,
    )

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

    u1_coding_complete = u1_coding_stage == "COMPLETE"
    u2_coding_complete = u2_coding_stage == "COMPLETE"
    u1_adjudication_complete = all(
        row["adjudication_status"] == "ADJUDICATED"
        for row in u1_adjudication
    )
    u2_adjudication_complete = all(
        row["adjudication_status"] == "ADJUDICATED"
        for row in u2_adjudication
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
        "u2_independent_double_coding": not u2_coding_complete,
        "u2_post_coding_adjudication": not u2_adjudication_complete,
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
        "u1_independent_double_coding": not u1_coding_complete,
        "u1_post_coding_adjudication": not u1_adjudication_complete,
    }

    blockers = [name for name, is_open in primary_human_open.items() if is_open]
    primary_machine_ready = _machine_gate_complete(
        machine_complete,
        PRIMARY_MACHINE_GATES,
    )
    external_validation_machine_ready = _machine_gate_complete(
        machine_complete,
        EXTERNAL_VALIDATION_MACHINE_GATES,
    )
    primary_preassembly_ready = (
        primary_machine_ready
        and not blockers
        and preoutcome_generality["v4_main_predictor_design_viable"]
    )

    return {
        "analysis": "balance_plant_v4_programme_readiness",
        "model_specification": "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4",
        "machine_complete": machine_complete,
        "primary_machine_gates": list(PRIMARY_MACHINE_GATES),
        "external_validation_machine_gates": list(
            EXTERNAL_VALIDATION_MACHINE_GATES
        ),
        "all_primary_machine_preparation_complete": primary_machine_ready,
        "all_external_validation_machine_preparation_complete": (
            external_validation_machine_ready
        ),
        "all_machine_preparation_complete": all(machine_complete.values()),
        "primary_human_open_gates": primary_human_open,
        "external_validation_open_gates": external_validation_open,
        "open_gate_names": blockers,
        "preoutcome_design_status": {
            "v4_main_predictor_design_viable": preoutcome_generality[
                "v4_main_predictor_design_viable"
            ],
            "v4_common_slope_design_full_rank": preoutcome_generality[
                "v4_preoutcome_slope_design_full_rank"
            ],
            "v4_universe_stratified_design_full_rank": preoutcome_generality[
                "v4_preoutcome_full_design_full_rank"
            ],
            "temporal_marginal_replication_ready": (
                preoutcome_generality[
                    "cross_universe_replicated_contrasts"
                ]["timing_SIMULTANEOUS_vs_ORDERED"]
            ),
            "temporal_common_support_ready": preoutcome_generality[
                "temporal_cross_universe_common_support_ready"
            ],
            "temporal_common_support_module_strata": preoutcome_generality[
                "temporal_common_support_module_strata"
            ],
        },
        "primary_model_assembly_ready": primary_preassembly_ready,
        "v4_estimability_ready_to_evaluate": primary_preassembly_ready,
        "v3_estimability_ready_to_evaluate": False,
        "reason": (
            "ready for frozen U2/U6 assembly and V4 estimability evaluation"
            if primary_preassembly_ready
            else (
                "U2/U6 independent coding/adjudication gates remain open; V4 model "
                "assembly and estimability must wait for adjudicated outcomes and "
                "predictor receipts"
            )
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

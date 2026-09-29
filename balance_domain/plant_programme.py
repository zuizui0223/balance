"""Programme-level non-pooled evidence map across BALANCE plant macro universes."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from .plant_confirmatory import (
    build_receipt_screening_coverage,
    load_plant_predictor_receipts,
)
from .plant_macro import load_plant_macro_ledger
from .plant_u1_full_screen import build_u1_full47_conflict_screen
from .plant_u2_screen import build_u2_conflict_screen_readout
from .plant_u3_cases import build_u3_case_readout
from .plant_u4 import build_u4_readout
from .plant_u6 import (
    build_u6_evidence_readiness,
    load_u6_cross_universe_dependence,
    load_u6_pass1_freeze_manifest,
    load_u6_pass2_adjudication,
    load_u6_pass2_double_coding,
)


def _screen_readout(path: Path, *, lane: str) -> dict:
    rows = load_plant_macro_ledger(path)
    conflict = Counter(r["conflict_status"] for r in rows)
    architecture = Counter(r["architecture_mode"] for r in rows)
    exclusions = Counter(
        r["exclusion_reason"] for r in rows if r["adjudication_status"] == "EXCLUDED"
    )
    return {
        "lane": lane,
        "n_records": len(rows),
        "n_dependency_groups": len({r["dependency_group"] for r in rows}),
        "conflict_status_counts": dict(sorted(conflict.items())),
        "architecture_mode_counts": dict(sorted(architecture.items())),
        "n_excluded": sum(exclusions.values()),
        "exclusion_reason_counts": dict(sorted(exclusions.items())),
    }


def build_plant_programme_map(
    *,
    u1_screening_path: Path,
    u2_screening_path: Path,
    u3_cases_path: Path,
    u3_universe_path: Path,
    u4_cases_path: Path,
    u1_blind_screen_path: Path | None = None,
    u1_production_screen_path: Path | None = None,
    u2_conflict_screen_path: Path | None = None,
    u6_freeze_path: Path | None = None,
    u6_coding_path: Path | None = None,
    u6_adjudication_path: Path | None = None,
    u6_predictor_receipts_path: Path | None = None,
    u6_dependence_path: Path | None = None,
) -> dict:
    u1_provisional = _screen_readout(u1_screening_path, lane="U1")
    if (u1_blind_screen_path is None) != (u1_production_screen_path is None):
        raise ValueError(
            "U1 full conflict readout requires both first20 and production27 screen paths"
        )
    u1_full = (
        build_u1_full47_conflict_screen(
            u1_blind_screen_path,
            u1_production_screen_path,
        )
        if u1_blind_screen_path is not None
        else None
    )
    u2_provisional = _screen_readout(u2_screening_path, lane="U2")
    u2_strict = (
        build_u2_conflict_screen_readout(u2_conflict_screen_path)
        if u2_conflict_screen_path is not None
        else None
    )
    u3 = build_u3_case_readout(u3_cases_path, u3_universe_path)
    u4 = build_u4_readout(u4_cases_path)

    u6_paths = (
        u6_freeze_path,
        u6_coding_path,
        u6_adjudication_path,
        u6_predictor_receipts_path,
        u6_dependence_path,
    )
    if any(path is not None for path in u6_paths) and not all(
        path is not None for path in u6_paths
    ):
        raise ValueError(
            "U6 programme readout requires freeze, coding, adjudication, predictor "
            "receipts, and dependence paths together"
        )

    u6 = None
    if u6_freeze_path is not None:
        freeze = load_u6_pass1_freeze_manifest(u6_freeze_path)
        coding = load_u6_pass2_double_coding(u6_coding_path, u6_freeze_path)
        adjudication = load_u6_pass2_adjudication(
            u6_adjudication_path,
            u6_freeze_path,
            coding,
        )
        receipts = load_plant_predictor_receipts(u6_predictor_receipts_path)
        dependence = load_u6_cross_universe_dependence(
            u6_dependence_path,
            u6_freeze_path,
        )
        readiness = build_u6_evidence_readiness(
            coding,
            adjudication,
            receipts,
            dependence,
        )
        receipt_coverage = build_receipt_screening_coverage(receipts)
        u6 = {
            "lane": "U6",
            "n_records": freeze["pass1_contract"]["n_anchor_review_references"],
            "n_dependency_groups": len(freeze["included_dependency_groups"]),
            "n_included_dependency_groups": len(freeze["included_dependency_groups"]),
            "pass1_status": freeze["status"],
            "pass2_coding_open": freeze["pass2"]["coding_open"],
            "predictor_source_screen_complete_groups": (
                receipt_coverage["n_complete_outcome_independent_clusters"]
            ),
            "predictor_adjudicated_complete_groups": (
                receipt_coverage["n_complete_adjudicated_clusters"]
            ),
            "evidence_readiness": readiness,
            "sampling_role": "CONFLICT_FIRST_POLLEN_THEFT_ARCHITECTURE_BLIND",
            "licensed_use": (
                "architecture-blind conflict-first replication plus independent "
                "routing/predictor coding"
            ),
            "not_licensed": (
                "primary model entry until coding, reliability, adjudication, and "
                "predictor-receipt gates close"
            ),
        }

    # Never compute a pooled positive fraction: the universes are intentionally
    # sampled for different purposes (broad specificity, mechanism, cases, stress test).
    return {
        "analysis": "balance_plant_macro_programme_map",
        "lanes": {
            "U1": {
                "lane": "U1",
                "n_records": (
                    u1_full["n_records"] if u1_full is not None
                    else u1_provisional["n_records"]
                ),
                "n_dependency_groups": (
                    u1_full["n_dependency_groups"] if u1_full is not None
                    else u1_provisional["n_dependency_groups"]
                ),
                "conflict_status_counts": (
                    u1_full["conflict_status_counts"] if u1_full is not None
                    else u1_provisional["conflict_status_counts"]
                ),
                "strict_conflict_source_screen_complete": u1_full is not None,
                "strict_conflict_positive_ids": (
                    u1_full["positive_conflict_ids"] if u1_full is not None else None
                ),
                "strict_conflict_unresolved_ids": (
                    u1_full["unresolved_candidate_ids"] if u1_full is not None else None
                ),
                "provisional_first20_macro_readout": u1_provisional,
                "sampling_role": "BROAD_INTERACTION_SPECIFICITY",
                "licensed_use": (
                    "tests whether herbivory-pollination literature survives the "
                    "shared-reproductive-coordinate and conflict gates"
                ),
                "not_licensed": "prevalence comparison with U2-U6",
            },
            "U2": {
                "lane": "U2",
                "n_records": (
                    u2_strict["n_dependency_groups"] if u2_strict is not None
                    else u2_provisional["n_records"]
                ),
                "n_dependency_groups": (
                    u2_strict["n_dependency_groups"] if u2_strict is not None
                    else u2_provisional["n_dependency_groups"]
                ),
                "conflict_status_counts": (
                    u2_strict["conflict_status_counts"] if u2_strict is not None
                    else u2_provisional["conflict_status_counts"]
                ),
                "strict_conflict_source_screen_complete": u2_strict is not None,
                "provisional_macro_readout": u2_provisional,
                "sampling_role": "MECHANISM_TARGETED_SEXUAL_INTERFERENCE",
                "licensed_use": (
                    "source-defined mechanism screen plus independent-coder reliability sample"
                ),
                "not_licensed": "natural prevalence of sexual interference",
            },
            "U3": {
                "lane": "U3",
                **u3,
                "sampling_role": "STRUCTURAL_POSITIVE_CASE_CONTROL_DEVELOPMENT",
                "licensed_use": "source-resolved heteranthery cases and matched-control design",
                "not_licensed": "prevalence or unmatched case coefficient",
            },
            "U4": {
                "lane": "U4",
                **u4,
                "sampling_role": "POLLINATOR_PREY_MECHANISM_STRESS_TEST",
                "licensed_use": (
                    "tests whether conflict, selfing buffer and spatial/signal architecture "
                    "can be distinguished within one function pair"
                ),
                "not_licensed": "prevalence of pollinator-prey conflict",
            },
            **({"U6": u6} if u6 is not None else {}),
        },
        "cross_lane_invariants": [
            "review_or_case_membership_does_not_imply_positive_conflict",
            "observed_separation_does_not_identify_historical_causation",
            "interaction_does_not_imply_shared_coordinate_conflict",
            "sampling_roles_are_not_exchangeable",
            "focal_architecture_outcome_cannot_license_confirmatory_predictors",
        ],
        "pooled_prevalence_estimate": None,
        "primary_model_contract": {
            "specification": "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4",
            "response": "architecture_class4",
            "primary_universes": [
                "U2_BARRETT_2002",
                "U6_POLLEN_THEFT_HARGREAVES_2009",
            ],
            "external_validation_universes": [
                "U1_HAAS_LORTIE_2020",
            ],
            "raw_predictors": [
                "module_substrate",
                "conflict_timing_geometry",
                "conflict_spatial_geometry",
            ],
            "fit_predictor_contrasts": [
                "module_opportunity2",
                "temporal_exposure3",
            ],
            "secondary_predictor_contrasts": [
                "spatial_exposure2",
            ],
            "maximum_main_fixed_coefficients": 15,
            "universe_stratified_intercepts": True,
            "predictor_receipts_required": True,
            "outcome_dependent_fallback_allowed": False,
            "u1_u3_u4_primary_denominator_allowed": False,
        },
        "primary_model_ready": False,
        "primary_model_blockers": [
            "U2 independent double coding incomplete",
            "U6 independent double coding incomplete",
            "three adjudicated outcome-independent predictor receipts per admitted U2/U6 cluster not yet closed",
            "final U2/U6 model assembly and cross-universe dependence ledger not yet closed",
            "v4 estimability gate cannot be evaluated until final adjudicated architecture classes are assembled",
        ],
        "parallel_nonblocking_work": [
            "U1 independent coding as external specificity validation",
            "U3 matched/case-control measurements and controls",
            "U4 pollinator-prey mechanism stress test",
        ],
        "claim_ceiling": (
            "programme_map_only_no_cross_lane_prevalence_pooling_"
            "no_direct_R_K_Phi_rho_xi_dB"
        ),
    }

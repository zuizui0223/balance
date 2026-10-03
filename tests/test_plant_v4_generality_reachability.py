import csv
import json
from pathlib import Path

from balance_domain.plant_preoutcome_generality import (
    build_preoutcome_generality_audit,
)
from balance_domain.plant_predictor_adjudication import IMMUTABLE_RECEIPT_FIELDS


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "BALANCE_PLANT_V4_GENERALITY_REACHABILITY_V1.json"
U2_CONFLICT = ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv"
U2_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U6_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
MODEL_SPEC = ROOT / "data" / "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4.json"
REACTIVATION = ROOT / "data" / "BALANCE_PLANT_V4_REACTIVATION_GATE_V1.json"


def _rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_v4_strict_generality_is_unreachable_under_frozen_receipt_surface():
    audit = build_preoutcome_generality_audit(
        U2_CONFLICT,
        U2_RECEIPTS,
        U6_RECEIPTS,
    )
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert "reported_value" in IMMUTABLE_RECEIPT_FIELDS
    assert audit["u2_complete_outcome_independent_predictor_groups"] == 8
    assert audit["u2_complete_predictor_groups_equal_source_positive"] is True
    assert audit["final_u2_licensed_rows_are_subset_only_under_frozen_receipts"] is True
    assert audit["temporal_common_support_module_strata"] == []
    assert audit[
        "temporal_common_support_reachable_without_predictor_receipt_expansion"
    ] is False
    assert audit["temporal_common_support_reachability_shortfall"] == {
        "SINGLE": {
            "U2": {
                "SIMULTANEOUS": 1,
                "ORDERED_OR_ALTERNATING": 0,
            },
            "U6": {
                "SIMULTANEOUS": 0,
                "ORDERED_OR_ALTERNATING": 0,
            },
        }
    }

    reachability = contract["current_reachability"]
    assert reachability[
        "strict_temporal_generality_reachable_without_predictor_expansion"
    ] is False
    assert reachability["limiting_cell"] == "U2_SINGLE_SIMULTANEOUS"
    assert reachability["current_blocks"] == 1
    assert reachability["required_blocks"] == 2
    assert reachability["main_V4_fit_affected"] is False


def test_any_prospective_reopening_must_expand_all_frozen_unresolved_u2_groups():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    expansion = contract["prospective_reopening_contract"]

    unresolved_groups = sorted({
        row["cluster_id"]
        for row in _rows(U2_RECEIPTS)
        if row["reported_value"] == "UNRESOLVED"
    })
    assert len(unresolved_groups) == 12
    assert expansion["selective_gap_filling_forbidden"] is True
    assert expansion["expansion_slots"] == 36
    assert expansion["expansion_group_ids"] == unresolved_groups
    assert expansion[
        "allowed_only_before_independent_architecture_outcomes_are_opened"
    ] is True
    assert expansion["common_support_threshold_unchanged"] is True


def test_active_v4_contracts_link_same_generality_reachability_ceiling():
    target = "data/BALANCE_PLANT_V4_GENERALITY_REACHABILITY_V1.json"
    model = json.loads(MODEL_SPEC.read_text(encoding="utf-8"))
    gate = json.loads(REACTIVATION.read_text(encoding="utf-8"))

    assert model["generality_reachability_contract"] == target
    assert gate["generality_reachability_contract"] == target
    assert model["claim_hierarchy"]["cross_universe_replicated"]["reachability"] == (
        "UNREACHABLE_WITHOUT_PROSPECTIVE_VERSIONED_PREDICTOR_RECEIPT_EXPANSION"
    )
    assert (
        model["temporal_generality_sensitivity"][
            "reachability_without_predictor_receipt_expansion"
        ]
        is False
    )
    assert (
        gate["current_v4_generality_reachability"][
            "strict_temporal_generality_reachable_without_predictor_receipt_expansion"
        ]
        is False
    )

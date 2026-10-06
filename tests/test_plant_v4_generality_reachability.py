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
PUBLICATION_STATUS = ROOT / "docs" / "PUBLICATION_STATUS.md"


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



def test_generality_reopening_contract_points_to_frozen_expansion_implementation():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    implementation = contract["prospective_reopening_contract"]["implementation"]

    expected_paths = {
        "coding_template": "data/BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv",
        "source_packet": "data/BALANCE_PLANT_U2_PREDICTOR_EXPANSION_SOURCE_PACKET_V2.csv",
        "coding_protocol": "docs/BALANCE_PLANT_U2_PREDICTOR_EXPANSION_PROTOCOL_V2.md",
        "packet_builder": "scripts/build_plant_u2_predictor_expansion_packet.py",
        "packet_workflow": ".github/workflows/build-plant-u2-predictor-expansion.yml",
        "v2_freeze_cli": "scripts/freeze_plant_u2_predictor_receipts_v2.py",
    }
    for key, rel in expected_paths.items():
        assert implementation[key] == rel
        assert (ROOT / rel).exists()

    assert implementation["validator_module"] == (
        "balance_domain.plant_predictor_expansion"
    )
    assert implementation["frozen_v2_output"] == (
        "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2.csv"
    )
    assert implementation["post_coding_status"] == (
        "FROZEN_SCREENED_AWAITING_INDEPENDENT_ADJUDICATION"
    )



def test_v2_route_is_executed_and_mechanically_reachable_but_real_support_unopened():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    model = json.loads(MODEL_SPEC.read_text(encoding="utf-8"))
    gate = json.loads(REACTIVATION.read_text(encoding="utf-8"))

    current_contract = contract["current_reachability"]
    assert current_contract["v2_expansion_handoff_executed"] is True
    assert current_contract["v2_mechanical_reachability_proven"] is True
    assert current_contract["v2_real_human_return_received"] is False
    assert current_contract["v2_frozen_receipt_frame_available"] is False
    assert current_contract["common_support_threshold_changed"] is False

    witness = contract["prospective_reopening_contract"][
        "constructive_mechanical_witness"
    ]
    assert witness["test"] == (
        "tests/test_plant_v4_end_to_end_prefit.py::"
        "test_u2_v2_expansion_has_constructive_strict_generality_witness"
    )

    v2 = model["claim_hierarchy"]["cross_universe_replicated"]["v2_route"]
    assert v2["handoff_executed"] is True
    assert v2["mechanical_reachability_proven"] is True
    assert v2["human_expansion_return_received"] is False
    assert v2["frozen_v2_receipt_frame_available"] is False
    assert v2["threshold_changed"] is False

    generality = model["temporal_generality_sensitivity"]
    assert generality["reachability_without_predictor_receipt_expansion"] is False
    assert generality["v2_expansion_route_mechanically_reachable"] is True
    assert generality["v2_real_support_status"] == (
        "AWAITING_COMPLETE_INDEPENDENT_EXPANSION_RETURN_FREEZE_"
        "ADJUDICATION_AND_FINAL_ARCHITECTURE_ADMISSION"
    )

    current = gate["current_v4_generality_reachability"]
    assert current[
        "strict_temporal_generality_reachable_without_predictor_receipt_expansion"
    ] is False
    assert current["v2_expansion_handoff_executed"] is True
    assert current["v2_route_mechanically_reachable_under_unchanged_gate"] is True
    assert current["v2_real_human_return_received"] is False
    assert current["v2_frozen_receipt_frame_available"] is False
    assert current["common_support_threshold_changed"] is False


def test_v2_reachability_does_not_predeclare_reactivation_or_real_common_support():
    model = json.loads(MODEL_SPEC.read_text(encoding="utf-8"))
    gate = json.loads(REACTIVATION.read_text(encoding="utf-8"))

    assert gate["standalone_reactivation_eligible"] is False
    assert gate["required_conditions"]["temporal_common_support_module_stratum_ready"] is False
    assert gate["required_conditions"]["temporal_generality_outcome_support_ready"] is False
    assert model["preoutcome_design_audit"]["v2_expansion_real_support_opened"] is False
    assert (
        model["preoutcome_design_audit"][
            "strict_temporal_generality_mechanically_reachable_via_v2_expansion"
        ]
        is True
    )



def test_publication_status_distinguishes_v1_ceiling_v2_reachability_and_real_evidence():
    text = PUBLICATION_STATUS.read_text(encoding="utf-8")
    assert "original frozen **U2 V1 predictor-receipt surface**" in text
    assert "V1 strict G1 route       = structurally unreachable" in text
    assert "V2 registered route      = prospectively executed / mechanically reachable" in text
    assert "real cross-universe G1   = unopened pending independent human returns" in text
    assert "The common-support threshold has not been weakened." in text

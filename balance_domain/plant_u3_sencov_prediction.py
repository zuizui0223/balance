"""Prospective Senna covesii routing prediction from pre-outcome module substrate.

The prediction is deliberately narrow. It converts the current U3 discovery
pattern into a falsifiable target before S. covesii routing is measured. It is
not an independent evolutionary replication because the target shares the
Senna dependence block with one discovery control.
"""
from __future__ import annotations

import json
from pathlib import Path

from .plant_u3_dependence import load_u3_dependence
from .plant_u3_matched_extraction import load_u3_matched_extraction


TARGET_TAXON = "Senna covesii"
TARGET_STATUS = "FROZEN_BEFORE_TARGET_ROUTING_OUTCOME"
PREDICTED_ROUTE = "WITHIN_FLOWER_DIVISION_OF_LABOUR"
TARGET_SUBSTRATE = "SERIAL_WITHIN_FLOWER"


def load_sencov_prediction(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("analysis") != "balance_u3_sencov_routing_prediction_v1":
        raise ValueError("wrong Senna covesii prediction analysis id")
    if payload.get("status") != TARGET_STATUS:
        raise ValueError("Senna covesii prediction must remain prospectively frozen")
    target = payload.get("target", {})
    if target.get("taxon") != TARGET_TAXON:
        raise ValueError("wrong Senna covesii prediction target")
    if target.get("module_substrate") != TARGET_SUBSTRATE:
        raise ValueError("Senna covesii target substrate drift")
    if target.get("predicted_routing_state") != PREDICTED_ROUTE:
        raise ValueError("Senna covesii predicted routing state drift")
    if target.get("routing_outcome_at_freeze") != "UNRESOLVED":
        raise ValueError("prediction must be frozen before target routing resolution")
    if payload.get("independent_block_replication") is not False:
        raise ValueError("Senna covesii prediction must not claim independent-block replication")
    return payload


def build_sencov_prediction_readout(
    prediction_path: Path,
    extraction_path: Path,
    dependence_path: Path,
    adjudication_path: Path,
    pair_path: Path,
    case_path: Path,
    universe_path: Path,
) -> dict:
    prediction = load_sencov_prediction(prediction_path)
    rows = load_u3_matched_extraction(
        extraction_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )
    dependence = load_u3_dependence(
        dependence_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )
    dep_by_pair = {r["pair_id"]: r["dependence_block_id"] for r in dependence}

    controls = [r for r in rows if r["taxon_role"] == "CONTROL"]
    target = next((r for r in controls if r["taxon"] == TARGET_TAXON), None)
    if target is None:
        raise ValueError("Senna covesii target is absent from matched extraction")
    if target["pollen_fate_conflict_status"] != "POSITIVE":
        raise ValueError("Senna covesii prediction requires positive binary conflict")
    if target["architecture_mode"] != "UNRESOLVED":
        raise ValueError("Senna covesii routing outcome is no longer blinded/unresolved")
    if target["module_substrate"] != TARGET_SUBSTRATE:
        raise ValueError("Senna covesii extraction substrate drift")

    discovery = [
        r
        for r in controls
        if r["taxon"] != TARGET_TAXON
        and r["pollen_fate_conflict_status"] == "POSITIVE"
        and r["architecture_mode"] != "UNRESOLVED"
    ]
    mapping: dict[str, set[str]] = {}
    for row in discovery:
        mapping.setdefault(row["module_substrate"], set()).add(row["architecture_mode"])

    serial_routes = mapping.get(TARGET_SUBSTRATE, set())
    if serial_routes != {PREDICTED_ROUTE}:
        raise ValueError(
            "discovery surface no longer uniquely supports the frozen serial-module prediction"
        )
    if mapping.get("REPEATED_FLOWERS") != {"AMONG_FLOWER_MODULE_DIVISION"}:
        raise ValueError("discovery repeated-flower routing pattern drift")

    discovery_receipts = sorted(
        [
            {
                "taxon": r["taxon"],
                "pair_id": r["pair_id"],
                "dependence_block_id": dep_by_pair[r["pair_id"]],
                "module_substrate": r["module_substrate"],
                "routing_state": r["architecture_mode"],
            }
            for r in discovery
        ],
        key=lambda x: x["taxon"],
    )
    target_pair_id = target["pair_id"]
    target_block = dep_by_pair[target_pair_id]
    discovery_blocks = {r["dependence_block_id"] for r in discovery_receipts}

    return {
        "analysis": "balance_u3_sencov_routing_prediction_readout_v1",
        "status": TARGET_STATUS,
        "target_taxon": TARGET_TAXON,
        "target_conflict_status": "POSITIVE",
        "target_module_substrate": TARGET_SUBSTRATE,
        "target_routing_status_at_freeze": "UNRESOLVED",
        "predicted_routing_state": PREDICTED_ROUTE,
        "discovery_receipts": discovery_receipts,
        "n_discovery_controls": len(discovery_receipts),
        "n_discovery_dependence_blocks": len(discovery_blocks),
        "target_dependence_block_id": target_block,
        "target_is_independent_new_dependence_block": target_block not in discovery_blocks,
        "prediction_scope": (
            "prospective_within_matched_lane_species_test_not_independent_"
            "evolutionary_replication"
        ),
        "support_rule": (
            "target routing is source-resolved under the frozen U3MEAS_SENCOV_001 "
            "measurement contract as WITHIN_FLOWER_DIVISION_OF_LABOUR"
        ),
        "falsification_rule": (
            "a source-resolved target routing state other than "
            "WITHIN_FLOWER_DIVISION_OF_LABOUR falsifies the frozen directional prediction"
        ),
        "inconclusive_rule": (
            "UNRESOLVED target classification due to insufficient precision neither "
            "supports nor falsifies the prediction"
        ),
        "claim_ceiling": (
            "single_target_prospective_routing_prediction_only_not_general_module_rule_"
            "not_independent_block_replication_not_causal_effect_not_historical_transition"
        ),
    }

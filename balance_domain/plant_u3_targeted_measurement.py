"""Prospective measurement contracts for the remaining U3 evidence ceilings."""
from __future__ import annotations

import json
from pathlib import Path


EXPECTED = {
    "U3MEAS_MONAUS_001": (
        "Monochoria australasica",
        "DIRECT_SPECIES_LEVEL_EFFECTIVE_ANIMAL_POLLINATION",
    ),
    "U3MEAS_MONCYA_001": (
        "Monochoria cyanea",
        "DIRECT_SPECIES_LEVEL_EFFECTIVE_ANIMAL_POLLINATION",
    ),
    "U3MEAS_OSBCHI_001": (
        "Osbeckia chinensis",
        "CONTROL_POLLEN_FATE_CONFLICT",
    ),
}

FORBIDDEN_SHORTCUTS = {
    "U3MEAS_MONAUS_001": {
        "bee territorial behaviour near plants",
        "general genus/family buzz-pollination statements",
    },
    "U3MEAS_MONCYA_001": {
        "general genus/family buzz-pollination statements",
    },
    "U3MEAS_OSBCHI_001": {
        "pollen extraction alone",
        "stigma contact alone",
    },
}


def load_u3_targeted_measurement_spec(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("analysis") != "balance_plant_u3_targeted_measurement_spec_v1":
        raise ValueError("wrong U3 targeted-measurement analysis id")
    if data.get("status") != "FROZEN_BEFORE_NEW_EVIDENCE":
        raise ValueError("U3 targeted measurement spec must remain prospectively frozen")

    targets = data.get("targets")
    if not isinstance(targets, dict) or set(targets) != set(EXPECTED):
        raise ValueError("U3 targeted measurement spec must register exactly three targets")

    for target_id, (taxon, gate) in EXPECTED.items():
        row = targets[target_id]
        if row.get("taxon") != taxon or row.get("gate") != gate:
            raise ValueError(f"{target_id} target identity drift")
        routes = row.get("admissible_routes")
        if not isinstance(routes, list) or not routes:
            raise ValueError(f"{target_id} requires at least one admissible evidence route")
        for route in routes:
            if not route.get("route") or not isinstance(route.get("required"), list):
                raise ValueError(f"{target_id} malformed evidence route")
            if not route["required"]:
                raise ValueError(f"{target_id} evidence route cannot be empty")

        insufficient = set(row.get("explicitly_insufficient") or [])
        if not FORBIDDEN_SHORTCUTS[target_id].issubset(insufficient):
            raise ValueError(f"{target_id} lost a registered fail-closed shortcut guard")
        if not row.get("pass_rule") or not row.get("claim_ceiling"):
            raise ValueError(f"{target_id} pass rule and claim ceiling must be frozen")

    rules = data.get("global_rules")
    if not isinstance(rules, list) or len(rules) < 4:
        raise ValueError("U3 targeted measurement spec requires global anti-leakage rules")
    return data


def build_u3_targeted_measurement_readout(path: Path) -> dict:
    data = load_u3_targeted_measurement_spec(path)
    targets = data["targets"]
    return {
        "analysis": data["analysis"],
        "n_targets": len(targets),
        "target_taxa": sorted(v["taxon"] for v in targets.values()),
        "gates": {v["taxon"]: v["gate"] for v in targets.values()},
        "route_counts": {
            v["taxon"]: len(v["admissible_routes"]) for v in targets.values()
        },
        "status": data["status"],
        "claim_ceiling": (
            "prospective_measurement_contract_only_not_observed_result_"
            "not_effect_estimate_not_gate_closure"
        ),
    }

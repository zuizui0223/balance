"""Prospective measurement contracts for the remaining U3 evidence ceilings."""
from __future__ import annotations

import json
from pathlib import Path


ANALYSIS_ID = "balance_plant_u3_targeted_measurement_spec_v2"

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
    "U3MEAS_SENCOV_001": (
        "Senna covesii",
        "CONFLICT_CONDITIONED_ROUTING_ARCHITECTURE",
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
    "U3MEAS_SENCOV_001": {
        "seven fertile stamens plus monosymmetry alone",
        "genus-level feeding-versus-pollinating stamen homology alone",
        "buzz visitation or pollen reward alone",
        "non-significant positional difference without an equivalence test",
        "pooled pollen deposition without source resolution by stamen position",
    },
}


def load_u3_targeted_measurement_spec(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("analysis") != ANALYSIS_ID:
        raise ValueError("wrong U3 targeted-measurement analysis id")
    if data.get("status") != "FROZEN_BEFORE_NEW_EVIDENCE":
        raise ValueError("U3 targeted measurement spec must remain prospectively frozen")

    targets = data.get("targets")
    if not isinstance(targets, dict) or set(targets) != set(EXPECTED):
        raise ValueError("U3 targeted measurement spec must register exactly four targets")

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

    sencov = targets["U3MEAS_SENCOV_001"]
    if sencov.get("position_groups") != {
        "median": "four median fertile stamen positions",
        "abaxial": "three abaxial fertile stamen positions",
    }:
        raise ValueError("Senna covesii positional groups must be frozen before routing outcomes")
    if not sencov.get("shared_integrated_rule"):
        raise ValueError("Senna covesii requires a prospective SHARED_INTEGRATED equivalence rule")
    if "equivalence" not in sencov["shared_integrated_rule"].casefold():
        raise ValueError("Senna covesii shared-integration rule must require equivalence evidence")

    rules = data.get("global_rules")
    if not isinstance(rules, list) or len(rules) < 6:
        raise ValueError("U3 targeted measurement spec requires global anti-leakage rules")
    return data


def build_u3_targeted_measurement_readout(path: Path) -> dict:
    data = load_u3_targeted_measurement_spec(path)
    targets = data["targets"]
    sencov = targets["U3MEAS_SENCOV_001"]
    return {
        "analysis": data["analysis"],
        "n_targets": len(targets),
        "target_taxa": sorted(v["taxon"] for v in targets.values()),
        "gates": {v["taxon"]: v["gate"] for v in targets.values()},
        "route_counts": {
            v["taxon"]: len(v["admissible_routes"]) for v in targets.values()
        },
        "senna_covesii_routing_contract_frozen": True,
        "senna_covesii_position_groups": sencov["position_groups"],
        "senna_covesii_shared_integrated_requires_equivalence": True,
        "status": data["status"],
        "claim_ceiling": (
            "prospective_measurement_contract_only_not_observed_result_"
            "not_effect_estimate_not_gate_closure"
        ),
    }

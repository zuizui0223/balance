from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_SENTINEL = "REQUIRED_BEFORE_USE"
READY_NUISANCE_STATUS = "NUISANCE_RECEIPT_READY_FOR_POWER_INPUT"


def _required_paths(value: Any, prefix: str = "") -> list[str]:
    missing: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            missing.extend(_required_paths(child, child_prefix))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            child_prefix = f"{prefix}[{idx}]"
            missing.extend(_required_paths(child, child_prefix))
    elif value == REQUIRED_SENTINEL:
        missing.append(prefix)
    return missing


def prepare(nuisance: dict, targets: dict) -> dict:
    errors: list[str] = []
    if nuisance.get("status") != READY_NUISANCE_STATUS:
        errors.append(
            f"nuisance_status_not_ready:{nuisance.get('status', 'MISSING')}"
        )

    missing_targets = _required_paths(targets)
    errors.extend(f"unfrozen_target:{path}" for path in missing_targets)

    target_rule = str(targets.get("target_source_rule", ""))
    if "Stage-0 observed treatment effects must not be used" not in target_rule:
        errors.append("target_source_rule_missing_stage0_anticircularity_guard")

    balance = targets.get("BALANCE", {})
    if balance.get("architecture_qualification_must_pass_before_powering") is not True:
        errors.append("balance_architecture_gate_not_required")

    result = {
        "analysis": "pedicularis_power_configuration_gate_v1",
        "status": "POWER_CONFIG_READY_FOR_SIMULATION" if not errors else "POWER_CONFIG_NOT_READY",
        "errors": errors,
        "claim_ceiling": (
            "simulation_input_only_not_a_power_result_and_not_empirical_evidence"
        ),
        "anti_circularity_rule": (
            "minimum meaningful effects are frozen independently of Stage-0 treatment-effect estimates"
        ),
        "nuisance": nuisance,
        "targets": targets,
    }
    if not errors:
        result["simulation_contract"] = {
            "primary_outcome": "undamaged_mature_viable_seeds_per_focal_flower",
            "cluster_unit": "plant_id",
            "ecological_design_cells": 40,
            "remaining_channel_assay_cells": 4,
            "choose_final_n_by": "hardest_required_registered_decision_or_route_one_paper_to_separate_design",
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("nuisance_json", type=Path)
    parser.add_argument("targets_json", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    nuisance = json.loads(args.nuisance_json.read_text(encoding="utf-8"))
    targets = json.loads(args.targets_json.read_text(encoding="utf-8"))
    result = prepare(nuisance, targets)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

    if result["status"] != "POWER_CONFIG_READY_FOR_SIMULATION":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

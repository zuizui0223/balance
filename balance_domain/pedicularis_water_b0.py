"""Fail-closed preregistered method-feasibility screening for Pedicularis B0.

Unit: one confirmed water-holding bract/whorl compartment per plant.
This module must NOT read pollen, seed outcomes, oviposition or other
biological treatment outcomes. A PASS establishes method feasibility only.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from math import isfinite
from statistics import fmean

SCHEMA = "PEDICULARIS_WATER_B0_METHOD_THRESHOLDS_V1"
ARMS = ("INTACT_WET", "INTACT_DRY", "INTACT_REFILLED_WET")
FIELDS = (
    "context_id", "population_id", "season_id", "protocol_version",
    "plant_id", "water_compartment_id", "block_id", "assigned_arm",
    "water_compartment_confirmed",
    "assignment_locked_before_measurement", "bract_perforated",
    "water_depth_early_mm", "water_depth_late_mm",
    "handling_duration_seconds", "abs_exsertion_shift_mm",
    "mechanical_damage", "pollinator_entry_unobstructed",
)
THRESHOLDS = (
    "min_independent_plants_per_arm", "min_blocks_per_arm",
    "min_wet_depth_mm", "max_dry_depth_mm",
    "min_water_fidelity_fraction", "max_missing_measurement_fraction",
    "max_mechanical_damage_fraction", "max_exsertion_shift_mm",
    "max_exsertion_offtarget_fraction",
    "min_pollinator_entry_unobstructed_fraction",
    "max_dry_vs_refilled_handling_gap_seconds",
)
INTEGER_THRESHOLDS = {
    "min_independent_plants_per_arm", "min_blocks_per_arm",
}
FRACTION_THRESHOLDS = {
    "min_water_fidelity_fraction", "max_missing_measurement_fraction",
    "max_mechanical_damage_fraction", "max_exsertion_offtarget_fraction",
    "min_pollinator_entry_unobstructed_fraction",
}


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonblank text")
    if value.strip().upper() == "REQUIRED_BEFORE_USE":
        raise ValueError(f"{name} must be frozen before use")
    return value.strip()


def _num(value, name, *, missing=False):
    if value is None or str(value).strip() == "":
        if missing:
            return None
        raise ValueError(f"{name} required")
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    try:
        x = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(f"{name} invalid numeric input") from exc
    if not isfinite(x) or x < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return x


def _bool(value, name):
    if str(value).strip() not in {"0", "1"}:
        raise ValueError(f"{name} must be exactly 0 or 1")
    return str(value).strip() == "1"


def _validate_config(config):
    if not isinstance(config, dict) or config.get("schema_version") != SCHEMA:
        raise ValueError("B0 method threshold schema mismatch")
    if config.get("status") != "FROZEN_PRE_OUTCOME":
        raise ValueError("B0 thresholds are not prospectively frozen")
    if config.get("blinded_to_reproductive_outcomes") is not True:
        raise ValueError("B0 method assessment must be blinded to outcomes")
    ids = {}
    for key in ("context_id", "population_id", "season_id", "protocol_version"):
        ids[key] = _text(config.get(key), key)
    _text(config.get("threshold_justification"), "threshold_justification")
    schedule = _text(config.get("randomization_schedule_sha256"),
                     "randomization_schedule_sha256")
    if len(schedule) != 64 or any(c not in "0123456789abcdef" for c in schedule):
        raise ValueError("randomization schedule SHA256 must be lowercase hex")
    limits = config.get("thresholds")
    if not isinstance(limits, dict) or set(limits) != set(THRESHOLDS):
        raise ValueError("B0 threshold key set mismatch")
    out = {}
    for key in THRESHOLDS:
        x = _num(limits[key], key)
        if key in INTEGER_THRESHOLDS:
            if not x.is_integer() or x < 2:
                raise ValueError(f"{key} requires integer >=2")
            out[key] = int(x)
        else:
            if key in FRACTION_THRESHOLDS and x > 1:
                raise ValueError(f"{key} requires fraction within [0,1]")
            out[key] = x
    if out["min_wet_depth_mm"] <= out["max_dry_depth_mm"]:
        raise ValueError("B0 wet and dry separation thresholds overlap")
    return ids, out


def evaluate_water_b0(rows, config):
    """Screen method feasibility; never estimate biological treatment effects."""
    ids, limits = _validate_config(config)
    rows = list(rows)
    if not rows:
        raise ValueError("no B0 method observations")
    groups = defaultdict(list)
    seen = set()
    seen_plants = set()
    errors = []
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != set(FIELDS):
            raise ValueError(f"B0 row {i} has noncanonical field set")
        for key in ids:
            if _text(row.get(key), f"row {i}.{key}") != ids[key]:
                raise ValueError(f"B0 row {i} mismatches frozen {key}")
        arm = _text(row["assigned_arm"], "assigned_arm")
        if arm not in ARMS:
            raise ValueError(f"unknown B0 assigned arm {arm}")
        plant = _text(row["plant_id"], "plant_id")
        compartment = _text(row["water_compartment_id"], "water_compartment_id")
        block = _text(row["block_id"], "block_id")
        if compartment in seen:
            raise ValueError("duplicate B0 water_compartment_id")
        seen.add(compartment)
        # Pilot v1 randomizes ONE water-holding compartment per plant.
        # Bracts may serve multiple flowers, so flower-level assignments
        # or repeated plant weights would create interference/pseudoreplication.
        if plant in seen_plants:
            raise ValueError("duplicate plant_id: B0 pilot requires one compartment per plant")
        seen_plants.add(plant)
        if not _bool(row["water_compartment_confirmed"],
                     "water_compartment_confirmed"):
            errors.append("physical_water_compartment_unverified")
        if not _bool(row["assignment_locked_before_measurement"],
                     "assignment_locked_before_measurement"):
            errors.append("assignment_not_prelocked")
        perforated = _bool(row["bract_perforated"], "bract_perforated")
        damaged = _bool(row["mechanical_damage"], "mechanical_damage")
        entry = _bool(row["pollinator_entry_unobstructed"],
                      "pollinator_entry_unobstructed")
        early = _num(row["water_depth_early_mm"], "water_depth_early_mm",
                     missing=True)
        late = _num(row["water_depth_late_mm"], "water_depth_late_mm",
                    missing=True)
        duration = _num(row["handling_duration_seconds"],
                        "handling_duration_seconds", missing=True)
        exsertion = _num(row["abs_exsertion_shift_mm"],
                         "abs_exsertion_shift_mm", missing=True)
        observed = {
            "plant_id": plant, "block_id": block, "perforated": perforated,
            "damaged": damaged, "entry": entry,
            "water_early": early, "water_late": late,
            "handling_duration": duration, "exsertion_shift": exsertion,
        }
        groups[arm].append(observed)
    reasons = set(errors)
    summaries = {}
    for arm in ARMS:
        data = groups[arm]
        if not data:
            reasons.add(f"missing_arm:{arm}")
            summaries[arm] = {"n_flowers": 0, "n_distinct_plants": 0,
                              "n_blocks": 0}
            continue
        plants = len({r["plant_id"] for r in data})
        blocks = len({r["block_id"] for r in data})
        if plants < limits["min_independent_plants_per_arm"]:
            reasons.add(f"insufficient_plants:{arm}")
        if blocks < limits["min_blocks_per_arm"]:
            reasons.add(f"insufficient_blocks:{arm}")
        if any(r["perforated"] for r in data):
            reasons.add(f"bract_perforation:{arm}")
        water_fidelity = sum(
            r["water_early"] is not None and r["water_late"] is not None
            and all(
                v >= limits["min_wet_depth_mm"] if arm != "INTACT_DRY"
                else v <= limits["max_dry_depth_mm"]
                for v in (r["water_early"], r["water_late"])
            ) for r in data
        ) / len(data)
        if water_fidelity < limits["min_water_fidelity_fraction"]:
            reasons.add(f"water_state_not_maintained:{arm}")
        missing = sum(
            r[k] is None for r in data
            for k in ("water_early", "water_late", "handling_duration",
                      "exsertion_shift")
        ) / (4 * len(data))
        if missing > limits["max_missing_measurement_fraction"]:
            reasons.add(f"method_measurements_missing:{arm}")
        damage = sum(r["damaged"] for r in data) / len(data)
        if damage > limits["max_mechanical_damage_fraction"]:
            reasons.add(f"damage_exceeds_limit:{arm}")
        off = sum(r["exsertion_shift"] is None
                  or r["exsertion_shift"] > limits["max_exsertion_shift_mm"]
                  for r in data) / len(data)
        if off > limits["max_exsertion_offtarget_fraction"]:
            reasons.add(f"exsertion_offtarget:{arm}")
        access = sum(r["entry"] for r in data) / len(data)
        if access < limits["min_pollinator_entry_unobstructed_fraction"]:
            reasons.add(f"pollinator_entry_restricted:{arm}")
        duration_values = [r["handling_duration"] for r in data
                           if r["handling_duration"] is not None]
        summaries[arm] = {
            "n_flowers": len(data), "n_distinct_plants": plants,
            "n_blocks": blocks, "water_fidelity_fraction": water_fidelity,
            "measurement_missing_fraction": missing,
            "mechanical_damage_fraction": damage,
            "exsertion_offtarget_fraction": off,
            "pollinator_entry_unobstructed_fraction": access,
            "mean_handling_seconds": fmean(duration_values)
            if duration_values else None,
            "n_perforated": sum(r["perforated"] for r in data),
        }
    dry = summaries["INTACT_DRY"].get("mean_handling_seconds")
    refill = summaries["INTACT_REFILLED_WET"].get("mean_handling_seconds")
    handling_gap = None
    if dry is None or refill is None:
        reasons.add("handling_duration_not_estimable")
    else:
        handling_gap = abs(dry-refill)
        if handling_gap > limits["max_dry_vs_refilled_handling_gap_seconds"]:
            reasons.add("dry_refilled_handling_not_matched")
    return {
        "schema_version": "PEDICULARIS_WATER_B0_METHOD_FEASIBILITY_RECEIPT_V1",
        "status": ("B0_METHOD_FEASIBILITY_SCREEN_PASSED_NOT_CAUSAL"
                   if not reasons else "B0_METHOD_FEASIBILITY_HOLD"),
        "context": ids, "assigned_arms": list(ARMS),
        "n_water_compartments": len(rows),
        "n_distinct_plants_total": len(seen_plants),
        "randomization_unit": "PLANT_WITH_ONE_WATER_COMPARTMENT_PER_PLANT",
        "arms": summaries,
        "handling_mean_gap_dry_refilled_seconds": handling_gap,
        "gate_reasons": sorted(reasons),
        "randomization_schedule_sha256": config["randomization_schedule_sha256"],
        "preoutcome_thresholds": limits,
        "independent_randomization_verified": False,
        "causal_water_effect_identified": False,
        "water_by_perforation_effect_identified": False,
        "functional_state_BALANCE_identified": False,
        "structural_architecture_BALANCE_identified": False,
        "claim_ceiling": (
            "method_only_without_outcomes_no_causal_water_contrast_"
            "no_architecture_or_BALANCE_result"
        ),
    }

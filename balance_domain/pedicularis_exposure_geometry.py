"""Prospective, outcome-blinded Pedicularis flower/whorl exposure geometry.

Crucial: published relative floral exsertion is NOT the same as
the vertical clearance of a verified oviposition site above water.
This is geometric measurement bookkeeping and a design-support audit,
not evidence of predator behaviour, selection, or architecture value.
"""
from __future__ import annotations

from collections import defaultdict
from math import isfinite

GEOMETRY_SCHEMA = "PEDICULARIS_EXPOSURE_GEOMETRY_PROTOCOL_V1"
ARMS = ("OBSERVATIONAL", "INTACT_WET", "INTACT_DRY", "INTACT_REFILLED_WET")
FIELDS = (
    "context_id", "population_id", "season_id", "protocol_version",
    "plant_id", "water_compartment_id", "flower_id", "observation_time_id",
    "assigned_water_arm", "flower_length_mm", "bract_height_mm",
    "flower_tip_elevation_mm", "bract_rim_elevation_mm",
    "water_surface_elevation_mm", "oviposition_site_elevation_mm",
    "oviposition_site_directly_verified", "positions_calibrated",
    "outcome_blinded_when_measured",
)
LIMIT_FIELDS = (
    "max_each_position_error_mm", "max_whorl_waterline_disagreement_mm",
    "min_waterline_clearance_contrast_mm",
    "max_within_flower_exsertion_difference",
    "max_within_flower_focal_geometry_drift_mm",
    "min_independent_compartments_with_contrast",
    "min_independent_plants_with_contrast",
)


def _txt(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} requires nonblank text")
    value = value.strip()
    if value.upper() == "REQUIRED_BEFORE_USE":
        raise ValueError(f"{name} must be frozen")
    return value


def _numeric(value, name):
    if isinstance(value, bool):
        raise ValueError(f"{name} cannot be boolean")
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return result


def _flag(value, name):
    if str(value).strip() not in {"0", "1"}:
        raise ValueError(f"{name} must be 0 or 1")
    return str(value).strip() == "1"


def _validate_config(config):
    if not isinstance(config, dict) or config.get("schema_version") != GEOMETRY_SCHEMA:
        raise ValueError("exposure geometry protocol schema mismatch")
    if config.get("status") != "FROZEN_BEFORE_EXPOSURE_OUTCOMES":
        raise ValueError("exposure geometry thresholds must be prospectively frozen")
    if config.get("all_heights_share_an_instrument_calibrated_vertical_datum") is not True:
        raise ValueError("all direct elevations must use a common calibrated vertical datum")
    if config.get("oviposition_site_definition_reviewed_before_outcome") is not True:
        raise ValueError("oviposition site must be defined before examining attack outcomes")
    ids = {key: _txt(config.get(key), key) for key in
           ("context_id", "population_id", "season_id", "protocol_version")}
    limits = config.get("thresholds")
    if not isinstance(limits, dict) or set(limits) != set(LIMIT_FIELDS):
        raise ValueError("exposure geometry threshold key set mismatch")
    limits = {key: _numeric(limits[key], key) for key in LIMIT_FIELDS}
    for key in ("min_independent_compartments_with_contrast",
                "min_independent_plants_with_contrast"):
        if int(limits[key]) != limits[key] or limits[key] < 2:
            raise ValueError(f"{key} must be an integer >= 2")
        limits[key] = int(limits[key])
    if limits["max_each_position_error_mm"] <= 0:
        raise ValueError("max_each_position_error_mm must be positive")
    if limits["min_waterline_clearance_contrast_mm"] <= (
        4 * limits["max_each_position_error_mm"]
    ):
        raise ValueError("contrast must exceed conservative four-position-error bound")
    if limits["max_within_flower_focal_geometry_drift_mm"] > limits["min_waterline_clearance_contrast_mm"] / 2:
        raise ValueError("focal morphology drift allowance must not swallow waterline contrast")
    if limits["max_within_flower_exsertion_difference"] > 1:
        raise ValueError("relative exsertion matching tolerance must be <= 1")
    return ids, limits


def audit_exposure_geometry(rows, config):
    """Quantify 2-axis measurement support, never attack rates or fitness."""
    ids, t = _validate_config(config)
    rows = list(rows)
    if not rows:
        raise ValueError("no geometry records")
    seen = set()
    whorl_owner = {}
    flower_owner = {}
    plant_arm = {}
    water_per_whorl_time = defaultdict(list)
    records = defaultdict(list)
    whorl_ids = set()
    plants = set()
    reasons = set()
    n_unverified = n_calibration = n_blinding = 0
    classification = defaultdict(int)
    max_pool_disagreement = 0.0

    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != set(FIELDS):
            raise ValueError(f"row {i} has unexpected geometry fields (no outcomes allowed)")
        for key, required in ids.items():
            if _txt(row[key], key) != required:
                raise ValueError(f"row {i} mismatched {key}")
        plant = _txt(row["plant_id"], "plant_id")
        whorl = _txt(row["water_compartment_id"], "water_compartment_id")
        flower = _txt(row["flower_id"], "flower_id")
        time = _txt(row["observation_time_id"], "observation_time_id")
        arm = _txt(row["assigned_water_arm"], "assigned_water_arm")
        if arm not in ARMS:
            raise ValueError("unregistered water-state arm")
        unique = (flower, time)
        if unique in seen:
            raise ValueError("duplicated flower/time observation")
        seen.add(unique)
        if whorl in whorl_owner and whorl_owner[whorl] != plant:
            raise ValueError("shared water compartment assigned to multiple plants")
        whorl_owner[whorl] = plant
        if flower in flower_owner and flower_owner[flower] != (plant, whorl):
            raise ValueError("flower changes water compartment across observations")
        flower_owner[flower] = (plant, whorl)
        if plant in plant_arm and plant_arm[plant] != arm:
            raise ValueError("one plant assigned incompatible water-state arms")
        plant_arm[plant] = arm
        whorl_ids.add(whorl)
        plants.add(plant)
        numeric = {key: _numeric(row[key], key) for key in (
            "flower_length_mm", "bract_height_mm", "flower_tip_elevation_mm",
            "bract_rim_elevation_mm", "water_surface_elevation_mm",
            "oviposition_site_elevation_mm",
        )}
        length = numeric["flower_length_mm"]
        if length <= 0:
            raise ValueError("flower length must be strictly positive")
        error = t["max_each_position_error_mm"]
        if numeric["water_surface_elevation_mm"] > (
            numeric["bract_rim_elevation_mm"] + 2*error
        ):
            raise ValueError("water surface above bract rim beyond measurement error")
        if numeric["oviposition_site_elevation_mm"] > (
            numeric["flower_tip_elevation_mm"] + 2*error
        ):
            raise ValueError("verified target site cannot be above flower tip")
        verified = _flag(row["oviposition_site_directly_verified"], "site_verified")
        calibrated = _flag(row["positions_calibrated"], "positions_calibrated")
        blinded = _flag(row["outcome_blinded_when_measured"], "outcome_blinded")
        n_unverified += not verified
        n_calibration += not calibrated
        n_blinding += not blinded
        exsertion = (length-numeric["bract_height_mm"])/length
        clearance = (numeric["oviposition_site_elevation_mm"]
                     - numeric["water_surface_elevation_mm"])
        pollinator_clearance = (numeric["flower_tip_elevation_mm"]
                                - numeric["bract_rim_elevation_mm"])
        if abs(clearance) <= 2*error:
            status = "WATERLINE_BOUNDARY_UNRESOLVED"
        elif clearance > 0:
            status = "SITE_ABOVE_WATERLINE_NOT_PROVEN_ACCESSIBLE"
        else:
            status = "SITE_SUBMERGED_NOT_PROVEN_PROTECTED"
        classification[status] += 1
        water_per_whorl_time[(whorl,time)].append(
            numeric["water_surface_elevation_mm"]
        )
        records[(plant,whorl,flower)].append({
            "time": time, "relative_exsertion": exsertion,
            "flower_length_mm": length,
            "bract_height_mm": numeric["bract_height_mm"],
            "flower_tip_elevation_mm": numeric["flower_tip_elevation_mm"],
            "bract_rim_elevation_mm": numeric["bract_rim_elevation_mm"],
            "water_surface_elevation_mm": numeric["water_surface_elevation_mm"],
            "oviposition_site_elevation_mm": numeric["oviposition_site_elevation_mm"],
            "site_waterline_clearance_mm": clearance,
            "flower_tip_rim_clearance_mm": pollinator_clearance,
            "site_verification_ok": verified and calibrated and blinded,
        })

    for values in water_per_whorl_time.values():
        difference = max(values)-min(values)
        max_pool_disagreement = max(max_pool_disagreement, difference)
        if difference > t["max_whorl_waterline_disagreement_mm"]:
            reasons.add("shared_whorl_waterline_measurements_inconsistent")
    if n_unverified:
        reasons.add("unverified_oviposition_site_coordinates")
    if n_calibration:
        reasons.add("uncalibrated_vertical_coordinates")
    if n_blinding:
        reasons.add("geometry_assessed_after_seeing_biological_outcomes")

    contrast_whorls = set()
    contrast_plants = set()
    contrasting_flowers = 0
    for (plant, whorl, flower), observations in records.items():
        if len(observations) < 2:
            continue
        # Same flower, approximately unchanged published exsertion coordinate,
        # yet large measured waterline/target-site difference across times.
        qualified = [
            x for x in observations if x["site_verification_ok"]
        ]
        morphology_keys = ("flower_length_mm", "bract_height_mm", "flower_tip_elevation_mm", "bract_rim_elevation_mm", "oviposition_site_elevation_mm")
        contrast = any(
            abs(x["relative_exsertion"] - y["relative_exsertion"])
            <= t["max_within_flower_exsertion_difference"]
            and all(abs(x[k]-y[k]) <= t["max_within_flower_focal_geometry_drift_mm"] for k in morphology_keys)
            and abs(x["water_surface_elevation_mm"] - y["water_surface_elevation_mm"])
            >= t["min_waterline_clearance_contrast_mm"]
            and abs(x["site_waterline_clearance_mm"] - y["site_waterline_clearance_mm"])
            >= t["min_waterline_clearance_contrast_mm"]
            for i, x in enumerate(qualified)
            for y in qualified[i+1:]
        )
        if contrast:
            contrasting_flowers += 1
            contrast_whorls.add(whorl)
            contrast_plants.add(plant)
    if len(contrast_whorls) < t["min_independent_compartments_with_contrast"]:
        reasons.add("insufficient_independent_waterline_contrasts")
    if len(contrast_plants) < t["min_independent_plants_with_contrast"]:
        reasons.add("insufficient_independent_plants_with_contrasts")

    return {
        "schema_version": "PEDICULARIS_EXPOSURE_GEOMETRY_SUPPORT_V1",
        "status": ("GEOMETRIC_TWO_AXIS_SUPPORT_ONLY_NOT_CAUSAL"
                   if not reasons else "EXPOSURE_GEOMETRY_SUPPORT_HOLD"),
        "n_flower_time_records": len(rows),
        "n_distinct_plants": len(plants),
        "n_distinct_whorl_water_compartments": len(whorl_ids),
        "n_distinct_flowers": len(records),
        "n_contrasting_flowers": contrasting_flowers,
        "n_contrasting_whorls": len(contrast_whorls),
        "n_independent_plants_with_contrasts": len(contrast_plants),
        "max_shared_whorl_waterline_disagreement_mm": max_pool_disagreement,
        "waterline_status_counts": dict(sorted(classification.items())),
        "unverified_oviposition_sites": n_unverified,
        "uncalibrated_observations": n_calibration,
        "outcome_unblinded_observations": n_blinding,
        "gate_reasons": sorted(reasons),
        "evidence_ceiling": (
            "geometry_and_design_support_only_not_water_causal_effect_"
            "not_predator_access_or_selection_and_not_architecture_value"
        ),
        "original_2016_exsertion_formula":
            "(flower_length_mm - bract_height_mm)/flower_length_mm",
        "waterline_clearance_formula":
            "oviposition_site_elevation_mm - water_surface_elevation_mm",
        "experimental_unit_caveat":
            "water surface shared at whorl, plant-level clustering required",
        "independent_experimental_randomization_verified": False,
        "ecological_effect_identified": False,
        "BALANCE_middle_world_identified": False,
    }

"""Prospective, outcome-free bract-local optical selectivity method screen.

This tests whether the *physical intervention* affects illuminated outer green
bracts while keeping fruit illumination and blossom microclimate compatible
with simultaneously measured, within-mother randomized shams. It never
estimates photosynthetic carbon translocation, seed fitness, a net alternative
architecture, or BALANCE occupancy.

The 2015 Dalechampia foil treatment enclosed the ENTIRE blossom; it cannot
be relabelled a bract-selective light perturbation. Source bracts close around
fruits after anthesis, so optical selectivity is a genuine feasibility risk.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from typing import Any

SCHEMA = "DALECHAMPIA_BRACT_ISOLATION_PILOT_V1"
ARMS = ("OPTICAL_SHAM", "BRACT_LOCAL_OPTICAL_ATTEMPT")
FIELD_NAMES = (
    "plant_id", "blossom_id", "arm", "allocation_sha256",
    "bract_par_before", "bract_par_after",
    "fruit_par_before", "fruit_par_after",
    "fruit_temperature_before_C", "fruit_temperature_after_C",
    "fruit_RH_before_percent", "fruit_RH_after_percent",
    "post_measurement_minute", "closure_intact", "visible_damage",
)
THRESHOLDS = (
    "minimum_selective_bract_PAR_reduction_fraction",
    "minimum_valid_reference_PAR_umol_m2_s",
    "maximum_sham_bract_PAR_change_fraction",
    "maximum_sham_fruit_PAR_change_fraction",
    "maximum_relative_fruit_PAR_change_vs_sham_fraction",
    "maximum_absolute_fruit_temperature_drift_C",
    "maximum_absolute_fruit_RH_drift_percentage_points",
    "maximum_pair_time_discrepancy_minutes",
)

# Prevent a spurious high PAR ratio caused by near-zero light measurements.
_MIN_REFERENCE_PAR = 0.000001


def _numeric(value: Any, label: str, *, minimum=None, maximum=None) -> float:
    if type(value) not in (float, int):
        raise ValueError(f"{label} must be a finite numeric observation")
    x=float(value)
    if not math.isfinite(x) or (minimum is not None and x < minimum) or (
        maximum is not None and x > maximum
    ):
        raise ValueError(f"{label} outside physical/calibration range")
    return x


def _integer(value: Any, label: str, *, minimum=1) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")
    return value


def _text(value: Any, label: str, *, minlength=1) -> str:
    if not isinstance(value, str) or len(value.strip()) < minlength:
        raise ValueError(f"{label} missing pre-outcome source identity/rationale")
    return value.strip()


def validate_pilot_config(spec: dict) -> dict:
    """Validate a self-declared frozen calibration specification (not chronology)."""
    if not isinstance(spec, dict) or set(spec) != {
        "schema_version", "status", "context_id",
        "randomization_sha256", "calibration_justification",
        "minimum_matched_independent_plants", "thresholds",
        "scope_exclusions"
    }:
        raise ValueError("bract-isolation pilot configuration schema changed")
    if spec["schema_version"] != SCHEMA:
        raise ValueError("bract-isolation schema_version mismatch")
    if spec["status"] != "SELF_DECLARED_FROZEN_BEFORE_REPRODUCTIVE_OUTCOMES":
        raise ValueError("thresholds are not declared frozen before outcomes")
    _text(spec["context_id"], "context_id")
    _text(spec["calibration_justification"], "calibration_justification", minlength=30)
    sha = _text(spec["randomization_sha256"], "randomization_sha256")
    if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("allocation schedule must have explicit SHA256 digest")
    _integer(spec["minimum_matched_independent_plants"],
             "minimum_matched_independent_plants", minimum=2)
    t=spec["thresholds"]
    if not isinstance(t, dict) or set(t) != set(THRESHOLDS):
        raise ValueError("complete physical tolerance calibration required")
    for key in THRESHOLDS:
        val=_numeric(t[key],f"thresholds.{key}",minimum=0)
        if key.endswith("_fraction") and not val <= 1:
            raise ValueError(f"{key} fraction must be <=1")
    if t["minimum_selective_bract_PAR_reduction_fraction"] <= 0:
        raise ValueError("selective-bract light reduction target must be positive")
    if t["minimum_valid_reference_PAR_umol_m2_s"] <= 0:
        raise ValueError("reference PAR must exceed a calibrated instrument detection threshold")
    exclusions=spec["scope_exclusions"]
    if not isinstance(exclusions, dict) or set(exclusions) != {
        "contains_reproductive_outcomes", "source_carbon_flow_verified",
        "structural_BALANCE_identified", "chronology_independently_verified"
    } or any(value is not False for value in exclusions.values()):
        raise ValueError("this method-only gate cannot contain biological outcomes")
    return spec


def evaluate_bract_local_optical_pilot(spec: dict, observations: list[dict]) -> dict:
    """One registered optical-sham and one bract-target blossom *per plant*.

    Return numerical method-only compatibility, never causal photosynthesis.
    Unbalanced/missing paired source structure raises rather than imputes.
    Non-qualifying physical methods return HOLD, not a positive biology result.
    """
    validate_pilot_config(spec)
    if not isinstance(observations, list) or not observations:
        raise ValueError("outcome-free method-only observations required")
    plants=defaultdict(dict)
    seen_blossoms=set()
    for row in observations:
        if not isinstance(row, dict) or set(row) != set(FIELD_NAMES):
            raise ValueError("unexpected columns (possibly biological outcomes)")
        mother=_text(row["plant_id"], "plant_id")
        blossom=_text(row["blossom_id"], "blossom_id")
        key=(mother,blossom)
        if key in seen_blossoms:
            raise ValueError("duplicate physical blossom source row")
        seen_blossoms.add(key)
        arm=_text(row["arm"], "arm")
        if arm not in ARMS or arm in plants[mother]:
            raise ValueError("unexpected arm or duplicate assigned arm within maternal plant")
        if row["allocation_sha256"] != spec["randomization_sha256"]:
            raise ValueError("allocation digest mismatches frozen randomization")
        x={}
        for field in (
            "bract_par_before","fruit_par_before"
        ):
            x[field]=_numeric(row[field],field,minimum=_MIN_REFERENCE_PAR)
        for field in ("bract_par_after","fruit_par_after"):
            x[field]=_numeric(row[field],field,minimum=0)
        for field in (
            "fruit_temperature_before_C","fruit_temperature_after_C",
        ):
            x[field]=_numeric(row[field],field,minimum=-30,maximum=70)
        for field in ("fruit_RH_before_percent","fruit_RH_after_percent"):
            x[field]=_numeric(row[field],field,minimum=0,maximum=100)
        x["post_measurement_minute"]=_numeric(row["post_measurement_minute"],
                                                 "post_measurement_minute",
                                                 minimum=0)
        for field in ("closure_intact","visible_damage"):
            if type(row[field]) is not bool:
                raise ValueError(f"{field} must be a directly checked boolean")
            x[field]=row[field]
        x["blossom_id"]=blossom
        plants[mother][arm]=x
    if any(set(pair) != set(ARMS) for pair in plants.values()):
        raise ValueError("every mother must have BOTH registered source arms")

    t=spec["thresholds"]
    failures=[]
    plant_receipts=[]
    for mother, pair in sorted(plants.items()):
        sham=pair["OPTICAL_SHAM"]
        target=pair["BRACT_LOCAL_OPTICAL_ATTEMPT"]
        b_sham=sham["bract_par_after"] / sham["bract_par_before"]
        f_sham=sham["fruit_par_after"] / sham["fruit_par_before"]
        b_target=target["bract_par_after"] / target["bract_par_before"]
        f_target=target["fruit_par_after"] / target["fruit_par_before"]
        relative_b=b_target / b_sham if b_sham>0 else math.inf
        relative_f=f_target / f_sham if f_sham>0 else math.inf
        problems=[]
        minimum_baseline=t["minimum_valid_reference_PAR_umol_m2_s"]
        if min(
            sham["bract_par_before"],target["bract_par_before"],
            sham["fruit_par_before"],target["fruit_par_before"],
        ) < minimum_baseline:
            problems.append("PRETREATMENT_PAR_BELOW_CALIBRATED_REFERENCE")
        if not math.isfinite(relative_b) or relative_b > (
            1-t["minimum_selective_bract_PAR_reduction_fraction"]
        ):
            problems.append("BRACT_PAR_NOT_SELECTIVELY_REDUCED")
        if not math.isfinite(relative_f) or abs(relative_f-1)> (
            t["maximum_relative_fruit_PAR_change_vs_sham_fraction"]
        ):
            problems.append("FRUIT_PAR_CHANGED_BY_BRACT_INTERVENTION")
        if abs(b_sham-1)>t["maximum_sham_bract_PAR_change_fraction"]:
            problems.append("SHAM_BRACT_PAR_UNSTABLE")
        if abs(f_sham-1)>t["maximum_sham_fruit_PAR_change_fraction"]:
            problems.append("SHAM_FRUIT_PAR_UNSTABLE")
        if abs(sham["post_measurement_minute"]-target["post_measurement_minute"]) > (
            t["maximum_pair_time_discrepancy_minutes"]
        ):
            problems.append("SHAM_TARGET_MEASUREMENTS_NOT_TIME_MATCHED")
        for label,row in pair.items():
            if abs(row["fruit_temperature_after_C"]-
                   row["fruit_temperature_before_C"]) > (
                    t["maximum_absolute_fruit_temperature_drift_C"]
            ):
                problems.append(f"{label}_FRUIT_TEMPERATURE_SHIFT")
            if abs(row["fruit_RH_after_percent"]-
                   row["fruit_RH_before_percent"]) > (
                    t["maximum_absolute_fruit_RH_drift_percentage_points"]
            ):
                problems.append(f"{label}_FRUIT_HUMIDITY_SHIFT")
            if not row["closure_intact"]:
                problems.append(f"{label}_BRACT_CLOSURE_CHANGED")
            if row["visible_damage"]:
                problems.append(f"{label}_VISIBLE_DAMAGE")
        if problems:
            failures.append(mother)
        plant_receipts.append({
            "plant_id":mother,
            "arm_blossoms":{
                arm:pair[arm]["blossom_id"] for arm in ARMS
            },
            "bract_PAR_ratio_target_relative_to_sham": (
                round(relative_b,6) if math.isfinite(relative_b) else None
            ),
            "fruit_PAR_ratio_target_relative_to_sham": (
                round(relative_f,6) if math.isfinite(relative_f) else None
            ),
            "physical_method_failures":sorted(set(problems)),
        })

    n=len(plants)
    sufficient=n>=spec["minimum_matched_independent_plants"]
    ok=sufficient and not failures
    return {
        "schema_version": SCHEMA,
        "status": (
            "METHOD_PROFILE_PASS_NOT_CARBON_CAUSAL_OR_FITNESS"
            if ok else "METHOD_SELECTIVITY_HOLD"
        ),
        "context_id":spec["context_id"],
        "n_unique_maternal_plants":n,
        "n_independently_assigned_blossoms":len(observations),
        "n_failed_maternal_blocks":len(failures),
        "minimum_matched_plants_reached":sufficient,
        "pairwise_method_receipts":plant_receipts,
        "biological_reproductive_outcomes_read":False,
        "selective_bract_carbon_causal_effect_identified":False,
        "fruit_photosynthetic_contribution_causally_ruled_out":False,
        "carbon_assimilation_translocation_to_seeds_verified":False,
        "structural_BALANCE_occupancy_identified":False,
        "new_independent_biological_clusters":0,
        "freeze_timestamp_independently_verified":False,
        "interpretation":(
            "method-only optical selectivity under self-declared calibration; "
            "does not establish independent randomization or historical freeze "
            "chronology; no seed-mass effect, isotope flux or net architecture"
        ),
    }


def input_sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_method_csv(raw: bytes) -> list[dict]:
    """Parse exact headers, no outcomes, strict numbers/boolean columns."""
    import csv
    import io

    try:
        text=raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("method CSV must be UTF-8") from exc
    reader=csv.DictReader(io.StringIO(text))
    if reader.fieldnames != list(FIELD_NAMES):
        raise ValueError("exact method-only CSV column header required")
    out=[]
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("malformed method-only data row")
        converted={}
        for field,value in row.items():
            if field in ("closure_intact","visible_damage"):
                if value not in ("true","false"):
                    raise ValueError("method-only boolean must be true or false")
                converted[field]=value=="true"
            elif field in (
                "plant_id","blossom_id","arm","allocation_sha256"
            ):
                converted[field]=value
            else:
                try:
                    converted[field]=float(value)
                except ValueError as exc:
                    raise ValueError("method-only optical measurement not numeric") from exc
        out.append(converted)
    return out

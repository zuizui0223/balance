"""Prospective, source-discrimination-only Dalechampia bract 13C assay screen.

IMPORTANT: no original isotope data exist in this repository. Synthetic tests
are never field observations, and a passing measured profile alone is NOT
proof of carbon transfer, allocation, or any fitness/structural BALANCE state.

A bract-labelled blossom and its unlabelled reference are deliberately placed
on DIFFERENT maternal plants; isotope could be translocated between blossoms
of the same mother and spoil an intra-mother sham.

Experimental randomized blocks contain exactly one independent mother for:
  SHAM_UNLABELLED         : sealed/handled, no target enriched 13CO2
  BRACT_13CO2_PULSE       : bract-targeted labelled gas, measure fruit leakage
  FRUIT_LEAK_MIMIC        : deliberately recreate at least the fruit gas dose
                            leaking in the target arm, WITHOUT a bract pulse
If the mimic seed signal could explain the target, return HOLD.

Integrated headspace 13CO2 excess *exposure* (atom%-hours) is not carbon mass
assimilated by fruit. Matching exposure does not guarantee matching uptake.
External assay calibration, randomization and monotonic dose-response remain
unverified by this software even if a supplied numeric profile screens PASS.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import io
import math
from typing import Any

SCHEMA="DALECHAMPIA_BRACT_13C_SOURCE_DISCRIMINATION_V1"
ARMS=("SHAM_UNLABELLED","BRACT_13CO2_PULSE","FRUIT_LEAK_MIMIC")
FIELDS=(
    "block_id","plant_id","blossom_id","arm","allocation_sha256",
    "postpollination_day","chase_hours",
    "seed_background_atom_percent_13c","bract_background_atom_percent_13c",
    "seed_postchase_atom_percent_13c","bract_postchase_atom_percent_13c",
    "seed_assay_sd_atom_percent","bract_assay_sd_atom_percent",
    "bract_gas_excess_auc_atompercent_hours",
    "fruit_gas_excess_auc_atompercent_hours",
    "ambient_gas_excess_auc_atompercent_hours",
    "fruit_temperature_C","fruit_RH_percent",
    "bract_closure_intact","no_visible_damage",
    "gas_monitor_QC_passed","isotope_lab_QC_passed",
)
THRESHOLDS=(
    "minimum_bract_source_excess_atom_percent",
    "minimum_seed_excess_over_sham_atom_percent",
    "minimum_seed_excess_over_fruit_mimic_atom_percent",
    "minimum_assay_contrast_z",
    "minimum_target_bract_gas_exposure_auc",
    "minimum_positive_mimic_fruit_gas_exposure_auc",
    "minimum_mimic_to_target_fruit_exposure_ratio",
    "maximum_target_fruit_to_bract_gas_exposure_ratio",
    "maximum_sham_mimic_bract_gas_exposure_auc",
    "maximum_ambient_gas_exposure_auc",
    "maximum_chase_time_span_hours",
    "maximum_postpollination_stage_span_days",
    "maximum_fruit_temperature_span_C",
    "maximum_fruit_RH_span_percentage_points",
)
BOOL_FIELDS={
    "bract_closure_intact","no_visible_damage",
    "gas_monitor_QC_passed","isotope_lab_QC_passed",
}
IDENTITY_FIELDS={
    "block_id","plant_id","blossom_id","arm","allocation_sha256",
}
ATOM_FIELDS={
    "seed_background_atom_percent_13c","bract_background_atom_percent_13c",
    "seed_postchase_atom_percent_13c","bract_postchase_atom_percent_13c",
}
POSITIVE_SD_FIELDS={
    "seed_assay_sd_atom_percent","bract_assay_sd_atom_percent",
}
GAS_FIELDS={
    "bract_gas_excess_auc_atompercent_hours",
    "fruit_gas_excess_auc_atompercent_hours",
    "ambient_gas_excess_auc_atompercent_hours",
}


def _number(v:Any, field:str, lo:float=0, hi:float|None=None) -> float:
    if type(v) not in (float,int):
        raise ValueError(f"{field} must be a finite numeric measurement")
    x=float(v)
    if not math.isfinite(x) or x<lo or (hi is not None and x>hi):
        raise ValueError(f"{field} outside registered measurement range")
    return x


def _text(v:Any, field:str) -> str:
    if not isinstance(v,str) or not v.strip():
        raise ValueError(f"{field} must be nonempty source text")
    return v.strip()


def _digest(v:Any, field:str) -> str:
    x=_text(v,field)
    if len(x)!=64 or any(c not in "0123456789abcdef" for c in x):
        raise ValueError(f"{field} must have a lowercase SHA256 fingerprint")
    return x


def validate_tracer_plan(plan:dict) -> dict:
    expected={
        "schema_version","status","context_id","assignment_sha256",
        "chamber_calibration_sha256","assay_calibration_sha256",
        "minimum_independent_randomized_blocks","thresholds","limitations",
        "source_dose_comparability_rationale",
    }
    if not isinstance(plan,dict) or set(plan)!=expected:
        raise ValueError("source tracer plan schema changed")
    if plan["schema_version"]!=SCHEMA:
        raise ValueError("source tracer plan version mismatch")
    if plan["status"]!="SELF_DECLARED_PRE_OUTCOME_NOT_EXTERNALLY_TIME_AUTHENTICATED":
        raise ValueError("source tracer calibration is NOT frozen")
    _text(plan["context_id"],"context_id")
    _digest(plan["assignment_sha256"],"assignment_sha256")
    _digest(plan["chamber_calibration_sha256"],"chamber_calibration_sha256")
    _digest(plan["assay_calibration_sha256"],"assay_calibration_sha256")
    if type(plan["minimum_independent_randomized_blocks"]) is not int or (
        plan["minimum_independent_randomized_blocks"]<3
    ):
        raise ValueError("at least three independent maternal randomized blocks required")
    rationale=_text(plan["source_dose_comparability_rationale"],
                    "source_dose_comparability_rationale")
    if len(rationale)<45:
        raise ValueError("fruit leak-mimic uptake/dose equivalence needs prior rationale")
    thresholds=plan["thresholds"]
    if not isinstance(thresholds,dict) or set(thresholds)!=set(THRESHOLDS):
        raise ValueError("complete prospective leakage and assay thresholds required")
    for name in THRESHOLDS:
        val=_number(thresholds[name],name)
        if name.endswith("exposure_ratio") and not val<=1 and name.startswith("maximum"):
            raise ValueError("maximum source leakage ratio cannot exceed one")
    for name in (
        "minimum_bract_source_excess_atom_percent",
        "minimum_seed_excess_over_sham_atom_percent",
        "minimum_seed_excess_over_fruit_mimic_atom_percent",
        "minimum_assay_contrast_z",
        "minimum_target_bract_gas_exposure_auc",
        "minimum_positive_mimic_fruit_gas_exposure_auc",
    ):
        if thresholds[name]<=0:
            raise ValueError(f"{name} must exceed calibrated detection background")
    if thresholds["minimum_assay_contrast_z"]<1.96:
        raise ValueError("minimum assay contrast z cannot be below 1.96")
    if thresholds["minimum_mimic_to_target_fruit_exposure_ratio"]<1:
        raise ValueError("leak mimic must match or exceed target fruit gas exposure")
    for name in (
        "minimum_bract_source_excess_atom_percent",
        "minimum_seed_excess_over_sham_atom_percent",
        "minimum_seed_excess_over_fruit_mimic_atom_percent",
    ):
        if thresholds[name]>100:
            raise ValueError("atom percent excess cannot exceed physical scale")
    limits=plan["limitations"]
    exact={
        "same_mother_isotope_arms_allowed",
        "external_freeze_chronology_verified",
        "dose_to_assimilation_monotonicity_verified",
        "bract_to_seed_carbon_route_causally_identified",
        "mature_seed_fitness_effect_identified",
        "structural_BALANCE_identified",
    }
    if not isinstance(limits,dict) or set(limits)!=exact or any(
        limits[k] is not False for k in exact
    ):
        raise ValueError("tracer method screen cannot assert resolved causal biology")
    return plan


def parse_tracer_csv(raw:bytes) -> list[dict]:
    try:
        text=raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("original tracer measurement CSV must be UTF-8") from exc
    reader=csv.DictReader(io.StringIO(text))
    if reader.fieldnames != list(FIELDS):
        raise ValueError("exact tracer-source CSV header required; no fitness columns")
    rows=[]
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("tracer source record has overflow or missing cells")
        record={}
        for field,val in row.items():
            if field in BOOL_FIELDS:
                if val not in ("true","false"):
                    raise ValueError("QC and physical integrity fields require true/false")
                record[field]=val=="true"
            elif field in IDENTITY_FIELDS:
                record[field]=val
            else:
                try:
                    record[field]=float(val)
                except ValueError as exc:
                    raise ValueError("isotope measurement not numeric") from exc
        rows.append(record)
    return rows


def screen_bract_13c_source(plan:dict, observations:list[dict]) -> dict:
    """Conservative per-block *screen*, not a biological treatment estimate.

    Comparisons use background-subtracted seed/bract atom-% excess and their
    ASSAY uncertainty only; sampling/biological variability and false positive
    rate of multiple blocks are NOT estimated by this receipt.
    """
    validate_tracer_plan(plan)
    if not isinstance(observations,list) or not observations:
        raise ValueError("real outcome/assay records required for tracer screen")
    blocks=defaultdict(dict)
    seen_plants=set()
    seen_blossoms=set()
    for item in observations:
        if not isinstance(item,dict) or set(item)!=set(FIELDS):
            raise ValueError("tracer assay source fields missing or contaminated with unrelated outcomes")
        block=_text(item["block_id"],"block_id")
        plant=_text(item["plant_id"],"plant_id")
        blossom=_text(item["blossom_id"],"blossom_id")
        arm=_text(item["arm"],"arm")
        if arm not in ARMS or arm in blocks[block]:
            raise ValueError("wrong/duplicate source arm in randomized block")
        if plant in seen_plants or (plant,blossom) in seen_blossoms:
            raise ValueError("one independent mother and blossom only once: avoid isotope cross-contamination")
        seen_plants.add(plant)
        seen_blossoms.add((plant,blossom))
        if item["allocation_sha256"]!=plan["assignment_sha256"]:
            raise ValueError("tracer assignment differs from prior declared digest")
        row={}
        for f in FIELDS:
            if f in IDENTITY_FIELDS:
                row[f]=item[f]
            elif f in BOOL_FIELDS:
                if type(item[f]) is not bool:
                    raise ValueError(f"{f} must be observed boolean")
                row[f]=item[f]
            elif f in ATOM_FIELDS:
                row[f]=_number(item[f],f,lo=0,hi=100)
            elif f in POSITIVE_SD_FIELDS:
                row[f]=_number(item[f],f,lo=0.000000001,hi=10)
            elif f in GAS_FIELDS:
                row[f]=_number(item[f],f,lo=0)
            elif f=="fruit_temperature_C":
                row[f]=_number(item[f],f,lo=-30,hi=70)
            elif f=="fruit_RH_percent":
                row[f]=_number(item[f],f,lo=0,hi=100)
            elif f=="chase_hours":
                row[f]=_number(item[f],f,lo=0.0000001)
            elif f=="postpollination_day":
                row[f]=_number(item[f],f,lo=0)
            else:
                raise ValueError(f"unregistered field {f}")
        blocks[block][arm]=row
    if any(set(v)!=set(ARMS) for v in blocks.values()):
        raise ValueError("each randomized block needs sham, bract target and leak mimic on DIFFERENT mothers")

    t=plan["thresholds"]
    results=[]
    for block,armset in sorted(blocks.items()):
        sham,target,mimic=(armset[k] for k in ARMS)
        fail=[]
        for a,r in armset.items():
            if not all(r[x] for x in BOOL_FIELDS):
                fail.append(f"{a}_PHYSICAL_OR_ASSAY_QC_FAILED")
        if max(x["chase_hours"] for x in armset.values())-min(
            x["chase_hours"] for x in armset.values()
        ) > t["maximum_chase_time_span_hours"]:
            fail.append("CHASE_TIME_NOT_MATCHED")
        if max(x["postpollination_day"] for x in armset.values())-min(
            x["postpollination_day"] for x in armset.values()
        ) > t["maximum_postpollination_stage_span_days"]:
            fail.append("POSTPOLLINATION_STAGE_NOT_MATCHED")
        if max(x["fruit_temperature_C"] for x in armset.values())-min(
            x["fruit_temperature_C"] for x in armset.values()
        ) > t["maximum_fruit_temperature_span_C"]:
            fail.append("FRUIT_TEMPERATURE_NOT_MATCHED")
        if max(x["fruit_RH_percent"] for x in armset.values())-min(
            x["fruit_RH_percent"] for x in armset.values()
        ) > t["maximum_fruit_RH_span_percentage_points"]:
            fail.append("FRUIT_HUMIDITY_NOT_MATCHED")
        if any(r["ambient_gas_excess_auc_atompercent_hours"] >
               t["maximum_ambient_gas_exposure_auc"] for r in armset.values()):
            fail.append("AMBIENT_LABEL_CONTAMINATION")

        source=target["bract_gas_excess_auc_atompercent_hours"]
        off_target=target["fruit_gas_excess_auc_atompercent_hours"]
        mimic_dose=mimic["fruit_gas_excess_auc_atompercent_hours"]
        if source<t["minimum_target_bract_gas_exposure_auc"]:
            fail.append("BRACT_SOURCE_PULSE_UNQUALIFIED")
        if source<=0 or off_target/source>t["maximum_target_fruit_to_bract_gas_exposure_ratio"]:
            fail.append("TARGET_FRUIT_GAS_LEAKAGE_EXCEEDS_CALIBRATED_LIMIT")
        if mimic_dose<t["minimum_positive_mimic_fruit_gas_exposure_auc"] or (
            off_target>0 and mimic_dose/off_target <
            t["minimum_mimic_to_target_fruit_exposure_ratio"]
        ):
            fail.append("FRUIT_LEAK_MIMIC_DOES_NOT_COVER_TARGET_LEAKAGE")
        if any(
            armset[arm]["bract_gas_excess_auc_atompercent_hours"] >
            t["maximum_sham_mimic_bract_gas_exposure_auc"]
            for arm in ("SHAM_UNLABELLED","FRUIT_LEAK_MIMIC")
        ):
            fail.append("CONTROL_BRACT_INADVERTENTLY_LABELLED")

        def ape(row,tissue):
            return (row[f"{tissue}_postchase_atom_percent_13c"] -
                    row[f"{tissue}_background_atom_percent_13c"])
        seed_sham, seed_target, seed_mimic=(ape(x,"seed") for x in
            (sham,target,mimic))
        bract_sham,bract_target,bract_mimic=(ape(x,"bract") for x in
            (sham,target,mimic))
        if (seed_target < 0 or seed_mimic < 0 or seed_sham < 0 or
                bract_target<0 or bract_mimic<0 or bract_sham<0):
            fail.append("NEGATIVE_APPARENT_EXCESS_BASELINE_OR_ASSAY_DRIFT")
        z=t["minimum_assay_contrast_z"]

        def clear(difference,first,second,sd_key,minimum):
            measurement_uncertainty=z*math.hypot(
                first[sd_key],second[sd_key]
            )
            return difference > max(minimum,measurement_uncertainty)

        if not clear(bract_target-bract_sham,target,sham,
                     "bract_assay_sd_atom_percent",
                     t["minimum_bract_source_excess_atom_percent"]):
            fail.append("BRACT_SOURCE_TISSUE_NOT_ENRICHED_ABOVE_SHAM")
        if not clear(seed_target-seed_sham,target,sham,
                     "seed_assay_sd_atom_percent",
                     t["minimum_seed_excess_over_sham_atom_percent"]):
            fail.append("TARGET_SEED_ENRICHMENT_NOT_ABOVE_UNLABELLED_SHAM")
        if not clear(seed_target-seed_mimic,target,mimic,
                     "seed_assay_sd_atom_percent",
                     t["minimum_seed_excess_over_fruit_mimic_atom_percent"]):
            fail.append("TARGET_SEED_ENRICHMENT_NOT_ABOVE_FRUIT_LEAK_MIMIC")
        if not clear(bract_sham-bract_mimic,sham,mimic,
                     "bract_assay_sd_atom_percent",0) and (
            bract_mimic-bract_sham >
            z*math.hypot(sham["bract_assay_sd_atom_percent"],
                         mimic["bract_assay_sd_atom_percent"])
        ):
            fail.append("LEAK_MIMIC_BRACT_ALSO_ENRICHED")
        results.append({
            "block_id":block,
            "independent_plants_by_arm": {
                arm:armset[arm]["plant_id"] for arm in ARMS
            },
            "target_seed_atom_percent_excess_minus_sham":round(seed_target-seed_sham,6),
            "target_seed_atom_percent_excess_minus_mimic":round(seed_target-seed_mimic,6),
            "target_bract_atom_percent_excess_minus_sham":round(bract_target-bract_sham,6),
            "target_fruit_to_bract_gas_exposure_ratio":(
                round(off_target/source,6) if source>0 else None
            ),
            "leak_mimic_to_target_fruit_gas_exposure_ratio":(
                round(mimic_dose/off_target,6) if off_target>0 else None
            ),
            "source_discrimination_method_failures":sorted(set(fail)),
        })
    enough=len(blocks)>=plan["minimum_independent_randomized_blocks"]
    passed=enough and all(
        not x["source_discrimination_method_failures"] for x in results
    )
    return {
        "schema_version":SCHEMA,
        "status":("COMPARTMENT_SOURCE_SIGNATURE_SCREEN_PASSED_NOT_CAUSAL_FITNESS"
                  if passed else "SOURCE_ATTRIBUTION_HOLD"),
        "n_randomized_blocks":len(blocks),
        "n_distinct_maternal_plants":len(seen_plants),
        "n_individual_blossoms":len(seen_blossoms),
        "minimum_independent_blocks_met":enough,
        "original_isotope_experimental_data_supplied":True,
        "per_block_source_screen":results,
        "assay_uncertainty_only_not_biological_CI":True,
        "external_chamber_calibration_verified":False,
        "external_pre_outcome_randomization_freeze_verified":False,
        "source_dose_to_tissue_uptake_monotonicity_verified":False,
        "estimated_source_specific_seed_carbon_mass_mg":None,
        "bract_derived_seed_carbon_transport_causally_identified":False,
        "late_reproductive_fitness_effect_identified":False,
        "strict_structural_BALANCE_identified":False,
        "additional_independent_biological_clusters":0,
        "interpretation":(
            "a physical gas-exposure and assay signal screen of supplied "
            "plant-independent tracer blocks, NOT isotopic carbon mass-balance, "
            "sampling inference, independently validated chamber leakage or "
            "net structural architecture fitness"
        ),
    }


def raw_sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

"""Only synthetic instrument profiles: NO Dalechampia field feasibility is claimed."""
from __future__ import annotations

import copy
import csv
import io
import json
from pathlib import Path

import pytest

from balance_domain.dalechampia_bract_isolation import (
    ARMS, FIELD_NAMES, SCHEMA,
    evaluate_bract_local_optical_pilot,
    parse_method_csv, validate_pilot_config,
)
from scripts.evaluate_dalechampia_bract_isolation import evaluate_files

ROOT=Path(__file__).resolve().parents[1]


def spec():
    return {
        "schema_version":SCHEMA,
        "status":"SELF_DECLARED_FROZEN_BEFORE_REPRODUCTIVE_OUTCOMES",
        "context_id":"SYNTHETIC_GREENHOUSE_NOT_REAL_FIELD",
        "randomization_sha256":"a"*64,
        "calibration_justification":(
            "SYNTHETIC ONLY: instrument calibrations and physical tolerances "
            "are fictitious and do not authorize any field causal result."
        ),
        "minimum_matched_independent_plants":3,
        "thresholds":{
            "minimum_selective_bract_PAR_reduction_fraction":.65,
            "maximum_sham_bract_PAR_change_fraction":.08,
            "maximum_sham_fruit_PAR_change_fraction":.08,
            "maximum_relative_fruit_PAR_change_vs_sham_fraction":.10,
            "maximum_absolute_fruit_temperature_drift_C":.5,
            "maximum_absolute_fruit_RH_drift_percentage_points":3.,
            "maximum_pair_time_discrepancy_minutes":2.,
        },
        "scope_exclusions":{
            "contains_reproductive_outcomes":False,
            "source_carbon_flow_verified":False,
            "structural_BALANCE_identified":False,
            "chronology_independently_verified":False,
        },
    }


def data(n=3):
    rows=[]
    for i in range(n):
        for arm in ARMS:
            target=arm=="BRACT_LOCAL_OPTICAL_ATTEMPT"
            rows.append({
                "plant_id":f"plant{i}",
                "blossom_id":f"b{i}-{'test' if target else 'sham'}",
                "arm":arm,
                "allocation_sha256":"a"*64,
                "bract_par_before":100,
                "bract_par_after":20 if target else 100,
                "fruit_par_before":60,
                "fruit_par_after":60,
                "fruit_temperature_before_C":26.,
                "fruit_temperature_after_C":26.1,
                "fruit_RH_before_percent":55.,
                "fruit_RH_after_percent":56.,
                "post_measurement_minute":10.,
                "closure_intact":True,
                "visible_damage":False,
            })
    return rows


def test_three_independent_synthetic_plant_pairs_only_pass_method_not_causality():
    v=evaluate_bract_local_optical_pilot(spec(),data())
    assert v["status"]=="METHOD_PROFILE_PASS_NOT_CARBON_CAUSAL_OR_FITNESS"
    assert (v["n_unique_maternal_plants"],v["n_independently_assigned_blossoms"])==(3,6)
    assert all(x["physical_method_failures"]==[] for x in v["pairwise_method_receipts"])
    assert v["biological_reproductive_outcomes_read"] is False
    assert v["selective_bract_carbon_causal_effect_identified"] is False
    assert v["fruit_photosynthetic_contribution_causally_ruled_out"] is False
    assert v["carbon_assimilation_translocation_to_seeds_verified"] is False
    assert v["structural_BALANCE_occupancy_identified"] is False
    assert v["freeze_timestamp_independently_verified"] is False


def test_shading_entire_blossom_fails_offtarget_fruit_light():
    rows=data()
    target=next(r for r in rows if r["arm"]=="BRACT_LOCAL_OPTICAL_ATTEMPT")
    target["fruit_par_after"]=15
    v=evaluate_bract_local_optical_pilot(spec(),rows)
    assert v["status"]=="METHOD_SELECTIVITY_HOLD"
    assert v["n_failed_maternal_blocks"]==1
    assert "FRUIT_PAR_CHANGED_BY_BRACT_INTERVENTION" in (
        v["pairwise_method_receipts"][0]["physical_method_failures"]
    )
    assert v["carbon_assimilation_translocation_to_seeds_verified"] is False


def test_bract_not_suppressed_or_sham_cloud_drift_holds():
    x=data()
    x[1]["bract_par_after"]=98
    out=evaluate_bract_local_optical_pilot(spec(),x)
    assert out["status"]=="METHOD_SELECTIVITY_HOLD"
    assert "BRACT_PAR_NOT_SELECTIVELY_REDUCED" in out["pairwise_method_receipts"][0]["physical_method_failures"]
    x=data()
    x[0]["bract_par_after"]=45
    out=evaluate_bract_local_optical_pilot(spec(),x)
    assert "SHAM_BRACT_PAR_UNSTABLE" in out["pairwise_method_receipts"][0]["physical_method_failures"]


def test_heat_humidity_damage_closure_and_time_cannot_be_ignored():
    x=data()
    target=x[1]
    target["fruit_temperature_after_C"]=28.
    target["fruit_RH_after_percent"]=66.
    target["closure_intact"]=False
    target["visible_damage"]=True
    target["post_measurement_minute"]=17.
    fail=evaluate_bract_local_optical_pilot(spec(),x)
    codes=fail["pairwise_method_receipts"][0]["physical_method_failures"]
    assert fail["status"]=="METHOD_SELECTIVITY_HOLD"
    assert any("FRUIT_TEMPERATURE_SHIFT" in n for n in codes)
    assert any("FRUIT_HUMIDITY_SHIFT" in n for n in codes)
    assert any("BRACT_CLOSURE_CHANGED" in n for n in codes)
    assert any("VISIBLE_DAMAGE" in n for n in codes)
    assert "SHAM_TARGET_MEASUREMENTS_NOT_TIME_MATCHED" in codes


def test_no_fabrication_for_unbalanced_design_duplicate_assignments_or_outcomes():
    x=data()
    with pytest.raises(ValueError,match="BOTH registered"):
        evaluate_bract_local_optical_pilot(spec(),x[:-1])
    x=data()
    with pytest.raises(ValueError,match="duplicate physical blossom"):
        evaluate_bract_local_optical_pilot(spec(),x+[copy.deepcopy(x[0])])
    x=data()
    x[0]["seedmass"]=30
    with pytest.raises(ValueError,match="unexpected columns"):
        evaluate_bract_local_optical_pilot(spec(),x)
    x=data()
    x[1]["allocation_sha256"]="b"*64
    with pytest.raises(ValueError,match="allocation digest"):
        evaluate_bract_local_optical_pilot(spec(),x)


def test_no_selectivity_pass_if_too_few_independent_plants():
    report=evaluate_bract_local_optical_pilot(spec(),data(2))
    assert report["status"]=="METHOD_SELECTIVITY_HOLD"
    assert report["minimum_matched_plants_reached"] is False


def test_unfrozen_invalid_template_and_malformed_thresholds_fail_closed():
    template=json.loads(
        (ROOT/"data/DALECHAMPIA_BRACT_ISOLATION_THRESHOLDS_TEMPLATE_V1.json").read_text()
    )
    with pytest.raises(ValueError,match="not declared frozen"):
        validate_pilot_config(template)
    c=spec()
    c["thresholds"]["minimum_selective_bract_PAR_reduction_fraction"]=None
    with pytest.raises(ValueError,match="finite numeric"):
        validate_pilot_config(c)
    c=spec()
    c["scope_exclusions"]["contains_reproductive_outcomes"]=True
    with pytest.raises(ValueError,match="method-only"):
        validate_pilot_config(c)


def test_exact_method_only_csv_header_and_runner_sha256(tmp_path):
    rows=data()
    x=io.StringIO()
    writer=csv.DictWriter(x,fieldnames=list(FIELD_NAMES),lineterminator="\n")
    writer.writeheader()
    for row in rows:
        formatted={k:(
            "true" if v is True else "false" if v is False else v
        ) for k,v in row.items()}
        writer.writerow(formatted)
    csvbytes=x.getvalue().encode()
    assert parse_method_csv(csvbytes)==rows
    assert (ROOT/"data/DALECHAMPIA_BRACT_ISOLATION_METHOD_ONLY_TEMPLATE_V1.csv").read_text().strip()==",".join(FIELD_NAMES)
    in_path=tmp_path/"measurements.csv";in_path.write_bytes(csvbytes)
    conf_path=tmp_path/"freeze.json";conf_path.write_text(json.dumps(spec()))
    dest=tmp_path/"receipt.json"
    out=evaluate_files(conf_path,in_path,dest)
    assert out["status"]=="METHOD_PROFILE_PASS_NOT_CARBON_CAUSAL_OR_FITNESS"
    assert len(out["calibration_spec_sha256"])==64
    assert len(out["method_only_observation_sha256"])==64
    assert json.loads(dest.read_text())==out
    with pytest.raises(ValueError,match="cannot overwrite"):
        evaluate_files(conf_path,in_path,dest)
    bad=csvbytes.replace(b"allocation_sha256",b"seed_mass")
    with pytest.raises(ValueError,match="exact method-only CSV"):
        parse_method_csv(bad)


def test_nonfinite_zero_baseline_and_boolean_numeric_errors():
    x=data()
    x[0]["fruit_par_before"]=0
    with pytest.raises(ValueError,match="physical/calibration"):
        evaluate_bract_local_optical_pilot(spec(),x)
    x=data()
    x[0]["bract_par_after"]=float("nan")
    with pytest.raises(ValueError,match="physical/calibration"):
        evaluate_bract_local_optical_pilot(spec(),x)
    x=data()
    x[0]["closure_intact"]="true"
    with pytest.raises(ValueError,match="directly checked boolean"):
        evaluate_bract_local_optical_pilot(spec(),x)

"""Synthetic tracer source-control tests. No Dalechampia 13C field data exist.

A PASS means supplied numbers satisfy an ASSAY SCREEN ONLY; neither physical
randomization chronology nor carbon uptake mass balance is demonstrated.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
from pathlib import Path

import pytest

from balance_domain.dalechampia_tracer_source import (
    ARMS,FIELDS,SCHEMA,parse_tracer_csv,screen_bract_13c_source,
    validate_tracer_plan,
)
from scripts.evaluate_dalechampia_bract_13c_source import build_receipt

ROOT=Path(__file__).resolve().parents[1]


def plan():
    return {
        "schema_version":SCHEMA,
        "status":"SELF_DECLARED_PRE_OUTCOME_NOT_EXTERNALLY_TIME_AUTHENTICATED",
        "context_id":"SYNTHETIC_STAGE_TEN_DAYS_NOT_REAL_PLANTS",
        "assignment_sha256":"a"*64,
        "chamber_calibration_sha256":"b"*64,
        "assay_calibration_sha256":"c"*64,
        "minimum_independent_randomized_blocks":3,
        "source_dose_comparability_rationale":(
            "SYNTHETIC only: fruit gas exposure mimic doses exceed target "
            "leakage; uptake equivalence is not established for real plants."
        ),
        "thresholds":{
            "minimum_bract_source_excess_atom_percent":.4,
            "minimum_seed_excess_over_sham_atom_percent":.05,
            "minimum_seed_excess_over_fruit_mimic_atom_percent":.05,
            "minimum_assay_contrast_z":1.96,
            "minimum_target_bract_gas_exposure_auc":25.,
            "minimum_positive_mimic_fruit_gas_exposure_auc":.1,
            "minimum_mimic_to_target_fruit_exposure_ratio":1.2,
            "maximum_target_fruit_to_bract_gas_exposure_ratio":.02,
            "maximum_sham_mimic_bract_gas_exposure_auc":.01,
            "maximum_ambient_gas_exposure_auc":.01,
            "maximum_chase_time_span_hours":.5,
            "maximum_postpollination_stage_span_days":1.,
            "maximum_fruit_temperature_span_C":1.,
            "maximum_fruit_RH_span_percentage_points":4.,
        },
        "limitations":{
            "same_mother_isotope_arms_allowed":False,
            "external_freeze_chronology_verified":False,
            "dose_to_assimilation_monotonicity_verified":False,
            "bract_to_seed_carbon_route_causally_identified":False,
            "mature_seed_fitness_effect_identified":False,
            "structural_BALANCE_identified":False,
        },
    }


def observations(n=3):
    records=[]
    for block in range(n):
        for i,arm in enumerate(ARMS):
            target=arm=="BRACT_13CO2_PULSE"
            mimic=arm=="FRUIT_LEAK_MIMIC"
            records.append({
                "block_id":f"independent-block-{block}",
                "plant_id":f"mother-{block}-{i}",
                "blossom_id":f"blossom-{block}-{i}",
                "arm":arm,
                "allocation_sha256":"a"*64,
                "postpollination_day":10.0,
                "chase_hours":24.0,
                "seed_background_atom_percent_13c":1.10,
                "bract_background_atom_percent_13c":1.10,
                "seed_postchase_atom_percent_13c":1.22 if target else (
                    1.125 if mimic else 1.101
                ),
                "bract_postchase_atom_percent_13c":3.10 if target else 1.101,
                "seed_ape_sd_atom_percent":.004,
                "bract_ape_sd_atom_percent":.004,
                "bract_gas_excess_auc_atompercent_hours":120. if target else 0.,
                "fruit_gas_excess_auc_atompercent_hours":.2 if target else (
                    .6 if mimic else 0.
                ),
                "ambient_gas_excess_auc_atompercent_hours":.001,
                "fruit_temperature_C":25.+i*.1,
                "fruit_RH_percent":55.+i*.2,
                "bract_closure_intact":True,
                "no_visible_damage":True,
                "gas_monitor_QC_passed":True,
                "isotope_lab_QC_passed":True,
            })
    return records


def test_source_control_screen_can_pass_without_promoting_assay_or_fitness():
    result=screen_bract_13c_source(plan(),observations())
    assert result["status"]=="COMPARTMENT_SOURCE_SIGNATURE_SCREEN_PASSED_NOT_CAUSAL_FITNESS"
    assert result["n_randomized_blocks"]==3
    assert result["n_distinct_maternal_plants"]==9
    assert result["n_individual_blossoms"]==9
    assert all(not r["source_discrimination_method_failures"]
               for r in result["per_block_source_screen"])
    assert result["external_chamber_calibration_verified"] is False
    assert result["external_pre_outcome_randomization_freeze_verified"] is False
    assert result["source_dose_to_tissue_uptake_monotonicity_verified"] is False
    assert result["estimated_source_specific_seed_carbon_mass_mg"] is None
    assert result["bract_derived_seed_carbon_transport_causally_identified"] is False
    assert result["late_reproductive_fitness_effect_identified"] is False
    assert result["strict_structural_BALANCE_identified"] is False
    assert result["assay_uncertainty_only_not_biological_CI"] is True


def test_seed_label_also_explained_by_fruit_leak_mimic_remains_hold():
    x=observations()
    r=next(v for v in x if v["arm"]=="FRUIT_LEAK_MIMIC")
    r["seed_postchase_atom_percent_13c"]=1.21
    result=screen_bract_13c_source(plan(),x)
    assert result["status"]=="SOURCE_ATTRIBUTION_HOLD"
    assert "TARGET_SEED_ENRICHMENT_NOT_ABOVE_FRUIT_LEAK_MIMIC" in (
        result["per_block_source_screen"][0]["source_discrimination_method_failures"]
    )


def test_high_headspace_leak_and_insufficient_mimic_are_not_source_attributed():
    x=observations()
    target=next(v for v in x if v["arm"]=="BRACT_13CO2_PULSE")
    target["fruit_gas_excess_auc_atompercent_hours"]=20.
    out=screen_bract_13c_source(plan(),x)
    assert out["status"]=="SOURCE_ATTRIBUTION_HOLD"
    problems=out["per_block_source_screen"][0]["source_discrimination_method_failures"]
    assert "TARGET_FRUIT_GAS_LEAKAGE_EXCEEDS_CALIBRATED_LIMIT" in problems
    assert "FRUIT_LEAK_MIMIC_DOES_NOT_COVER_TARGET_LEAKAGE" in problems


def test_biological_same_mother_sham_is_rejected_due_to_possible_carbon_transfer():
    x=observations()
    x[1]["plant_id"]=x[0]["plant_id"]
    with pytest.raises(ValueError,match="one independent mother"):
        screen_bract_13c_source(plan(),x)
    x=observations()
    x[3]["plant_id"]=x[0]["plant_id"]
    with pytest.raises(ValueError,match="one independent mother"):
        screen_bract_13c_source(plan(),x)


def test_mimic_labelling_bract_or_ambient_contamination_holds():
    x=observations()
    x[2]["bract_postchase_atom_percent_13c"]=1.4
    out=screen_bract_13c_source(plan(),x)
    assert "LEAK_MIMIC_BRACT_ALSO_ENRICHED" in (
        out["per_block_source_screen"][0]["source_discrimination_method_failures"]
    )
    x=observations()
    x[0]["ambient_gas_excess_auc_atompercent_hours"]=.1
    assert "AMBIENT_LABEL_CONTAMINATION" in (
        screen_bract_13c_source(plan(),x)["per_block_source_screen"][0]
        ["source_discrimination_method_failures"]
    )


def test_analytical_noise_or_negative_background_excess_is_not_false_positive():
    x=observations()
    x[1]["seed_ape_sd_atom_percent"]=.5
    out=screen_bract_13c_source(plan(),x)
    assert "TARGET_SEED_ENRICHMENT_NOT_ABOVE_UNLABELLED_SHAM" in (
        out["per_block_source_screen"][0]["source_discrimination_method_failures"]
    )
    x=observations()
    x[0]["seed_postchase_atom_percent_13c"]=1.01
    out=screen_bract_13c_source(plan(),x)
    assert "NEGATIVE_APPARENT_EXCESS_BASELINE_OR_ASSAY_DRIFT" in (
        out["per_block_source_screen"][0]["source_discrimination_method_failures"]
    )


def test_stage_chase_temperature_RH_tissue_injury_and_QC_bring_hold():
    x=observations()
    x[1]["chase_hours"]=30.
    x[1]["postpollination_day"]=13.
    x[1]["fruit_temperature_C"]=29.
    x[1]["fruit_RH_percent"]=80.
    x[1]["bract_closure_intact"]=False
    x[1]["gas_monitor_QC_passed"]=False
    out=screen_bract_13c_source(plan(),x)
    errors=out["per_block_source_screen"][0]["source_discrimination_method_failures"]
    assert out["status"]=="SOURCE_ATTRIBUTION_HOLD"
    for name in ("CHASE_TIME_NOT_MATCHED","POSTPOLLINATION_STAGE_NOT_MATCHED",
                 "FRUIT_TEMPERATURE_NOT_MATCHED","FRUIT_HUMIDITY_NOT_MATCHED",
                 "BRACT_13CO2_PULSE_PHYSICAL_OR_ASSAY_QC_FAILED"):
        assert name in errors


def test_dont_impute_missing_block_or_replace_allocation():
    x=observations()
    with pytest.raises(ValueError,match="each randomized block needs"):
        screen_bract_13c_source(plan(),x[:-1])
    x=observations()
    x[0]["allocation_sha256"]="f"*64
    with pytest.raises(ValueError,match="tracer assignment differs"):
        screen_bract_13c_source(plan(),x)
    x=observations()
    x[1]["mature_seed_mass_mg"]=25
    with pytest.raises(ValueError,match="contaminated"):
        screen_bract_13c_source(plan(),x)


def test_too_few_independent_blocks_is_hold_not_positive():
    out=screen_bract_13c_source(plan(),observations(2))
    assert out["n_distinct_maternal_plants"]==6
    assert out["minimum_independent_blocks_met"] is False
    assert out["status"]=="SOURCE_ATTRIBUTION_HOLD"


def test_template_deliberately_cannot_be_used_as_frozen_source():
    template=json.loads((ROOT/"data/DALECHAMPIA_BRACT_13C_CALIBRATION_TEMPLATE_V1.json").read_text())
    with pytest.raises(ValueError,match="NOT frozen"):
        validate_tracer_plan(template)
    x=plan()
    x["thresholds"]["minimum_mimic_to_target_fruit_exposure_ratio"]=.5
    with pytest.raises(ValueError,match="match or exceed"):
        validate_tracer_plan(x)
    x=plan()
    x["limitations"]["structural_BALANCE_identified"]=True
    with pytest.raises(ValueError,match="cannot assert"):
        validate_tracer_plan(x)
    x=plan()
    x["thresholds"]["maximum_target_fruit_to_bract_gas_exposure_ratio"]=None
    with pytest.raises(ValueError,match="finite numeric"):
        validate_tracer_plan(x)


def test_exact_csv_and_runner_hash_pinning_without_research_results(tmp_path):
    rows=observations()
    buffer=io.StringIO()
    writer=csv.DictWriter(buffer,fieldnames=list(FIELDS),lineterminator="\n")
    writer.writeheader()
    for r in rows:
        writer.writerow({
            key:("true" if val is True else "false" if val is False else val)
            for key,val in r.items()
        })
    original_csv=buffer.getvalue().encode()
    assert parse_tracer_csv(original_csv)==rows
    config=tmp_path/"calibration.json"
    config.write_text(json.dumps(plan()),encoding="utf-8")
    source=tmp_path/"source.csv";source.write_bytes(original_csv)
    out_path=tmp_path/"receipt.json"
    receipt=build_receipt(config,source,out_path)
    assert receipt["status"]=="COMPARTMENT_SOURCE_SIGNATURE_SCREEN_PASSED_NOT_CAUSAL_FITNESS"
    assert len(receipt["calibration_json_sha256"])==64
    assert len(receipt["isotope_measurement_csv_sha256"])==64
    assert json.loads(out_path.read_text())==receipt
    with pytest.raises(ValueError,match="refusing to overwrite"):
        build_receipt(config,source,out_path)
    assert (ROOT/"data/DALECHAMPIA_BRACT_13C_MEASUREMENTS_TEMPLATE_V1.csv").read_text().strip()==",".join(FIELDS)
    with pytest.raises(ValueError,match="exact tracer-source CSV"):
        parse_tracer_csv(original_csv.replace(b"fruit_temperature_C",b"seed_count"))


def test_nonphysical_inputs_and_unexpected_controls_rejected():
    x=observations()
    x[0]["seed_postchase_atom_percent_13c"]=float("nan")
    with pytest.raises(ValueError,match="measurement range"):
        screen_bract_13c_source(plan(),x)
    x=observations()
    x[0]["isotope_lab_QC_passed"]=1
    with pytest.raises(ValueError,match="observed boolean"):
        screen_bract_13c_source(plan(),x)
    x=observations()
    x[0]["arm"]="FOIL_WHOLE_BLOSSOM"
    with pytest.raises(ValueError,match="wrong/duplicate source arm"):
        screen_bract_13c_source(plan(),x)

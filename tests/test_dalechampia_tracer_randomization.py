"""Synthetic blocked randomization tests: NO real isotope signal or new plants.

A significant treatment REGIME difference is not proof of carbon source.
The real prospective calibration and trial randomization have not happened.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
from pathlib import Path

import pytest

from balance_domain.dalechampia_tracer_randomization import (
    PRIMARY, SCHEMA, analyze_block_randomization,
    block_resolution_table, exact_two_sided_resolution,
    minimum_blocks_to_reject_two_sided, validate_inference_plan,
)
from balance_domain.dalechampia_tracer_source import FIELDS, parse_tracer_csv
from scripts.analyze_dalechampia_13c_block_randomization import build_inferential_receipt

ROOT=Path(__file__).resolve().parents[1]


def source_plan():
    return {
        "schema_version":"DALECHAMPIA_BRACT_13C_SOURCE_DISCRIMINATION_V1",
        "status":"SELF_DECLARED_PRE_OUTCOME_NOT_EXTERNALLY_TIME_AUTHENTICATED",
        "context_id":"SYNTHETIC_ONLY_NO_DALECHAMPIA_FIELD_ASSAY",
        "assignment_sha256":"a"*64,
        "chamber_calibration_sha256":"b"*64,
        "assay_calibration_sha256":"c"*64,
        "minimum_independent_randomized_blocks":3,
        "source_dose_comparability_rationale":(
            "ARTIFICIAL: doses are selected to pass synthetic control logic; "
            "there is no actual fruit-uptake equivalence calibration."
        ),
        "thresholds":{
            "minimum_bract_source_excess_atom_percent":0.4,
            "minimum_seed_excess_over_sham_atom_percent":0.05,
            "minimum_seed_excess_over_fruit_mimic_atom_percent":0.05,
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


def inferential_plan(source_sha=None):
    return {
        "schema_version":SCHEMA,
        "status":"SELF_DECLARED_BEFORE_OUTCOMES_NOT_TIME_VERIFIED",
        "context_id":"SYNTHETIC_ONLY_NO_DALECHAMPIA_FIELD_ASSAY",
        "calibration_plan_sha256":source_sha or "f"*64,
        "primary_contrast":PRIMARY,
        "test_sidedness":"TWO_SIDED",
        "two_sided_alpha":0.05,
        "max_exact_blocks":16,
        "monte_carlo_draws":10000,
        "monte_carlo_seed":20261018,
        "blocks_with_zero_effect_or_failed_QC_dropped":False,
        "scope_exclusions":{
            "randomization_chronology_verified":False,
            "plant_interference_ignored":False,
            "calibrated_uptake_monotonicity_verified":False,
            "causal_bract_to_seed_carbon_source_identified":False,
            "bract_specific_mature_seed_fitness_identified":False,
            "structural_BALANCE_occupancy_identified":False,
        },
    }


def fake_records(n=6):
    records=[]
    for block in range(n):
        for i,arm in enumerate((
            "SHAM_UNLABELLED","BRACT_13CO2_PULSE","FRUIT_LEAK_MIMIC"
        )):
            bract=arm=="BRACT_13CO2_PULSE"
            mimic=arm=="FRUIT_LEAK_MIMIC"
            records.append({
                "block_id":f"synthetic_block_{block:02d}",
                "plant_id":f"synthetic_mother_{block}_{i}",
                "blossom_id":f"synthetic_blossom_{block}_{i}",
                "arm":arm,
                "allocation_sha256":"a"*64,
                "postpollination_day":10.,
                "chase_hours":24.,
                "seed_background_atom_percent_13c":1.1,
                "bract_background_atom_percent_13c":1.1,
                "seed_postchase_atom_percent_13c":(
                    1.22 if bract else 1.125 if mimic else 1.101
                ),
                "bract_postchase_atom_percent_13c":3.1 if bract else 1.101,
                "seed_ape_sd_atom_percent":.004,
                "bract_ape_sd_atom_percent":.004,
                "bract_gas_excess_auc_atompercent_hours":120. if bract else 0.,
                "fruit_gas_excess_auc_atompercent_hours":.2 if bract else .6 if mimic else 0.,
                "ambient_gas_excess_auc_atompercent_hours":.001,
                "fruit_temperature_C":25.+i*.1,
                "fruit_RH_percent":55.+i*.2,
                "bract_closure_intact":True,
                "no_visible_damage":True,
                "gas_monitor_QC_passed":True,
                "isotope_lab_QC_passed":True,
            })
    return records


def run(n=6, records=None, *, config=None, calibration=None):
    cal=calibration or source_plan()
    conf=config or inferential_plan("f"*64)
    return analyze_block_randomization(
        cal,conf,records if records is not None else fake_records(n),
        actual_calibration_sha256="f"*64,
    )


def test_p_value_support_is_six_three_arm_blocks_eighteen_independent_mothers():
    frozen=json.loads((ROOT/"data/DALECHAMPIA_13C_EXACT_RANDOMIZATION_RESOLUTION_V1.json").read_text())
    exact=block_resolution_table(.05,n_start=3,n_stop=14)
    assert frozen==exact
    assert frozen["minimum_blocks_with_possible_two_sided_p_below_or_equal_alpha"]==6
    assert frozen["minimum_independent_maternal_plants_at_resolution_floor"]==18
    assert [exact_two_sided_resolution(n) for n in range(3,7)]==[
        .25,.125,.0625,.03125
    ]
    assert minimum_blocks_to_reject_two_sided(.01)==8
    assert frozen["not_actual_power_or_biological_effect"] is True
    assert all(x["n_independent_maternal_plants"]==3*x["n_independent_blocks"]
               for x in frozen["rows"])


def test_perfect_synthetic_difference_is_exact_n6_p03125_no_causal_claim():
    r=run(n=6)
    assert r["status"]=="BLOCKED_RANDOMIZED_TRACER_REGIME_CONTRAST_NOT_CARBON_SOURCE_CAUSALITY"
    assert r["n_independent_randomized_three_arm_blocks"]==6
    assert r["n_independent_maternal_plants"]==18
    assert r["n_total_source_isotope_rows"]==18
    assert r["design_has_sufficient_p_value_resolution"] is True
    assert r["source_screen_original_status"]=="COMPARTMENT_SOURCE_SIGNATURE_SCREEN_PASSED_NOT_CAUSAL_FITNESS"
    p=r["sharp_no_regime_effect_randomization_inference"]
    assert p["mode"]=="EXACT_ENUMERATION_OF_ALL_MATCHED_SIGN_ASSIGNMENTS"
    assert p["permutations_evaluated"]==64
    assert p["two_sided_p"]==.03125
    assert p["one_sided_positive_p_descriptive"]==.015625
    assert p["p_value_at_or_below_alpha"] is True
    assert r["all_preassigned_blocks_included_without_APE_based_exclusion"] is True
    assert r["p_value_is_about_randomized_regime_difference_only"] is True
    assert r["randomization_chronology_externally_verified"] is False
    assert r["fruit_dose_response_and_absorption_equivalence_verified"] is False
    assert r["source_specific_C13_to_seed_transport_caused_by_bract"] is False
    assert r["estimated_fraction_seed_carbon_from_bract"] is None
    assert r["mature_seed_fitness_effect_identified"] is False
    assert r["structural_BALANCE_occupancy_identified"] is False


@pytest.mark.parametrize("n,floor",[(3,.25),(4,.125),(5,.0625),(6,.03125),(8,.0078125)])
def test_perfectly_aligned_pairs_cannot_beat_exact_support_floor(n,floor):
    r=run(n)
    p=r["sharp_no_regime_effect_randomization_inference"]
    assert p["two_sided_p"]==floor
    assert r["exact_minimum_attainable_two_sided_p"]==floor
    assert r["design_has_sufficient_p_value_resolution"]==(n>=6)
    assert p["permutations_evaluated"]==2**n


def test_no_source_screen_posthoc_selection_even_if_one_block_fails():
    rows=fake_records()
    # This makes the leak-exposure source assay screen fail for the first
    # randomized block but must NOT drop it to inflate the significance.
    target=next(r for r in rows if r["block_id"].endswith("00")
                and r["arm"]=="BRACT_13CO2_PULSE")
    target["fruit_gas_excess_auc_atompercent_hours"]=20.
    r=run(records=rows)
    assert r["source_screen_original_status"]=="SOURCE_ATTRIBUTION_HOLD"
    assert r["n_independent_randomized_three_arm_blocks"]==6
    assert r["n_total_source_isotope_rows"]==18
    assert r["sharp_no_regime_effect_randomization_inference"]["permutations_evaluated"]==64
    assert "TARGET_FRUIT_GAS_LEAKAGE_EXCEEDS_CALIBRATED_LIMIT" in (
        r["source_screen_numeric_method_failures_by_block"]["synthetic_block_00"]
    )
    assert r["screen_status_not_used_to_select_inference_blocks"] is True
    assert r["source_specific_C13_to_seed_transport_caused_by_bract"] is False


def test_mixed_difference_signs_and_zero_case_do_not_fake_p_significance():
    rows=fake_records()
    target=next(r for r in rows if r["block_id"].endswith("00")
                and r["arm"]=="BRACT_13CO2_PULSE")
    target["seed_postchase_atom_percent_13c"]=1.12
    result=run(records=rows)
    assert result["n_independent_randomized_three_arm_blocks"]==6
    assert result["sharp_no_regime_effect_randomization_inference"]["two_sided_p"]>.03125

    rows=fake_records()
    for rec in rows:
        if rec["arm"]=="BRACT_13CO2_PULSE":
            rec["seed_postchase_atom_percent_13c"]=1.125
    zero=run(records=rows)
    assert zero["sharp_no_regime_effect_randomization_inference"]["two_sided_p"]==1.
    assert zero["sharp_no_regime_effect_randomization_inference"]["p_value_at_or_below_alpha"] is False


def test_large_n_monte_carlo_is_seeded_and_marked_not_exact():
    r1=run(n=17)
    r2=run(n=17)
    p=r1["sharp_no_regime_effect_randomization_inference"]
    assert p==r2["sharp_no_regime_effect_randomization_inference"]
    assert p["mode"]=="DETERMINISTIC_MONTE_CARLO_SIGN_FLIP_NOT_EXACT"
    assert p["permutations_evaluated"]==10000
    assert p["plus_one_randomization_correction_used"] is True
    assert p["p_value_monte_carlo_standard_error"]>=0
    assert p["two_sided_p"]>0
    assert r1["n_independent_maternal_plants"]==51


def test_duplicate_independent_parent_and_missing_arm_still_fail():
    rows=fake_records()
    rows[1]["plant_id"]=rows[0]["plant_id"]
    with pytest.raises(ValueError,match="independent mother"):
        run(records=rows)
    with pytest.raises(ValueError,match="each randomized block needs"):
        run(records=fake_records()[:-1])


def test_plan_calibration_digest_and_unsigned_chronology_fail_closed():
    c=inferential_plan()
    with pytest.raises(ValueError,match="bound to the actual isotope calibration SHA256"):
        analyze_block_randomization(source_plan(),c,fake_records(6),
                                    actual_calibration_sha256="e"*64)
    d=copy.deepcopy(c)
    d["status"]="POSTHOC_ALL_DATA_KNOWN"
    with pytest.raises(ValueError,match="NOT externally frozen"):
        validate_inference_plan(d)
    d=copy.deepcopy(c)
    d["scope_exclusions"]["causal_bract_to_seed_carbon_source_identified"]=True
    with pytest.raises(ValueError,match="must not claim"):
        validate_inference_plan(d)
    d=copy.deepcopy(c)
    d["blocks_with_zero_effect_or_failed_QC_dropped"]=True
    with pytest.raises(ValueError,match="post-outcome exclusions"):
        validate_inference_plan(d)
    d=copy.deepcopy(c)
    d["test_sidedness"]="ONE_SIDED"
    with pytest.raises(ValueError,match="primary two-sided"):
        validate_inference_plan(d)


def test_unfilled_future_trial_template_is_invalid():
    template=json.loads((ROOT/"data/DALECHAMPIA_13C_BLOCK_RANDOMIZATION_TEMPLATE_V1.json").read_text())
    with pytest.raises(ValueError,match="NOT externally frozen"):
        validate_inference_plan(template)
    assert template["status"]=="NOT_FROZEN_REQUIRES_EXTERNALLY_DATED_PREOUTCOME_REGISTRATION"


def test_source_csv_and_sha_pinned_readout_without_real_field_claim(tmp_path):
    cal=source_plan()
    raw_json=json.dumps(cal).encode("utf-8")
    digest=hashlib.sha256(raw_json).hexdigest()
    infer=inferential_plan(digest)
    rows=fake_records(6)
    buffer=io.StringIO()
    writer=csv.DictWriter(buffer,fieldnames=list(FIELDS),lineterminator="\n")
    writer.writeheader()
    for item in rows:
        writer.writerow({
            key:("true" if value is True else "false" if value is False else value)
            for key,value in item.items()
        })
    raw=buffer.getvalue().encode("utf-8")
    assert parse_tracer_csv(raw)==rows
    calp=tmp_path/"cal.json";calp.write_bytes(raw_json)
    inp=tmp_path/"inference.json";inp.write_text(json.dumps(infer),encoding="utf-8")
    dat=tmp_path/"isotope.csv";dat.write_bytes(raw)
    out=tmp_path/"result.json"
    result=build_inferential_receipt(calp,inp,dat,out)
    assert result["sharp_no_regime_effect_randomization_inference"]["two_sided_p"]==.03125
    assert result["source_calibration_sha256"]==digest
    assert result["observed_isotope_measurement_sha256"]==hashlib.sha256(raw).hexdigest()
    assert json.loads(out.read_text(encoding="utf-8"))==result
    assert result["external_pre_outcome_protocol_time_authenticated"] is False
    with pytest.raises(ValueError,match="refusing to overwrite"):
        build_inferential_receipt(calp,inp,dat,out)

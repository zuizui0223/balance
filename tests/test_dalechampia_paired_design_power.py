"""Numerical planning scenarios from actual PR236 blossom/seed covariance; not a field result."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from balance_domain.dalechampia_paired_design_power import (
    plan_paired_blossom_scenarios,
    validate_source_variance_receipt,
    _normal_power,
)

ROOT=Path(__file__).resolve().parents[1]


def source():
    return json.loads((ROOT/"data/DALECHAMPIA_2015_NESTED_BLOSSOM_SOURCE_VERIFIED_V1.json").read_text())


def scenarios():
    return json.loads((ROOT/"data/DALECHAMPIA_BRACT_ISOLATION_POWER_SCENARIOS_V1.json").read_text())


def test_original_covariance_not_treated_as_true_isolated_carbon_effect():
    s=source()
    v=validate_source_variance_receipt(s)
    assert v["blossom_variance_mg2"]==14.499685
    assert v["seed_residual_variance_mg2"]==3.808892
    assert v["maternal_variance_mg2"]==15.190316
    result=plan_paired_blossom_scenarios(scenarios(),s)
    assert result["status"]=="ILLUSTRATIVE_SOURCE_ANCHORED_NORMAL_POWER_ONLY"
    assert result["source_var_receipt_not_new_field_data"] is True
    assert result["normal_small_cluster_uncertainty_not_included"] is True
    assert result["stage_specific_seed_mass_does_not_equal_mature_fitness"] is True
    assert result["carbon_specific_effect_size_not_yet_observed"] is True
    assert result["pilot_feasibility_not_yet_demonstrated"] is True
    assert result["structural_BALANCE_occupancy_identified"] is False


def test_true_replication_is_matched_mothers_not_1000_seeds():
    r=plan_paired_blossom_scenarios(scenarios(),source())
    v={x["scenario_id"]:x for x in r["scenarios"]}
    assert v["foil_magnitude_only_one_blossom"]["minimum_independent_maternal_plants_normal_approx"]==71
    assert v["foil_magnitude_only_two_blossoms"]["minimum_independent_maternal_plants_normal_approx"]==36
    assert v["one_mg_one_blossom"]["minimum_independent_maternal_plants_normal_approx"]==236
    assert v["weak_half_mg_one_blossom"]["minimum_independent_maternal_plants_normal_approx"]==941
    assert all(x["plants_are_not_seeds_or_blossoms"] for x in r["scenarios"])
    assert v["foil_magnitude_only_one_blossom"]["hypothetical_effect_mg"]==1.83
    assert v["foil_magnitude_only_two_blossoms"]["approximate_power_at_evaluated_n"]>=.8


def test_seed_subsamples_do_not_replace_independent_blossoms():
    design=scenarios()
    baseline=plan_paired_blossom_scenarios(design,source())["scenarios"]
    entries={x["scenario_id"]:x for x in baseline}
    a=entries["foil_magnitude_only_two_blossoms_four_seeds"]
    b=entries["foil_magnitude_only_two_blossoms"]
    assert a["minimum_independent_maternal_plants_normal_approx"]>=b["minimum_independent_maternal_plants_normal_approx"]
    p4,se4=_normal_power(1.83,30,2,4,14.499685,3.808892,.05)
    p8,se8=_normal_power(1.83,30,2,8,14.499685,3.808892,.05)
    assert p8 > p4
    assert se8 < se4


def test_pairing_and_independence_assumptions_cannot_be_switched_off():
    design=scenarios()
    design["assumptions"]["no_interference_between_blossoms"]=False
    with pytest.raises(ValueError,match="independence assumptions"):
        plan_paired_blossom_scenarios(design,source())
    design=scenarios()
    design["assumptions"]["mature_seed_fitness_equivalence_assumed"]=True
    with pytest.raises(ValueError,match="overstate"):
        plan_paired_blossom_scenarios(design,source())
    design=scenarios()
    design["assumptions"]["bract_local_effect_size_empirically_known"]=True
    with pytest.raises(ValueError,match="overstate"):
        plan_paired_blossom_scenarios(design,source())


def test_source_variance_drift_and_false_BALANCE_claim_fail_closed():
    src=source()
    src["random_intercept_comparison"]["maternal_plus_blossom"]["blossom_variance"]=2.0
    with pytest.raises(ValueError,match="component drifted"):
        plan_paired_blossom_scenarios(scenarios(),src)
    src=source()
    src["interpretation_limits"]["structural_BALANCE_occupancy_identified"]=True
    with pytest.raises(ValueError,match="NOT structural BALANCE"):
        plan_paired_blossom_scenarios(scenarios(),src)


def test_no_arbitrary_n_or_seed_count_and_no_nan_are_accepted():
    d=scenarios()
    d["scenarios"][0]["usable_measured_seeds_per_blossom"]=10
    with pytest.raises(ValueError,match="at most 9"):
        plan_paired_blossom_scenarios(d,source())
    d=scenarios()
    d["scenarios"][0]["hypothetical_effect_mg"]=float("nan")
    with pytest.raises(ValueError,match="planning domain"):
        plan_paired_blossom_scenarios(d,source())
    d=scenarios()
    d["scenarios"][0]["scenario_id"]=d["scenarios"][1]["scenario_id"]
    with pytest.raises(ValueError,match="duplicate"):
        plan_paired_blossom_scenarios(d,source())


def test_very_small_effect_exceeds_cap_but_does_not_fabricate_power():
    d=scenarios()
    d["assumptions"]["max_maternal_plants"]=10
    d["scenarios"]=[d["scenarios"][0]]
    r=plan_paired_blossom_scenarios(d,source())["scenarios"][0]
    assert r["target_reached_under_assumptions"] is False
    assert r["minimum_independent_maternal_plants_normal_approx"] is None
    assert r["evaluated_at_n_mothers"]==10
    assert r["approximate_power_at_evaluated_n"]<.8

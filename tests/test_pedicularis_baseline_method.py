"""Synthetic method-only contracts; these are NOT Pedicularis field observations."""
from __future__ import annotations

import copy

import pytest

from balance_domain.pedicularis_baseline import (
    ARMS, FIELDS, evaluate_pedicularis_baseline_method,
)


def config():
    return {
        "schema_version": "PEDICULARIS_SCH_XY_BASELINE_METHOD_V1",
        "status": "FROZEN_PRE_OUTCOME",
        "blinded_to_biological_outcomes": True,
        "expected_sch_water_state": "XY_Y0_DRY",
        "context_id": "SYNTHETIC_P_A_2027",
        "population_id": "P_A",
        "season_id": "2027",
        "protocol_version": "PREOUTCOME_METHOD_A",
        "fitness_scale_id": "UNDAMAGED_SEEDS_PER_FOCAL_FLOWER",
        "threshold_justification": "Synthetic pre-outcome method design fixture only",
        "thresholds": {
            "min_independent_plants_per_arm": 2,
            "max_dry_water_depth_mm": 1.0,
            "min_wet_water_depth_mm": 5.0,
            "max_within_arm_water_depth_range_mm": 2.0,
            "max_sch_y0_profile_endpoint_gap_mm": 0.5,
        },
    }


def rows():
    depths = {
        "SCH_FIXED": [(0.2, 0.4), (0.3, 0.5)],
        "XY_Y0_DRY": [(0.1, 0.3), (0.2, 0.4)],
        "XY_Y1_WET": [(6.0, 6.4), (6.3, 6.5)],
    }
    return [
        {
            "context_id": "SYNTHETIC_P_A_2027",
            "population_id": "P_A",
            "season_id": "2027",
            "protocol_version": "PREOUTCOME_METHOD_A",
            "plant_id": f"{arm}_plant_{i}",
            "water_compartment_id": f"{arm}_compartment_{i}",
            "arm": arm,
            "water_depth_early_mm": early,
            "water_depth_late_mm": late,
        }
        for arm, pairs in depths.items()
        for i, (early, late) in enumerate(pairs)
    ]


def test_schema_is_method_only_and_screen_pass_never_promotes_biology():
    assert "undamaged_seed_count" not in FIELDS
    assert "pollen_grains" not in FIELDS
    out = evaluate_pedicularis_baseline_method(rows(), config())
    assert out.status == "BASELINE_METHOD_PROFILE_SCREEN_PASSED_NOT_CAUSAL"
    assert out.reasons == ()
    assert out.plant_counts == {arm: 2 for arm in ARMS}
    assert out.sch_y0_profile_endpoint_gap_mm == pytest.approx(0.1)
    assert out.claim_level == "METHOD_PROFILE_ONLY_NOT_CAUSAL_OR_ARCHITECTURE"
    assert out.reproduction_outcomes_read is False
    assert out.source_field_lineage_verified is False
    assert out.structural_architecture_cost_identified is False


@pytest.mark.parametrize("changed", ["SCH_FIXED", "XY_Y0_DRY"])
def test_missing_water_state_fails_closed(changed):
    data = [row for row in rows() if row["arm"] != changed]
    out = evaluate_pedicularis_baseline_method(data, config())
    assert out.status == "BASELINE_METHOD_HOLD"
    assert f"insufficient_independent_plants:{changed}" in out.reasons


def test_sch_naturally_wet_does_not_get_relabelled_to_dry_y0():
    data = rows()
    for row in data:
        if row["arm"] == "SCH_FIXED":
            row["water_depth_early_mm"] = 6.0
            row["water_depth_late_mm"] = 6.1
    out = evaluate_pedicularis_baseline_method(data, config())
    assert out.status == "BASELINE_METHOD_HOLD"
    assert "baseline_not_reliably_dry:SCH_FIXED" in out.reasons
    assert "sch_y0_water_profile_not_matched" in out.reasons


def test_wet_state_must_actually_differ():
    data = rows()
    for row in data:
        if row["arm"] == "XY_Y1_WET":
            row["water_depth_early_mm"] = 0.2
            row["water_depth_late_mm"] = 0.5
    out = evaluate_pedicularis_baseline_method(data, config())
    assert out.status == "BASELINE_METHOD_HOLD"
    assert "xy_y1_not_reliably_wet" in out.reasons


def test_nonmatching_dry_profiles_hold_even_if_both_called_y0():
    data = rows()
    for row in data:
        if row["arm"] == "SCH_FIXED":
            row["water_depth_early_mm"] = 0.0
            row["water_depth_late_mm"] = 0.0
        if row["arm"] == "XY_Y0_DRY":
            row["water_depth_early_mm"] = 0.9
            row["water_depth_late_mm"] = 1.0
    out = evaluate_pedicularis_baseline_method(data, config())
    assert out.status == "BASELINE_METHOD_HOLD"
    assert "sch_y0_water_profile_not_matched" in out.reasons


def test_method_data_cannot_include_or_impute_biological_outcomes():
    data = rows()
    data[0]["undamaged_seed_count"] = 42
    with pytest.raises(ValueError, match="method-only canonical columns"):
        evaluate_pedicularis_baseline_method(data, config())


def test_plant_is_cluster_and_cannot_count_independent_in_multiple_arms():
    data = rows()
    data[-1]["plant_id"] = data[0]["plant_id"]
    with pytest.raises(ValueError, match="duplicate plant_id"):
        evaluate_pedicularis_baseline_method(data, config())


def test_hydrologic_compartment_is_not_an_independent_duplicate():
    data = rows()
    data[-1]["water_compartment_id"] = data[0]["water_compartment_id"]
    with pytest.raises(ValueError, match="duplicate water_compartment_id"):
        evaluate_pedicularis_baseline_method(data, config())


def test_context_mismatch_and_postoutcome_freeze_fail_closed():
    data = rows()
    data[0]["season_id"] = "different"
    with pytest.raises(ValueError, match="season_id"):
        evaluate_pedicularis_baseline_method(data, config())
    conf = config()
    conf["status"] = "FROZEN_AFTER_OUTCOME"
    with pytest.raises(ValueError, match="pre-outcome"):
        evaluate_pedicularis_baseline_method(rows(), conf)


def test_unfrozen_baseline_choice_and_outcome_blinding_fail_closed():
    c = config()
    c["expected_sch_water_state"] = "XY_Y1_WET"
    with pytest.raises(ValueError, match="dry y0"):
        evaluate_pedicularis_baseline_method(rows(), c)
    c = config()
    c["blinded_to_biological_outcomes"] = False
    with pytest.raises(ValueError, match="blinded"):
        evaluate_pedicularis_baseline_method(rows(), c)


def test_invalid_numeric_tolerances_not_reinterpreted():
    c = config()
    c["thresholds"]["min_independent_plants_per_arm"] = 1.5
    with pytest.raises(ValueError, match="integer"):
        evaluate_pedicularis_baseline_method(rows(), c)
    c = config()
    c["thresholds"]["min_wet_water_depth_mm"] = 0.5
    with pytest.raises(ValueError, match="not overlap"):
        evaluate_pedicularis_baseline_method(rows(), c)
    data = rows()
    data[0]["water_depth_early_mm"] = True
    with pytest.raises(ValueError, match="boolean"):
        evaluate_pedicularis_baseline_method(data, config())


def test_repeated_dependent_water_compartments_cannot_inflate_support():
    data = rows()
    extra = copy.deepcopy(data[0])
    extra["water_compartment_id"] = "new_whorl_same_plant"
    data.append(extra)
    with pytest.raises(ValueError, match="duplicate plant_id"):
        evaluate_pedicularis_baseline_method(data, config())


def test_method_cli_writes_hashed_receipt_and_refuses_overwrite(tmp_path):
    import csv
    import hashlib
    import json

    from scripts.evaluate_pedicularis_baseline import build_receipt

    csv_path = tmp_path / "baseline.csv"
    conf_path = tmp_path / "thresholds.json"
    out_path = tmp_path / "receipt.json"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows())
    conf_path.write_text(json.dumps(config(), sort_keys=True), encoding="utf-8")
    result = build_receipt(csv_path, conf_path, out_path)
    assert out_path.exists()
    assert result["status"] == "BASELINE_METHOD_PROFILE_SCREEN_PASSED_NOT_CAUSAL"
    assert result["source_csv_sha256"] == hashlib.sha256(csv_path.read_bytes()).hexdigest()
    assert result["frozen_config_sha256"] == hashlib.sha256(conf_path.read_bytes()).hexdigest()
    assert result["functional_state_BALANCE_identified"] is False
    assert result["structural_architecture_BALANCE_identified"] is False
    with pytest.raises(ValueError, match="already exists"):
        build_receipt(csv_path, conf_path, out_path)


def test_unfrozen_production_template_cannot_pass(tmp_path):
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    template_path = root / "data/PEDICULARIS_SCH_XY_BASELINE_THRESHOLDS_TEMPLATE_V1.json"
    template = json.loads(template_path.read_text(encoding="utf-8"))
    assert template["status"] != "FROZEN_PRE_OUTCOME"
    with pytest.raises(ValueError, match="pre-outcome"):
        evaluate_pedicularis_baseline_method(rows(), template)


def test_registered_baseline_amendment_never_claims_field_result():
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    d = json.loads((root / "data/PEDICULARIS_BALANCE_COMPARATOR_AMENDMENT_V2.json").read_text())
    gate = d["baseline_method_screen"]
    assert gate["status"] == "NO_REAL_FIELD_PROFILE_SCREEN_RUN"
    assert gate["real_source_lineage_verification"] is False
    assert gate["active_producer_verified"] is False
    assert gate["functional_state_BALANCE_identified"] is False

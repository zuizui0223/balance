"""Synthetic-only method-validation tests: no real Pedicularis observations."""
import copy
import csv
import json
from pathlib import Path

import pytest

from balance_domain.pedicularis_water_b0 import (
    ARMS, FIELDS, SCHEMA, evaluate_water_b0,
)
from scripts.evaluate_pedicularis_water_b0 import build_receipt


def _config():
    return {
        "schema_version": SCHEMA,
        "status": "FROZEN_PRE_OUTCOME",
        "context_id": "TEST_POP_2026",
        "population_id": "TEST_POP",
        "season_id": "2026_TEST",
        "protocol_version": "SYNTHETIC_PROTOCOL_V1",
        "blinded_to_reproductive_outcomes": True,
        "threshold_justification": "Synthetic tests only; not biological thresholds",
        "randomization_schedule_sha256": "a" * 64,
        "thresholds": {
            "min_independent_plants_per_arm": 4,
            "min_blocks_per_arm": 2,
            "min_wet_depth_mm": 1.5,
            "max_dry_depth_mm": 0.5,
            "min_water_fidelity_fraction": 0.9,
            "max_missing_measurement_fraction": 0.02,
            "max_mechanical_damage_fraction": 0.1,
            "max_exsertion_shift_mm": 0.4,
            "max_exsertion_offtarget_fraction": 0.1,
            "min_pollinator_entry_unobstructed_fraction": 0.95,
            "max_dry_vs_refilled_handling_gap_seconds": 3.0,
        },
    }


def _rows():
    out = []
    for arm in ARMS:
        for i in range(6):
            dry = arm == "INTACT_DRY"
            out.append({
                "context_id": "TEST_POP_2026",
                "population_id": "TEST_POP",
                "season_id": "2026_TEST",
                "protocol_version": "SYNTHETIC_PROTOCOL_V1",
                "plant_id": f"P_{arm}_{i+1}",
                "water_compartment_id": f"WC_{arm}_{i+1}",
                "water_compartment_confirmed": "1",
                "block_id": f"B{i%2+1}",
                "assigned_arm": arm,
                "assignment_locked_before_measurement": "1",
                "bract_perforated": "0",
                "water_depth_early_mm": "0.2" if dry else "2.4",
                "water_depth_late_mm": "0.3" if dry else "2.1",
                "handling_duration_seconds": (
                    "0" if arm == "INTACT_WET" else "10"
                ),
                "abs_exsertion_shift_mm": "0.1",
                "mechanical_damage": "0",
                "pollinator_entry_unobstructed": "1",
            })
    return out


def test_synthetic_method_pass_never_promotes_biological_fitness():
    result = evaluate_water_b0(_rows(), _config())
    assert result["status"] == "B0_METHOD_FEASIBILITY_SCREEN_PASSED_NOT_CAUSAL"
    assert result["gate_reasons"] == []
    assert result["n_water_compartments"] == 18
    assert result["n_distinct_plants_total"] == 18
    for arm in ARMS:
        assert result["arms"][arm]["n_distinct_plants"] == 6
        assert result["arms"][arm]["n_blocks"] == 2
        assert result["arms"][arm]["water_fidelity_fraction"] == 1
    assert result["independent_randomization_verified"] is False
    assert result["causal_water_effect_identified"] is False
    assert result["functional_state_BALANCE_identified"] is False
    assert result["structural_architecture_BALANCE_identified"] is False


def test_failed_water_depth_and_breached_bract_hold():
    data = _rows()
    dry = next(row for row in data if row["assigned_arm"] == "INTACT_DRY")
    dry["water_depth_late_mm"] = "3.0"
    dry["bract_perforated"] = "1"
    result = evaluate_water_b0(data, _config())
    assert result["status"] == "B0_METHOD_FEASIBILITY_HOLD"
    assert "water_state_not_maintained:INTACT_DRY" in result["gate_reasons"]
    assert "bract_perforation:INTACT_DRY" in result["gate_reasons"]


def test_handling_mismatch_and_pollinator_access_fail_closed():
    data = _rows()
    for item in data:
        if item["assigned_arm"] == "INTACT_REFILLED_WET":
            item["handling_duration_seconds"] = "25"
        if item["assigned_arm"] == "INTACT_WET":
            item["pollinator_entry_unobstructed"] = "0"
    result = evaluate_water_b0(data, _config())
    assert "dry_refilled_handling_not_matched" in result["gate_reasons"]
    assert "pollinator_entry_restricted:INTACT_WET" in result["gate_reasons"]


def test_missingness_is_not_an_imputed_success():
    data = _rows()
    data[0]["water_depth_early_mm"] = ""
    result = evaluate_water_b0(data, _config())
    assert "method_measurements_missing:INTACT_WET" in result["gate_reasons"]
    assert "water_state_not_maintained:INTACT_WET" in result["gate_reasons"]


def test_unfrozen_and_bad_thresholds_rejected():
    conf = _config()
    conf["status"] = "TEMPLATE_NOT_FROZEN"
    with pytest.raises(ValueError, match="not prospectively frozen"):
        evaluate_water_b0(_rows(), conf)
    conf = _config()
    conf["thresholds"]["min_wet_depth_mm"] = 0.3
    with pytest.raises(ValueError, match="overlap"):
        evaluate_water_b0(_rows(), conf)
    conf = _config()
    conf["thresholds"]["min_water_fidelity_fraction"] = "REQUIRED_BEFORE_USE"
    with pytest.raises(ValueError, match="invalid numeric"):
        evaluate_water_b0(_rows(), conf)


def test_unregistered_field_cannot_inject_biological_outcomes():
    data = _rows()
    data[0]["undamaged_seed_count"] = "999"
    with pytest.raises(ValueError, match="noncanonical field"):
        evaluate_water_b0(data, _config())


def test_duplicate_source_units_and_unlocked_assignments():
    data = _rows()
    data[1]["water_compartment_id"] = data[0]["water_compartment_id"]
    with pytest.raises(ValueError, match="duplicate"):
        evaluate_water_b0(data, _config())
    data = _rows()
    data[1]["plant_id"] = data[0]["plant_id"]
    with pytest.raises(ValueError, match="one compartment per plant"):
        evaluate_water_b0(data, _config())
    data = _rows()
    data[0]["assignment_locked_before_measurement"] = "0"
    result = evaluate_water_b0(data, _config())
    assert "assignment_not_prelocked" in result["gate_reasons"]


def test_unverified_water_compartment_holds_pilot():
    data = _rows()
    data[0]["water_compartment_confirmed"] = "0"
    out = evaluate_water_b0(data, _config())
    assert out["status"] == "B0_METHOD_FEASIBILITY_HOLD"
    assert "physical_water_compartment_unverified" in out["gate_reasons"]


def test_cli_writes_exact_input_hashes_and_no_overwrite(tmp_path):
    pilot = tmp_path / "pilot.csv"
    config_file = tmp_path / "thresholds.json"
    output = tmp_path / "receipt.json"
    with pilot.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(_rows())
    config_file.write_text(json.dumps(_config()), encoding="utf-8")
    receipt = build_receipt(pilot, config_file, output)
    assert receipt["status"] == "B0_METHOD_FEASIBILITY_SCREEN_PASSED_NOT_CAUSAL"
    assert len(receipt["source_csv_sha256"]) == 64
    assert len(receipt["threshold_config_sha256"]) == 64
    assert json.loads(output.read_text())["claim_ceiling"].startswith("method_only")
    with pytest.raises(ValueError, match="already exists"):
        build_receipt(pilot, config_file, output)


def test_template_stays_unfrozen_and_biology_free():
    root = Path(__file__).resolve().parents[1]
    conf = json.loads((root /
        "data/PEDICULARIS_WATER_B0_METHOD_THRESHOLDS_TEMPLATE_V1.json"
    ).read_text(encoding="utf-8"))
    assert conf["status"] == "TEMPLATE_NOT_FROZEN"
    assert conf["thresholds"]["min_wet_depth_mm"] == "REQUIRED_BEFORE_USE"
    header = (root / "data/PEDICULARIS_WATER_B0_METHOD_PILOT_TEMPLATE_V1.csv"
              ).read_text(encoding="utf-8").strip().split(",")
    assert tuple(header) == FIELDS
    assert not any("seed" in k or "egg" in k or "fitness" in k for k in header)

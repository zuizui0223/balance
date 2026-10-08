"""Synthetic-only tests of water treatment allocation across density strata."""
import copy
import csv
import json
from pathlib import Path

import pytest

from balance_domain.pedicularis_density_water_allocation import (
    SCHEMA, FIELDS, ARMS, assess_density_water_allocation,
)


def protocol():
    return {
        "schema_version": SCHEMA,
        "status": "FROZEN_PRE_OUTCOME",
        "context_id": "SYNTHETIC_CTX",
        "population_id": "SYNTHETIC_POP",
        "season_id": "SYNTHETIC_SEASON",
        "protocol_version": "TEST_PROTOCOL_V1",
        "density_cutoffs_justification":
            "Synthetic fixtures use source-like cutoffs, not field thresholds",
        "allocation_locked_before_biological_outcomes": True,
        "water_method_B0_status": "B0_METHOD_FEASIBILITY_SCREEN_PASSED_NOT_CAUSAL",
        "water_B0_receipt_sha256": "a" * 64,
        "water_B0_context_id": "SYNTHETIC_B0_CONTEXT",
        "water_B0_protocol_version": "SYNTHETIC_B0_METHOD_V1",
        "thresholds": {
            "sparse_max_density_flowering_plants_m2": 2,
            "dense_min_density_flowering_plants_m2": 5,
            "min_patches_per_stratum": 2,
            "min_plants_per_arm_per_patch": 2,
            "min_blocks_with_all_three_arms_per_patch": 2,
        },
    }



def method_receipt():
    return {
        "schema_version": "PEDICULARIS_WATER_B0_METHOD_FEASIBILITY_RECEIPT_V1",
        "status": "B0_METHOD_FEASIBILITY_SCREEN_PASSED_NOT_CAUSAL",
        "context": {
            "context_id": "SYNTHETIC_B0_CONTEXT",
            "population_id": "SYNTHETIC_POP",
            "season_id": "SYNTHETIC_SEASON",
            "protocol_version": "SYNTHETIC_B0_METHOD_V1",
        },
        "randomization_unit": "PLANT_WITH_ONE_WATER_COMPARTMENT_PER_PLANT",
        "gate_reasons": [],
        "causal_water_effect_identified": False,
        "structural_architecture_BALANCE_identified": False,
        "claim_ceiling": "method_only_no_causal_water_contrast",
    }


def assess(rows, conf):
    return assess_density_water_allocation(
        rows, conf, b0_method_receipt=method_receipt(),
        b0_method_sha256="a"*64,
    )


def sample_rows():
    rows = []
    for stratum, density in (("SPARSE", "1"), ("DENSE", "8")):
        for patch in range(2):
            for block in range(2):
                for arm in ARMS:
                    prefix = f"{stratum}_P{patch}_B{block}_{arm}"
                    rows.append({
                        "context_id": "SYNTHETIC_CTX",
                        "population_id": "SYNTHETIC_POP",
                        "season_id": "SYNTHETIC_SEASON",
                        "protocol_version": "TEST_PROTOCOL_V1",
                        "site_id": "SITE0",
                        "patch_id": f"{stratum}_{patch}",
                        "randomization_block_id": f"B{block}",
                        "plant_id": f"PLANT_{prefix}",
                        "water_compartment_id": f"WATER_{prefix}",
                        "assigned_water_arm": arm,
                        "preassignment_density_flowering_plants_m2": density,
                        "preassignment_patch_size_flowering_plants": "10",
                        "assignment_locked_before_outcomes": "1",
                        "water_compartment_confirmed": "1",
                    })
    return rows


def test_qualifies_balanced_patch_density_water_allocation_without_biological_promotion():
    result = assess(sample_rows(), protocol())
    assert result["status"] == "DENSITY_STRATIFIED_WATER_ALLOCATION_SUPPORTED_NOT_EFFECT"
    assert result["n_independent_plants"] == 24
    assert result["n_independent_patches"] == 4
    assert result["patches_by_stratum"] == {"DENSE": 2, "SPARSE": 2}
    assert result["gate_reasons"] == []
    for patch in result["patches"]:
        assert patch["n_plants_by_arm"] == {arm: 2 for arm in sorted(ARMS)}
        assert patch["n_blocks_with_all_arms"] == 2
    assert result["plant_water_randomization_verified_independently"] is False
    assert result["causal_patch_density_effect_identified"] is False
    assert result["water_by_density_effect_heterogeneity_identified"] is False
    assert result["BALANCE_worldline_occupancy_identified"] is False


def test_intermediate_density_not_silently_discarded():
    rows = sample_rows()
    for row in rows:
        if row["patch_id"] == "SPARSE_0":
            row["preassignment_density_flowering_plants_m2"] = "3"
    report = assess(rows, protocol())
    assert report["status"] == "DENSITY_WATER_ALLOCATION_HOLD"
    assert "intermediate_density_patch_requires_preregistered_route" in report["gate_reasons"]
    assert report["patches_by_stratum"]["SPARSE"] == 1
    assert len(report["patches"]) == 4


def test_missing_one_water_arm_in_patch_is_a_positivity_failure():
    rows = [x for x in sample_rows()
            if not (x["patch_id"] == "DENSE_0"
                    and x["assigned_water_arm"] == "INTACT_DRY")]
    report = assess(rows, protocol())
    assert report["status"] == "DENSITY_WATER_ALLOCATION_HOLD"
    assert "insufficient_arm_support:SITE0/DENSE_0/INTACT_DRY" in report["gate_reasons"]


def test_block_by_arm_confounding_cannot_be_corrected_afterwards():
    rows = sample_rows()
    for row in rows:
        row["randomization_block_id"] += "_" + row["assigned_water_arm"]
    report = assess(rows, protocol())
    assert any(x.startswith("within_patch_arms_confounded_with_blocks")
               for x in report["gate_reasons"])


def test_plant_and_water_compartment_pseudoreplication_rejected():
    rows = sample_rows()
    rows[1]["plant_id"] = rows[0]["plant_id"]
    with pytest.raises(ValueError, match="duplicate plant ID"):
        assess(rows, protocol())
    rows = sample_rows()
    rows[1]["water_compartment_id"] = rows[0]["water_compartment_id"]
    with pytest.raises(ValueError, match="duplicate water-compartment ID"):
        assess(rows, protocol())


def test_inconsistent_patch_baseline_and_impossible_patch_n_rejected():
    rows = sample_rows()
    rows[0]["preassignment_density_flowering_plants_m2"] = "1.8"
    with pytest.raises(ValueError, match="patch baseline density/size changed"):
        assess(rows, protocol())
    rows = sample_rows()
    for row in rows:
        if row["patch_id"] == "SPARSE_0":
            row["preassignment_patch_size_flowering_plants"] = "5"
    with pytest.raises(ValueError, match="exceed patch"):
        assess(rows, protocol())


def test_unfrozen_cutoffs_and_unqualified_water_method_rejected():
    c = protocol()
    c["status"] = "TEMPLATE_NOT_FROZEN"
    with pytest.raises(ValueError, match="not prospectively frozen"):
        assess(sample_rows(), c)
    c = protocol()
    c["thresholds"]["sparse_max_density_flowering_plants_m2"] = 6
    with pytest.raises(ValueError, match="strata overlap"):
        assess(sample_rows(), c)
    c = protocol()
    c["water_method_B0_status"] = "B0_METHOD_FEASIBILITY_HOLD"
    with pytest.raises(ValueError, match="B0 method required|validated water-only B0"):
        assess(sample_rows(), c)
    c = protocol()
    c["water_B0_receipt_sha256"] = "REQUIRED_BEFORE_USE"
    with pytest.raises(ValueError, match="not prospectively frozen"):
        assess(sample_rows(), c)


def test_no_biological_outcomes_or_unlocked_assignments():
    rows = sample_rows()
    rows[0]["seed_predation_rate"] = "0.01"
    with pytest.raises(ValueError, match="noncanonical"):
        assess(rows, protocol())
    rows = sample_rows()
    rows[0]["assignment_locked_before_outcomes"] = "0"
    rows[1]["water_compartment_confirmed"] = "0"
    report = assess(rows, protocol())
    assert "assignment_not_preoutcome_locked" in report["gate_reasons"]
    assert "unverified_shared_water_compartment" in report["gate_reasons"]


def test_source_template_requires_all_cutoffs_to_be_prospectively_frozen():
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root /
        "data/PEDICULARIS_DENSITY_WATER_ALLOCATION_PROTOCOL_TEMPLATE_V1.json"
    ).read_text(encoding="utf-8"))
    assert cfg["status"] == "TEMPLATE_NOT_FROZEN"
    assert cfg["water_method_B0_status"] == "REQUIRED_BEFORE_USE"
    assert all(v == "REQUIRED_BEFORE_USE" for v in cfg["thresholds"].values())
    header = (root /
        "data/PEDICULARIS_DENSITY_WATER_ALLOCATION_TEMPLATE_V1.csv"
    ).read_text(encoding="utf-8").strip().split(",")
    assert tuple(header) == FIELDS
    assert not any(x in header for x in
                   ("seed_count", "pollen_grains", "oviposition_count", "predation_rate"))



def test_cli_binds_both_input_sha256_and_refuses_overwrite(tmp_path):
    from scripts.audit_pedicularis_density_water_allocation import build_receipt
    rows_file = tmp_path / "allocation.csv"
    config_file = tmp_path / "frozen-protocol.json"
    receipt_file = tmp_path / "allocation-receipt.json"
    with rows_file.open("w", encoding="utf-8", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sample_rows())
    b0 = tmp_path / "b0-method-receipt.json"
    b0.write_text(json.dumps(method_receipt()), encoding="utf-8")
    import hashlib
    cfg = protocol()
    cfg["water_B0_receipt_sha256"] = hashlib.sha256(b0.read_bytes()).hexdigest()
    config_file.write_text(json.dumps(cfg), encoding="utf-8")
    result = build_receipt(rows_file, config_file, b0, receipt_file)
    assert result["status"] == "DENSITY_STRATIFIED_WATER_ALLOCATION_SUPPORTED_NOT_EFFECT"
    assert len(result["allocation_csv_sha256"]) == 64
    assert len(result["protocol_json_sha256"]) == 64
    assert json.loads(receipt_file.read_text())["water_effect_identified"] is False
    with pytest.raises(ValueError, match="already exists"):
        build_receipt(rows_file, config_file, b0, receipt_file)


def test_csv_does_not_accept_previously_observed_fitness_columns(tmp_path):
    from scripts.audit_pedicularis_density_water_allocation import build_receipt
    csv_path = tmp_path / "with-outcomes.csv"
    fields = list(FIELDS) + ["seed_damage_fraction"]
    with csv_path.open("w", encoding="utf-8", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=fields)
        writer.writeheader()
        for row in sample_rows():
            writer.writerow({**row, "seed_damage_fraction": "0.2"})
    config_file = tmp_path / "protocol.json"
    b0 = tmp_path / "b0-method-receipt.json"
    b0.write_text(json.dumps(method_receipt()), encoding="utf-8")
    import hashlib
    cfg = protocol()
    cfg["water_B0_receipt_sha256"] = hashlib.sha256(b0.read_bytes()).hexdigest()
    config_file.write_text(json.dumps(cfg), encoding="utf-8")
    with pytest.raises(ValueError, match="canonical schema"):
        build_receipt(csv_path, config_file, b0, tmp_path / "unused.json")



def test_b0_context_mismatch_and_bad_receipt_cannot_qualify_design():
    method = method_receipt()
    method["context"]["population_id"] = "WRONG_POP"
    with pytest.raises(ValueError, match="contexts do not match"):
        assess_density_water_allocation(
            sample_rows(), protocol(),
            b0_method_receipt=method, b0_method_sha256="a"*64)
    method = method_receipt()
    method["status"] = "B0_METHOD_FEASIBILITY_HOLD"
    with pytest.raises(ValueError, match="B0 method PASS"):
        assess_density_water_allocation(
            sample_rows(), protocol(),
            b0_method_receipt=method, b0_method_sha256="a"*64)
    with pytest.raises(ValueError, match="source-hash|SHA256"):
        assess_density_water_allocation(
            sample_rows(), protocol(),
            b0_method_receipt=method_receipt(), b0_method_sha256="b"*64)
    method = method_receipt()
    method["context"]["protocol_version"] = "WRONG_METHOD_VERSION"
    with pytest.raises(ValueError, match="method context/version not registered"):
        assess_density_water_allocation(
            sample_rows(), protocol(),
            b0_method_receipt=method, b0_method_sha256="a"*64)

import csv
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_pedicularis_stage0_nuisance_receipt.py"
TARGETS = ROOT / "data" / "PEDICULARIS_POWER_TARGETS_TEMPLATE_V1.json"
CONTRACT = ROOT / "docs" / "PEDICULARIS_POWER_CALIBRATION_CONTRACT_V1.md"


def _module():
    spec = spec_from_file_location("ped_stage0_nuisance", SCRIPT)
    mod = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _write_pilot(path: Path, n_plants: int = 5, flowers_per_plant: int = 4):
    fields = [
        "plant_id",
        "flower_id",
        "assigned_z_level",
        "D_state",
        "G_state",
        "P_state",
        "undamaged_mature_viable_seed_count",
        "flower_retained_to_maturity",
        "missing_or_loss_reason",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for p in range(n_plants):
            for f in range(flowers_per_plant):
                writer.writerow(
                    {
                        "plant_id": f"P{p+1}",
                        "flower_id": f"P{p+1}_F{f+1}",
                        "assigned_z_level": f"Z{(f % 2) + 1}",
                        "D_state": str(f % 2),
                        "G_state": str((f // 2) % 2),
                        "P_state": str((p + f) % 2),
                        "undamaged_mature_viable_seed_count": str(10 + 2 * p + f),
                        "flower_retained_to_maturity": "1",
                        "missing_or_loss_reason": "",
                    }
                )


def test_stage0_nuisance_builder_returns_ready_receipt_with_cluster_dependence(tmp_path):
    pilot = tmp_path / "pilot.csv"
    _write_pilot(pilot)
    result = _module().build_receipt(pilot, min_complete=20, min_plants=5)
    assert result["status"] == "NUISANCE_RECEIPT_READY_FOR_POWER_INPUT"
    assert result["counts"]["rows"] == 20
    assert result["counts"]["unique_plants"] == 5
    assert result["counts"]["complete_seed_outcomes"] == 20
    assert result["counts"]["retention_fraction"] == pytest.approx(1.0)
    assert result["seed_count_nuisance"]["mean"] > 0
    assert result["seed_count_nuisance"]["variance"] > 0
    assert result["plant_dependence"]["status"] == "ESTIMABLE"
    assert result["plant_dependence"]["icc_one_way"] is not None
    assert "not_evidence_for_SCH_conflict" in result["claim_ceiling"]
    assert "must not be used" in result["anti_circularity_rule"]


def test_stage0_nuisance_builder_fails_closed_when_pilot_is_too_small(tmp_path):
    pilot = tmp_path / "pilot.csv"
    _write_pilot(pilot, n_plants=2, flowers_per_plant=2)
    result = _module().build_receipt(pilot, min_complete=20, min_plants=5)
    assert result["status"] == "NUISANCE_RECEIPT_INCOMPLETE"
    assert any("complete_outcomes_below_minimum" in x for x in result["gate_reasons"])
    assert any("plants_below_minimum" in x for x in result["gate_reasons"])


def test_stage0_nuisance_builder_rejects_missing_required_columns(tmp_path):
    pilot = tmp_path / "bad.csv"
    pilot.write_text("plant_id,flower_id\nP1,F1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        _module().build_receipt(pilot)


def test_power_target_template_is_fail_closed_and_separates_targets_from_pilot():
    data = json.loads(TARGETS.read_text(encoding="utf-8"))
    assert data["status"] == "DO_NOT_RUN_POWER_UNTIL_ALL_REQUIRED_TARGETS_ARE_FROZEN"
    assert data["nuisance_parameter_source"] == "PEDICULARIS_STAGE0_NUISANCE_RECEIPT_V1.json"
    assert "Stage-0 observed treatment effects must not be used" in data["target_source_rule"]
    assert data["SCH"]["min_state_optimum_separation_z_units"] == "REQUIRED_BEFORE_USE"
    assert data["BALANCE"]["architecture_qualification_must_pass_before_powering"] is True
    assert data["BITA"]["four_way_equivalence_margin_seed_units_per_flower"] == "REQUIRED_BEFORE_USE"


def test_power_contract_keeps_sample_size_unfrozen_until_nuisance_and_targets_are_frozen():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "pilot treatment effects" in text
    assert "minimum meaningful effects" in text
    assert "FINAL_SAMPLE_SIZE = NOT FROZEN" in text
    assert "A sample size that detects a P or G main effect but cannot resolve optimum geometry is not an SCH-powered design" in text
    assert "no amount of sample size rescues the estimand" in text
    assert "A design powered only for `Delta_AD W > 0` is not automatically powered" in text

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_pedicularis_power_config.py"
TARGET_TEMPLATE = ROOT / "data" / "PEDICULARIS_POWER_TARGETS_TEMPLATE_V1.json"


def _module():
    spec = spec_from_file_location("ped_power_gate", SCRIPT)
    mod = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _ready_nuisance():
    return {
        "status": "NUISANCE_RECEIPT_READY_FOR_POWER_INPUT",
        "claim_ceiling": "stage0_nuisance_parameters_only_not_evidence",
        "counts": {"unique_plants": 12, "complete_seed_outcomes": 48},
        "seed_count_nuisance": {"mean": 12.0, "variance": 30.0, "zero_fraction": 0.05},
        "plant_dependence": {"status": "ESTIMABLE", "icc_one_way": 0.2},
    }


def _fully_frozen_targets():
    targets = json.loads(TARGET_TEMPLATE.read_text(encoding="utf-8"))
    replacements = {
        "SCH": {
            "min_state_optimum_separation_z_units": 0.5,
            "min_optimum_shift_z_units": 0.25,
            "min_abs_component_gradient_seed_units_per_z": 1.0,
            "minimum_combined_surface_curvature_seed_units_per_z2": 0.5,
            "minimum_interior_distance_from_tested_boundary_z_units": 0.25,
        },
        "BALANCE": {"min_abs_Delta_W_seed_units_per_flower": 2.0},
        "BITA": {
            "min_abs_Delta_AD_W_seed_units_per_flower": 2.0,
            "min_positive_A1_seed_units_per_flower": 1.0,
            "four_way_equivalence_margin_seed_units_per_flower": 1.0,
            "m0_equivalence_margin_seed_units_per_flower_if_zero_baseline_claimed": 0.5,
        },
        "design": {
            "candidate_plants": 40,
            "candidate_flowers_per_plant": 8,
            "allocation_rule": "frozen_test_allocation",
            "attrition_inflation_rule": "inflate_by_registered_retention_fraction",
        },
    }
    for section, values in replacements.items():
        targets[section].update(values)
    return targets


def test_template_fails_closed_before_targets_are_frozen():
    mod = _module()
    targets = json.loads(TARGET_TEMPLATE.read_text(encoding="utf-8"))
    result = mod.prepare(_ready_nuisance(), targets)
    assert result["status"] == "POWER_CONFIG_NOT_READY"
    assert any(err.startswith("unfrozen_target:") for err in result["errors"])
    assert "simulation_contract" not in result


def test_incomplete_nuisance_receipt_blocks_power_even_with_frozen_targets():
    mod = _module()
    nuisance = _ready_nuisance()
    nuisance["status"] = "NUISANCE_RECEIPT_INCOMPLETE"
    result = mod.prepare(nuisance, _fully_frozen_targets())
    assert result["status"] == "POWER_CONFIG_NOT_READY"
    assert any(err.startswith("nuisance_status_not_ready") for err in result["errors"])


def test_power_config_becomes_ready_only_after_nuisance_and_targets_are_frozen():
    mod = _module()
    result = mod.prepare(_ready_nuisance(), _fully_frozen_targets())
    assert result["status"] == "POWER_CONFIG_READY_FOR_SIMULATION"
    assert result["errors"] == []
    assert result["simulation_contract"]["ecological_design_cells"] == 40
    assert result["simulation_contract"]["remaining_channel_assay_cells"] == 4
    assert "not_a_power_result" in result["claim_ceiling"]
    assert "independently of Stage-0" in result["anti_circularity_rule"]

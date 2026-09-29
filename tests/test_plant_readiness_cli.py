from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "report_plant_v4_readiness.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("report_plant_v4_readiness", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_canonical_v4_readiness_report_matches_current_frozen_state():
    module = _load_module()
    out = module.build_report()

    readiness = out["programme_readiness"]
    assert out["analysis"] == "balance_plant_v4_readiness_snapshot"
    assert readiness["model_specification"] == "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4"
    assert readiness["all_machine_preparation_complete"] is True
    assert readiness["primary_model_assembly_ready"] is False
    assert readiness["v4_estimability_ready_to_evaluate"] is False
    assert readiness["preoutcome_design_status"] == {
        "v4_main_predictor_design_viable": True,
        "v4_common_slope_design_full_rank": True,
        "v4_universe_stratified_design_full_rank": True,
        "temporal_marginal_replication_ready": True,
        "temporal_common_support_ready": False,
        "temporal_common_support_module_strata": [],
    }

    gate = out["standalone_reactivation_gate"]
    assert gate["standalone_reactivation_eligible"] is False
    assert gate["activation_action"] == "KEEP_DORMANT"
    assert "temporal_common_support_module_stratum_ready" in gate["blockers"]

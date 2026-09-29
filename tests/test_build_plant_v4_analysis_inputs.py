import importlib
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
cli = importlib.import_module("build_plant_v4_analysis_inputs")


def test_v4_analysis_cli_reports_current_readiness_without_building():
    out = cli.current_readiness()
    assert out["model_specification"] == "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4"
    assert out["all_machine_preparation_complete"] is True
    assert out["primary_model_assembly_ready"] is False
    assert out["v4_estimability_ready_to_evaluate"] is False
    assert set(out["open_gate_names"]) == {
        "u2_independent_double_coding",
        "u2_post_coding_adjudication",
        "u6_independent_double_coding",
        "u6_post_coding_adjudication",
        "u2_predictor_independent_adjudication",
        "u6_predictor_independent_adjudication",
    }


def test_v4_analysis_cli_build_fails_closed_while_human_gates_are_open(tmp_path):
    with pytest.raises(RuntimeError, match="V4 primary assembly is not ready"):
        cli.build_outputs(tmp_path)
    assert not any(tmp_path.iterdir())

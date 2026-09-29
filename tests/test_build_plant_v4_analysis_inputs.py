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



def test_v4_analysis_cli_external_workspace_overrides_only_mutable_human_files(tmp_path):
    defaults = cli._paths()
    workspace = tmp_path / "handoff"
    workspace.mkdir()

    u2_override = workspace / defaults["u2_worksheet"].name
    u2_override.write_text(defaults["u2_worksheet"].read_text(encoding="utf-8"), encoding="utf-8")
    frozen_fake = workspace / defaults["u6_freeze"].name
    frozen_fake.write_text("{}", encoding="utf-8")

    paths = cli._paths(workspace)
    assert paths["u2_worksheet"] == u2_override
    assert paths["u6_freeze"] == defaults["u6_freeze"]
    assert paths["u2_sources"] == defaults["u2_sources"]
    assert paths["u6_sources"] == defaults["u6_sources"]


def test_v4_analysis_cli_malformed_mutable_override_fails_closed(tmp_path):
    workspace = tmp_path / "handoff"
    workspace.mkdir()
    bad = workspace / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv"
    bad.write_text(
        "cluster_id,coder_id,conflict_status\n"
        "bad,CODER_A,POSITIVE\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="neither valid blank nor fully completed"):
        cli.current_readiness(input_dir=workspace)

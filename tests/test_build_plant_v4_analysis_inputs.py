import csv
import importlib
import json
import sys
from pathlib import Path

import pytest

from balance_domain.plant_macro_agreement import FIELDS


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
cli = importlib.import_module("build_plant_v4_analysis_inputs")
merge_cli = importlib.import_module("merge_plant_coder_returns")

U2_SAMPLE = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"
HANDOFF_MANIFEST = ROOT / "data" / "BALANCE_PLANT_CODER_HANDOFF_MANIFEST_V1.json"


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



def _u2_groups():
    with U2_SAMPLE.open(encoding="utf-8", newline="") as handle:
        return [row["dependency_group"] for row in csv.DictReader(handle)]


def _write_u2_return(path, coder_id):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for i, group in enumerate(_u2_groups()):
            writer.writerow({
                "cluster_id": group,
                "coder_id": coder_id,
                "conflict_status": (
                    "POSITIVE" if i < 8 else "NO_DEMONSTRATED_CONFLICT"
                ),
                "architecture_mode": (
                    "SHARED_INTEGRATED" if i % 2 == 0 else "TEMPORAL_SEPARATION"
                ),
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "notes": "",
            })


def test_coder_return_workspace_connects_to_v4_readiness(tmp_path):
    a = tmp_path / "coder_a.csv"
    b = tmp_path / "coder_b.csv"
    workspace = tmp_path / "workspace"
    _write_u2_return(a, "CODER_A")
    _write_u2_return(b, "CODER_B")

    out = merge_cli.merge_lane(
        lane="U2",
        coder_a=a,
        coder_b=b,
        out_dir=workspace,
    )
    merged = Path(out["merged"])
    assert cli._paths(workspace)["u2_worksheet"] == merged

    readiness = cli.current_readiness(input_dir=workspace)
    assert readiness["primary_human_open_gates"]["u2_independent_double_coding"] is False
    assert readiness["primary_human_open_gates"]["u2_post_coding_adjudication"] is True
    assert readiness["primary_model_assembly_ready"] is False


def test_handoff_manifest_post_handoff_paths_exist_in_production_layer():
    data = json.loads(HANDOFF_MANIFEST.read_text(encoding="utf-8"))
    analysis = data["post_handoff_analysis"]
    assert analysis["readiness_cli"] == "scripts/build_plant_v4_analysis_inputs.py"
    assert analysis["manual_workflow"] == ".github/workflows/build-plant-v4-analysis-inputs.yml"
    assert (ROOT / analysis["readiness_cli"]).exists()
    assert (ROOT / analysis["manual_workflow"]).exists()

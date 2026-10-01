import csv
import hashlib
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



def _write_minimal_composed_workspace(path):
    path.mkdir()
    files = {}
    for basename in cli.PRIMARY_HUMAN_BASENAMES:
        target = path / basename
        target.write_text(f"synthetic::{basename}\n", encoding="utf-8")
        files[basename] = {
            "composed_sha256": hashlib.sha256(target.read_bytes()).hexdigest()
        }
    receipt = {
        "schema_version": "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_V1",
        "analysis": "balance_plant_v4_human_input_workspace",
        "primary_model_assembly_ready": True,
        "primary_human_open_gates": {
            "u2_independent_double_coding": False,
            "u2_post_coding_adjudication": False,
            "u6_independent_double_coding": False,
            "u6_post_coding_adjudication": False,
            "u2_predictor_independent_adjudication": False,
            "u6_predictor_independent_adjudication": False,
        },
        "next_step": "BUILD_V4_ANALYSIS_INPUTS",
        "files": files,
    }
    receipt_path = path / cli.HUMAN_WORKSPACE_RECEIPT
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt_path


def test_analysis_builder_requires_receipt_bound_composed_workspace(tmp_path):
    workspace = tmp_path / "composed"
    receipt_path = _write_minimal_composed_workspace(workspace)

    path, receipt = cli._validated_human_workspace_receipt(workspace)
    assert path == receipt_path
    assert receipt["primary_model_assembly_ready"] is True


def test_analysis_builder_rejects_composed_workspace_hash_drift(tmp_path):
    workspace = tmp_path / "composed"
    _write_minimal_composed_workspace(workspace)
    target = workspace / cli.PRIMARY_HUMAN_BASENAMES[0]
    target.write_bytes(target.read_bytes() + b"tamper")

    with pytest.raises(ValueError, match="human workspace SHA256 mismatch"):
        cli._validated_human_workspace_receipt(workspace)


def test_analysis_builder_rejects_unreceipted_workspace(tmp_path):
    workspace = tmp_path / "composed"
    workspace.mkdir()
    with pytest.raises(ValueError, match="human workspace receipt is missing"):
        cli._validated_human_workspace_receipt(workspace)



def test_analysis_builder_writes_atomic_receipt_bound_output_workspace(tmp_path, monkeypatch):
    workspace = tmp_path / "composed"
    human_receipt_path = _write_minimal_composed_workspace(workspace)
    out_dir = tmp_path / "analysis_inputs"

    monkeypatch.setattr(
        cli,
        "current_readiness",
        lambda input_dir=None: {
            "primary_model_assembly_ready": True,
            "open_gate_names": [],
        },
    )
    monkeypatch.setattr(cli, "load_double_coding", lambda path: [])
    monkeypatch.setattr(cli, "load_u2_double_code_sample", lambda path: [])
    monkeypatch.setattr(cli, "load_u2_adjudication", lambda *args, **kwargs: [])
    monkeypatch.setattr(cli, "load_plant_predictor_receipts", lambda path: [])
    monkeypatch.setattr(cli, "load_u2_source_packet", lambda path: [])
    monkeypatch.setattr(cli, "load_u6_pass2_double_coding", lambda *args, **kwargs: [])
    monkeypatch.setattr(cli, "load_u6_pass2_adjudication", lambda *args, **kwargs: [])
    monkeypatch.setattr(cli, "load_u6_cross_universe_dependence", lambda *args, **kwargs: [])
    monkeypatch.setattr(cli, "load_u6_frozen_source_packet", lambda *args, **kwargs: [])

    assembly = [{
        field: (
            "row-1" if field == "analysis_row_id"
            else "synthetic"
        )
        for field in cli.ASSEMBLY_FIELDS
    }]
    monkeypatch.setattr(
        cli,
        "build_v4_licensed_assembly",
        lambda **kwargs: assembly,
    )
    pipeline = {
        "assembly_readout": {"ready_for_primary_fit": True},
        "main_stan_input": {"stan_data": {"N": 1}, "metadata": {"kind": "main"}},
        "prior_sensitivity_stan_input": {
            "stan_data": {"N": 1},
            "metadata": {"kind": "prior"},
        },
        "temporal_generality_stan_input": None,
        "temporal_generality_prior_sensitivity_stan_input": None,
        "temporal_generality_status": "NOT_READY",
        "temporal_generality_blockers": ["shared_module_timing_common_support"],
    }
    monkeypatch.setattr(cli, "build_v4_analysis_inputs", lambda rows: pipeline)

    result = cli.build_outputs(out_dir, input_dir=workspace)
    assert Path(result["analysis_input_receipt"]).is_file()
    assert Path(result["source_human_workspace_receipt"]).read_bytes() == (
        human_receipt_path.read_bytes()
    )

    receipt = json.loads(
        Path(result["analysis_input_receipt"]).read_text(encoding="utf-8")
    )
    assert receipt["active_fit_jobs"] == [
        "PRIMARY",
        "PRIMARY_PRIOR_SENSITIVITY",
    ]
    assert receipt["temporal_generality_status"] == "NOT_READY"
    assert receipt["analysis_input_provenance_contract"] == (
        "data/BALANCE_PLANT_V4_ANALYSIS_INPUT_PROVENANCE_V1.json"
    )
    contract_path = ROOT / receipt["analysis_input_provenance_contract"]
    assert receipt["analysis_input_provenance_contract_sha256"] == hashlib.sha256(
        contract_path.read_bytes()
    ).hexdigest()
    assert receipt["source_human_workspace_receipt_sha256"] == hashlib.sha256(
        human_receipt_path.read_bytes()
    ).hexdigest()
    for key, basename in receipt["outputs"].items():
        path = out_dir / basename
        assert path.is_file()
        assert receipt["output_sha256"][key] == hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

    with pytest.raises(ValueError, match="output directory already exists"):
        cli.build_outputs(out_dir, input_dir=workspace)



def test_analysis_input_provenance_contract_is_frozen_and_matches_builder():
    contract = cli._load_analysis_input_provenance_contract()
    assert contract["source_workspace"]["required_primary_files"] == list(
        cli.PRIMARY_HUMAN_BASENAMES
    )
    assert contract["source_workspace"]["file_sha256_must_match_receipt"] is True
    assert contract["output_workspace"]["existing_output_directory_overwrite_allowed"] is False
    assert contract["output_workspace"]["write_mode"] == (
        "temporary_sibling_workspace_then_atomic_rename"
    )

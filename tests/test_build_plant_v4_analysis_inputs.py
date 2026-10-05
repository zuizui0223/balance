import csv
import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest

from balance_domain.plant_macro_agreement import FIELDS
from balance_domain.plant_v4_workspace import (
    U2_ADJUDICATION,
    U2_CODING,
    U2_PREDICTOR,
    U2_PREDICTOR_V2,
    U2_PREDICTOR_V2_FROZEN,
    U2_PREDICTOR_V2_FREEZE_RECEIPT,
    U6_ADJUDICATION,
    U6_CODING,
    U6_PREDICTOR,
)


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
    out_dir = tmp_path / "analysis"
    with pytest.raises(RuntimeError, match="V4 primary assembly is not ready"):
        cli.build_outputs(out_dir)
    assert not out_dir.exists()


def test_v4_analysis_cli_rejects_existing_output_workspace_before_gate_evaluation(tmp_path):
    out_dir = tmp_path / "analysis"
    out_dir.mkdir()
    sentinel = out_dir / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")

    with pytest.raises(ValueError, match="output directory already exists"):
        cli.build_outputs(out_dir)

    assert sentinel.read_text(encoding="utf-8") == "preserve"



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



def _write_dummy_composed_workspace(
    path,
    *,
    include_external=False,
    u2_version="V1",
):
    path.mkdir()
    if u2_version == "V1":
        basenames = set(cli.PRIMARY_MUTABLE_BASENAMES)
    elif u2_version == "V2":
        basenames = set(cli.PRIMARY_COMMON_BASENAMES) | set(
            cli.U2_V2_PROVENANCE_BASENAMES
        )
    else:
        raise ValueError(u2_version)
    if include_external:
        basenames |= cli.EXTERNAL_MUTABLE_BASENAMES

    files = {}
    for basename in sorted(basenames):
        target = path / basename
        target.write_text(f"{basename}\n", encoding="utf-8")
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        files[basename] = {
            "source": f"/immutable/source/{basename}",
            "source_sha256": digest,
            "composed_sha256": digest,
        }

    receipt = {
        "schema_version": "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_V1",
        "analysis": "balance_plant_v4_human_input_workspace",
        "external_validation_included": include_external,
        "u2_predictor_receipt_version": u2_version,
        "u2_predictor_reviewed_basename": (
            U2_PREDICTOR if u2_version == "V1" else U2_PREDICTOR_V2
        ),
        "u2_predictor_frozen_baseline_basename": (
            U2_PREDICTOR
            if u2_version == "V1"
            else U2_PREDICTOR_V2_FROZEN
        ),
        "u2_predictor_freeze_receipt_basename": (
            None if u2_version == "V1" else U2_PREDICTOR_V2_FREEZE_RECEIPT
        ),
        "files": files,
        "primary_human_open_gates": {
            "u2_independent_double_coding": False,
            "u2_post_coding_adjudication": False,
            "u6_independent_double_coding": False,
            "u6_post_coding_adjudication": False,
            "u2_predictor_independent_adjudication": False,
            "u6_predictor_independent_adjudication": False,
        },
        "primary_model_assembly_ready": True,
        "v4_estimability_ready_to_evaluate": True,
        "next_step": "BUILD_V4_ANALYSIS_INPUTS",
        "claim_ceiling": "validated_human_input_composition_only_no_model_effect",
    }
    receipt_path = path / cli.COMPOSED_WORKSPACE_RECEIPT
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt_path


def test_v4_production_build_requires_canonical_composed_workspace_receipt(tmp_path):
    workspace = tmp_path / "handoff"
    workspace.mkdir()

    with pytest.raises(ValueError, match="requires the canonical composed human-input"):
        cli.build_outputs(tmp_path / "analysis", input_dir=workspace)


def test_v4_composed_workspace_receipt_hash_binding_is_fail_closed(tmp_path):
    workspace = tmp_path / "handoff"
    receipt_path = _write_dummy_composed_workspace(workspace)

    validated = cli._validate_composed_input_workspace(workspace)
    assert validated["receipt_path"] == receipt_path
    assert validated["receipt_sha256"] == hashlib.sha256(
        receipt_path.read_bytes()
    ).hexdigest()

    target = workspace / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
    target.write_bytes(target.read_bytes() + b"\n")

    with pytest.raises(ValueError, match="composed workspace SHA256 mismatch"):
        cli._validate_composed_input_workspace(workspace)


def test_v4_composed_workspace_receipt_rejects_file_set_drift(tmp_path):
    workspace = tmp_path / "handoff"
    receipt_path = _write_dummy_composed_workspace(workspace)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["files"].pop("BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv")
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="file set disagrees"):
        cli._validate_composed_input_workspace(workspace)



def test_analysis_builder_copies_source_receipt_and_hash_binds_outputs(tmp_path, monkeypatch):
    workspace = tmp_path / "composed"
    human_receipt_path = _write_dummy_composed_workspace(workspace)
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
    monkeypatch.setattr(
        cli,
        "load_predictor_adjudication_return",
        lambda reviewed, frozen: [],
    )
    monkeypatch.setattr(cli, "load_u2_source_packet", lambda path: [])
    monkeypatch.setattr(cli, "load_u6_pass2_double_coding", lambda *args, **kwargs: [])
    monkeypatch.setattr(cli, "load_u6_pass2_adjudication", lambda *args, **kwargs: [])
    monkeypatch.setattr(cli, "load_u6_cross_universe_dependence", lambda *args, **kwargs: [])
    monkeypatch.setattr(cli, "load_u6_frozen_source_packet", lambda *args, **kwargs: [])

    assembly = [{
        field: ("row-1" if field == "analysis_row_id" else "synthetic")
        for field in cli.ASSEMBLY_FIELDS
    }]
    monkeypatch.setattr(cli, "build_v4_licensed_assembly", lambda **kwargs: assembly)
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
    copied = Path(result["source_human_workspace_receipt"])
    assert copied.name == cli.COMPOSED_WORKSPACE_RECEIPT
    assert copied.read_bytes() == human_receipt_path.read_bytes()

    receipt_path = Path(result["analysis_inputs_receipt"])
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["source_human_workspace_receipt"] == cli.COMPOSED_WORKSPACE_RECEIPT
    assert receipt["source_human_workspace_receipt_copied"] is True
    assert receipt["source_human_workspace_receipt_sha256"] == hashlib.sha256(
        copied.read_bytes()
    ).hexdigest()
    assert receipt["primary_fit_ready"] is True
    assert receipt["temporal_generality_status"] == "NOT_READY"

    for basename, expected_sha in receipt["files_sha256"].items():
        path = out_dir / basename
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha

    with pytest.raises(ValueError, match="output directory already exists"):
        cli.build_outputs(out_dir, input_dir=workspace)



def test_v4_analysis_builder_primary_basenames_match_compositor_contract():
    assert cli.PRIMARY_MUTABLE_BASENAMES == {
        U2_CODING,
        U2_ADJUDICATION,
        U2_PREDICTOR,
        U6_CODING,
        U6_ADJUDICATION,
        U6_PREDICTOR,
    }



def test_v4_composed_workspace_v2_selects_reviewed_and_frozen_v2_paths(tmp_path):
    workspace = tmp_path / "handoff_v2"
    _write_dummy_composed_workspace(workspace, u2_version="V2")

    validated = cli._validate_composed_input_workspace(workspace)
    assert validated["u2_predictor_receipt_version"] == "V2"
    assert validated["u2_predictor_reviewed_basename"] == U2_PREDICTOR_V2
    assert (
        validated["u2_predictor_frozen_baseline_basename"]
        == U2_PREDICTOR_V2_FROZEN
    )
    assert (
        validated["u2_predictor_freeze_receipt_basename"]
        == U2_PREDICTOR_V2_FREEZE_RECEIPT
    )

    paths = cli._paths(
        workspace,
        composed_receipt=validated["receipt"],
    )
    assert paths["u2_receipts"] == workspace / U2_PREDICTOR_V2
    assert paths["u2_receipts_frozen"] == workspace / U2_PREDICTOR_V2_FROZEN
    assert paths["u2_v2_freeze_receipt"] == (
        workspace / U2_PREDICTOR_V2_FREEZE_RECEIPT
    )


def test_v4_composed_workspace_rejects_v2_file_set_without_version_metadata(tmp_path):
    workspace = tmp_path / "handoff_v2_bad"
    receipt_path = _write_dummy_composed_workspace(workspace, u2_version="V2")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["u2_predictor_receipt_version"] = "V1"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="V1 U2 predictor basename drifted"):
        cli._validate_composed_input_workspace(workspace)


def test_analysis_builder_propagates_v2_predictor_provenance(tmp_path, monkeypatch):
    workspace = tmp_path / "composed_v2"
    human_receipt_path = _write_dummy_composed_workspace(
        workspace,
        u2_version="V2",
    )
    out_dir = tmp_path / "analysis_inputs_v2"

    monkeypatch.setattr(
        cli,
        "current_readiness",
        lambda input_dir=None: {
            "primary_model_assembly_ready": True,
            "open_gate_names": [],
        },
    )
    monkeypatch.setattr(
        cli,
        "load_predictor_adjudication_return",
        lambda reviewed, frozen: [],
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
        field: ("row-1" if field == "analysis_row_id" else "synthetic")
        for field in cli.ASSEMBLY_FIELDS
    }]
    monkeypatch.setattr(cli, "build_v4_licensed_assembly", lambda **kwargs: assembly)
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
    receipt = json.loads(
        Path(result["analysis_inputs_receipt"]).read_text(encoding="utf-8")
    )
    assert receipt["u2_predictor_receipt_version"] == "V2"
    assert receipt["u2_predictor_reviewed_basename"] == U2_PREDICTOR_V2
    assert receipt["u2_predictor_frozen_baseline_basename"] == (
        U2_PREDICTOR_V2_FROZEN
    )
    assert receipt["u2_predictor_freeze_receipt_basename"] == (
        U2_PREDICTOR_V2_FREEZE_RECEIPT
    )
    assert receipt["u2_predictor_reviewed_sha256"] == hashlib.sha256(
        (workspace / U2_PREDICTOR_V2).read_bytes()
    ).hexdigest()
    assert receipt["u2_predictor_frozen_baseline_sha256"] == hashlib.sha256(
        (workspace / U2_PREDICTOR_V2_FROZEN).read_bytes()
    ).hexdigest()
    assert Path(result["source_human_workspace_receipt"]).read_bytes() == (
        human_receipt_path.read_bytes()
    )

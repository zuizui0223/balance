import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "BALANCE_PLANT_CODER_HANDOFF_MANIFEST_V1.json"


def test_coder_handoff_manifest_points_only_to_existing_frozen_surfaces():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["status"] == "READY_FOR_HUMAN_INDEPENDENT_CODING"
    assert data["shared"]["frozen_coder_ids"] == ["CODER_A", "CODER_B"]
    assert data["shared"]["reliability_trigger_raw_agreement"] == 0.80
    assert data["shared"]["no_source_adjudication_before_reliability_pass"] is True

    assert data["lanes"]["U1"]["primary_model_denominator"] is False
    assert data["lanes"]["U2"]["primary_model_denominator"] is True
    assert data["lanes"]["U6"]["primary_model_denominator"] is True

    path_keys = {
        "U1": ["sample", "source_packet", "worksheet", "post_coding_adjudication", "predictor_receipts"],
        "U2": ["sample", "source_packet", "worksheet", "post_coding_adjudication", "predictor_receipts"],
        "U6": ["pass1_freeze", "source_packet", "worksheet", "post_coding_adjudication", "predictor_receipts"],
    }
    for lane, keys in path_keys.items():
        for key in keys:
            path = ROOT / data["lanes"][lane][key]
            assert path.exists(), f"missing {lane} {key}: {path}"


def test_coder_handoff_sequence_keeps_reliability_before_adjudication():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    seq = data["return_sequence"]
    reliability_index = next(i for i, step in enumerate(seq) if step.startswith("agreement report"))
    repair_index = next(i for i, step in enumerate(seq) if "raw agreement <0.80" in step)
    adjudication_index = next(i for i, step in enumerate(seq) if step.startswith("only after reliability pass"))
    predictor_index = next(i for i, step in enumerate(seq) if step.startswith("separately adjudicate predictor"))
    fit_index = next(i for i, step in enumerate(seq) if step.startswith("fit V4"))

    assert reliability_index < repair_index < adjudication_index < predictor_index < fit_index
    assert data["current_primary_model"] == "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4"
    assert data["current_publication_status"] == "DORMANT_PAPER_BRANCH"



def test_coder_handoff_manifest_registers_deterministic_packet_builder():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    packet = data["packet_builder"]
    assert packet["script"] == "scripts/build_plant_coder_packets.py"
    assert packet["deterministic_zip"] is True
    assert packet["evidence_identity_rule"].startswith(
        "coder A and coder B receive byte-identical"
    )
    assert set(packet["outputs"]) == {
        "BALANCE_PLANT_CODER_A_PACKET_V1.zip",
        "BALANCE_PLANT_CODER_A_PACKET_V1.json",
        "BALANCE_PLANT_CODER_B_PACKET_V1.zip",
        "BALANCE_PLANT_CODER_B_PACKET_V1.json",
    }
    assert packet["workflow"] == ".github/workflows/build-plant-coder-packets.yml"
    assert packet["runbook"] == "docs/BALANCE_PLANT_CODER_PACKET_RUNBOOK_V1.md"
    assert packet["trigger"] == "workflow_dispatch_only"
    assert (ROOT / packet["script"]).exists()
    assert (ROOT / packet["workflow"]).exists()
    assert (ROOT / packet["runbook"]).exists()



def test_handoff_manifest_separates_predictor_adjudication_from_architecture_coding():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    predictor = data["predictor_adjudication"]
    assert predictor["protocol"] == (
        "docs/BALANCE_PLANT_PREDICTOR_RECEIPT_ADJUDICATION_PROTOCOL_V1.md"
    )
    assert predictor["builder"] == "scripts/build_plant_predictor_adjudication_packet.py"
    assert predictor["workflow"] == (
        ".github/workflows/build-plant-predictor-adjudication-packet.yml"
    )
    assert predictor["architecture_outputs_included"] is False
    assert predictor["applicable_primary_universes"] == ["U2", "U6"]
    assert (ROOT / predictor["protocol"]).exists()
    assert (ROOT / predictor["builder"]).exists()
    assert (ROOT / predictor["workflow"]).exists()



def test_handoff_manifest_registers_post_handoff_v4_analysis_workflow():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    analysis = data["post_handoff_analysis"]
    assert analysis["readiness_cli"] == "scripts/build_plant_v4_analysis_inputs.py"
    assert analysis["manual_workflow"] == ".github/workflows/build-plant-v4-analysis-inputs.yml"
    assert analysis["build_command"].endswith("--build")
    assert "forbidden while any U2/U6" in analysis["fail_closed_rule"]
    assert (
        "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_INPUT.json when the stricter "
        "generality gate is ready"
    ) in analysis["outputs"]
    assert (
        "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_PRIOR_SENSITIVITY_INPUT.json "
        "when the stricter generality gate is ready"
    ) in analysis["outputs"]
    # The production analysis builder is a downstream integration surface.
    # This handoff unit freezes its path/contract without requiring that
    # downstream extraction to be present in the same PR.
    assert analysis["readiness_cli"].startswith("scripts/")
    assert analysis["manual_workflow"].startswith(".github/workflows/")



def test_handoff_manifest_registers_validated_return_ingestion_workspace():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ret = data["return_ingestion"]
    assert ret["merger_module"] == "balance_domain/plant_coder_return.py"
    assert ret["intake_contract"] == (
        "data/BALANCE_PLANT_HUMAN_RETURN_INTAKE_CONTRACT_V1.json"
    )
    assert ret["intake_cli"] == "scripts/audit_plant_human_returns.py"
    assert ret["intake_runbook"] == "docs/BALANCE_PLANT_HUMAN_RETURN_INTAKE_V1.md"
    assert ret["primary_architecture_return_file_count"] == 4
    assert ret["external_validation_return_file_count"] == 2
    assert ret["predictor_review_return_file_count"] == 2
    assert "U1 latency never blocks" in ret["stage_independence_rule"]
    assert ret["standard_entrypoint"].startswith(
        "python scripts/audit_plant_human_returns.py"
    )
    assert ret["cli"] == "scripts/merge_plant_coder_returns.py"
    assert ret["tracked_data_overwrite_required"] is False
    assert ret["downstream_analysis_cli"] == "scripts/build_plant_v4_analysis_inputs.py"
    assert ret["downstream_input_option"] == "--input-dir"
    assert "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv" in ret[
        "mutable_workspace_basenames"
    ]
    assert "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv" in ret[
        "mutable_workspace_basenames"
    ]
    assert any("source packets" in item for item in ret["immutable_repo_inputs"])
    assert "silently replaced" in ret["fail_closed_rule"]
    assert (ROOT / ret["merger_module"]).exists()
    assert (ROOT / ret["cli"]).exists()
    assert (ROOT / ret["intake_contract"]).exists()
    assert (ROOT / ret["intake_cli"]).exists()
    assert (ROOT / ret["intake_runbook"]).exists()



def test_handoff_manifest_registers_canonical_agreement_reporting():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    agreement = data["agreement_reporting"]
    assert agreement["module"] == "balance_domain/plant_agreement_report.py"
    assert agreement["cli"] == "scripts/report_plant_coder_agreement.py"
    assert agreement["threshold_raw_agreement"] == 0.80
    assert agreement["low_agreement_action"] == (
        "CODEBOOK_REPAIR_AND_INDEPENDENT_RECODE_SAME_FROZEN_GROUPS"
    )
    assert agreement["pass_action"] == "SOURCE_ADJUDICATION"
    assert agreement["exact_disagreement_list_required"] is True
    assert agreement["adjudication_allowed_only_if_all_fields_pass"] is True
    assert (ROOT / agreement["module"]).exists()
    assert (ROOT / agreement["cli"]).exists()



def test_handoff_manifest_registers_architecture_adjudication_entrypoints():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    adjudication = data["architecture_adjudication"]
    assert adjudication["contract"] == (
        "data/BALANCE_PLANT_ARCHITECTURE_ADJUDICATION_HANDOFF_V1.json"
    )
    assert adjudication["protocol"] == (
        "docs/BALANCE_PLANT_ARCHITECTURE_ADJUDICATION_PROTOCOL_V1.md"
    )
    assert adjudication["module"] == (
        "balance_domain.plant_architecture_adjudication"
    )
    assert adjudication["packet_cli"] == (
        "scripts/build_plant_architecture_adjudication_packet.py"
    )
    assert adjudication["return_cli"] == (
        "scripts/validate_plant_architecture_adjudication.py"
    )
    assert adjudication["primary_scope"]["lanes"] == ["U2", "U6"]
    assert adjudication["primary_scope"]["blocks_primary_v4"] is True
    assert adjudication["external_scope"]["lanes"] == ["U1"]
    assert adjudication["external_scope"]["blocks_primary_v4"] is False
    for key in ("contract", "protocol", "module", "packet_cli", "return_cli"):
        assert (ROOT / adjudication[key]).exists()

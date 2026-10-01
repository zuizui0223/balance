import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "BALANCE_PLANT_V4_EXECUTION_SEQUENCE_V1.json"
HANDOFF = ROOT / "data" / "BALANCE_PLANT_CODER_HANDOFF_MANIFEST_V1.json"


def test_v4_execution_sequence_is_frozen_and_ordered():
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert data["status"] == "FROZEN_PRE_OUTCOME_END_TO_END_OPERATIONAL_SEQUENCE"
    ids = [stage["id"] for stage in data["stages"]]
    assert ids == [
        "S1_HUMAN_RETURN_INTAKE",
        "S2_PRIMARY_ARCHITECTURE_ADJUDICATION_PACKET",
        "S3_PRIMARY_ARCHITECTURE_ADJUDICATION_RETURN",
        "S4_OPTIONAL_U1_EXTERNAL_ADJUDICATION",
        "S5_COMPOSE_V4_HUMAN_INPUT_WORKSPACE",
        "S6_BUILD_V4_ANALYSIS_INPUT_BUNDLE",
        "S7_RUN_FROZEN_CMDSTAN",
        "S8_POSTFIT_AND_REACTIVATION_REVIEW",
    ]
    assert data["stages"][6]["required_cmdstan_version"] == "2.40.0"
    assert data["stages"][7]["cli"] == "scripts/evaluate_plant_v4_reactivation.py"
    assert data["stages"][7]["publication_status_change_automatic"] is False
    assert data["stages"][7]["evidence_bridge"] == (
        "balance_domain.plant_reactivation.evaluate_v4_reactivation_evidence"
    )
    assert data["stage_independence"]["predictor_review_may_finish_before_architecture_returns"] is True
    assert data["stage_independence"]["U1_external_may_finish_later_than_primary"] is True


def test_v4_execution_sequence_references_existing_cli_and_contract_surfaces():
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    expected_paths = {
        "scripts/audit_plant_human_returns.py",
        "scripts/build_plant_architecture_adjudication_packet.py",
        "scripts/validate_plant_architecture_adjudication.py",
        "scripts/compose_plant_v4_human_workspace.py",
        "scripts/build_plant_v4_analysis_inputs.py",
        "scripts/run_plant_v4_cmdstan.py",
        "scripts/evaluate_plant_v4_reactivation.py",
        "data/BALANCE_PLANT_HUMAN_RETURN_INTAKE_CONTRACT_V1.json",
        "data/BALANCE_PLANT_V4_ANALYSIS_INPUT_BUNDLE_CONTRACT_V1.json",
        "data/BALANCE_PLANT_V4_FIT_EXECUTION_CONTRACT_V1.json",
        "data/BALANCE_PLANT_V4_ESTIMAND_STANDARDIZATION_V1.json",
        "data/BALANCE_PLANT_V4_POSTERIOR_DECISION_RULES_V1.json",
        "data/BALANCE_PLANT_V4_REACTIVATION_GATE_V1.json",
        "docs/BALANCE_PLANT_V4_EXECUTION_SEQUENCE_V1.md",
    }
    for rel in sorted(expected_paths):
        assert (ROOT / rel).exists(), rel

    for stage in data["stages"]:
        cli = stage.get("cli")
        if cli:
            assert (ROOT / cli).exists(), cli


def test_handoff_manifest_registers_single_end_to_end_sequence():
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    seq = handoff["end_to_end_execution"]
    assert seq["contract"] == "data/BALANCE_PLANT_V4_EXECUTION_SEQUENCE_V1.json"
    assert seq["runbook"] == "docs/BALANCE_PLANT_V4_EXECUTION_SEQUENCE_V1.md"
    assert seq["starting_state"] == "PACKETS_GENERATED_AWAITING_INDEPENDENT_HUMAN_RETURNS"
    assert seq["automatic_publication_reactivation"] is False

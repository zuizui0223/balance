import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from balance_domain.plant_reactivation import (
    derive_v4_reactivation_conditions,
    evaluate_v4_reactivation_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_plant_v4_reactivation.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("evaluate_plant_v4_reactivation", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _human_receipt():
    return {
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
    }


def _assembly_readout():
    return {
        "analysis": "balance_plant_confirmatory_model_assembly_v4",
        "ready_for_primary_fit": True,
        "v4_estimability": {
            "temporal_cross_universe_common_support_ready": True,
            "temporal_cross_universe_outcome_support_ready": True,
            "temporal_cross_universe_generality_ready": True,
        },
    }


def _fit_receipt(*, generality=True):
    jobs = ["PRIMARY", "PRIMARY_PRIOR_SENSITIVITY"]
    if generality:
        jobs += [
            "TEMPORAL_GENERALITY",
            "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY",
        ]
    return {
        "schema_version": "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1",
        "execution_status": "COMPLETE",
        "postfit_decision_allowed": True,
        "diagnostic_failures": [],
        "active_jobs": jobs,
        "temporal_generality_expected_from_assembly": generality,
    }


def _generality_summary(
    *,
    u2="SUPPORTED",
    u6="SUPPORTED",
    interaction="NO_PRACTICALLY_LARGE_CONTRADICTION",
):
    supported = (
        u2 == "SUPPORTED"
        and u6 == "SUPPORTED"
        and interaction == "NO_PRACTICALLY_LARGE_CONTRADICTION"
    )
    return {
        "analysis": "balance_plant_v4_temporal_generality_postfit_summary",
        "decision": {
            "u2_directional_label": u2,
            "u6_directional_label": u6,
            "interaction_label": interaction,
            "cross_universe_generality_supported": supported,
        },
    }


def test_reactivation_bridge_can_be_evidence_eligible_without_auto_activation():
    out = evaluate_v4_reactivation_evidence(
        human_workspace_receipt=_human_receipt(),
        assembly_readout=_assembly_readout(),
        fit_execution_receipt=_fit_receipt(),
        temporal_generality_postfit_summary=_generality_summary(),
    )
    assert out["derived_conditions"] == {
        "u2_independent_coding_and_adjudication_complete": True,
        "u6_independent_coding_and_adjudication_complete": True,
        "u2_u6_predictor_independence_adjudication_complete": True,
        "v4_primary_estimability_pass": True,
        "v4_primary_fit_complete": True,
        "temporal_generality_sensitivity_fit_complete": True,
        "temporal_common_support_module_stratum_ready": True,
        "temporal_generality_outcome_support_ready": True,
        "u2_ordered_vs_simultaneous_direction_resolved": True,
        "u6_ordered_vs_simultaneous_direction_resolved": True,
        "directionally_concordant_across_u2_u6": True,
        "contradictory_universe_interaction_exceeds_practical_margin": False,
    }
    assert out["gate"]["standalone_reactivation_eligible"] is True
    assert out["gate"]["activation_action"] == (
        "HUMAN_REVIEW_REQUIRED_BEFORE_PUBLICATION_STATUS_CHANGE"
    )
    assert out["publication_status_changed"] is False


def test_reactivation_bridge_does_not_treat_concordant_negative_direction_as_eligible():
    out = evaluate_v4_reactivation_evidence(
        human_workspace_receipt=_human_receipt(),
        assembly_readout=_assembly_readout(),
        fit_execution_receipt=_fit_receipt(),
        temporal_generality_postfit_summary=_generality_summary(
            u2="CONTRADICTED",
            u6="CONTRADICTED",
        ),
    )
    conditions = out["derived_conditions"]
    assert conditions["u2_ordered_vs_simultaneous_direction_resolved"] is False
    assert conditions["u6_ordered_vs_simultaneous_direction_resolved"] is False
    assert conditions["directionally_concordant_across_u2_u6"] is False
    assert out["gate"]["standalone_reactivation_eligible"] is False


def test_reactivation_bridge_without_generality_fit_stays_dormant():
    out = evaluate_v4_reactivation_evidence(
        human_workspace_receipt=_human_receipt(),
        assembly_readout=_assembly_readout(),
        fit_execution_receipt=_fit_receipt(generality=False),
        temporal_generality_postfit_summary=None,
    )
    conditions = out["derived_conditions"]
    assert conditions["v4_primary_fit_complete"] is True
    assert conditions["temporal_generality_sensitivity_fit_complete"] is False
    assert conditions["u2_ordered_vs_simultaneous_direction_resolved"] is False
    assert conditions[
        "contradictory_universe_interaction_exceeds_practical_margin"
    ] is None
    assert out["gate"]["standalone_reactivation_eligible"] is False


def test_reactivation_bridge_rejects_internally_inconsistent_generality_decision():
    summary = _generality_summary()
    summary["decision"]["cross_universe_generality_supported"] = False
    with pytest.raises(ValueError, match="internally inconsistent"):
        derive_v4_reactivation_conditions(
            human_workspace_receipt=_human_receipt(),
            assembly_readout=_assembly_readout(),
            fit_execution_receipt=_fit_receipt(),
            temporal_generality_postfit_summary=summary,
        )


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_evidence_workspaces(tmp_path):
    input_dir = tmp_path / "inputs"
    fit_dir = tmp_path / "fit"
    input_dir.mkdir()
    fit_dir.mkdir()

    human_path = input_dir / "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_RECEIPT_V1.json"
    _write_json(human_path, _human_receipt())

    assembly_path = input_dir / "BALANCE_PLANT_V4_LICENSED_ASSEMBLY.csv"
    assembly_path.write_text("analysis_row_id\nsynthetic\n", encoding="utf-8")

    readout_path = input_dir / "BALANCE_PLANT_V4_ASSEMBLY_READOUT.json"
    _write_json(readout_path, _assembly_readout())

    analysis_path = input_dir / "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json"
    analysis = {
        "schema_version": "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1",
        "primary_fit_ready": True,
        "source_human_workspace_receipt_sha256": _sha(human_path),
        "files_sha256": {
            "BALANCE_PLANT_V4_ASSEMBLY_READOUT.json": _sha(readout_path),
        },
    }
    _write_json(analysis_path, analysis)

    primary_path = fit_dir / "BALANCE_PLANT_V4_PRIMARY_POSTFIT_SUMMARY.json"
    _write_json(primary_path, {"analysis": "synthetic-primary"})

    generality_path = (
        fit_dir / "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_POSTFIT_SUMMARY.json"
    )
    _write_json(generality_path, _generality_summary())

    fit_path = fit_dir / "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1.json"
    fit = {
        **_fit_receipt(),
        "analysis_input_receipt_sha256": _sha(analysis_path),
        "source_human_workspace_receipt_sha256": _sha(human_path),
        "licensed_assembly_sha256": _sha(assembly_path),
        "postfit_outputs": {
            "primary": str(primary_path),
            "temporal_generality": str(generality_path),
        },
        "postfit_output_sha256": {
            "primary": _sha(primary_path),
            "temporal_generality": _sha(generality_path),
        },
    }
    _write_json(fit_path, fit)
    return input_dir, fit_dir


def test_receipt_bound_reactivation_cli_reconstructs_eligibility(tmp_path):
    module = _load_script()
    input_dir, fit_dir = _build_evidence_workspaces(tmp_path)
    out = module.evaluate_from_workspaces(input_dir=input_dir, fit_dir=fit_dir)
    assert out["gate"]["standalone_reactivation_eligible"] is True
    assert out["publication_status_changed"] is False
    assert len(out["evidence_provenance"]["fit_execution_receipt_sha256"]) == 64


def test_receipt_bound_reactivation_cli_rejects_upstream_hash_drift(tmp_path):
    module = _load_script()
    input_dir, fit_dir = _build_evidence_workspaces(tmp_path)
    human = input_dir / "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_RECEIPT_V1.json"
    human.write_bytes(human.read_bytes() + b"\n")

    with pytest.raises(ValueError, match="human-workspace receipt SHA256 mismatch"):
        module.evaluate_from_workspaces(input_dir=input_dir, fit_dir=fit_dir)



def test_reactivation_bridge_rejects_generality_job_assembly_mismatch():
    assembly = _assembly_readout()
    fit = _fit_receipt(generality=False)
    fit["temporal_generality_expected_from_assembly"] = True
    with pytest.raises(ValueError, match="generality expectation disagrees"):
        derive_v4_reactivation_conditions(
            human_workspace_receipt=_human_receipt(),
            assembly_readout=assembly,
            fit_execution_receipt=fit,
            temporal_generality_postfit_summary=None,
        )


def test_receipt_bound_reactivation_cli_rejects_noncanonical_postfit_name(tmp_path):
    module = _load_script()
    input_dir, fit_dir = _build_evidence_workspaces(tmp_path)
    fit_path = fit_dir / "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1.json"
    fit = json.loads(fit_path.read_text(encoding="utf-8"))
    fit["postfit_outputs"]["primary"] = str(fit_dir / "other-primary.json")
    _write_json(fit_path, fit)

    with pytest.raises(ValueError, match="primary postfit output basename drifted"):
        module.evaluate_from_workspaces(input_dir=input_dir, fit_dir=fit_dir)

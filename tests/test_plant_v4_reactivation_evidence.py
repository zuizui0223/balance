import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from balance_domain.plant_reactivation import (
    derive_v4_reactivation_conditions,
    evaluate_v4_reactivation_evidence,
)
from balance_domain.plant_v4_decision import temporal_generality_decision


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


def _assembly_readout(*, generality=True):
    return {
        "analysis": "balance_plant_confirmatory_model_assembly_v4",
        "ready_for_primary_fit": True,
        "v4_estimability": {
            "temporal_cross_universe_common_support_ready": generality,
            "temporal_cross_universe_outcome_support_ready": generality,
            "temporal_cross_universe_generality_ready": generality,
            "temporal_common_support_module_strata": (
                ["SINGLE"] if generality else []
            ),
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
    p_positive = {
        "SUPPORTED": 0.99,
        "CONTRADICTED": 0.01,
        "INCONCLUSIVE": 0.50,
    }
    u2_p = p_positive[u2]
    u6_p = p_positive[u6]
    gamma_tail = (
        0.99 if interaction == "PRACTICALLY_CONTRADICTORY" else 0.01
    )
    decision = temporal_generality_decision(
        preoutcome_common_support_ready=True,
        per_universe_outcome_support_ready=True,
        u2_p_positive_primary=u2_p,
        u2_p_positive_sensitivity=u2_p,
        u6_p_positive_primary=u6_p,
        u6_p_positive_sensitivity=u6_p,
        p_gamma_below_negative_margin_primary=gamma_tail,
        p_gamma_below_negative_margin_sensitivity=gamma_tail,
    )
    assert decision["u2_directional_label"] == u2
    assert decision["u6_directional_label"] == u6
    assert decision["interaction_label"] == interaction
    return {
        "analysis": "balance_plant_v4_temporal_generality_postfit_summary",
        "standardization_module_strata": ["SINGLE"],
        "universe_contrasts": {
            "U2_BARRETT_2002": {
                "primary_prior": {
                    "p_positive": u2_p,
                    "p_negative": 1.0 - u2_p,
                },
                "sensitivity_prior": {
                    "p_positive": u2_p,
                    "p_negative": 1.0 - u2_p,
                },
            },
            "U6_POLLEN_THEFT_HARGREAVES_2009": {
                "primary_prior": {
                    "p_positive": u6_p,
                    "p_negative": 1.0 - u6_p,
                },
                "sensitivity_prior": {
                    "p_positive": u6_p,
                    "p_negative": 1.0 - u6_p,
                },
            },
        },
        "interaction_negative_margin_probability": {
            "primary_prior": gamma_tail,
            "sensitivity_prior": gamma_tail,
            "margin_log_odds": -1.0,
        },
        "decision": decision,
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
        assembly_readout=_assembly_readout(generality=False),
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
    with pytest.raises(ValueError, match="does not match posterior probabilities"):
        derive_v4_reactivation_conditions(
            human_workspace_receipt=_human_receipt(),
            assembly_readout=_assembly_readout(),
            fit_execution_receipt=_fit_receipt(),
            temporal_generality_postfit_summary=summary,
        )


def test_reactivation_bridge_rejects_label_probability_mismatch():
    summary = _generality_summary()
    summary["universe_contrasts"]["U2_BARRETT_2002"]["primary_prior"][
        "p_positive"
    ] = 0.60
    summary["universe_contrasts"]["U2_BARRETT_2002"]["primary_prior"][
        "p_negative"
    ] = 0.40

    with pytest.raises(ValueError, match="does not match posterior probabilities"):
        derive_v4_reactivation_conditions(
            human_workspace_receipt=_human_receipt(),
            assembly_readout=_assembly_readout(),
            fit_execution_receipt=_fit_receipt(),
            temporal_generality_postfit_summary=summary,
        )


def test_reactivation_bridge_rejects_interaction_tail_label_mismatch():
    summary = _generality_summary()
    summary["interaction_negative_margin_probability"]["primary_prior"] = 0.99

    with pytest.raises(ValueError, match="does not match posterior probabilities"):
        derive_v4_reactivation_conditions(
            human_workspace_receipt=_human_receipt(),
            assembly_readout=_assembly_readout(),
            fit_execution_receipt=_fit_receipt(),
            temporal_generality_postfit_summary=summary,
        )


def test_reactivation_bridge_rejects_standardization_strata_drift():
    summary = _generality_summary()
    summary["standardization_module_strata"] = ["MODULAR"]

    with pytest.raises(ValueError, match="standardization strata disagree"):
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


def _chain_execution_metadata(chain_id):
    return {
        "method": "sample",
        "algorithm": "hmc",
        "engine": "nuts",
        "num_chains": 1,
        "chain_id": chain_id,
        "seed": 20260930,
        "num_samples": 2000,
        "num_warmup": 1000,
        "save_warmup": False,
        "thin": 1,
        "adapt_delta": 0.99,
        "max_depth": 15,
        "metric": "diag_e",
        "output_sig_figs": 18,
        "refresh": 100,
    }


def _write_fit_job_evidence(fit_dir, fit):
    fit["input_wrapper_sha256"] = {}
    fit["job_receipts"] = {}
    fit["job_receipt_sha256"] = {}

    for index, job_id in enumerate(fit["active_jobs"], start=1):
        job_dir = fit_dir / job_id
        job_dir.mkdir()

        wrapper_sha = f"{index:x}" * 64
        fit["input_wrapper_sha256"][job_id] = wrapper_sha

        stan_data = job_dir / "stan_data.json"
        stan_data.write_text(
            json.dumps({"job": job_id}, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        chain_hashes = {}
        for chain_id in range(1, 5):
            chain = job_dir / f"chain_{chain_id}.csv"
            chain.write_text(
                f"synthetic {job_id} chain {chain_id}\n",
                encoding="utf-8",
            )
            chain_hashes[chain.name] = _sha(chain)

        summary = job_dir / "stansummary.csv"
        summary.write_text(f"synthetic {job_id} summary\n", encoding="utf-8")

        receipt = {
            "schema_version": "BALANCE_PLANT_V4_FIT_JOB_RECEIPT_V1",
            "job_id": job_id,
            "cmdstan_version": "2.40.0",
            "n_chains": 4,
            "draws_per_chain": [2000, 2000, 2000, 2000],
            "n_draws_total": 8000,
            "chain_ids": [1, 2, 3, 4],
            "chain_execution_metadata": [
                _chain_execution_metadata(chain_id)
                for chain_id in range(1, 5)
            ],
            "input_wrapper_sha256": wrapper_sha,
            "materialized_stan_data_sha256": _sha(stan_data),
            "chain_csv_sha256": chain_hashes,
            "stansummary_sha256": _sha(summary),
            "diagnostics": {
                "status": "PASS",
                "checks": {
                    "divergences": True,
                    "treedepth": True,
                    "ebfmi": True,
                    "rhat": True,
                    "ess_bulk": True,
                    "ess_tail": True,
                },
                "automatic_retuning_permitted": False,
            },
        }
        receipt_path = job_dir / "FIT_RECEIPT.json"
        _write_json(receipt_path, receipt)
        fit["job_receipts"][job_id] = str(receipt_path)
        fit["job_receipt_sha256"][job_id] = _sha(receipt_path)


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
    _write_fit_job_evidence(fit_dir, fit)
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



def test_receipt_bound_reactivation_cli_rejects_fit_job_chain_hash_drift(tmp_path):
    module = _load_script()
    input_dir, fit_dir = _build_evidence_workspaces(tmp_path)
    chain = fit_dir / "PRIMARY" / "chain_1.csv"
    chain.write_bytes(chain.read_bytes() + b"drift\n")

    with pytest.raises(ValueError, match="PRIMARY chain_1.csv SHA256 mismatch"):
        module.evaluate_from_workspaces(input_dir=input_dir, fit_dir=fit_dir)


def test_receipt_bound_reactivation_cli_rejects_fit_job_stansummary_hash_drift(
    tmp_path,
):
    module = _load_script()
    input_dir, fit_dir = _build_evidence_workspaces(tmp_path)
    summary = fit_dir / "PRIMARY" / "stansummary.csv"
    summary.write_bytes(summary.read_bytes() + b"drift\n")

    with pytest.raises(ValueError, match="PRIMARY stansummary SHA256 mismatch"):
        module.evaluate_from_workspaces(input_dir=input_dir, fit_dir=fit_dir)


def test_receipt_bound_reactivation_cli_rejects_master_job_diagnostic_drift(
    tmp_path,
):
    module = _load_script()
    input_dir, fit_dir = _build_evidence_workspaces(tmp_path)
    fit_path = fit_dir / "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1.json"
    fit = json.loads(fit_path.read_text(encoding="utf-8"))
    fit["diagnostic_failures"] = ["PRIMARY"]
    fit["postfit_decision_allowed"] = False
    _write_json(fit_path, fit)

    with pytest.raises(ValueError, match="diagnostic failures disagree"):
        module.evaluate_from_workspaces(input_dir=input_dir, fit_dir=fit_dir)


def test_receipt_bound_reactivation_cli_rejects_fit_job_chain_metadata_drift(
    tmp_path,
):
    module = _load_script()
    input_dir, fit_dir = _build_evidence_workspaces(tmp_path)

    job_receipt_path = fit_dir / "PRIMARY" / "FIT_RECEIPT.json"
    job = json.loads(job_receipt_path.read_text(encoding="utf-8"))
    job["chain_execution_metadata"][0]["seed"] = 999
    _write_json(job_receipt_path, job)

    master_path = fit_dir / "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1.json"
    master = json.loads(master_path.read_text(encoding="utf-8"))
    master["job_receipt_sha256"]["PRIMARY"] = _sha(job_receipt_path)
    _write_json(master_path, master)

    with pytest.raises(ValueError, match="chain execution metadata drifted"):
        module.evaluate_from_workspaces(input_dir=input_dir, fit_dir=fit_dir)


def test_reactivation_bridge_rejects_generality_job_assembly_mismatch():
    assembly = _assembly_readout()
    fit = _fit_receipt(generality=False)
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

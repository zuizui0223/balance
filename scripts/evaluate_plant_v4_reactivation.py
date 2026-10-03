#!/usr/bin/env python3
"""Evaluate BALANCE V4 reactivation evidence from immutable fit/input workspaces."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_reactivation import (  # noqa: E402
    evaluate_v4_reactivation_evidence,
)
from balance_domain.plant_v4_cmdstan import load_fit_execution_contract  # noqa: E402


FIT_RECEIPT = "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1.json"
ANALYSIS_RECEIPT = "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json"
HUMAN_RECEIPT = "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_RECEIPT_V1.json"
ASSEMBLY = "BALANCE_PLANT_V4_LICENSED_ASSEMBLY.csv"
ASSEMBLY_READOUT = "BALANCE_PLANT_V4_ASSEMBLY_READOUT.json"
PRIMARY_POSTFIT = "BALANCE_PLANT_V4_PRIMARY_POSTFIT_SUMMARY.json"
GENERALITY_POSTFIT = "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_POSTFIT_SUMMARY.json"
FIT_CONTRACT = ROOT / "data" / "BALANCE_PLANT_V4_FIT_EXECUTION_CONTRACT_V1.json"
FIT_JOB_RECEIPT = "FIT_RECEIPT.json"
FIT_JOB_IDS = {
    "PRIMARY",
    "PRIMARY_PRIOR_SENSITIVITY",
    "TEMPORAL_GENERALITY",
    "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"required V4 evidence file is missing: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"V4 evidence file must be a JSON object: {path}")
    return data


def _require_hash(*, label: str, path: Path, expected: object) -> str:
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError(f"{label} expected SHA256 is missing or invalid")
    observed = _sha256(path)
    if observed != expected:
        raise ValueError(f"{label} SHA256 mismatch: {observed} != {expected}")
    return observed


def _validate_fit_job_evidence(*, fit_dir: Path, fit_receipt: dict) -> dict:
    contract = load_fit_execution_contract(FIT_CONTRACT)
    required_version = contract["required_cmdstan_version"]
    sampling = contract["sampling"]

    active_jobs = fit_receipt.get("active_jobs")
    if not isinstance(active_jobs, list) or not active_jobs:
        raise ValueError("V4 fit execution receipt lacks active jobs")
    if len(active_jobs) != len(set(active_jobs)):
        raise ValueError("V4 fit execution receipt repeats active jobs")
    unknown = sorted(set(active_jobs) - FIT_JOB_IDS)
    if unknown:
        raise ValueError("V4 fit execution receipt has unknown jobs: " + ", ".join(unknown))

    job_paths = fit_receipt.get("job_receipts")
    job_hashes = fit_receipt.get("job_receipt_sha256")
    wrapper_hashes = fit_receipt.get("input_wrapper_sha256")
    if not isinstance(job_paths, dict) or set(job_paths) != set(active_jobs):
        raise ValueError("V4 fit execution receipt job receipt map disagrees with active jobs")
    if not isinstance(job_hashes, dict) or set(job_hashes) != set(active_jobs):
        raise ValueError("V4 fit execution receipt job receipt hashes disagree with active jobs")
    if not isinstance(wrapper_hashes, dict) or set(wrapper_hashes) != set(active_jobs):
        raise ValueError("V4 fit execution receipt wrapper hashes disagree with active jobs")

    expected_chain_names = {
        f"chain_{chain_id}.csv"
        for chain_id in range(1, int(sampling["chains"]) + 1)
    }
    failures = []
    verified = {}
    for job_id in active_jobs:
        declared_path = Path(str(job_paths[job_id]))
        if declared_path.name != FIT_JOB_RECEIPT or declared_path.parent.name != job_id:
            raise ValueError(f"V4 fit job receipt path drifted for {job_id}")

        job_dir = fit_dir / job_id
        receipt_path = job_dir / FIT_JOB_RECEIPT
        receipt_sha = _require_hash(
            label=f"{job_id} fit-job receipt",
            path=receipt_path,
            expected=job_hashes[job_id],
        )
        receipt = _load_json(receipt_path)
        if receipt.get("schema_version") != "BALANCE_PLANT_V4_FIT_JOB_RECEIPT_V1":
            raise ValueError(f"{job_id} fit-job receipt schema mismatch")
        if receipt.get("job_id") != job_id:
            raise ValueError(f"{job_id} fit-job receipt job ID mismatch")
        if receipt.get("cmdstan_version") != required_version:
            raise ValueError(f"{job_id} fit-job CmdStan version mismatch")
        if receipt.get("n_chains") != int(sampling["chains"]):
            raise ValueError(f"{job_id} fit-job chain count mismatch")
        if receipt.get("draws_per_chain") != [
            int(sampling["num_samples"]) // int(sampling["thin"])
        ] * int(sampling["chains"]):
            raise ValueError(f"{job_id} fit-job draw count mismatch")
        if receipt.get("n_draws_total") != (
            int(sampling["chains"])
            * (int(sampling["num_samples"]) // int(sampling["thin"]))
        ):
            raise ValueError(f"{job_id} fit-job total draw count mismatch")
        expected_chain_ids = list(range(1, int(sampling["chains"]) + 1))
        if receipt.get("chain_ids") != expected_chain_ids:
            raise ValueError(f"{job_id} fit-job chain IDs mismatch")

        metadata = receipt.get("chain_execution_metadata")
        if not isinstance(metadata, list) or len(metadata) != int(sampling["chains"]):
            raise ValueError(f"{job_id} fit-job chain execution metadata is incomplete")
        for chain_id, item in zip(expected_chain_ids, metadata):
            if not isinstance(item, dict):
                raise ValueError(f"{job_id} fit-job chain metadata must be objects")
            expected = {
                "method": "sample",
                "algorithm": "hmc",
                "engine": "nuts",
                "num_chains": 1,
                "chain_id": chain_id,
                "seed": sampling["seed"],
                "num_samples": sampling["num_samples"],
                "num_warmup": sampling["num_warmup"],
                "save_warmup": sampling["save_warmup"],
                "thin": sampling["thin"],
                "adapt_delta": sampling["adapt_delta"],
                "max_depth": sampling["max_depth"],
                "metric": sampling["metric"],
                "output_sig_figs": sampling["output_sig_figs"],
                "refresh": sampling["refresh"],
            }
            if item != expected:
                raise ValueError(
                    f"{job_id} fit-job chain execution metadata drifted for "
                    f"chain {chain_id}"
                )

        if receipt.get("input_wrapper_sha256") != wrapper_hashes[job_id]:
            raise ValueError(f"{job_id} fit-job wrapper SHA256 disagrees with master receipt")

        stan_data_path = job_dir / "stan_data.json"
        stan_data_sha = _require_hash(
            label=f"{job_id} materialized Stan data",
            path=stan_data_path,
            expected=receipt.get("materialized_stan_data_sha256"),
        )

        chain_hashes = receipt.get("chain_csv_sha256")
        if not isinstance(chain_hashes, dict) or set(chain_hashes) != expected_chain_names:
            raise ValueError(f"{job_id} fit-job chain hash set mismatch")
        observed_chain_hashes = {}
        for name in sorted(expected_chain_names):
            path = job_dir / name
            observed_chain_hashes[name] = _require_hash(
                label=f"{job_id} {name}",
                path=path,
                expected=chain_hashes[name],
            )

        stansummary_path = job_dir / "stansummary.csv"
        stansummary_sha = _require_hash(
            label=f"{job_id} stansummary",
            path=stansummary_path,
            expected=receipt.get("stansummary_sha256"),
        )

        diagnostics = receipt.get("diagnostics")
        if not isinstance(diagnostics, dict) or diagnostics.get("status") not in {"PASS", "FAIL"}:
            raise ValueError(f"{job_id} fit-job diagnostics status is invalid")
        if diagnostics["status"] == "FAIL":
            failures.append(job_id)

        verified[job_id] = {
            "fit_job_receipt_sha256": receipt_sha,
            "materialized_stan_data_sha256": stan_data_sha,
            "chain_csv_sha256": observed_chain_hashes,
            "stansummary_sha256": stansummary_sha,
            "chain_ids": expected_chain_ids,
            "diagnostic_status": diagnostics["status"],
        }

    declared_failures = fit_receipt.get("diagnostic_failures")
    if declared_failures != failures:
        raise ValueError(
            "V4 master fit receipt diagnostic failures disagree with job receipts"
        )
    if fit_receipt.get("postfit_decision_allowed") is not (not failures):
        raise ValueError(
            "V4 master fit receipt postfit decision flag disagrees with job diagnostics"
        )

    return {
        "fit_execution_contract_sha256": _sha256(FIT_CONTRACT),
        "jobs": verified,
    }


def evaluate_from_workspaces(*, input_dir: Path, fit_dir: Path) -> dict:
    """Verify the immutable evidence chain and evaluate reactivation eligibility."""
    fit_receipt_path = fit_dir / FIT_RECEIPT
    fit_receipt = _load_json(fit_receipt_path)
    if (
        fit_receipt.get("schema_version")
        != "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1"
    ):
        raise ValueError("V4 fit execution receipt schema mismatch")

    fit_job_evidence = _validate_fit_job_evidence(
        fit_dir=fit_dir,
        fit_receipt=fit_receipt,
    )

    analysis_receipt_path = input_dir / ANALYSIS_RECEIPT
    analysis_receipt = _load_json(analysis_receipt_path)
    if (
        analysis_receipt.get("schema_version")
        != "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1"
    ):
        raise ValueError("V4 analysis-input receipt schema mismatch")
    if analysis_receipt.get("primary_fit_ready") is not True:
        raise ValueError("V4 analysis-input receipt is not primary-fit ready")
    _require_hash(
        label="analysis-input receipt",
        path=analysis_receipt_path,
        expected=fit_receipt.get("analysis_input_receipt_sha256"),
    )

    human_receipt_path = input_dir / HUMAN_RECEIPT
    human_receipt = _load_json(human_receipt_path)
    _require_hash(
        label="human-workspace receipt",
        path=human_receipt_path,
        expected=fit_receipt.get("source_human_workspace_receipt_sha256"),
    )
    if (
        analysis_receipt.get("source_human_workspace_receipt_sha256")
        != fit_receipt.get("source_human_workspace_receipt_sha256")
    ):
        raise ValueError(
            "fit and analysis receipts disagree on source human-workspace receipt SHA256"
        )

    assembly_path = input_dir / ASSEMBLY
    _require_hash(
        label="licensed assembly",
        path=assembly_path,
        expected=fit_receipt.get("licensed_assembly_sha256"),
    )

    receipt_hashes = analysis_receipt.get("files_sha256")
    if not isinstance(receipt_hashes, dict):
        raise ValueError("V4 analysis-input receipt lacks files_sha256")
    assembly_readout_path = input_dir / ASSEMBLY_READOUT
    _require_hash(
        label="assembly readout",
        path=assembly_readout_path,
        expected=receipt_hashes.get(ASSEMBLY_READOUT),
    )
    assembly_readout = _load_json(assembly_readout_path)

    postfit_outputs = fit_receipt.get("postfit_outputs")
    postfit_hashes = fit_receipt.get("postfit_output_sha256")
    if not isinstance(postfit_outputs, dict) or not isinstance(postfit_hashes, dict):
        raise ValueError("V4 fit execution receipt lacks postfit output maps")

    primary_path = fit_dir / PRIMARY_POSTFIT
    if "primary" in postfit_outputs:
        if Path(str(postfit_outputs["primary"])).name != PRIMARY_POSTFIT:
            raise ValueError("V4 primary postfit output basename drifted")
        _require_hash(
            label="primary postfit summary",
            path=primary_path,
            expected=postfit_hashes.get("primary"),
        )
    elif fit_receipt.get("execution_status") == "COMPLETE":
        raise ValueError("complete V4 fit receipt lacks primary postfit summary")

    generality = None
    if "temporal_generality" in postfit_outputs:
        if (
            Path(str(postfit_outputs["temporal_generality"])).name
            != GENERALITY_POSTFIT
        ):
            raise ValueError("V4 temporal-generality postfit output basename drifted")
        generality_path = fit_dir / GENERALITY_POSTFIT
        _require_hash(
            label="temporal-generality postfit summary",
            path=generality_path,
            expected=postfit_hashes.get("temporal_generality"),
        )
        generality = _load_json(generality_path)
    elif "TEMPORAL_GENERALITY" in set(fit_receipt.get("active_jobs") or ()):
        raise ValueError(
            "V4 fit receipt activated temporal generality but lacks postfit summary"
        )

    evidence = evaluate_v4_reactivation_evidence(
        human_workspace_receipt=human_receipt,
        assembly_readout=assembly_readout,
        fit_execution_receipt=fit_receipt,
        temporal_generality_postfit_summary=generality,
    )
    return {
        **evidence,
        "evidence_provenance": {
            "fit_execution_receipt_sha256": _sha256(fit_receipt_path),
            "fit_job_evidence": fit_job_evidence,
            "analysis_input_receipt_sha256": _sha256(analysis_receipt_path),
            "human_workspace_receipt_sha256": _sha256(human_receipt_path),
            "licensed_assembly_sha256": _sha256(assembly_path),
            "assembly_readout_sha256": _sha256(assembly_readout_path),
            "primary_postfit_summary_sha256": (
                _sha256(primary_path) if primary_path.is_file() else None
            ),
            "temporal_generality_postfit_summary_sha256": (
                _sha256(fit_dir / GENERALITY_POSTFIT)
                if (fit_dir / GENERALITY_POSTFIT).is_file()
                else None
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--fit-dir", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate_from_workspaces(
        input_dir=args.input_dir.resolve(),
        fit_dir=args.fit_dir.resolve(),
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

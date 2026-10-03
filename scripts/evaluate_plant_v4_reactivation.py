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

from balance_domain.plant_analysis_pipeline import build_v4_analysis_inputs  # noqa: E402
from balance_domain.plant_model_assembly import load_model_assembly  # noqa: E402
from balance_domain.plant_reactivation import (  # noqa: E402
    evaluate_v4_reactivation_evidence,
)
from balance_domain.plant_v4_cmdstan import (  # noqa: E402
    combine_cmdstan_chains,
    evaluate_diagnostics,
    load_fit_execution_contract,
    read_stansummary_csv,
)
from balance_domain.plant_v4_estimands import (  # noqa: E402
    summarize_v4_primary_postfit,
    summarize_v4_temporal_generality_postfit,
)


FIT_RECEIPT = "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1.json"
ANALYSIS_RECEIPT = "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json"
HUMAN_RECEIPT = "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_RECEIPT_V1.json"
ASSEMBLY = "BALANCE_PLANT_V4_LICENSED_ASSEMBLY.csv"
ASSEMBLY_READOUT = "BALANCE_PLANT_V4_ASSEMBLY_READOUT.json"
PRIMARY_POSTFIT = "BALANCE_PLANT_V4_PRIMARY_POSTFIT_SUMMARY.json"
GENERALITY_POSTFIT = "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_POSTFIT_SUMMARY.json"
FIT_CONTRACT = ROOT / "data" / "BALANCE_PLANT_V4_FIT_EXECUTION_CONTRACT_V1.json"
FIT_JOB_RECEIPT = "FIT_RECEIPT.json"
FIT_BUILD_DIR = "_cmdstan_build"


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



def _job_specs(contract: dict) -> dict[str, dict]:
    model_by_role = {
        "PRIMARY": contract["primary_model"],
        "TEMPORAL_GENERALITY": contract["temporal_generality_model"],
    }
    out = {}
    for item in contract["fit_jobs"]:
        role = item["model"]
        if role not in model_by_role:
            raise ValueError(f"V4 fit contract has unknown model role {role!r}")
        out[item["id"]] = {
            "input": item["input"],
            "model_source": model_by_role[role],
            "require_gamma": role == "TEMPORAL_GENERALITY",
            "parameter_families": (
                ("alpha", "beta", "gamma_u6_ordered")
                if role == "TEMPORAL_GENERALITY"
                else ("alpha", "beta")
            ),
        }
    return out


def _compiled_executable(fit_dir: Path, model_source: str) -> Path:
    stem = Path(model_source).stem
    build_dir = fit_dir / FIT_BUILD_DIR
    candidates = [build_dir / stem, build_dir / f"{stem}.exe"]
    existing = [path for path in candidates if path.is_file()]
    if len(existing) != 1:
        raise ValueError(
            f"V4 compiled model executable is missing or ambiguous for {model_source}"
        )
    return existing[0]


def _verify_fit_evidence_chain(
    *,
    input_dir: Path,
    fit_dir: Path,
    fit_receipt: dict,
    analysis_receipt: dict,
) -> dict:
    """Rebuild the fit evidence chain from immutable files, not receipt assertions."""
    contract = load_fit_execution_contract(FIT_CONTRACT)
    _require_hash(
        label="current V4 fit execution contract",
        path=FIT_CONTRACT,
        expected=fit_receipt.get("contract_sha256"),
    )
    if fit_receipt.get("required_cmdstan_version") != contract["required_cmdstan_version"]:
        raise ValueError("V4 fit receipt required CmdStan version drifted")
    if fit_receipt.get("preflight_cmdstan_version") != contract["required_cmdstan_version"]:
        raise ValueError("V4 fit receipt preflight CmdStan version drifted")
    if fit_receipt.get("automatic_retuning_permitted") is not False:
        raise ValueError("V4 fit receipt must forbid automatic retuning")

    specs = _job_specs(contract)
    active_jobs = fit_receipt.get("active_jobs")
    if not isinstance(active_jobs, list) or not active_jobs:
        raise ValueError("V4 fit receipt lacks active jobs")
    if len(active_jobs) != len(set(active_jobs)):
        raise ValueError("V4 fit receipt repeats an active job")
    if not set(active_jobs) <= set(specs):
        raise ValueError("V4 fit receipt contains an unregistered active job")
    for job_id in specs:
        job_dir = fit_dir / job_id
        if job_dir.exists() != (job_id in active_jobs):
            raise ValueError(
                f"V4 fit workspace contains stale or missing job directory {job_id}"
            )

    receipt_paths = fit_receipt.get("job_receipts")
    receipt_hashes = fit_receipt.get("job_receipt_sha256")
    wrapper_hashes = fit_receipt.get("input_wrapper_sha256")
    if not all(isinstance(value, dict) for value in (
        receipt_paths,
        receipt_hashes,
        wrapper_hashes,
    )):
        raise ValueError("V4 fit receipt lacks job/input integrity maps")
    expected_jobs = set(active_jobs)
    if (
        set(receipt_paths) != expected_jobs
        or set(receipt_hashes) != expected_jobs
        or set(wrapper_hashes) != expected_jobs
    ):
        raise ValueError("V4 fit receipt job/input integrity maps drifted")

    analysis_hashes = analysis_receipt.get("files_sha256")
    if not isinstance(analysis_hashes, dict):
        raise ValueError("V4 analysis-input receipt lacks files_sha256")

    assembly = load_model_assembly(input_dir / ASSEMBLY)
    deterministic = build_v4_analysis_inputs(assembly)
    assembly_readout = _load_json(input_dir / ASSEMBLY_READOUT)
    if assembly_readout != deterministic["assembly_readout"]:
        raise ValueError(
            "V4 assembly readout does not match deterministic rebuild from assembly"
        )
    expected_wrappers = {
        "PRIMARY": deterministic["main_stan_input"],
        "PRIMARY_PRIOR_SENSITIVITY": deterministic[
            "prior_sensitivity_stan_input"
        ],
    }
    if deterministic["temporal_generality_stan_input"] is not None:
        expected_wrappers["TEMPORAL_GENERALITY"] = deterministic[
            "temporal_generality_stan_input"
        ]
        expected_wrappers["TEMPORAL_GENERALITY_PRIOR_SENSITIVITY"] = deterministic[
            "temporal_generality_prior_sensitivity_stan_input"
        ]
    if set(active_jobs) != set(expected_wrappers):
        raise ValueError(
            "V4 fit active jobs do not match deterministic assembly rebuild"
        )

    sampling = contract["sampling"]
    expected_draws_per_chain = (
        int(sampling["num_samples"]) // int(sampling["thin"])
    )
    draws: dict[str, list[dict]] = {}
    diagnostics: dict[str, dict] = {}

    for job_id in active_jobs:
        spec = specs[job_id]
        recorded_job_path = Path(str(receipt_paths[job_id]))
        if (
            recorded_job_path.name != FIT_JOB_RECEIPT
            or recorded_job_path.parent.name != job_id
        ):
            raise ValueError(f"V4 {job_id} job receipt path drifted")
        job_dir = fit_dir / job_id
        job_receipt_path = job_dir / FIT_JOB_RECEIPT
        _require_hash(
            label=f"{job_id} job receipt",
            path=job_receipt_path,
            expected=receipt_hashes[job_id],
        )
        job = _load_json(job_receipt_path)
        if job.get("schema_version") != "BALANCE_PLANT_V4_FIT_JOB_RECEIPT_V1":
            raise ValueError(f"V4 {job_id} job receipt schema mismatch")
        if job.get("job_id") != job_id:
            raise ValueError(f"V4 {job_id} job receipt ID mismatch")

        model_source = spec["model_source"]
        if job.get("model_source") != model_source:
            raise ValueError(f"V4 {job_id} model source path drifted")
        model_path = ROOT / model_source
        _require_hash(
            label=f"{job_id} model source",
            path=model_path,
            expected=job.get("model_source_sha256"),
        )
        copied_model = fit_dir / FIT_BUILD_DIR / Path(model_source).name
        if _sha256(copied_model) != _sha256(model_path):
            raise ValueError(f"V4 {job_id} compiled-source copy differs from model source")
        executable = _compiled_executable(fit_dir, model_source)
        _require_hash(
            label=f"{job_id} compiled model",
            path=executable,
            expected=job.get("model_executable_sha256"),
        )

        wrapper_name = spec["input"]
        if Path(str(job.get("input_wrapper", ""))).name != wrapper_name:
            raise ValueError(f"V4 {job_id} input wrapper basename drifted")
        wrapper_path = input_dir / wrapper_name
        wrapper_sha = _require_hash(
            label=f"{job_id} input wrapper",
            path=wrapper_path,
            expected=job.get("input_wrapper_sha256"),
        )
        if wrapper_hashes[job_id] != wrapper_sha:
            raise ValueError(f"V4 {job_id} overall/job input wrapper SHA256 mismatch")
        if analysis_hashes.get(wrapper_name) != wrapper_sha:
            raise ValueError(f"V4 {job_id} input wrapper disagrees with analysis receipt")

        raw_data_path = job_dir / "stan_data.json"
        _require_hash(
            label=f"{job_id} materialized Stan data",
            path=raw_data_path,
            expected=job.get("materialized_stan_data_sha256"),
        )
        wrapper = _load_json(wrapper_path)
        if wrapper != expected_wrappers[job_id]:
            raise ValueError(
                f"V4 {job_id} input wrapper does not match deterministic assembly rebuild"
            )
        raw_data = _load_json(raw_data_path)
        if wrapper.get("stan_data") != raw_data:
            raise ValueError(
                f"V4 {job_id} materialized Stan data differs from input wrapper"
            )

        chain_paths = [
            job_dir / f"chain_{chain_id}.csv"
            for chain_id in range(1, int(sampling["chains"]) + 1)
        ]
        expected_chain_hashes = job.get("chain_csv_sha256")
        expected_chain_names = {path.name for path in chain_paths}
        if (
            not isinstance(expected_chain_hashes, dict)
            or set(expected_chain_hashes) != expected_chain_names
        ):
            raise ValueError(f"V4 {job_id} chain SHA256 map drifted")
        for path in chain_paths:
            _require_hash(
                label=f"{job_id} {path.name}",
                path=path,
                expected=expected_chain_hashes[path.name],
            )

        combined = combine_cmdstan_chains(
            chain_paths,
            require_gamma=spec["require_gamma"],
            max_depth=int(sampling["max_depth"]),
            expected_chains=int(sampling["chains"]),
            expected_draws_per_chain=expected_draws_per_chain,
            required_version=contract["required_cmdstan_version"],
            expected_sampling=sampling,
        )
        observed_key_by_receipt_key = {
            "cmdstan_version": "stan_version",
            "chain_ids": "chain_ids",
            "chain_execution_metadata": "execution_metadata",
            "n_chains": "n_chains",
            "draws_per_chain": "draws_per_chain",
            "n_draws_total": "n_draws_total",
        }
        for key, observed_key in observed_key_by_receipt_key.items():
            if job.get(key) != combined[observed_key]:
                raise ValueError(f"V4 {job_id} {key} disagrees with chain CSVs")

        summary_path = job_dir / "stansummary.csv"
        _require_hash(
            label=f"{job_id} stansummary",
            path=summary_path,
            expected=job.get("stansummary_sha256"),
        )
        stan_summary = read_stansummary_csv(
            summary_path,
            parameter_families=spec["parameter_families"],
        )
        recomputed_diagnostics = evaluate_diagnostics(
            combined,
            stan_summary,
            contract=contract,
        )
        if job.get("diagnostics") != recomputed_diagnostics:
            raise ValueError(f"V4 {job_id} diagnostics disagree with fit evidence")

        draws[job_id] = combined["draws"]
        diagnostics[job_id] = recomputed_diagnostics

    expected_failures = sorted(
        job_id
        for job_id, result in diagnostics.items()
        if result["status"] != "PASS"
    )
    if sorted(fit_receipt.get("diagnostic_failures") or []) != expected_failures:
        raise ValueError("V4 overall diagnostic-failure list disagrees with job evidence")
    if fit_receipt.get("postfit_decision_allowed") is not (not expected_failures):
        raise ValueError("V4 overall postfit decision flag disagrees with diagnostics")
    if fit_receipt.get("execution_status") == "COMPLETE" and expected_failures:
        raise ValueError("complete V4 fit receipt contains diagnostic failures")

    if not {"PRIMARY", "PRIMARY_PRIOR_SENSITIVITY"} <= set(draws):
        raise ValueError("V4 fit evidence lacks the registered primary fit pair")
    primary_summary = summarize_v4_primary_postfit(
        assembly,
        primary_draws=draws["PRIMARY"],
        sensitivity_draws=draws["PRIMARY_PRIOR_SENSITIVITY"],
    )

    generality_jobs = {
        "TEMPORAL_GENERALITY",
        "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY",
    }
    generality_summary = None
    if generality_jobs <= set(draws):
        generality_summary = summarize_v4_temporal_generality_postfit(
            assembly,
            primary_draws=draws["TEMPORAL_GENERALITY"],
            sensitivity_draws=draws[
                "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY"
            ],
        )
    elif set(draws) & generality_jobs:
        raise ValueError("V4 fit evidence contains an incomplete generality fit pair")

    return {
        "primary_summary": primary_summary,
        "temporal_generality_summary": generality_summary,
        "job_receipt_sha256": {
            job_id: _sha256(fit_dir / job_id / FIT_JOB_RECEIPT)
            for job_id in active_jobs
        },
        "chain_csv_sha256": {
            job_id: {
                f"chain_{chain_id}.csv": _sha256(
                    fit_dir / job_id / f"chain_{chain_id}.csv"
                )
                for chain_id in range(1, int(sampling["chains"]) + 1)
            }
            for job_id in active_jobs
        },
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
    active_jobs = set(fit_receipt.get("active_jobs") or ())
    expected_postfit = {"primary"}
    if {
        "TEMPORAL_GENERALITY",
        "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY",
    } <= active_jobs:
        expected_postfit.add("temporal_generality")
    if set(postfit_outputs) != expected_postfit or set(postfit_hashes) != expected_postfit:
        raise ValueError("V4 fit postfit output maps contain stale or missing entries")
    if (
        "temporal_generality" not in expected_postfit
        and (fit_dir / GENERALITY_POSTFIT).exists()
    ):
        raise ValueError("V4 fit workspace contains stale temporal-generality postfit output")

    primary_path = fit_dir / PRIMARY_POSTFIT
    primary = None
    if "primary" in postfit_outputs:
        if Path(str(postfit_outputs["primary"])).name != PRIMARY_POSTFIT:
            raise ValueError("V4 primary postfit output basename drifted")
        _require_hash(
            label="primary postfit summary",
            path=primary_path,
            expected=postfit_hashes.get("primary"),
        )
        primary = _load_json(primary_path)
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

    reverified = _verify_fit_evidence_chain(
        input_dir=input_dir,
        fit_dir=fit_dir,
        fit_receipt=fit_receipt,
        analysis_receipt=analysis_receipt,
    )
    if primary != reverified["primary_summary"]:
        raise ValueError(
            "V4 primary postfit summary does not match recomputation from chain CSVs"
        )
    if generality != reverified["temporal_generality_summary"]:
        raise ValueError(
            "V4 temporal-generality postfit summary does not match recomputation "
            "from chain CSVs"
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
            "reverified_job_receipt_sha256": reverified["job_receipt_sha256"],
            "reverified_chain_csv_sha256": reverified["chain_csv_sha256"],
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

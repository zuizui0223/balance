#!/usr/bin/env python3
"""Run the frozen BALANCE plant V4 CmdStan fit and post-fit summaries."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_analysis_pipeline import build_v4_analysis_inputs  # noqa: E402
from balance_domain.plant_model_assembly import load_model_assembly  # noqa: E402
from balance_domain.plant_v4_cmdstan import (  # noqa: E402
    cmdstan_sample_argv,
    combine_cmdstan_chains,
    evaluate_diagnostics,
    load_fit_execution_contract,
    materialize_stan_data,
    read_stansummary_csv,
    sha256_file,
)
from balance_domain.plant_v4_estimands import (  # noqa: E402
    summarize_v4_primary_postfit,
    summarize_v4_temporal_generality_postfit,
)


CONTRACT = ROOT / "data" / "BALANCE_PLANT_V4_FIT_EXECUTION_CONTRACT_V1.json"
DEFAULT_INPUT = ROOT / "release" / "generated" / "plant_v4_analysis_inputs"
DEFAULT_OUT = ROOT / "release" / "generated" / "plant_v4_fit"
ANALYSIS_INPUT_RECEIPT = "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json"
HUMAN_WORKSPACE_RECEIPT = "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_RECEIPT_V1.json"
PRIMARY_HUMAN_BASENAMES = (
    "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
    "BALANCE_PLANT_U2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
    "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv",
    "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
    "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
)

FIT_SPECS = {
    "PRIMARY": {
        "input": "BALANCE_PLANT_V4_STAN_INPUT.json",
        "model": ROOT / "comparative" / "models" / "BALANCE_PLANT_V4_MULTINOMIAL.stan",
        "require_gamma": False,
    },
    "PRIMARY_PRIOR_SENSITIVITY": {
        "input": "BALANCE_PLANT_V4_PRIOR_SENSITIVITY_INPUT.json",
        "model": ROOT / "comparative" / "models" / "BALANCE_PLANT_V4_MULTINOMIAL.stan",
        "require_gamma": False,
    },
    "TEMPORAL_GENERALITY": {
        "input": "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_INPUT.json",
        "model": ROOT / "comparative" / "models" / "BALANCE_PLANT_V4_TEMPORAL_GENERALITY.stan",
        "require_gamma": True,
    },
    "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY": {
        "input": "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_PRIOR_SENSITIVITY_INPUT.json",
        "model": ROOT / "comparative" / "models" / "BALANCE_PLANT_V4_TEMPORAL_GENERALITY.stan",
        "require_gamma": True,
    },
}


def _exe_suffix() -> str:
    return ".exe" if os.name == "nt" else ""


def _ensure_stanc(
    *,
    cmdstan_dir: Path,
    make_command: str,
    log_dir: Path,
) -> Path:
    """Install the release-matched stanc binary using CmdStan's own make target."""
    stanc = cmdstan_dir / "bin" / f"stanc{_exe_suffix()}"
    if stanc.exists():
        return stanc
    _run_checked(
        [make_command, f"bin/stanc{_exe_suffix()}"],
        cwd=cmdstan_dir,
        log_path=log_dir / "stanc.install.log",
    )
    if not stanc.exists():
        raise RuntimeError("CmdStan make bin/stanc did not create the compiler")
    return stanc


def _cmdstan_version(cmdstan_dir: Path) -> str:
    stanc = cmdstan_dir / "bin" / f"stanc{_exe_suffix()}"
    if not stanc.exists():
        raise FileNotFoundError(f"CmdStan stanc executable is missing: {stanc}")
    proc = subprocess.run(
        [str(stanc), "--version"],
        cwd=cmdstan_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("unable to read CmdStan/stanc version")
    match = re.search(r"(?<!\d)(\d+\.\d+\.\d+)(?!\d)", proc.stdout or "")
    if match is None:
        raise ValueError(f"could not parse CmdStan/stanc version: {proc.stdout!r}")
    return match.group(1)


def _run_checked(argv: list[str], *, cwd: Path, log_path: Path) -> None:
    proc = subprocess.run(
        argv,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(proc.stdout or "", encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed with exit code {proc.returncode}: {' '.join(argv)}; "
            f"see {log_path}"
        )


def _compile_model(
    *,
    cmdstan_dir: Path,
    stan_path: Path,
    build_dir: Path,
    make_command: str,
) -> Path:
    build_dir.mkdir(parents=True, exist_ok=True)
    copied_stan = build_dir / stan_path.name
    copied_stan.write_bytes(stan_path.read_bytes())
    target = copied_stan.with_suffix("")
    executable = Path(f"{target}{_exe_suffix()}")
    _run_checked(
        [make_command, str(target)],
        cwd=cmdstan_dir,
        log_path=build_dir / f"{stan_path.stem}.compile.log",
    )
    if not executable.exists():
        raise RuntimeError(f"CmdStan compile did not create executable: {executable}")
    return executable


def _ensure_stansummary(
    *,
    cmdstan_dir: Path,
    make_command: str,
    log_dir: Path,
) -> Path:
    executable = cmdstan_dir / "bin" / f"stansummary{_exe_suffix()}"
    if executable.exists():
        return executable
    _run_checked(
        [make_command, f"bin/stansummary{_exe_suffix()}"],
        cwd=cmdstan_dir,
        log_path=log_dir / "stansummary.compile.log",
    )
    if not executable.exists():
        raise RuntimeError("CmdStan stansummary executable is unavailable")
    return executable


def _run_chain(
    *,
    executable: Path,
    data_path: Path,
    output_path: Path,
    chain_id: int,
    contract: dict,
    cwd: Path,
) -> tuple[list[str], Path]:
    argv = cmdstan_sample_argv(
        executable,
        data_path,
        output_path,
        chain_id=chain_id,
        contract=contract,
    )
    log_path = output_path.with_suffix(".log")
    _run_checked(argv, cwd=cwd, log_path=log_path)
    if not output_path.exists():
        raise RuntimeError(f"CmdStan chain output missing: {output_path}")
    return argv, log_path


def _run_fit_job(
    *,
    job_id: str,
    spec: dict,
    wrapper_path: Path,
    executable: Path,
    cmdstan_dir: Path,
    stansummary: Path,
    contract: dict,
    out_dir: Path,
) -> dict:
    job_dir = out_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    raw_data = job_dir / "stan_data.json"
    input_provenance = materialize_stan_data(wrapper_path, raw_data)

    chains = int(contract["sampling"]["chains"])
    chain_files = [
        job_dir / f"chain_{chain_id}.csv"
        for chain_id in range(1, chains + 1)
    ]
    command_argv: dict[str, list[str]] = {}
    with ThreadPoolExecutor(max_workers=chains) as pool:
        futures = {
            pool.submit(
                _run_chain,
                executable=executable,
                data_path=raw_data,
                output_path=chain_files[chain_id - 1],
                chain_id=chain_id,
                contract=contract,
                cwd=job_dir,
            ): chain_id
            for chain_id in range(1, chains + 1)
        }
        for future in as_completed(futures):
            chain_id = futures[future]
            argv, _log = future.result()
            command_argv[str(chain_id)] = argv

    summary_path = job_dir / "stansummary.csv"
    summary_log = job_dir / "stansummary.log"
    summary_argv = [
        str(stansummary),
        "--csv_filename",
        str(summary_path),
        "--sig_figs",
        str(contract["sampling"]["output_sig_figs"]),
        *(str(path) for path in chain_files),
    ]
    _run_checked(summary_argv, cwd=cmdstan_dir, log_path=summary_log)

    expected_draws_per_chain = (
        int(contract["sampling"]["num_samples"])
        // int(contract["sampling"]["thin"])
    )
    combined = combine_cmdstan_chains(
        chain_files,
        require_gamma=bool(spec["require_gamma"]),
        max_depth=int(contract["sampling"]["max_depth"]),
        expected_chains=int(contract["sampling"]["chains"]),
        expected_draws_per_chain=expected_draws_per_chain,
        required_version=contract["required_cmdstan_version"],
    )
    families = (
        ("alpha", "beta", "gamma_u6_ordered")
        if spec["require_gamma"]
        else ("alpha", "beta")
    )
    stan_summary = read_stansummary_csv(
        summary_path,
        parameter_families=families,
    )
    diagnostics = evaluate_diagnostics(
        combined,
        stan_summary,
        contract=contract,
    )

    receipt = {
        "schema_version": "BALANCE_PLANT_V4_FIT_JOB_RECEIPT_V1",
        "job_id": job_id,
        "model_source": str(spec["model"].relative_to(ROOT)),
        "model_source_sha256": sha256_file(spec["model"]),
        "model_executable_sha256": sha256_file(executable),
        "input_wrapper": str(wrapper_path),
        "input_wrapper_sha256": input_provenance["wrapper_sha256"],
        "materialized_stan_data_sha256": input_provenance["stan_data_sha256"],
        "cmdstan_version": combined["stan_version"],
        "n_chains": combined["n_chains"],
        "draws_per_chain": combined["draws_per_chain"],
        "n_draws_total": combined["n_draws_total"],
        "chain_csv_sha256": {
            path.name: sha256_file(path)
            for path in chain_files
        },
        "commands": command_argv,
        "stansummary_command": summary_argv,
        "stansummary_sha256": sha256_file(summary_path),
        "diagnostics": diagnostics,
        "claim_ceiling": "fit_execution_receipt_only_no_effect_interpretation",
    }
    receipt_path = job_dir / "FIT_RECEIPT.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "receipt": receipt,
        "receipt_path": receipt_path,
        "draws": combined["draws"],
        "diagnostics": diagnostics,
    }



def _load_json_object(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"required V4 input is missing: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"V4 input must be a JSON object: {path}")
    return data


def _validate_input_bundle(input_dir: Path) -> dict:
    """Require one receipt-bound assembly/wrapper bundle from a validated human workspace."""
    provenance_path = input_dir / ANALYSIS_INPUT_RECEIPT
    provenance = _load_json_object(provenance_path)
    if provenance.get("schema_version") != "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1":
        raise ValueError("V4 analysis-input receipt schema mismatch")
    if provenance.get("analysis") != "balance_plant_v4_analysis_inputs":
        raise ValueError("V4 analysis-input receipt analysis mismatch")

    human_receipt_name = provenance.get("source_human_workspace_receipt")
    if human_receipt_name != HUMAN_WORKSPACE_RECEIPT:
        raise ValueError("V4 analysis-input receipt human-workspace receipt name drifted")
    human_receipt_path = input_dir / HUMAN_WORKSPACE_RECEIPT
    if not human_receipt_path.is_file():
        raise FileNotFoundError(
            f"required V4 human workspace receipt copy is missing: {human_receipt_path}"
        )
    human_receipt_sha256 = sha256_file(human_receipt_path)
    if human_receipt_sha256 != provenance.get("source_human_workspace_receipt_sha256"):
        raise ValueError("V4 human workspace receipt SHA256 mismatch")
    human_receipt = _load_json_object(human_receipt_path)
    if human_receipt.get("schema_version") != "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_V1":
        raise ValueError("copied V4 human workspace receipt schema mismatch")
    if human_receipt.get("analysis") != "balance_plant_v4_human_input_workspace":
        raise ValueError("copied V4 human workspace receipt analysis mismatch")
    if human_receipt.get("primary_model_assembly_ready") is not True:
        raise ValueError("copied V4 human workspace receipt is not assembly ready")
    if any((human_receipt.get("primary_human_open_gates") or {}).values()):
        raise ValueError("copied V4 human workspace receipt has primary human gates open")

    source_file_hashes = provenance.get("source_human_workspace_file_sha256") or {}
    human_files = human_receipt.get("files") or {}
    if set(source_file_hashes) != set(PRIMARY_HUMAN_BASENAMES):
        raise ValueError("V4 analysis-input receipt primary human file set drifted")
    for basename, expected in source_file_hashes.items():
        item = human_files.get(basename)
        if not isinstance(item, dict) or item.get("composed_sha256") != expected:
            raise ValueError(
                f"V4 human-workspace/analysis-input receipt mismatch for {basename}"
            )

    assembly_name = (provenance.get("outputs") or {}).get("licensed_assembly")
    if assembly_name != "BALANCE_PLANT_V4_LICENSED_ASSEMBLY.csv":
        raise ValueError("V4 analysis-input receipt licensed assembly name drifted")
    assembly_path = input_dir / assembly_name
    if not assembly_path.exists():
        raise FileNotFoundError(f"required V4 licensed assembly is missing: {assembly_path}")
    assembly_sha256 = sha256_file(assembly_path)
    expected_hashes = provenance.get("output_sha256") or {}
    if assembly_sha256 != expected_hashes.get("licensed_assembly"):
        raise ValueError("V4 licensed assembly SHA256 does not match analysis-input receipt")

    readout_name = (provenance.get("outputs") or {}).get("assembly_readout")
    if readout_name != "BALANCE_PLANT_V4_ASSEMBLY_READOUT.json":
        raise ValueError("V4 analysis-input receipt assembly readout name drifted")
    readout_path = input_dir / readout_name
    if not readout_path.is_file():
        raise FileNotFoundError(f"required V4 assembly readout is missing: {readout_path}")
    if sha256_file(readout_path) != expected_hashes.get("assembly_readout"):
        raise ValueError("V4 assembly readout SHA256 does not match analysis-input receipt")

    assembly = load_model_assembly(assembly_path)
    expected = build_v4_analysis_inputs(assembly)

    expected_by_job = {
        "PRIMARY": expected["main_stan_input"],
        "PRIMARY_PRIOR_SENSITIVITY": expected["prior_sensitivity_stan_input"],
        "TEMPORAL_GENERALITY": expected["temporal_generality_stan_input"],
        "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY": expected[
            "temporal_generality_prior_sensitivity_stan_input"
        ],
    }

    active_jobs = []
    wrapper_sha256 = {}
    for job_id in ("PRIMARY", "PRIMARY_PRIOR_SENSITIVITY"):
        path = input_dir / FIT_SPECS[job_id]["input"]
        actual = _load_json_object(path)
        if actual != expected_by_job[job_id]:
            raise ValueError(
                f"{job_id} input does not match deterministic rebuild from licensed assembly"
            )
        observed = sha256_file(path)
        if observed != expected_hashes.get(job_id):
            raise ValueError(f"{job_id} SHA256 does not match analysis-input receipt")
        if (provenance.get("outputs") or {}).get(job_id) != path.name:
            raise ValueError(f"{job_id} filename does not match analysis-input receipt")
        active_jobs.append(job_id)
        wrapper_sha256[job_id] = observed

    generality_jobs = (
        "TEMPORAL_GENERALITY",
        "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY",
    )
    expected_generality = expected_by_job["TEMPORAL_GENERALITY"] is not None
    if (
        expected_by_job["TEMPORAL_GENERALITY_PRIOR_SENSITIVITY"] is not None
    ) != expected_generality:
        raise ValueError("internal V4 generality pipeline produced an incomplete pair")

    generality_paths = [
        input_dir / FIT_SPECS[job_id]["input"]
        for job_id in generality_jobs
    ]
    present = [path.exists() for path in generality_paths]
    if expected_generality:
        if not all(present):
            raise ValueError(
                "licensed assembly requires both temporal-generality input files"
            )
        for job_id, path in zip(generality_jobs, generality_paths):
            actual = _load_json_object(path)
            if actual != expected_by_job[job_id]:
                raise ValueError(
                    f"{job_id} input does not match deterministic rebuild from licensed assembly"
                )
            observed = sha256_file(path)
            if observed != expected_hashes.get(job_id):
                raise ValueError(f"{job_id} SHA256 does not match analysis-input receipt")
            if (provenance.get("outputs") or {}).get(job_id) != path.name:
                raise ValueError(f"{job_id} filename does not match analysis-input receipt")
            active_jobs.append(job_id)
            wrapper_sha256[job_id] = observed
    elif any(present):
        raise ValueError(
            "temporal-generality inputs are present even though the licensed assembly "
            "does not pass the frozen generality support gate"
        )

    if provenance.get("active_fit_jobs") != active_jobs:
        raise ValueError("V4 analysis-input receipt active fit jobs disagree with assembly")
    expected_status = "READY" if expected_generality else "NOT_READY"
    if provenance.get("temporal_generality_status") != expected_status:
        raise ValueError("V4 analysis-input receipt generality status disagrees with assembly")

    return {
        "assembly": assembly,
        "assembly_path": assembly_path,
        "assembly_sha256": assembly_sha256,
        "analysis_input_receipt_path": provenance_path,
        "analysis_input_receipt_sha256": sha256_file(provenance_path),
        "source_human_workspace_receipt_path": human_receipt_path,
        "source_human_workspace_receipt_sha256": human_receipt_sha256,
        "active_jobs": active_jobs,
        "wrapper_sha256": wrapper_sha256,
        "temporal_generality_expected": expected_generality,
    }


def run_all(
    *,
    cmdstan_dir: Path,
    input_dir: Path = DEFAULT_INPUT,
    out_dir: Path = DEFAULT_OUT,
    contract_path: Path = CONTRACT,
    make_command: str = "make",
) -> dict:
    contract = load_fit_execution_contract(contract_path)
    input_bundle = _validate_input_bundle(input_dir)
    if out_dir.exists():
        raise ValueError(
            "V4 fit output directory already exists; choose a new immutable "
            "workspace so previous fit evidence is never mixed or overwritten"
        )
    out_dir.mkdir(parents=True, exist_ok=False)
    build_dir = out_dir / "_cmdstan_build"
    build_dir.mkdir(parents=True, exist_ok=True)
    _ensure_stanc(
        cmdstan_dir=cmdstan_dir,
        make_command=make_command,
        log_dir=build_dir,
    )
    cmdstan_version = _cmdstan_version(cmdstan_dir)
    required_version = contract["required_cmdstan_version"]
    if cmdstan_version != required_version:
        raise RuntimeError(
            f"CmdStan version mismatch: required {required_version}, "
            f"found {cmdstan_version}"
        )

    active_jobs = list(input_bundle["active_jobs"])

    model_executables: dict[Path, Path] = {}
    for job_id in active_jobs:
        model = FIT_SPECS[job_id]["model"]
        if model not in model_executables:
            model_executables[model] = _compile_model(
                cmdstan_dir=cmdstan_dir,
                stan_path=model,
                build_dir=build_dir,
                make_command=make_command,
            )
    stansummary = _ensure_stansummary(
        cmdstan_dir=cmdstan_dir,
        make_command=make_command,
        log_dir=build_dir,
    )

    fits = {}
    for job_id in active_jobs:
        spec = FIT_SPECS[job_id]
        fits[job_id] = _run_fit_job(
            job_id=job_id,
            spec=spec,
            wrapper_path=input_dir / spec["input"],
            executable=model_executables[spec["model"]],
            cmdstan_dir=cmdstan_dir,
            stansummary=stansummary,
            contract=contract,
            out_dir=out_dir,
        )

    diagnostic_failures = [
        job_id
        for job_id, fit in fits.items()
        if fit["diagnostics"]["status"] != "PASS"
    ]
    overall = {
        "schema_version": "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1",
        "contract": str(contract_path),
        "contract_sha256": sha256_file(contract_path),
        "required_cmdstan_version": required_version,
        "preflight_cmdstan_version": cmdstan_version,
        "active_jobs": active_jobs,
        "source_human_workspace_receipt": str(
            input_bundle["source_human_workspace_receipt_path"]
        ),
        "source_human_workspace_receipt_sha256": input_bundle[
            "source_human_workspace_receipt_sha256"
        ],
        "analysis_input_receipt": str(input_bundle["analysis_input_receipt_path"]),
        "analysis_input_receipt_sha256": input_bundle[
            "analysis_input_receipt_sha256"
        ],
        "licensed_assembly": str(input_bundle["assembly_path"]),
        "licensed_assembly_sha256": input_bundle["assembly_sha256"],
        "input_wrapper_sha256": input_bundle["wrapper_sha256"],
        "temporal_generality_expected_from_assembly": input_bundle[
            "temporal_generality_expected"
        ],
        "job_receipts": {
            job_id: str(fit["receipt_path"])
            for job_id, fit in fits.items()
        },
        "diagnostic_failures": diagnostic_failures,
        "postfit_decision_allowed": not diagnostic_failures,
        "automatic_retuning_permitted": False,
        "claim_ceiling": "fit_execution_status_only_no_publication_decision",
    }

    overall_path = out_dir / "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1.json"
    overall_path.write_text(
        json.dumps(overall, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if diagnostic_failures:
        raise RuntimeError(
            "V4 CmdStan diagnostics failed; posterior decisions are blocked: "
            + ", ".join(diagnostic_failures)
        )

    assembly = input_bundle["assembly"]
    primary_summary = summarize_v4_primary_postfit(
        assembly,
        primary_draws=fits["PRIMARY"]["draws"],
        sensitivity_draws=fits["PRIMARY_PRIOR_SENSITIVITY"]["draws"],
    )
    primary_path = out_dir / "BALANCE_PLANT_V4_PRIMARY_POSTFIT_SUMMARY.json"
    primary_path.write_text(
        json.dumps(primary_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    generality_path = None
    if "TEMPORAL_GENERALITY" in fits:
        generality_summary = summarize_v4_temporal_generality_postfit(
            assembly,
            primary_draws=fits["TEMPORAL_GENERALITY"]["draws"],
            sensitivity_draws=fits[
                "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY"
            ]["draws"],
        )
        generality_path = (
            out_dir / "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_POSTFIT_SUMMARY.json"
        )
        generality_path.write_text(
            json.dumps(generality_summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return {
        "execution_receipt": str(overall_path),
        "primary_postfit_summary": str(primary_path),
        "temporal_generality_postfit_summary": (
            str(generality_path) if generality_path is not None else None
        ),
        "diagnostics": "PASS",
        "claim_ceiling": "postfit_reporting_outputs_not_publication_decision",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmdstan-dir", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--contract", type=Path, default=CONTRACT)
    parser.add_argument("--make-command", default="make")
    args = parser.parse_args()

    result = run_all(
        cmdstan_dir=args.cmdstan_dir.resolve(),
        input_dir=args.input_dir.resolve(),
        out_dir=args.out_dir.resolve(),
        contract_path=args.contract.resolve(),
        make_command=args.make_command,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

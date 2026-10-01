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


def run_all(
    *,
    cmdstan_dir: Path,
    input_dir: Path = DEFAULT_INPUT,
    out_dir: Path = DEFAULT_OUT,
    contract_path: Path = CONTRACT,
    make_command: str = "make",
) -> dict:
    contract = load_fit_execution_contract(contract_path)
    out_dir.mkdir(parents=True, exist_ok=True)
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

    required = ("PRIMARY", "PRIMARY_PRIOR_SENSITIVITY")
    for job_id in required:
        path = input_dir / FIT_SPECS[job_id]["input"]
        if not path.exists():
            raise FileNotFoundError(f"required V4 input is missing: {path}")

    generality_paths = [
        input_dir / FIT_SPECS[job_id]["input"]
        for job_id in (
            "TEMPORAL_GENERALITY",
            "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY",
        )
    ]
    if generality_paths[0].exists() != generality_paths[1].exists():
        raise ValueError(
            "temporal generality primary and prior-sensitivity inputs must exist together"
        )
    active_jobs = list(required)
    if all(path.exists() for path in generality_paths):
        active_jobs.extend((
            "TEMPORAL_GENERALITY",
            "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY",
        ))

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

    assembly_path = input_dir / "BALANCE_PLANT_V4_LICENSED_ASSEMBLY.csv"
    assembly = load_model_assembly(assembly_path)
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

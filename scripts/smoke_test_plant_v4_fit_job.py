#!/usr/bin/env python3
"""Run short real-CmdStan smoke jobs through the production V4 fit-job path."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_plant_v4_cmdstan as runner  # noqa: E402
import smoke_test_plant_v4_cmdstan as model_smoke  # noqa: E402
from balance_domain.plant_analysis_pipeline import build_v4_analysis_inputs  # noqa: E402


PRIMARY_MODEL = model_smoke.PRIMARY_MODEL
GENERALITY_MODEL = model_smoke.GENERALITY_MODEL


def _row(
    row_id: str,
    universe: str,
    mode: str,
    module: str,
    timing: str,
    spatial: str = "SAME_UNIT",
) -> dict[str, str]:
    return {
        "analysis_row_id": row_id,
        "universe_id": universe,
        "dependency_group": row_id,
        "dependence_block": f"block::{row_id}",
        "system_taxon": row_id,
        "conflict_family": (
            "SEXUAL_INTERFERENCE"
            if universe == "U2_BARRETT_2002"
            else "POLLEN_REWARD_GAMETE"
        ),
        "conflict_receipt_status": "ADJUDICATED_POSITIVE",
        "architecture_mode": mode,
        "module_substrate": module,
        "conflict_timing_geometry": timing,
        "conflict_spatial_geometry": spatial,
        "architecture_adjudication_status": "ADJUDICATED",
        "predictor_receipt_status": "THREE_ADJUDICATED_OUTCOME_INDEPENDENT",
        "source_basis": "synthetic_engine_smoke",
        "claim_ceiling": "synthetic_engine_smoke_only",
    }


def production_wrapper_smoke_rows() -> list[dict[str, str]]:
    """Return a synthetic licensed assembly that opens all four frozen V4 fit jobs."""
    u2 = "U2_BARRETT_2002"
    u6 = "U6_POLLEN_THEFT_HARGREAVES_2009"
    return [
        _row("u2_s1", u2, "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row("u2_s2", u2, "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _row("u2_n1", u2, "TEMPORAL_SEPARATION", "SERIAL_WITHIN_FLOWER", "SEASONALLY_ALTERNATING"),
        _row("u2_n2", u2, "SPATIAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row("u2_n3", u2, "TEMPORAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _row("u2_d1", u2, "WITHIN_FLOWER_DIVISION_OF_LABOUR", "REPEATED_FLOWERS", "CONTEXT_DEPENDENT"),
        _row("u2_m1", u2, "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "MIXED", "BETWEEN_MODULES"),
        _row("u6_s1", u6, "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row("u6_n1", u6, "TEMPORAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _row("u6_n2", u6, "SPATIAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row("u6_d1", u6, "AMONG_FLOWER_MODULE_DIVISION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row("u6_m1", u6, "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEASONALLY_ALTERNATING"),
    ]


SMOKE_SAMPLING = {
    "chains": 4,
    "num_warmup": 25,
    "num_samples": 25,
    "save_warmup": False,
    "thin": 1,
    "adapt_delta": 0.8,
    "max_depth": 10,
    "metric": "diag_e",
    "seed": 20261002,
    "output_sig_figs": 12,
    "refresh": 0,
}

# These thresholds are intentionally permissive: the purpose of this smoke is
# external-engine / parser compatibility, not convergence certification.
SMOKE_DIAGNOSTICS = {
    "max_divergences": 100,
    "max_treedepth_hits": 100,
    "min_ebfmi": 0.0,
    "max_parameter_rhat": 100.0,
    "min_parameter_ess_bulk": 0.0,
    "min_parameter_ess_tail": 0.0,
    "automatic_retuning_allowed": False,
}

SMOKE_CONTRACT = {
    "required_cmdstan_version": "2.40.0",
    "sampling": SMOKE_SAMPLING,
    "diagnostics": SMOKE_DIAGNOSTICS,
}


def _write_wrapper(path: Path, *, wrapper_payload: dict) -> None:
    """Write an unmodified wrapper produced by the production V4 pre-fit pipeline."""
    if set(wrapper_payload) != {"stan_data", "metadata"}:
        raise ValueError("production V4 wrapper must contain stan_data and metadata")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(wrapper_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _run_job(
    *,
    job_id: str,
    model: Path,
    wrapper_payload: dict,
    require_gamma: bool,
    executable: Path,
    cmdstan_dir: Path,
    stansummary: Path,
    work_dir: Path,
) -> dict:
    wrapper = work_dir / "inputs" / f"{job_id}.json"
    _write_wrapper(wrapper, wrapper_payload=wrapper_payload)
    fit = runner._run_fit_job(
        job_id=job_id,
        spec={
            "model": model,
            "require_gamma": require_gamma,
        },
        wrapper_path=wrapper,
        executable=executable,
        cmdstan_dir=cmdstan_dir,
        stansummary=stansummary,
        contract=SMOKE_CONTRACT,
        out_dir=work_dir,
    )
    receipt = fit["receipt"]
    return {
        "job_id": job_id,
        "model": str(model.relative_to(ROOT)),
        "n_chains": receipt["n_chains"],
        "draws_per_chain": receipt["draws_per_chain"],
        "n_draws_total": receipt["n_draws_total"],
        "cmdstan_version": receipt["cmdstan_version"],
        "stansummary_sha256": receipt["stansummary_sha256"],
        "diagnostics_observed": receipt["diagnostics"]["observed"],
        "diagnostic_thresholds_are_smoke_only": True,
        "fit_receipt": str(fit["receipt_path"]),
    }


def run_smoke(
    *,
    cmdstan_dir: Path,
    work_dir: Path,
    make_command: str = "make",
) -> dict:
    if work_dir.exists():
        raise ValueError("CmdStan fit-job smoke work directory already exists")
    work_dir.mkdir(parents=True)

    runner._ensure_stanc(
        cmdstan_dir=cmdstan_dir,
        make_command=make_command,
        log_dir=work_dir,
    )
    version = runner._cmdstan_version(cmdstan_dir)
    if version != "2.40.0":
        raise RuntimeError(f"CmdStan fit-job smoke requires 2.40.0, found {version}")

    build_dir = work_dir / "_build"
    build_dir.mkdir()
    primary_executable = runner._compile_model(
        cmdstan_dir=cmdstan_dir,
        stan_path=PRIMARY_MODEL,
        build_dir=build_dir,
        make_command=make_command,
    )
    generality_executable = runner._compile_model(
        cmdstan_dir=cmdstan_dir,
        stan_path=GENERALITY_MODEL,
        build_dir=build_dir,
        make_command=make_command,
    )
    stansummary = runner._ensure_stansummary(
        cmdstan_dir=cmdstan_dir,
        make_command=make_command,
        log_dir=build_dir,
    )

    pipeline = build_v4_analysis_inputs(production_wrapper_smoke_rows())
    if pipeline["temporal_generality_status"] != "READY":
        raise RuntimeError("synthetic production-wrapper smoke must open all four V4 jobs")

    primary = _run_job(
        job_id="PRIMARY_SMOKE",
        model=PRIMARY_MODEL,
        wrapper_payload=pipeline["main_stan_input"],
        require_gamma=False,
        executable=primary_executable,
        cmdstan_dir=cmdstan_dir,
        stansummary=stansummary,
        work_dir=work_dir,
    )
    primary_prior = _run_job(
        job_id="PRIMARY_PRIOR_SENSITIVITY_SMOKE",
        model=PRIMARY_MODEL,
        wrapper_payload=pipeline["prior_sensitivity_stan_input"],
        require_gamma=False,
        executable=primary_executable,
        cmdstan_dir=cmdstan_dir,
        stansummary=stansummary,
        work_dir=work_dir,
    )
    generality = _run_job(
        job_id="GENERALITY_SMOKE",
        model=GENERALITY_MODEL,
        wrapper_payload=pipeline["temporal_generality_stan_input"],
        require_gamma=True,
        executable=generality_executable,
        cmdstan_dir=cmdstan_dir,
        stansummary=stansummary,
        work_dir=work_dir,
    )
    generality_prior = _run_job(
        job_id="GENERALITY_PRIOR_SENSITIVITY_SMOKE",
        model=GENERALITY_MODEL,
        wrapper_payload=pipeline["temporal_generality_prior_sensitivity_stan_input"],
        require_gamma=True,
        executable=generality_executable,
        cmdstan_dir=cmdstan_dir,
        stansummary=stansummary,
        work_dir=work_dir,
    )

    receipt = {
        "analysis": "balance_plant_v4_cmdstan_fit_job_smoke",
        "cmdstan_version": version,
        "sampling": SMOKE_SAMPLING,
        "input_surface": "production_build_v4_analysis_inputs_from_synthetic_licensed_assembly",
        "synthetic_analysis_rows": len(production_wrapper_smoke_rows()),
        "active_job_shape": [
            "PRIMARY",
            "PRIMARY_PRIOR_SENSITIVITY",
            "TEMPORAL_GENERALITY",
            "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY",
        ],
        "diagnostic_policy": (
            "permissive_smoke_thresholds_parser_compatibility_only"
        ),
        "primary": primary,
        "primary_prior_sensitivity": primary_prior,
        "generality": generality,
        "generality_prior_sensitivity": generality_prior,
        "claim_ceiling": (
            "production_wrapper_engine_parser_smoke_only_not_production_fit_or_diagnostics"
        ),
    }
    (work_dir / "FIT_JOB_SMOKE_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmdstan-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--make-command", default="make")
    args = parser.parse_args()
    result = run_smoke(
        cmdstan_dir=args.cmdstan_dir.resolve(),
        work_dir=args.work_dir.resolve(),
        make_command=args.make_command,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

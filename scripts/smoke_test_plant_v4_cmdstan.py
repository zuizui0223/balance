#!/usr/bin/env python3
"""Compile and minimally sample both BALANCE plant V4 Stan models with CmdStan 2.40.0."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_plant_v4_cmdstan as runner  # noqa: E402
from balance_domain.plant_v4_cmdstan import (  # noqa: E402
    cmdstan_sample_argv,
    read_cmdstan_chain,
)


PRIMARY_MODEL = ROOT / "comparative" / "models" / "BALANCE_PLANT_V4_MULTINOMIAL.stan"
GENERALITY_MODEL = (
    ROOT / "comparative" / "models" / "BALANCE_PLANT_V4_TEMPORAL_GENERALITY.stan"
)

SMOKE_SAMPLING = {
    "chains": 1,
    "num_warmup": 25,
    "num_samples": 25,
    "save_warmup": False,
    "thin": 1,
    "adapt_delta": 0.8,
    "max_depth": 10,
    "metric": "diag_e",
    "seed": 20261001,
    "output_sig_figs": 12,
    "refresh": 0,
}

BASE_DATA = {
    "N": 12,
    "K": 4,
    "U": 2,
    "P": 3,
    "X": [
        [0, 0, 0],
        [0, 1, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 0, 1],
        [1, 0, 1],
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [0, 1, 0],
        [0, 0, 0],
        [0, 1, 0],
    ],
    "y": [1, 2, 3, 4, 2, 3, 1, 2, 3, 4, 1, 2],
    "universe": [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
    "slope_prior_sd": 0.75,
    "intercept_prior_sd": 1.5,
}


def smoke_data(*, generality: bool) -> dict:
    data = json.loads(json.dumps(BASE_DATA))
    if generality:
        data["u6_ordered"] = [
            int(u == 2 and x[1] == 1)
            for u, x in zip(data["universe"], data["X"])
        ]
        data["interaction_prior_sd"] = 0.75
    return data


def _write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _posterior_header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        for raw in handle:
            if raw.startswith("#"):
                continue
            return next(csv.reader([raw.rstrip("\n")]))
    raise ValueError(f"CmdStan smoke output has no CSV header: {path}")


def _run_model(
    *,
    name: str,
    model: Path,
    data: dict,
    cmdstan_dir: Path,
    work_dir: Path,
    make_command: str,
    require_gamma: bool,
) -> dict:
    model_dir = work_dir / name
    build_dir = model_dir / "build"
    model_dir.mkdir(parents=True, exist_ok=True)
    executable = runner._compile_model(
        cmdstan_dir=cmdstan_dir,
        stan_path=model,
        build_dir=build_dir,
        make_command=make_command,
    )
    data_path = model_dir / "data.json"
    output_path = model_dir / "chain_1.csv"
    _write_json(data_path, data)
    argv = cmdstan_sample_argv(
        executable,
        data_path,
        output_path,
        chain_id=1,
        contract={"sampling": SMOKE_SAMPLING},
    )
    runner._run_checked(
        argv,
        cwd=model_dir,
        log_path=model_dir / "sample.log",
    )
    if not output_path.is_file():
        raise RuntimeError(f"CmdStan smoke output missing: {output_path}")

    header = _posterior_header(output_path)
    if not any(name.startswith("alpha.") for name in header):
        raise ValueError(f"{name} smoke output lacks alpha parameters")
    if not any(name.startswith("beta.") for name in header):
        raise ValueError(f"{name} smoke output lacks beta parameters")
    gamma_present = any(name.startswith("gamma_u6_ordered.") for name in header)
    if gamma_present is not require_gamma:
        raise ValueError(f"{name} gamma parameter presence disagrees with model contract")

    # Route the real CmdStan 2.40.0 CSV through the same parser used by the
    # production runner. This catches engine/header/comment drift that a raw
    # header-presence check cannot detect.
    parsed = read_cmdstan_chain(output_path, require_gamma=require_gamma)
    if parsed["n_draws"] != SMOKE_SAMPLING["num_samples"]:
        raise ValueError(
            f"{name} production parser recovered {parsed['n_draws']} draws; "
            f"expected {SMOKE_SAMPLING['num_samples']}"
        )
    if parsed["stan_version"] != "2.40.0":
        raise ValueError(
            f"{name} production parser version drifted: {parsed['stan_version']!r}"
        )

    return {
        "model": str(model.relative_to(ROOT)),
        "executable": str(executable),
        "data": str(data_path),
        "output": str(output_path),
        "n_columns": len(header),
        "gamma_present": gamma_present,
        "production_parser": {
            "n_draws": parsed["n_draws"],
            "stan_version": parsed["stan_version"],
            "divergences": parsed["divergences"],
            "max_treedepth_observed": parsed["max_treedepth_observed"],
            "ebfmi": parsed["ebfmi"],
        },
    }


def run_smoke(
    *,
    cmdstan_dir: Path,
    work_dir: Path,
    make_command: str = "make",
) -> dict:
    if work_dir.exists():
        raise ValueError("CmdStan smoke work directory already exists")
    work_dir.mkdir(parents=True)

    runner._ensure_stanc(
        cmdstan_dir=cmdstan_dir,
        make_command=make_command,
        log_dir=work_dir,
    )
    version = runner._cmdstan_version(cmdstan_dir)
    if version != "2.40.0":
        raise RuntimeError(f"CmdStan smoke requires 2.40.0, found {version}")

    primary = _run_model(
        name="primary",
        model=PRIMARY_MODEL,
        data=smoke_data(generality=False),
        cmdstan_dir=cmdstan_dir,
        work_dir=work_dir,
        make_command=make_command,
        require_gamma=False,
    )
    generality = _run_model(
        name="generality",
        model=GENERALITY_MODEL,
        data=smoke_data(generality=True),
        cmdstan_dir=cmdstan_dir,
        work_dir=work_dir,
        make_command=make_command,
        require_gamma=True,
    )
    receipt = {
        "analysis": "balance_plant_v4_cmdstan_smoke",
        "cmdstan_version": version,
        "sampling": SMOKE_SAMPLING,
        "primary": primary,
        "generality": generality,
        "claim_ceiling": "engine_compatibility_smoke_only_not_production_fit",
    }
    (work_dir / "SMOKE_RECEIPT.json").write_text(
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

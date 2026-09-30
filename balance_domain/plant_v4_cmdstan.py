"""CmdStan execution and diagnostic contracts for BALANCE plant model V4.

This module intentionally has no CmdStanPy dependency. It builds/validates CmdStan CLI
commands, materializes raw Stan data from the audited pre-fit wrappers, parses CmdStan CSV
draws, and applies fail-closed diagnostics. The actual executable invocation lives in the
companion script.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Iterable


CONTRACT_SCHEMA = "BALANCE_PLANT_V4_FIT_EXECUTION_CONTRACT_V1"
PRIMARY_FAMILIES = ("alpha", "beta")
GENERALITY_FAMILIES = ("alpha", "beta", "gamma_u6_ordered")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_fit_execution_contract(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != CONTRACT_SCHEMA:
        raise ValueError("V4 fit execution contract schema mismatch")
    if data.get("status") != "FROZEN_PRE_OUTCOME_BEFORE_INDEPENDENT_ARCHITECTURE_CODING":
        raise ValueError("V4 fit execution contract is not frozen pre-outcome")
    if data.get("required_cmdstan_version") != "2.40.0":
        raise ValueError("V4 fit execution contract CmdStan version drifted")
    sampling = data.get("sampling", {})
    required_sampling = {
        "chains": 4,
        "num_warmup": 1000,
        "num_samples": 2000,
        "save_warmup": False,
        "thin": 1,
        "adapt_delta": 0.99,
        "max_depth": 15,
        "metric": "diag_e",
        "seed": 20260930,
        "output_sig_figs": 18,
        "refresh": 100,
    }
    if sampling != required_sampling:
        raise ValueError("V4 fit sampling contract drifted")
    diagnostics = data.get("diagnostics", {})
    required_diagnostics = {
        "max_divergences": 0,
        "max_treedepth_hits": 0,
        "min_ebfmi": 0.3,
        "max_parameter_rhat": 1.01,
        "min_parameter_ess_bulk": 400,
        "min_parameter_ess_tail": 400,
    }
    for key, value in required_diagnostics.items():
        if diagnostics.get(key) != value:
            raise ValueError(f"V4 diagnostic contract drifted for {key}")
    if diagnostics.get("automatic_retuning_allowed") is not False:
        raise ValueError("V4 fit contract must forbid automatic retuning")
    return data


def materialize_stan_data(wrapper_path: Path, output_path: Path) -> dict:
    """Write only the frozen Stan data block from an audited wrapper JSON."""
    wrapper = json.loads(wrapper_path.read_text(encoding="utf-8"))
    if set(wrapper) != {"stan_data", "metadata"}:
        raise ValueError("V4 Stan input wrapper must contain exactly stan_data and metadata")
    data = wrapper["stan_data"]
    if not isinstance(data, dict) or not data:
        raise ValueError("V4 Stan input wrapper has no stan_data object")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "wrapper_sha256": sha256_file(wrapper_path),
        "stan_data_sha256": sha256_file(output_path),
        "metadata": wrapper["metadata"],
    }


def cmdstan_sample_argv(
    executable: Path,
    data_file: Path,
    output_file: Path,
    *,
    chain_id: int,
    contract: dict,
) -> list[str]:
    sampling = contract["sampling"]
    if chain_id < 1 or chain_id > int(sampling["chains"]):
        raise ValueError("chain_id outside frozen chain range")
    return [
        str(executable),
        "sample",
        f"num_warmup={sampling['num_warmup']}",
        f"num_samples={sampling['num_samples']}",
        f"save_warmup={1 if sampling['save_warmup'] else 0}",
        f"thin={sampling['thin']}",
        "adapt",
        f"delta={sampling['adapt_delta']}",
        "algorithm=hmc",
        "engine=nuts",
        f"max_depth={sampling['max_depth']}",
        f"metric={sampling['metric']}",
        "data",
        f"file={data_file}",
        "output",
        f"file={output_file}",
        f"refresh={sampling['refresh']}",
        f"sig_figs={sampling['output_sig_figs']}",
        "random",
        f"seed={sampling['seed']}",
        f"id={chain_id}",
    ]


def _finite(value: str, label: str) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} is not numeric") from exc
    if not math.isfinite(x):
        raise ValueError(f"{label} must be finite")
    return x


def _csv_parts(path: Path) -> tuple[dict[str, str], list[str], list[dict[str, str]]]:
    comments: dict[str, str] = {}
    header: str | None = None
    data_lines: list[str] = []
    key_value = re.compile(r"^#\s*([A-Za-z0-9_]+)\s*=\s*(.*?)\s*(?:\(Default\))?\s*$")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            match = key_value.match(line)
            if match:
                comments.setdefault(match.group(1), match.group(2).strip())
            continue
        if header is None:
            header = line
        else:
            data_lines.append(line)
    if header is None:
        raise ValueError(f"CmdStan CSV has no header: {path}")
    reader = csv.DictReader([header, *data_lines])
    rows = list(reader)
    if not rows:
        raise ValueError(f"CmdStan CSV has no sampling draws: {path}")
    return comments, list(reader.fieldnames or ()), rows


def _required_draw_columns(require_gamma: bool) -> list[str]:
    columns = [
        *(f"alpha.{u}.{k}" for k in range(1, 4) for u in range(1, 3)),
        *(f"beta.{p}.{k}" for k in range(1, 4) for p in range(1, 4)),
    ]
    if require_gamma:
        columns.extend(f"gamma_u6_ordered.{k}" for k in range(1, 4))
    return columns


def read_cmdstan_chain(path: Path, *, require_gamma: bool) -> dict:
    """Parse one post-warmup CmdStan chain into evaluator-shaped draws."""
    comments, fields, rows = _csv_parts(path)
    required_sampler = {
        "divergent__",
        "treedepth__",
        "energy__",
    }
    missing_sampler = sorted(required_sampler - set(fields))
    if missing_sampler:
        raise ValueError(f"CmdStan CSV missing sampler diagnostics: {missing_sampler}")
    missing_draws = sorted(set(_required_draw_columns(require_gamma)) - set(fields))
    if missing_draws:
        raise ValueError(f"CmdStan CSV missing V4 parameters: {missing_draws}")

    draws = []
    energies: list[float] = []
    divergences = 0
    treedepths: list[int] = []
    for row_number, row in enumerate(rows, start=2):
        alpha = [
            [_finite(row[f"alpha.{u}.{k}"], f"row {row_number} alpha.{u}.{k}") for k in range(1, 4)]
            for u in range(1, 3)
        ]
        beta = [
            [_finite(row[f"beta.{p}.{k}"], f"row {row_number} beta.{p}.{k}") for k in range(1, 4)]
            for p in range(1, 4)
        ]
        draw = {"alpha": alpha, "beta": beta}
        if require_gamma:
            draw["gamma_u6_ordered"] = [
                _finite(
                    row[f"gamma_u6_ordered.{k}"],
                    f"row {row_number} gamma_u6_ordered.{k}",
                )
                for k in range(1, 4)
            ]
        draws.append(draw)
        divergent = _finite(row["divergent__"], f"row {row_number} divergent__")
        if divergent not in {0.0, 1.0}:
            raise ValueError(f"row {row_number} divergent__ must be exactly 0 or 1")
        divergences += int(divergent)

        treedepth = _finite(row["treedepth__"], f"row {row_number} treedepth__")
        if treedepth < 0 or not treedepth.is_integer():
            raise ValueError(
                f"row {row_number} treedepth__ must be a non-negative integer"
            )
        treedepths.append(int(treedepth))
        energies.append(_finite(row["energy__"], f"row {row_number} energy__"))

    if len(energies) < 2:
        ebfmi = 0.0
    else:
        energy_mean = sum(energies) / len(energies)
        variance = sum(
            (x - energy_mean) ** 2 for x in energies
        ) / (len(energies) - 1)
        transition = sum(
            (energies[i] - energies[i - 1]) ** 2
            for i in range(1, len(energies))
        ) / len(energies)
        ebfmi = transition / variance if variance > 0 else 0.0

    version = None
    if all(key in comments for key in (
        "stan_version_major",
        "stan_version_minor",
        "stan_version_patch",
    )):
        version = ".".join(
            comments[key].split()[0]
            for key in (
                "stan_version_major",
                "stan_version_minor",
                "stan_version_patch",
            )
        )

    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "n_draws": len(draws),
        "draws": draws,
        "stan_version": version,
        "divergences": divergences,
        "max_treedepth_observed": max(treedepths),
        "treedepths": treedepths,
        "ebfmi": ebfmi,
    }


def combine_cmdstan_chains(
    paths: Iterable[Path],
    *,
    require_gamma: bool,
    max_depth: int,
) -> dict:
    chains = [read_cmdstan_chain(Path(path), require_gamma=require_gamma) for path in paths]
    if not chains:
        raise ValueError("V4 fit requires at least one chain CSV")
    versions = {chain["stan_version"] for chain in chains}
    if None in versions:
        raise ValueError("CmdStan chain version metadata is required")
    if len(versions) != 1:
        raise ValueError("CmdStan chain version mismatch")
    return {
        "chains": chains,
        "draws": [draw for chain in chains for draw in chain["draws"]],
        "stan_version": next(iter(versions)),
        "divergences": sum(chain["divergences"] for chain in chains),
        "treedepth_hits": sum(
            sum(depth >= max_depth for depth in chain["treedepths"])
            for chain in chains
        ),
        "min_ebfmi": min(chain["ebfmi"] for chain in chains),
    }


def _norm_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def read_stansummary_csv(path: Path, *, parameter_families: Iterable[str]) -> dict:
    """Read the stansummary CSV and return parameter-only convergence diagnostics."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or ())
        rows = list(reader)
    if not fields or not rows:
        raise ValueError("stansummary CSV is empty")

    normalized = {_norm_header(field): field for field in fields}
    name_field = normalized.get("name") or normalized.get("variable") or fields[0]
    rhat_field = normalized.get("rhat")
    bulk_field = normalized.get("essbulk")
    tail_field = normalized.get("esstail")
    if not all((rhat_field, bulk_field, tail_field)):
        raise ValueError("stansummary CSV lacks R_hat/ESS_bulk/ESS_tail columns")

    families = tuple(parameter_families)
    selected = []
    for row in rows:
        name = (row.get(name_field) or "").strip()
        normalized_name = name.replace("[", ".").replace("]", "").replace(",", ".")
        if not any(
            normalized_name == family
            or normalized_name.startswith(f"{family}.")
            for family in families
        ):
            continue
        selected.append({
            "name": name,
            "rhat": _finite(row[rhat_field], f"{name} R_hat"),
            "ess_bulk": _finite(row[bulk_field], f"{name} ESS_bulk"),
            "ess_tail": _finite(row[tail_field], f"{name} ESS_tail"),
        })
    if not selected:
        raise ValueError("stansummary CSV contains no registered V4 parameters")
    return {
        "parameters": selected,
        "max_rhat": max(row["rhat"] for row in selected),
        "min_ess_bulk": min(row["ess_bulk"] for row in selected),
        "min_ess_tail": min(row["ess_tail"] for row in selected),
        "sha256": sha256_file(path),
    }


def evaluate_diagnostics(
    chain_summary: dict,
    stansummary: dict,
    *,
    contract: dict,
) -> dict:
    rules = contract["diagnostics"]
    checks = {
        "divergences": chain_summary["divergences"] <= rules["max_divergences"],
        "treedepth": chain_summary["treedepth_hits"] <= rules["max_treedepth_hits"],
        "ebfmi": chain_summary["min_ebfmi"] >= rules["min_ebfmi"],
        "rhat": stansummary["max_rhat"] <= rules["max_parameter_rhat"],
        "ess_bulk": stansummary["min_ess_bulk"] >= rules["min_parameter_ess_bulk"],
        "ess_tail": stansummary["min_ess_tail"] >= rules["min_parameter_ess_tail"],
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "observed": {
            "divergences": chain_summary["divergences"],
            "treedepth_hits": chain_summary["treedepth_hits"],
            "min_ebfmi": chain_summary["min_ebfmi"],
            "max_parameter_rhat": stansummary["max_rhat"],
            "min_parameter_ess_bulk": stansummary["min_ess_bulk"],
            "min_parameter_ess_tail": stansummary["min_ess_tail"],
        },
        "automatic_retuning_permitted": False,
    }

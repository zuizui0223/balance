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

    required_integrity = {
        "expected_chain_count": 4,
        "expected_postwarmup_draws_per_chain": 2000,
        "unique_chain_paths_required": True,
        "chain_cmdstan_version_must_equal_required": True,
        "stansummary_complete_parameter_set_required": True,
        "primary_parameter_count": 15,
        "generality_parameter_count": 18,
    }
    if data.get("chain_integrity") != required_integrity:
        raise ValueError("V4 fit chain-integrity contract drifted")

    required_input_integrity = {
        "licensed_assembly_required": True,
        "wrappers_must_equal_deterministic_rebuild_from_assembly": True,
        "primary_and_primary_sensitivity_required": True,
        "generality_pair_presence_must_match_assembly_support_gate": True,
        "generality_primary_and_sensitivity_must_exist_together": True,
        "record_licensed_assembly_sha256": True,
        "record_input_wrapper_sha256": True,
        "analysis_input_receipt_required": True,
        "analysis_input_receipt_files_must_match_workspace": True,
        "record_analysis_input_receipt_sha256": True,
        "record_source_human_workspace_receipt_sha256": True,
    }
    if data.get("input_bundle_integrity") != required_input_integrity:
        raise ValueError("V4 fit input-bundle integrity contract drifted")

    required_workspace = {
        "existing_output_directory_overwrite_allowed": False,
        "one_run_per_workspace": True,
        "stale_optional_outputs_forbidden": True,
        "new_run_requires_new_output_directory": True,
    }
    if data.get("workspace_policy") != required_workspace:
        raise ValueError("V4 fit workspace policy drifted")
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
    expected_chains: int | None = None,
    expected_draws_per_chain: int | None = None,
    required_version: str | None = None,
) -> dict:
    paths = [Path(path) for path in paths]
    if not paths:
        raise ValueError("V4 fit requires at least one chain CSV")
    if len({str(path.resolve()) for path in paths}) != len(paths):
        raise ValueError("V4 fit chain paths must be unique")
    if expected_chains is not None and len(paths) != expected_chains:
        raise ValueError(
            f"V4 fit requires exactly {expected_chains} chains, found {len(paths)}"
        )

    chains = [
        read_cmdstan_chain(path, require_gamma=require_gamma)
        for path in paths
    ]
    if expected_draws_per_chain is not None:
        bad = [
            (Path(chain["path"]).name, chain["n_draws"])
            for chain in chains
            if chain["n_draws"] != expected_draws_per_chain
        ]
        if bad:
            detail = ", ".join(f"{name}={n}" for name, n in bad)
            raise ValueError(
                "CmdStan chain draw count drifted from frozen sampling contract: "
                + detail
            )

    versions = {chain["stan_version"] for chain in chains}
    if None in versions:
        raise ValueError("CmdStan chain version metadata is required")
    if len(versions) != 1:
        raise ValueError("CmdStan chain version mismatch")
    version = next(iter(versions))
    if required_version is not None and version != required_version:
        raise ValueError(
            f"CmdStan chain version must be {required_version}, found {version}"
        )

    return {
        "chains": chains,
        "n_chains": len(chains),
        "draws_per_chain": [chain["n_draws"] for chain in chains],
        "n_draws_total": sum(chain["n_draws"] for chain in chains),
        "draws": [draw for chain in chains for draw in chain["draws"]],
        "stan_version": version,
        "divergences": sum(chain["divergences"] for chain in chains),
        "treedepth_hits": sum(
            sum(depth >= max_depth for depth in chain["treedepths"])
            for chain in chains
        ),
        "min_ebfmi": min(chain["ebfmi"] for chain in chains),
    }


def _norm_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _expected_stansummary_parameters(
    parameter_families: Iterable[str],
) -> set[str]:
    families = tuple(parameter_families)
    expected: set[str] = set()
    for family in families:
        if family == "alpha":
            expected.update(
                f"alpha.{u}.{k}"
                for u in range(1, 3)
                for k in range(1, 4)
            )
        elif family == "beta":
            expected.update(
                f"beta.{p}.{k}"
                for p in range(1, 4)
                for k in range(1, 4)
            )
        elif family == "gamma_u6_ordered":
            expected.update(
                f"gamma_u6_ordered.{k}"
                for k in range(1, 4)
            )
        else:
            raise ValueError(f"unregistered V4 parameter family {family!r}")
    return expected


def read_stansummary_csv(path: Path, *, parameter_families: Iterable[str]) -> dict:
    """Read stansummary and require the complete registered parameter set."""
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
    expected = _expected_stansummary_parameters(families)
    selected = []
    seen: set[str] = set()
    for row in rows:
        name = (row.get(name_field) or "").strip()
        normalized_name = name.replace("[", ".").replace("]", "").replace(",", ".")
        if not any(
            normalized_name == family
            or normalized_name.startswith(f"{family}.")
            for family in families
        ):
            continue
        if normalized_name in seen:
            raise ValueError(
                f"stansummary CSV repeats registered parameter {name!r}"
            )
        seen.add(normalized_name)
        selected.append({
            "name": name,
            "normalized_name": normalized_name,
            "rhat": _finite(row[rhat_field], f"{name} R_hat"),
            "ess_bulk": _finite(row[bulk_field], f"{name} ESS_bulk"),
            "ess_tail": _finite(row[tail_field], f"{name} ESS_tail"),
        })

    missing = sorted(expected - seen)
    unexpected = sorted(seen - expected)
    if missing or unexpected:
        detail = []
        if missing:
            detail.append("missing=" + ",".join(missing))
        if unexpected:
            detail.append("unexpected=" + ",".join(unexpected))
        raise ValueError(
            "stansummary registered parameter set mismatch: " + "; ".join(detail)
        )

    return {
        "parameters": selected,
        "n_parameters": len(selected),
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

import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from types import SimpleNamespace

import pytest

from balance_domain.plant_analysis_pipeline import build_v4_analysis_inputs
from balance_domain.plant_model_assembly import FIELDS as ASSEMBLY_FIELDS

from balance_domain.plant_v4_cmdstan import (
    cmdstan_sample_argv,
    combine_cmdstan_chains,
    evaluate_diagnostics,
    load_fit_execution_contract,
    materialize_stan_data,
    read_cmdstan_chain,
    read_stansummary_csv,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "BALANCE_PLANT_V4_FIT_EXECUTION_CONTRACT_V1.json"


def test_fit_execution_contract_is_frozen_before_outcome():
    data = load_fit_execution_contract(CONTRACT)
    assert data["required_cmdstan_version"] == "2.40.0"
    assert data["analysis_input_bundle_contract"] == (
        "data/BALANCE_PLANT_V4_ANALYSIS_INPUT_BUNDLE_CONTRACT_V1.json"
    )
    assert data["sampling"] == {
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
    assert data["diagnostics"]["automatic_retuning_allowed"] is False
    assert data["input_bundle_integrity"] == {
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
    assert data["workspace_policy"] == {
        "existing_output_directory_overwrite_allowed": False,
        "one_run_per_workspace": True,
        "stale_optional_outputs_forbidden": True,
        "new_run_requires_new_output_directory": True,
    }
    assert data["fit_output_integrity"] == {
        "job_receipt_sha256_required": True,
        "successful_postfit_output_sha256_required": True,
        "diagnostic_failure_receipt_must_record_no_postfit_outputs": True,
        "execution_status_required": True,
        "complete_status_requires_postfit_outputs": True,
    }
    assert data["chain_integrity"] == {
        "expected_chain_count": 4,
        "expected_postwarmup_draws_per_chain": 2000,
        "unique_chain_paths_required": True,
        "chain_cmdstan_version_must_equal_required": True,
        "stansummary_complete_parameter_set_required": True,
        "primary_parameter_count": 15,
        "generality_parameter_count": 18,
    }


def test_cmdstan_argv_uses_only_frozen_sampling_settings(tmp_path):
    contract = load_fit_execution_contract(CONTRACT)
    argv = cmdstan_sample_argv(
        tmp_path / "model",
        tmp_path / "data.json",
        tmp_path / "chain_1.csv",
        chain_id=1,
        contract=contract,
    )
    assert argv == [
        str(tmp_path / "model"),
        "sample",
        "num_warmup=1000",
        "num_samples=2000",
        "save_warmup=0",
        "thin=1",
        "adapt",
        "delta=0.99",
        "algorithm=hmc",
        "engine=nuts",
        "max_depth=15",
        "metric=diag_e",
        "data",
        f"file={tmp_path / 'data.json'}",
        "output",
        f"file={tmp_path / 'chain_1.csv'}",
        "refresh=100",
        "sig_figs=18",
        "random",
        "seed=20260930",
        "id=1",
    ]


def test_materialize_stan_data_strips_audit_metadata(tmp_path):
    wrapper = tmp_path / "wrapper.json"
    wrapper.write_text(
        json.dumps({
            "stan_data": {"N": 2, "K": 4},
            "metadata": {"analysis": "audit-only"},
        }),
        encoding="utf-8",
    )
    raw = tmp_path / "data.json"
    out = materialize_stan_data(wrapper, raw)
    assert json.loads(raw.read_text(encoding="utf-8")) == {"K": 4, "N": 2}
    assert out["metadata"] == {"analysis": "audit-only"}
    assert "stan_data_sha256" in out


def _chain_csv(path: Path, *, gamma=False, version="2.40.0", divergent=0, depth=7):
    fields = [
        "lp__",
        "accept_stat__",
        "stepsize__",
        "treedepth__",
        "n_leapfrog__",
        "divergent__",
        "energy__",
    ]
    fields += [f"alpha.{u}.{k}" for k in range(1, 4) for u in range(1, 3)]
    fields += [f"beta.{p}.{k}" for k in range(1, 4) for p in range(1, 4)]
    if gamma:
        fields += [f"gamma_u6_ordered.{k}" for k in range(1, 4)]

    major, minor, patch = version.split(".")
    lines = [
        f"# stan_version_major = {major}",
        f"# stan_version_minor = {minor}",
        f"# stan_version_patch = {patch}",
        ",".join(fields),
    ]
    energies = [1.0, 2.0, 1.2, 2.1]
    for i, energy in enumerate(energies):
        row = {
            "lp__": -1.0,
            "accept_stat__": 0.99,
            "stepsize__": 0.1,
            "treedepth__": depth,
            "n_leapfrog__": 15,
            "divergent__": divergent if i == 0 else 0,
            "energy__": energy,
        }
        for u in range(1, 3):
            for k in range(1, 4):
                row[f"alpha.{u}.{k}"] = 0.1 * u * k
        for p in range(1, 4):
            for k in range(1, 4):
                row[f"beta.{p}.{k}"] = 0.01 * p * k
        if gamma:
            for k in range(1, 4):
                row[f"gamma_u6_ordered.{k}"] = -0.1 * k
        lines.append(",".join(str(row[field]) for field in fields))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_cmdstan_chain_parser_builds_evaluator_draws_and_diagnostics(tmp_path):
    path = tmp_path / "chain.csv"
    _chain_csv(path, gamma=True)
    out = read_cmdstan_chain(path, require_gamma=True)
    assert out["stan_version"] == "2.40.0"
    assert out["n_draws"] == 4
    assert out["divergences"] == 0
    assert out["max_treedepth_observed"] == 7
    assert out["ebfmi"] > 0.3
    assert out["draws"][0]["alpha"][1][2] == pytest.approx(0.6)
    assert out["draws"][0]["beta"][2][1] == pytest.approx(0.06)
    assert out["draws"][0]["gamma_u6_ordered"][0] == pytest.approx(-0.1)


def test_cmdstan_chain_parser_rejects_nonfinite_parameter(tmp_path):
    path = tmp_path / "chain.csv"
    _chain_csv(path, gamma=False)
    text = path.read_text(encoding="utf-8")
    text = text.replace("0.01", "NaN", 1)
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="finite"):
        read_cmdstan_chain(path, require_gamma=False)


def test_combine_chains_counts_divergences_and_depth_hits(tmp_path):
    paths = []
    for i in range(4):
        path = tmp_path / f"chain_{i}.csv"
        _chain_csv(
            path,
            gamma=False,
            divergent=1 if i == 0 else 0,
            depth=15 if i == 1 else 7,
        )
        paths.append(path)
    out = combine_cmdstan_chains(paths, require_gamma=False, max_depth=15)
    assert out["divergences"] == 1
    assert out["treedepth_hits"] == 4
    assert len(out["draws"]) == 16


def _stansummary(path: Path, *, rhat=1.0, ess_bulk=1000, ess_tail=900):
    fields = [
        "name",
        "Mean",
        "MCSE",
        "StdDev",
        "MAD",
        "5%",
        "50%",
        "95%",
        "ESS_bulk",
        "ESS_tail",
        "ESS_bulk/s",
        "R_hat",
    ]
    names = [
        *(f"alpha[{u},{k}]" for u in range(1, 3) for k in range(1, 4)),
        *(f"beta[{p},{k}]" for p in range(1, 4) for k in range(1, 4)),
        *(f"gamma_u6_ordered[{k}]" for k in range(1, 4)),
        "log_lik[1]",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for name in names:
            writer.writerow({
                "name": name,
                "Mean": 0,
                "MCSE": 0.01,
                "StdDev": 1,
                "MAD": 1,
                "5%": -1,
                "50%": 0,
                "95%": 1,
                "ESS_bulk": ess_bulk,
                "ESS_tail": ess_tail,
                "ESS_bulk/s": 100,
                "R_hat": rhat,
            })


def test_stansummary_parser_limits_diagnostics_to_registered_parameters(tmp_path):
    path = tmp_path / "summary.csv"
    _stansummary(path, rhat=1.005, ess_bulk=800, ess_tail=700)
    out = read_stansummary_csv(
        path,
        parameter_families=("alpha", "beta", "gamma_u6_ordered"),
    )
    assert len(out["parameters"]) == 18
    assert out["n_parameters"] == 18
    assert out["max_rhat"] == pytest.approx(1.005)
    assert out["min_ess_bulk"] == 800
    assert out["min_ess_tail"] == 700
    assert all(not row["name"].startswith("log_lik") for row in out["parameters"])


def test_diagnostic_gate_is_fail_closed(tmp_path):
    contract = load_fit_execution_contract(CONTRACT)
    chain = {
        "divergences": 0,
        "treedepth_hits": 0,
        "min_ebfmi": 0.8,
    }
    summary = {
        "max_rhat": 1.005,
        "min_ess_bulk": 800,
        "min_ess_tail": 700,
    }
    passed = evaluate_diagnostics(chain, summary, contract=contract)
    assert passed["status"] == "PASS"
    assert all(passed["checks"].values())

    summary["max_rhat"] = 1.02
    failed = evaluate_diagnostics(chain, summary, contract=contract)
    assert failed["status"] == "FAIL"
    assert failed["checks"]["rhat"] is False
    assert failed["automatic_retuning_permitted"] is False



def test_v4_fit_execution_contract_is_linked_across_active_surfaces():
    target = "data/BALANCE_PLANT_V4_FIT_EXECUTION_CONTRACT_V1.json"
    spec = json.loads(
        (ROOT / "data" / "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4.json").read_text(
            encoding="utf-8"
        )
    )
    rules = json.loads(
        (ROOT / "data" / "BALANCE_PLANT_V4_POSTERIOR_DECISION_RULES_V1.json").read_text(
            encoding="utf-8"
        )
    )
    handoff = json.loads(
        (ROOT / "data" / "BALANCE_PLANT_CODER_HANDOFF_MANIFEST_V1.json").read_text(
            encoding="utf-8"
        )
    )
    assert spec["fit_execution_contract"] == target
    assert spec["fit_execution_runner"] == "scripts/run_plant_v4_cmdstan.py"
    assert rules["fit_execution_contract"] == target
    assert handoff["post_handoff_analysis"]["fit_execution_contract"] == target
    assert handoff["post_handoff_analysis"]["fit_runner"] == (
        "scripts/run_plant_v4_cmdstan.py"
    )


def test_runner_fit_specs_match_frozen_contract():
    runner_path = ROOT / "scripts" / "run_plant_v4_cmdstan.py"
    module_spec = importlib.util.spec_from_file_location("run_plant_v4_cmdstan", runner_path)
    runner = importlib.util.module_from_spec(module_spec)
    assert module_spec.loader is not None
    module_spec.loader.exec_module(runner)

    contract = load_fit_execution_contract(CONTRACT)
    registered = {item["id"]: item for item in contract["fit_jobs"]}
    assert set(runner.FIT_SPECS) == set(registered)
    for job_id, item in registered.items():
        assert runner.FIT_SPECS[job_id]["input"] == item["input"]



def test_cmdstan_chain_parser_rejects_invalid_sampler_flags(tmp_path):
    path = tmp_path / "bad_divergent.csv"
    _chain_csv(path, gamma=False)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    header_index = next(i for i, line in enumerate(lines) if not line.startswith("#"))
    fields = lines[header_index].split(",")
    divergent_index = fields.index("divergent__")
    first = lines[header_index + 1].split(",")
    first[divergent_index] = "2"
    lines[header_index + 1] = ",".join(first)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exactly 0 or 1"):
        read_cmdstan_chain(path, require_gamma=False)

    path = tmp_path / "bad_depth.csv"
    _chain_csv(path, gamma=False)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    header_index = next(i for i, line in enumerate(lines) if not line.startswith("#"))
    fields = lines[header_index].split(",")
    depth_index = fields.index("treedepth__")
    first = lines[header_index + 1].split(",")
    first[depth_index] = "3.5"
    lines[header_index + 1] = ",".join(first)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="non-negative integer"):
        read_cmdstan_chain(path, require_gamma=False)


def test_combine_chains_requires_cmdstan_version_metadata(tmp_path):
    paths = []
    for i in range(4):
        path = tmp_path / f"chain_{i}.csv"
        _chain_csv(path, gamma=False)
        text = path.read_text(encoding="utf-8")
        text = "\n".join(
            line for line in text.splitlines()
            if not line.startswith("# stan_version_")
        ) + "\n"
        path.write_text(text, encoding="utf-8")
        paths.append(path)

    with pytest.raises(ValueError, match="version metadata is required"):
        combine_cmdstan_chains(paths, require_gamma=False, max_depth=15)



def test_runner_preflight_reads_frozen_cmdstan_version(tmp_path, monkeypatch):
    runner_path = ROOT / "scripts" / "run_plant_v4_cmdstan.py"
    module_spec = importlib.util.spec_from_file_location(
        "run_plant_v4_cmdstan_version_test",
        runner_path,
    )
    runner = importlib.util.module_from_spec(module_spec)
    assert module_spec.loader is not None
    module_spec.loader.exec_module(runner)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stanc = bin_dir / "stanc"
    stanc.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout="stanc3 v2.40.0 (Unix)\n",
        ),
    )
    assert runner._cmdstan_version(tmp_path) == "2.40.0"


def test_runner_preflight_rejects_unparseable_cmdstan_version(tmp_path, monkeypatch):
    runner_path = ROOT / "scripts" / "run_plant_v4_cmdstan.py"
    module_spec = importlib.util.spec_from_file_location(
        "run_plant_v4_cmdstan_bad_version_test",
        runner_path,
    )
    runner = importlib.util.module_from_spec(module_spec)
    assert module_spec.loader is not None
    module_spec.loader.exec_module(runner)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "stanc").write_text("", encoding="utf-8")

    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout="unknown compiler version\n",
        ),
    )
    with pytest.raises(ValueError, match="could not parse"):
        runner._cmdstan_version(tmp_path)



def test_runner_bootstraps_stanc_with_cmdstan_make_target(tmp_path, monkeypatch):
    runner_path = ROOT / "scripts" / "run_plant_v4_cmdstan.py"
    module_spec = importlib.util.spec_from_file_location(
        "run_plant_v4_cmdstan_bootstrap_test",
        runner_path,
    )
    runner = importlib.util.module_from_spec(module_spec)
    assert module_spec.loader is not None
    module_spec.loader.exec_module(runner)

    calls = []

    def fake_run_checked(argv, *, cwd, log_path):
        calls.append((argv, cwd, log_path))
        (tmp_path / "bin").mkdir(exist_ok=True)
        (tmp_path / "bin" / "stanc").write_text("", encoding="utf-8")

    monkeypatch.setattr(runner, "_run_checked", fake_run_checked)
    stanc = runner._ensure_stanc(
        cmdstan_dir=tmp_path,
        make_command="make",
        log_dir=tmp_path / "logs",
    )
    assert stanc == tmp_path / "bin" / "stanc"
    assert calls[0][0] == ["make", "bin/stanc"]
    assert calls[0][1] == tmp_path
    assert calls[0][2] == tmp_path / "logs" / "stanc.install.log"


def test_runner_does_not_reinstall_existing_stanc(tmp_path, monkeypatch):
    runner_path = ROOT / "scripts" / "run_plant_v4_cmdstan.py"
    module_spec = importlib.util.spec_from_file_location(
        "run_plant_v4_cmdstan_existing_stanc_test",
        runner_path,
    )
    runner = importlib.util.module_from_spec(module_spec)
    assert module_spec.loader is not None
    module_spec.loader.exec_module(runner)

    (tmp_path / "bin").mkdir()
    stanc = tmp_path / "bin" / "stanc"
    stanc.write_text("", encoding="utf-8")

    def should_not_run(*args, **kwargs):
        raise AssertionError("existing stanc must not trigger make")

    monkeypatch.setattr(runner, "_run_checked", should_not_run)
    assert runner._ensure_stanc(
        cmdstan_dir=tmp_path,
        make_command="make",
        log_dir=tmp_path / "logs",
    ) == stanc



def test_combine_chains_requires_frozen_count_draws_unique_paths_and_version(tmp_path):
    paths = []
    for i in range(4):
        path = tmp_path / f"chain_complete_{i}.csv"
        _chain_csv(path, gamma=False, version="2.40.0")
        paths.append(path)

    out = combine_cmdstan_chains(
        paths,
        require_gamma=False,
        max_depth=15,
        expected_chains=4,
        expected_draws_per_chain=4,
        required_version="2.40.0",
    )
    assert out["n_chains"] == 4
    assert out["draws_per_chain"] == [4, 4, 4, 4]
    assert out["n_draws_total"] == 16

    with pytest.raises(ValueError, match="exactly 4 chains"):
        combine_cmdstan_chains(
            paths[:3],
            require_gamma=False,
            max_depth=15,
            expected_chains=4,
            expected_draws_per_chain=4,
            required_version="2.40.0",
        )

    with pytest.raises(ValueError, match="chain paths must be unique"):
        combine_cmdstan_chains(
            [paths[0], paths[0], paths[2], paths[3]],
            require_gamma=False,
            max_depth=15,
            expected_chains=4,
            expected_draws_per_chain=4,
            required_version="2.40.0",
        )

    with pytest.raises(ValueError, match="draw count drifted"):
        combine_cmdstan_chains(
            paths,
            require_gamma=False,
            max_depth=15,
            expected_chains=4,
            expected_draws_per_chain=5,
            required_version="2.40.0",
        )

    with pytest.raises(ValueError, match="must be 2.39.0"):
        combine_cmdstan_chains(
            paths,
            require_gamma=False,
            max_depth=15,
            expected_chains=4,
            expected_draws_per_chain=4,
            required_version="2.39.0",
        )


def test_stansummary_requires_complete_registered_parameter_set(tmp_path):
    path = tmp_path / "summary_complete.csv"
    _stansummary(path)
    out = read_stansummary_csv(
        path,
        parameter_families=("alpha", "beta"),
    )
    assert out["n_parameters"] == 15

    rows = path.read_text(encoding="utf-8").splitlines()
    missing = tmp_path / "summary_missing.csv"
    missing.write_text(
        "\n".join(
            line for line in rows
            if "alpha[1,1]" not in line
        ) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="parameter set mismatch"):
        read_stansummary_csv(
            missing,
            parameter_families=("alpha", "beta"),
        )

    duplicate = tmp_path / "summary_duplicate.csv"
    alpha_line = next(line for line in rows if "alpha[1,1]" in line)
    duplicate.write_text(
        "\n".join([*rows, alpha_line]) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="repeats registered parameter"):
        read_stansummary_csv(
            duplicate,
            parameter_families=("alpha", "beta"),
        )



def _assembly_row(row_id, universe, mode, module, timing, spatial="SAME_UNIT"):
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
        "source_basis": "synthetic",
        "claim_ceiling": "comparative_only",
    }


def _generality_ready_assembly():
    u2 = "U2_BARRETT_2002"
    u6 = "U6_POLLEN_THEFT_HARGREAVES_2009"
    return [
        _assembly_row("u2_s1", u2, "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _assembly_row("u2_s2", u2, "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _assembly_row("u2_n1", u2, "TEMPORAL_SEPARATION", "SERIAL_WITHIN_FLOWER", "SEASONALLY_ALTERNATING"),
        _assembly_row("u2_n2", u2, "SPATIAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _assembly_row("u2_n3", u2, "TEMPORAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _assembly_row("u2_d1", u2, "WITHIN_FLOWER_DIVISION_OF_LABOUR", "REPEATED_FLOWERS", "CONTEXT_DEPENDENT"),
        _assembly_row("u2_m1", u2, "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "MIXED", "BETWEEN_MODULES"),
        _assembly_row("u6_s1", u6, "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _assembly_row("u6_n1", u6, "TEMPORAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _assembly_row("u6_n2", u6, "SPATIAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _assembly_row("u6_d1", u6, "AMONG_FLOWER_MODULE_DIVISION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _assembly_row("u6_m1", u6, "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEASONALLY_ALTERNATING"),
    ]


def _load_runner(name):
    runner_path = ROOT / "scripts" / "run_plant_v4_cmdstan.py"
    module_spec = importlib.util.spec_from_file_location(name, runner_path)
    runner = importlib.util.module_from_spec(module_spec)
    assert module_spec.loader is not None
    module_spec.loader.exec_module(runner)
    return runner


def _write_prefit_bundle(path, rows):
    path.mkdir()
    assembly = path / "BALANCE_PLANT_V4_LICENSED_ASSEMBLY.csv"
    with assembly.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ASSEMBLY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    pipeline = build_v4_analysis_inputs(rows)
    readout = path / "BALANCE_PLANT_V4_ASSEMBLY_READOUT.json"
    readout.write_text(
        json.dumps(pipeline["assembly_readout"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    payloads = {
        "BALANCE_PLANT_V4_STAN_INPUT.json": pipeline["main_stan_input"],
        "BALANCE_PLANT_V4_PRIOR_SENSITIVITY_INPUT.json": (
            pipeline["prior_sensitivity_stan_input"]
        ),
    }
    if pipeline["temporal_generality_stan_input"] is not None:
        payloads["BALANCE_PLANT_V4_TEMPORAL_GENERALITY_INPUT.json"] = (
            pipeline["temporal_generality_stan_input"]
        )
        payloads[
            "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_PRIOR_SENSITIVITY_INPUT.json"
        ] = pipeline["temporal_generality_prior_sensitivity_stan_input"]

    for name, payload in payloads.items():
        (path / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    generated = {
        assembly.name: assembly,
        readout.name: readout,
        **{name: path / name for name in payloads},
    }
    receipt = {
        "schema_version": "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1",
        "analysis": "balance_plant_v4_analysis_input_bundle",
        "source_human_workspace_receipt_sha256": "a" * 64,
        "source_human_workspace_receipt": "/synthetic/human-workspace-receipt.json",
        "files_sha256": {
            name: hashlib.sha256(file.read_bytes()).hexdigest()
            for name, file in sorted(generated.items())
        },
        "temporal_generality_status": pipeline["temporal_generality_status"],
        "primary_fit_ready": True,
        "workspace_policy": "one_build_per_immutable_output_directory",
        "claim_ceiling": "prefit_input_provenance_only_no_fitted_effect",
    }
    (path / "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return pipeline


def test_runner_preflight_binds_all_wrappers_to_one_licensed_assembly(tmp_path):
    runner = _load_runner("run_plant_v4_cmdstan_input_bundle_test")
    input_dir = tmp_path / "inputs"
    _write_prefit_bundle(input_dir, _generality_ready_assembly())

    out = runner._validate_input_bundle(input_dir)
    assert out["active_jobs"] == [
        "PRIMARY",
        "PRIMARY_PRIOR_SENSITIVITY",
        "TEMPORAL_GENERALITY",
        "TEMPORAL_GENERALITY_PRIOR_SENSITIVITY",
    ]
    assert out["temporal_generality_expected"] is True
    assert len(out["wrapper_sha256"]) == 4
    assert out["assembly_sha256"]
    assert out["analysis_input_receipt_sha256"]
    assert out["source_human_workspace_receipt_sha256"] == "a" * 64


def test_runner_preflight_rejects_wrapper_from_different_assembly(tmp_path):
    runner = _load_runner("run_plant_v4_cmdstan_mixed_bundle_test")
    input_dir = tmp_path / "inputs"
    _write_prefit_bundle(input_dir, _generality_ready_assembly())

    prior_path = input_dir / "BALANCE_PLANT_V4_PRIOR_SENSITIVITY_INPUT.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    prior["stan_data"]["X"][0][0] = 1 - prior["stan_data"]["X"][0][0]
    prior_path.write_text(json.dumps(prior), encoding="utf-8")

    with pytest.raises(ValueError, match="does not match deterministic rebuild"):
        runner._validate_input_bundle(input_dir)


def test_runner_preflight_rejects_stale_generality_files_when_gate_is_closed(tmp_path):
    runner = _load_runner("run_plant_v4_cmdstan_stale_generality_test")
    ready_dir = tmp_path / "ready"
    ready_pipeline = _write_prefit_bundle(ready_dir, _generality_ready_assembly())

    blocked_rows = _generality_ready_assembly()
    next(
        row for row in blocked_rows
        if row["analysis_row_id"] == "u6_m1"
    )["conflict_timing_geometry"] = "SIMULTANEOUS"
    blocked_dir = tmp_path / "blocked"
    blocked_pipeline = _write_prefit_bundle(blocked_dir, blocked_rows)
    assert blocked_pipeline["temporal_generality_stan_input"] is None

    for name, key in (
        (
            "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_INPUT.json",
            "temporal_generality_stan_input",
        ),
        (
            "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_PRIOR_SENSITIVITY_INPUT.json",
            "temporal_generality_prior_sensitivity_stan_input",
        ),
    ):
        (blocked_dir / name).write_text(
            json.dumps(ready_pipeline[key]),
            encoding="utf-8",
        )

    with pytest.raises(ValueError, match="present even though"):
        runner._validate_input_bundle(blocked_dir)


def test_runner_refuses_existing_fit_workspace_before_any_execution(tmp_path):
    runner = _load_runner("run_plant_v4_cmdstan_immutable_workspace_test")
    input_dir = tmp_path / "inputs"
    _write_prefit_bundle(input_dir, _generality_ready_assembly())

    out_dir = tmp_path / "fit"
    out_dir.mkdir()
    sentinel = out_dir / "sentinel.txt"
    sentinel.write_text("preserve prior fit evidence", encoding="utf-8")

    with pytest.raises(ValueError, match="output directory already exists"):
        runner.run_all(
            cmdstan_dir=tmp_path / "cmdstan",
            input_dir=input_dir,
            out_dir=out_dir,
            contract_path=CONTRACT,
        )

    assert sentinel.read_text(encoding="utf-8") == "preserve prior fit evidence"



def test_runner_preflight_requires_analysis_input_receipt(tmp_path):
    runner = _load_runner("run_plant_v4_cmdstan_missing_analysis_receipt_test")
    input_dir = tmp_path / "inputs"
    _write_prefit_bundle(input_dir, _generality_ready_assembly())
    (input_dir / "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json").unlink()

    with pytest.raises(FileNotFoundError, match="required V4 input is missing"):
        runner._validate_input_bundle(input_dir)


def test_runner_preflight_rejects_analysis_receipt_hash_drift(tmp_path):
    runner = _load_runner("run_plant_v4_cmdstan_analysis_hash_drift_test")
    input_dir = tmp_path / "inputs"
    _write_prefit_bundle(input_dir, _generality_ready_assembly())

    readout = input_dir / "BALANCE_PLANT_V4_ASSEMBLY_READOUT.json"
    readout.write_bytes(readout.read_bytes() + b"\n")

    with pytest.raises(ValueError, match="analysis-input receipt SHA256 mismatch"):
        runner._validate_input_bundle(input_dir)


def test_runner_preflight_requires_source_human_workspace_receipt_hash(tmp_path):
    runner = _load_runner("run_plant_v4_cmdstan_human_receipt_hash_test")
    input_dir = tmp_path / "inputs"
    _write_prefit_bundle(input_dir, _generality_ready_assembly())

    receipt_path = input_dir / "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["source_human_workspace_receipt_sha256"] = None
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    with pytest.raises(ValueError, match="lacks source human-workspace receipt SHA256"):
        runner._validate_input_bundle(input_dir)



def _fake_run_all_boundary(monkeypatch, runner, tmp_path, *, diagnostic_status):
    assembly_path = tmp_path / "assembly.csv"
    assembly_path.write_text("synthetic\n", encoding="utf-8")
    analysis_receipt = tmp_path / "analysis_receipt.json"
    analysis_receipt.write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(
        runner,
        "_validate_input_bundle",
        lambda _input_dir: {
            "assembly": [{"synthetic": "row"}],
            "assembly_path": assembly_path,
            "assembly_sha256": hashlib.sha256(assembly_path.read_bytes()).hexdigest(),
            "active_jobs": ["PRIMARY", "PRIMARY_PRIOR_SENSITIVITY"],
            "wrapper_sha256": {
                "PRIMARY": "1" * 64,
                "PRIMARY_PRIOR_SENSITIVITY": "2" * 64,
            },
            "analysis_input_receipt_path": analysis_receipt,
            "analysis_input_receipt_sha256": hashlib.sha256(
                analysis_receipt.read_bytes()
            ).hexdigest(),
            "source_human_workspace_receipt_sha256": "3" * 64,
            "temporal_generality_expected": False,
        },
    )
    monkeypatch.setattr(runner, "_ensure_stanc", lambda **kwargs: tmp_path / "stanc")
    monkeypatch.setattr(runner, "_cmdstan_version", lambda _path: "2.40.0")
    monkeypatch.setattr(
        runner,
        "_compile_model",
        lambda **kwargs: tmp_path / "compiled-model",
    )
    monkeypatch.setattr(
        runner,
        "_ensure_stansummary",
        lambda **kwargs: tmp_path / "stansummary",
    )

    def fake_fit(*, job_id, out_dir, **kwargs):
        job_dir = out_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        receipt_path = job_dir / "FIT_RECEIPT.json"
        receipt_path.write_text(
            json.dumps({"job_id": job_id, "status": diagnostic_status}) + "\n",
            encoding="utf-8",
        )
        return {
            "receipt": {"job_id": job_id},
            "receipt_path": receipt_path,
            "draws": [],
            "diagnostics": {"status": diagnostic_status},
        }

    monkeypatch.setattr(runner, "_run_fit_job", fake_fit)
    return assembly_path


def test_runner_complete_receipt_hash_binds_job_and_postfit_outputs(tmp_path, monkeypatch):
    runner = _load_runner("run_plant_v4_cmdstan_final_receipt_success_test")
    _fake_run_all_boundary(
        monkeypatch,
        runner,
        tmp_path,
        diagnostic_status="PASS",
    )
    monkeypatch.setattr(
        runner,
        "summarize_v4_primary_postfit",
        lambda *args, **kwargs: {"analysis": "synthetic-primary"},
    )

    out_dir = tmp_path / "fit-success"
    result = runner.run_all(
        cmdstan_dir=tmp_path / "cmdstan",
        input_dir=tmp_path / "inputs",
        out_dir=out_dir,
        contract_path=CONTRACT,
    )
    assert result["execution_status"] == "COMPLETE"

    receipt_path = out_dir / "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["execution_status"] == "COMPLETE"
    assert receipt["diagnostic_failures"] == []
    assert set(receipt["job_receipt_sha256"]) == {
        "PRIMARY",
        "PRIMARY_PRIOR_SENSITIVITY",
    }
    for job_id, path in receipt["job_receipts"].items():
        assert receipt["job_receipt_sha256"][job_id] == hashlib.sha256(
            Path(path).read_bytes()
        ).hexdigest()

    assert set(receipt["postfit_outputs"]) == {"primary"}
    primary_path = Path(receipt["postfit_outputs"]["primary"])
    assert receipt["postfit_output_sha256"]["primary"] == hashlib.sha256(
        primary_path.read_bytes()
    ).hexdigest()


def test_runner_diagnostic_failure_receipt_has_no_postfit_outputs(tmp_path, monkeypatch):
    runner = _load_runner("run_plant_v4_cmdstan_final_receipt_failure_test")
    _fake_run_all_boundary(
        monkeypatch,
        runner,
        tmp_path,
        diagnostic_status="FAIL",
    )

    def should_not_summarize(*args, **kwargs):
        raise AssertionError("postfit summary must not run after diagnostic failure")

    monkeypatch.setattr(runner, "summarize_v4_primary_postfit", should_not_summarize)

    out_dir = tmp_path / "fit-fail"
    with pytest.raises(RuntimeError, match="diagnostics failed"):
        runner.run_all(
            cmdstan_dir=tmp_path / "cmdstan",
            input_dir=tmp_path / "inputs",
            out_dir=out_dir,
            contract_path=CONTRACT,
        )

    receipt = json.loads(
        (out_dir / "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1.json")
        .read_text(encoding="utf-8")
    )
    assert receipt["execution_status"] == "DIAGNOSTIC_FAIL"
    assert receipt["postfit_decision_allowed"] is False
    assert receipt["postfit_outputs"] == {}
    assert receipt["postfit_output_sha256"] == {}
    assert set(receipt["job_receipt_sha256"]) == {
        "PRIMARY",
        "PRIMARY_PRIOR_SENSITIVITY",
    }

import csv
import hashlib
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest

from balance_domain.plant_analysis_pipeline import build_v4_analysis_inputs
from balance_domain.plant_model_assembly import FIELDS as ASSEMBLY_FIELDS
from balance_domain.plant_v4_cmdstan import (
    combine_cmdstan_chains,
    evaluate_diagnostics,
    read_stansummary_csv,
)
from balance_domain.plant_v4_estimands import summarize_v4_primary_postfit


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_plant_v4_reactivation.py"
CONTRACT = ROOT / "data" / "BALANCE_PLANT_V4_FIT_EXECUTION_CONTRACT_V1.json"


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "evaluate_plant_v4_reactivation_fit_evidence",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _row(row_id, universe, mode, module, timing, spatial="SAME_UNIT"):
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


def _primary_only_rows():
    u2 = "U2_BARRETT_2002"
    u6 = "U6_POLLEN_THEFT_HARGREAVES_2009"
    rows = [
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
        _row("u6_m1", u6, "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
    ]
    pipeline = build_v4_analysis_inputs(rows)
    assert pipeline["main_fit_ready"] is True
    assert pipeline["temporal_generality_status"] == "NOT_READY"
    return rows, pipeline


def _chain_csv(path: Path, *, chain_id: int, sampling: dict):
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
    lines = [
        "# stan_version_major = 2",
        "# stan_version_minor = 40",
        "# stan_version_patch = 0",
        "# method = sample (Default)",
        f"# num_samples = {sampling['num_samples']}",
        f"# num_warmup = {sampling['num_warmup']}",
        f"# save_warmup = {'true' if sampling['save_warmup'] else 'false'} (Default)",
        f"# thin = {sampling['thin']} (Default)",
        f"# delta = {sampling['adapt_delta']} (Default)",
        "# algorithm = hmc (Default)",
        "# engine = nuts (Default)",
        f"# max_depth = {sampling['max_depth']} (Default)",
        f"# metric = {sampling['metric']} (Default)",
        "# num_chains = 1 (Default)",
        f"# id = {chain_id} (Default)",
        f"# seed = {sampling['seed']}",
        f"# refresh = {sampling['refresh']}",
        f"# sig_figs = {sampling['output_sig_figs']}",
        ",".join(fields),
    ]
    energies = [1.0, 2.0, 1.2, 2.1]
    for i, energy in enumerate(energies):
        row = {
            "lp__": -1.0,
            "accept_stat__": 0.99,
            "stepsize__": 0.1,
            "treedepth__": 7,
            "n_leapfrog__": 15,
            "divergent__": 0,
            "energy__": energy,
        }
        for u in range(1, 3):
            for k in range(1, 4):
                row[f"alpha.{u}.{k}"] = 0.05 * u * k + 0.001 * i
        for p in range(1, 4):
            for k in range(1, 4):
                row[f"beta.{p}.{k}"] = 0.02 * p * k + 0.001 * i
        lines.append(",".join(str(row[field]) for field in fields))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _stansummary(path: Path):
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
                "ESS_bulk": 1000,
                "ESS_tail": 900,
                "ESS_bulk/s": 100,
                "R_hat": 1.0,
            })


def _build_fit_evidence(tmp_path):
    rows, pipeline = _primary_only_rows()
    input_dir = tmp_path / "inputs"
    fit_dir = tmp_path / "fit"
    input_dir.mkdir()
    fit_dir.mkdir()

    assembly_path = input_dir / "BALANCE_PLANT_V4_LICENSED_ASSEMBLY.csv"
    with assembly_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ASSEMBLY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    readout_path = input_dir / "BALANCE_PLANT_V4_ASSEMBLY_READOUT.json"
    readout_path.write_text(
        json.dumps(pipeline["assembly_readout"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    wrappers = {
        "PRIMARY": (
            "BALANCE_PLANT_V4_STAN_INPUT.json",
            pipeline["main_stan_input"],
        ),
        "PRIMARY_PRIOR_SENSITIVITY": (
            "BALANCE_PLANT_V4_PRIOR_SENSITIVITY_INPUT.json",
            pipeline["prior_sensitivity_stan_input"],
        ),
    }
    for _job_id, (name, payload) in wrappers.items():
        (input_dir / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    analysis_receipt = {
        "files_sha256": {
            readout_path.name: _sha(readout_path),
            **{
                name: _sha(input_dir / name)
                for name, _payload in wrappers.values()
            },
        }
    }

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    smoke = deepcopy(contract)
    smoke["sampling"] = {
        **contract["sampling"],
        "num_warmup": 0,
        "num_samples": 4,
    }
    sampling = smoke["sampling"]

    build_dir = fit_dir / "_cmdstan_build"
    build_dir.mkdir()
    model_source = ROOT / contract["primary_model"]
    copied_model = build_dir / model_source.name
    copied_model.write_bytes(model_source.read_bytes())
    executable = build_dir / model_source.stem
    executable.write_bytes(b"synthetic compiled model")

    job_paths = {}
    job_hashes = {}
    wrapper_hashes = {}
    all_draws = {}
    for job_id, (wrapper_name, _payload) in wrappers.items():
        job_dir = fit_dir / job_id
        job_dir.mkdir()
        wrapper_path = input_dir / wrapper_name
        raw_data = job_dir / "stan_data.json"
        wrapper = json.loads(wrapper_path.read_text(encoding="utf-8"))
        raw_data.write_text(
            json.dumps(wrapper["stan_data"], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        chain_paths = []
        for chain_id in range(1, 5):
            path = job_dir / f"chain_{chain_id}.csv"
            _chain_csv(path, chain_id=chain_id, sampling=sampling)
            chain_paths.append(path)
        summary_path = job_dir / "stansummary.csv"
        _stansummary(summary_path)

        combined = combine_cmdstan_chains(
            chain_paths,
            require_gamma=False,
            max_depth=sampling["max_depth"],
            expected_chains=sampling["chains"],
            expected_draws_per_chain=sampling["num_samples"],
            required_version="2.40.0",
            expected_sampling=sampling,
        )
        summary = read_stansummary_csv(
            summary_path,
            parameter_families=("alpha", "beta"),
        )
        diagnostics = evaluate_diagnostics(
            combined,
            summary,
            contract=smoke,
        )
        assert diagnostics["status"] == "PASS"
        all_draws[job_id] = combined["draws"]

        receipt = {
            "schema_version": "BALANCE_PLANT_V4_FIT_JOB_RECEIPT_V1",
            "job_id": job_id,
            "model_source": contract["primary_model"],
            "model_source_sha256": _sha(model_source),
            "model_executable_sha256": _sha(executable),
            "input_wrapper": str(wrapper_path),
            "input_wrapper_sha256": _sha(wrapper_path),
            "materialized_stan_data_sha256": _sha(raw_data),
            "cmdstan_version": combined["stan_version"],
            "chain_ids": combined["chain_ids"],
            "chain_execution_metadata": combined["execution_metadata"],
            "n_chains": combined["n_chains"],
            "draws_per_chain": combined["draws_per_chain"],
            "n_draws_total": combined["n_draws_total"],
            "chain_csv_sha256": {
                path.name: _sha(path) for path in chain_paths
            },
            "commands": {},
            "stansummary_command": [],
            "stansummary_sha256": _sha(summary_path),
            "diagnostics": diagnostics,
            "claim_ceiling": "fit_execution_receipt_only_no_effect_interpretation",
        }
        receipt_path = job_dir / "FIT_RECEIPT.json"
        receipt_path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        job_paths[job_id] = str(receipt_path)
        job_hashes[job_id] = _sha(receipt_path)
        wrapper_hashes[job_id] = _sha(wrapper_path)

    primary_summary = summarize_v4_primary_postfit(
        rows,
        primary_draws=all_draws["PRIMARY"],
        sensitivity_draws=all_draws["PRIMARY_PRIOR_SENSITIVITY"],
    )
    fit_receipt = {
        "schema_version": "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1",
        "contract_sha256": _sha(CONTRACT),
        "required_cmdstan_version": "2.40.0",
        "preflight_cmdstan_version": "2.40.0",
        "active_jobs": ["PRIMARY", "PRIMARY_PRIOR_SENSITIVITY"],
        "input_wrapper_sha256": wrapper_hashes,
        "job_receipts": job_paths,
        "job_receipt_sha256": job_hashes,
        "diagnostic_failures": [],
        "postfit_decision_allowed": True,
        "execution_status": "COMPLETE",
        "automatic_retuning_permitted": False,
    }
    return input_dir, fit_dir, analysis_receipt, fit_receipt, smoke, primary_summary


def test_reactivation_reverifies_job_chain_and_recomputes_postfit(tmp_path, monkeypatch):
    module = _load_script()
    input_dir, fit_dir, analysis, fit, smoke, expected = _build_fit_evidence(tmp_path)
    monkeypatch.setattr(module, "load_fit_execution_contract", lambda _path: smoke)

    out = module._verify_fit_evidence_chain(
        input_dir=input_dir,
        fit_dir=fit_dir,
        fit_receipt=fit,
        analysis_receipt=analysis,
    )
    assert out["primary_summary"] == expected
    assert out["temporal_generality_summary"] is None
    assert set(out["job_receipt_sha256"]) == {
        "PRIMARY",
        "PRIMARY_PRIOR_SENSITIVITY",
    }
    assert all(len(job_hashes) == 4 for job_hashes in out["chain_csv_sha256"].values())


def test_reactivation_fit_evidence_rejects_chain_hash_drift(tmp_path, monkeypatch):
    module = _load_script()
    input_dir, fit_dir, analysis, fit, smoke, _expected = _build_fit_evidence(tmp_path)
    monkeypatch.setattr(module, "load_fit_execution_contract", lambda _path: smoke)

    chain = fit_dir / "PRIMARY" / "chain_1.csv"
    chain.write_bytes(chain.read_bytes() + b"\n")

    with pytest.raises(ValueError, match="chain_1.csv SHA256 mismatch"):
        module._verify_fit_evidence_chain(
            input_dir=input_dir,
            fit_dir=fit_dir,
            fit_receipt=fit,
            analysis_receipt=analysis,
        )


def test_reactivation_fit_evidence_rejects_model_receipt_drift(tmp_path, monkeypatch):
    module = _load_script()
    input_dir, fit_dir, analysis, fit, smoke, _expected = _build_fit_evidence(tmp_path)
    monkeypatch.setattr(module, "load_fit_execution_contract", lambda _path: smoke)

    job_path = fit_dir / "PRIMARY" / "FIT_RECEIPT.json"
    job = json.loads(job_path.read_text(encoding="utf-8"))
    job["model_source_sha256"] = "0" * 64
    job_path.write_text(
        json.dumps(job, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    fit["job_receipt_sha256"]["PRIMARY"] = _sha(job_path)

    with pytest.raises(ValueError, match="model source SHA256 mismatch"):
        module._verify_fit_evidence_chain(
            input_dir=input_dir,
            fit_dir=fit_dir,
            fit_receipt=fit,
            analysis_receipt=analysis,
        )



def test_reactivation_fit_evidence_rejects_stale_inactive_job_directory(
    tmp_path,
    monkeypatch,
):
    module = _load_script()
    input_dir, fit_dir, analysis, fit, smoke, _expected = _build_fit_evidence(tmp_path)
    monkeypatch.setattr(module, "load_fit_execution_contract", lambda _path: smoke)

    (fit_dir / "TEMPORAL_GENERALITY").mkdir()

    with pytest.raises(ValueError, match="stale or missing job directory"):
        module._verify_fit_evidence_chain(
            input_dir=input_dir,
            fit_dir=fit_dir,
            fit_receipt=fit,
            analysis_receipt=analysis,
        )

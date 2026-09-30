import csv
import json
import math
from pathlib import Path

import pytest

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

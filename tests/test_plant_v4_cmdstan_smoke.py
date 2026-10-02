import importlib.util
from pathlib import Path

from balance_domain.plant_v4_cmdstan import cmdstan_sample_argv


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "smoke_test_plant_v4_cmdstan.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("smoke_test_plant_v4_cmdstan", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_cmdstan_smoke_data_matches_both_frozen_model_schemas(tmp_path):
    module = _load_module()
    primary = module.smoke_data(generality=False)
    generality = module.smoke_data(generality=True)

    assert set(primary) == {
        "N",
        "K",
        "U",
        "P",
        "X",
        "y",
        "universe",
        "slope_prior_sd",
        "intercept_prior_sd",
    }
    assert set(generality) == set(primary) | {
        "u6_ordered",
        "interaction_prior_sd",
    }
    assert primary["N"] == 12
    assert len(primary["X"]) == primary["N"]
    assert len(primary["y"]) == primary["N"]
    assert len(primary["universe"]) == primary["N"]
    assert generality["u6_ordered"] == [
        int(u == 2 and x[1] == 1)
        for u, x in zip(generality["universe"], generality["X"])
    ]
    assert sum(generality["u6_ordered"]) == 3


def test_cmdstan_smoke_uses_short_nonproduction_sampling_contract():
    module = _load_module()
    sampling = module.SMOKE_SAMPLING
    assert sampling["chains"] == 1
    assert sampling["num_warmup"] == 25
    assert sampling["num_samples"] == 25
    assert sampling["seed"] == 20261001

    argv = cmdstan_sample_argv(
        Path("/tmp/model"),
        Path("/tmp/data.json"),
        Path("/tmp/out.csv"),
        chain_id=1,
        contract={"sampling": sampling},
    )
    assert "num_warmup=25" in argv
    assert "num_samples=25" in argv
    assert "seed=20261001" in argv
    assert "id=1" in argv


def test_cmdstan_smoke_is_explicitly_not_the_production_fit():
    module = _load_module()
    assert module.SMOKE_SAMPLING["adapt_delta"] == 0.8
    assert module.SMOKE_SAMPLING["max_depth"] == 10
    assert module.SMOKE_SAMPLING["output_sig_figs"] == 12



def _write_fake_cmdstan_csv(path, *, require_gamma):
    fields = [
        "lp__",
        "accept_stat__",
        "stepsize__",
        "treedepth__",
        "n_leapfrog__",
        "divergent__",
        "energy__",
    ]
    fields += [
        f"alpha.{u}.{k}"
        for k in range(1, 4)
        for u in range(1, 3)
    ]
    fields += [
        f"beta.{p}.{k}"
        for k in range(1, 4)
        for p in range(1, 4)
    ]
    if require_gamma:
        fields += [f"gamma_u6_ordered.{k}" for k in range(1, 4)]
    lines = [
        "# stan_version_major = 2",
        "# stan_version_minor = 40",
        "# stan_version_patch = 0",
        ",".join(fields),
    ]
    for i in range(25):
        row = []
        for field in fields:
            if field == "treedepth__":
                row.append("5")
            elif field == "divergent__":
                row.append("0")
            elif field == "energy__":
                row.append(str(10.0 + i * 0.1))
            else:
                row.append("0.1")
        lines.append(",".join(row))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_cmdstan_smoke_routes_realistic_csv_through_production_parser(tmp_path, monkeypatch):
    module = _load_module()

    executable = tmp_path / "fake-model"
    executable.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        module.runner,
        "_compile_model",
        lambda **kwargs: executable,
    )

    def fake_run_checked(argv, *, cwd, log_path):
        output_tokens = [token for token in argv if token.startswith("file=")]
        output = Path(output_tokens[-1].split("=", 1)[1])
        require_gamma = "generality" in str(output)
        _write_fake_cmdstan_csv(output, require_gamma=require_gamma)
        log_path.write_text("synthetic smoke\n", encoding="utf-8")

    monkeypatch.setattr(module.runner, "_run_checked", fake_run_checked)

    primary = module._run_model(
        name="primary",
        model=module.PRIMARY_MODEL,
        data=module.smoke_data(generality=False),
        cmdstan_dir=tmp_path / "cmdstan",
        work_dir=tmp_path / "work-primary",
        make_command="make",
        require_gamma=False,
    )
    generality = module._run_model(
        name="generality",
        model=module.GENERALITY_MODEL,
        data=module.smoke_data(generality=True),
        cmdstan_dir=tmp_path / "cmdstan",
        work_dir=tmp_path / "work-generality",
        make_command="make",
        require_gamma=True,
    )

    for out in (primary, generality):
        parsed = out["production_parser"]
        assert parsed["n_draws"] == 25
        assert parsed["stan_version"] == "2.40.0"
        assert parsed["divergences"] == 0
        assert parsed["max_treedepth_observed"] == 5
        assert parsed["ebfmi"] > 0
    assert primary["gamma_present"] is False
    assert generality["gamma_present"] is True

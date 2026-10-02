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

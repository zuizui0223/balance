import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "smoke_test_plant_v4_fit_job.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "smoke_test_plant_v4_fit_job",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_fit_job_smoke_is_four_chain_short_engine_test():
    module = _load_module()
    sampling = module.SMOKE_SAMPLING
    assert sampling == {
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
    assert module.SMOKE_CONTRACT["required_cmdstan_version"] == "2.40.0"
    diagnostics = module.SMOKE_DIAGNOSTICS
    assert diagnostics["automatic_retuning_allowed"] is False
    assert diagnostics["min_ebfmi"] == 0.0
    assert diagnostics["max_parameter_rhat"] == 100.0
    assert diagnostics["min_parameter_ess_bulk"] == 0.0
    assert diagnostics["min_parameter_ess_tail"] == 0.0


def test_fit_job_smoke_orchestrates_production_job_for_both_models(
    tmp_path,
    monkeypatch,
):
    module = _load_module()
    cmdstan_dir = tmp_path / "cmdstan"
    cmdstan_dir.mkdir()

    monkeypatch.setattr(module.runner, "_ensure_stanc", lambda **kwargs: None)
    monkeypatch.setattr(module.runner, "_cmdstan_version", lambda path: "2.40.0")

    primary_exe = tmp_path / "primary-exe"
    generality_exe = tmp_path / "generality-exe"
    primary_exe.write_text("", encoding="utf-8")
    generality_exe.write_text("", encoding="utf-8")

    def fake_compile_model(*, stan_path, **kwargs):
        if stan_path == module.PRIMARY_MODEL:
            return primary_exe
        if stan_path == module.GENERALITY_MODEL:
            return generality_exe
        raise AssertionError(stan_path)

    monkeypatch.setattr(module.runner, "_compile_model", fake_compile_model)
    summary = tmp_path / "stansummary"
    summary.write_text("", encoding="utf-8")
    monkeypatch.setattr(module.runner, "_ensure_stansummary", lambda **kwargs: summary)

    calls = []

    def fake_run_fit_job(**kwargs):
        calls.append(kwargs)
        job_dir = kwargs["out_dir"] / kwargs["job_id"]
        job_dir.mkdir(parents=True, exist_ok=True)
        receipt_path = job_dir / "FIT_RECEIPT.json"
        require_gamma = kwargs["spec"]["require_gamma"]
        receipt = {
            "n_chains": 4,
            "draws_per_chain": [25, 25, 25, 25],
            "n_draws_total": 100,
            "cmdstan_version": "2.40.0",
            "stansummary_sha256": "a" * 64 if not require_gamma else "b" * 64,
            "diagnostics": {
                "observed": {
                    "divergences": 0,
                    "treedepth_hits": 0,
                    "min_ebfmi": 0.5,
                    "max_parameter_rhat": 1.05,
                    "min_parameter_ess_bulk": 20,
                    "min_parameter_ess_tail": 20,
                }
            },
        }
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        return {
            "receipt": receipt,
            "receipt_path": receipt_path,
            "draws": [],
            "diagnostics": {"status": "PASS"},
        }

    monkeypatch.setattr(module.runner, "_run_fit_job", fake_run_fit_job)

    out = module.run_smoke(
        cmdstan_dir=cmdstan_dir,
        work_dir=tmp_path / "work",
    )

    assert [call["job_id"] for call in calls] == [
        "PRIMARY_SMOKE",
        "GENERALITY_SMOKE",
    ]
    assert calls[0]["spec"]["require_gamma"] is False
    assert calls[1]["spec"]["require_gamma"] is True
    assert calls[0]["contract"] == module.SMOKE_CONTRACT
    assert calls[1]["contract"] == module.SMOKE_CONTRACT

    for call in calls:
        wrapper = json.loads(call["wrapper_path"].read_text(encoding="utf-8"))
        assert set(wrapper) == {"stan_data", "metadata"}
        assert wrapper["metadata"]["claim_ceiling"] == (
            "engine_parser_smoke_only_not_production_fit"
        )

    assert out["primary"]["n_draws_total"] == 100
    assert out["generality"]["n_draws_total"] == 100
    assert out["primary"]["stansummary_sha256"] == "a" * 64
    assert out["generality"]["stansummary_sha256"] == "b" * 64
    assert out["claim_ceiling"] == (
        "engine_stansummary_parser_smoke_only_not_production_fit_or_diagnostics"
    )

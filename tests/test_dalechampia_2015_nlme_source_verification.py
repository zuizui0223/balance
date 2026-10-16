"""Verified public-Dryad R nlme readout; no original seed data in these fixtures."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/DALECHAMPIA_2015_PUBLISHED_NLME_REPLAY_CONTRACT_V1.json"
OBSERVED = ROOT / "data/DALECHAMPIA_2015_PUBLISHED_NLME_REPLAY_VERIFIED_V1.json"


def test_original_R_and_independent_python_agree_on_six_modern_model_aics():
    source = json.loads(CONTRACT.read_text(encoding="utf-8"))
    real = json.loads(OBSERVED.read_text(encoding="utf-8"))
    assert real["status"] == "SIX_MODELS_SOURCE_REPLAYED_BUT_PUBLISHED_AIC_DISCREPANCY_HOLD"
    assert len(real["six_source_candidate_models"]) == 6
    assert all(abs(x["delta"]) > 140 for x in real["six_source_candidate_models"])
    for x in real["six_source_candidate_models"]:
        r = x["replay_aic"]
        py = source["independent_python_check_before_R"]["ml_aic"][x["model"]]
        assert r == pytest.approx(py, abs=0.001)
        assert r - x["original_aic"] == pytest.approx(x["delta"], abs=0.000003)


def test_source_AIC_discrepancy_is_not_a_biological_effect_claim():
    real = json.loads(OBSERVED.read_text(encoding="utf-8"))
    lim = real["interpretation_limits"]
    assert lim["six_source_table2_aic_matches_within_one_unit"] is False
    assert lim["python_R_interimplementation_agreement"] is True
    assert lim["source_publication_error_proven"] is False
    assert lim["source_original_R_script_recovered"] is False
    assert lim["common_net_fitness_and_structural_BALANCE_identified"] is False
    assert lim["new_independent_biological_cluster"] is False
    assert real["source_artifact"]["raw_n_seed_rows_used"] == 1103
    assert real["source_artifact"]["raw_n_mothers"] == 36


def test_source_relative_varident_improvement_is_reproduced_without_absolute_AIC_match():
    real = json.loads(OBSERVED.read_text(encoding="utf-8"))
    v = real["residual_variance_comparison"]
    assert v["source_improvement"] == pytest.approx(-18.3)
    assert v["replay_improvement"] == pytest.approx(-20.811815)
    assert v["replay_varident_aic"] == pytest.approx(6131.600024)
    assert v["replay_homoscedastic_aic"] == pytest.approx(6152.411839)


def test_exact_source_fit_reports_historical_mismatch_not_manufactured_accuracy():
    real = json.loads(OBSERVED.read_text(encoding="utf-8"))
    src = real["source_artifact"]
    assert len(src["archive_generated_readout_sha256"]) == 64
    assert src["artifact_id"] == 12054043845
    assert real["source_runners"][0].startswith("R nlme")
    terms = {v["term"]: v for v in real["primary_reml_fixed_effects"]}
    assert terms["treatcodebag"]["replay"] == pytest.approx(-1.841252)
    assert terms["treatcodebag"]["replay_se"] == pytest.approx(0.318239)
    assert terms["ped"]["replay"] == pytest.approx(14.228079)
    assert terms["treatcodecutcont"]["original"] == pytest.approx(0.29)

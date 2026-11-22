"""Static contract guards for the genuine-source R colony/bee robustness audit.

The live R reanalysis is separately executed by GitHub Actions; these tests
only prevent accidental changes to the locked design or evidentiary scope.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R_SCRIPT = ROOT / "scripts" / "check_wilkins_2022_bee_level_robustness.R"
WORKFLOW = ROOT / ".github" / "workflows" / "wilkins-2022-architecture-reanalysis.yml"


def test_guardrails_check_original_publisher_bytes_and_single_bee_grain():
    text = R_SCRIPT.read_text(encoding="utf-8")
    assert "0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62" in text
    assert 'stopifnot(nrow(raw) == 60L' in text
    assert 'stopifnot(nrow(d) == 59L' in text
    assert '!anyDuplicated(raw$BeeID)' in text
    assert 'd$log_body_vs_basket <- log(d$BodyPollen / d$CorbiculaPollen)' in text
    assert 'n_colonies=3L' in text


def test_both_fixed_full_and_reduced_models_have_one_observation_per_bee():
    script = R_SCRIPT.read_text(encoding="utf-8")
    assert 'full_three_way = log_body_vs_basket ~ Treatment * width_centered *' in script
    assert 'reduced_two_way = log_body_vs_basket ~ Treatment * width_centered +' in script
    assert 'key <- "TreatmentSham:width_centered"' in script
    assert 'single_fit(d, specs[[label]], label)' in script
    assert 'single_fit(d[d$ColonyID != colony, , drop=FALSE]' in script
    assert 'single_fit(d[-index, , drop=FALSE]' in script
    assert 'all(full$n_bees == 59L)' in script
    assert 'nrow(bee_deleted)==118L' in script


def test_hc3_reports_hierarchy_without_claiming_colony_robust_p_values():
    script = R_SCRIPT.read_text(encoding="utf-8")
    assert 'h <- hatvalues(fit)' in script
    assert 'crossprod(X * as.numeric(e/(1-h)))' in script
    assert 'no_colony_robust_p_value=TRUE' in script
    assert 'POSTOPEN_BEE_LEVEL_SENSITIVITY_NOT_CONFIRMATORY' in script
    assert 'no_genetic_paternity=TRUE' in script
    assert 'n_colony_deletions_preserving_sign' in script
    assert 'n_bee_deletions_preserving_sign' in script


def test_workflow_runs_real_source_replay_and_bee_robustness_then_artifacts():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    original = workflow.index("Rscript scripts/replay_wilkins_2022_architecture.R")
    sensitivity = workflow.index(
        "Rscript scripts/check_wilkins_2022_bee_level_robustness.R"
    )
    artifact = workflow.index("uses: actions/upload-artifact@v4")
    assert 0 < original < sensitivity < artifact

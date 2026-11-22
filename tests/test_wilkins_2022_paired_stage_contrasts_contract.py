"""Regression guards for explicit matched bee pollen-stage contrast audit.

The numerical fit is executed in the source-authenticated R workflow.
These guards protect scientific scope and source reproducibility only.
"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"check_wilkins_2022_paired_stage_contrasts.R"
WORKFLOW=ROOT/".github"/"workflows"/"wilkins-2022-architecture-reanalysis.yml"


def test_same_original_source_and_59_bee_pairs():
    s=SCRIPT.read_text(encoding="utf-8")
    assert "0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62" in s
    assert "stopifnot(nrow(dat) == 60L, !anyDuplicated(dat$BeeID)" in s
    assert "stopifnot(nrow(d)==59L" in s
    assert 'd$body_basket <- log(d$BodyPollen/d$CorbiculaPollen)' in s
    assert 'd$stigma_body <- log(d$StigmaPollen/d$BodyPollen)' in s
    assert 'd$stigma_basket <- log(d$StigmaPollen/d$CorbiculaPollen)' in s
    assert "d$body_basket+d$stigma_body-d$stigma_basket" in s


def test_cross_endpoint_variance_preserves_within_bee_covariance():
    s=SCRIPT.read_text(encoding="utf-8")
    assert 'responses <- cbind(body_basket=d$body_basket,stigma_body=d$stigma_body)' in s
    assert "scores <- residual*bee_multiplier" in s
    assert "V <- crossprod(scores)" in s
    assert "chol(V)" in s
    assert 'stigma_vs_basket=c(1,1)' in s
    assert 'difference_body_vs_basket_minus_stigma_vs_basket=c(0,-1)' in s
    assert "statistic <- drop(t(b)%*%solve(V,b))" in s


def test_only_two_fixed_covariate_designs_and_no_fitness_claims():
    s=SCRIPT.read_text(encoding="utf-8")
    assert "with_postvisit_time = ~ Treatment*width_centered+time_centered+ColonyID" in s
    assert "without_postvisit_time = ~ Treatment*width_centered+ColonyID" in s
    assert 'abs(body$beta_free_minus_joined_headwidth_per_mm-3.17546609)>0.002' in s
    assert 'abs(stigma_body$beta_free_minus_joined_headwidth_per_mm+2.78571840)>0.002' in s
    assert "no_measured_male_genetic_paternity=TRUE" in s
    assert "exploratory_postopen=TRUE" in s
    assert "no_colony_robust_p_values=TRUE" in s


def test_source_replay_runs_before_paired_stage_and_stores_metadata():
    w=WORKFLOW.read_text(encoding="utf-8")
    original=w.index("Rscript scripts/replay_wilkins_2022_architecture.R")
    after=w.index("Rscript scripts/check_wilkins_2022_paired_stage_contrasts.R")
    artifact=w.index("uses: actions/upload-artifact@v4")
    assert original<after<artifact
    assert "paired_stage_effect_contrasts.csv" in SCRIPT.read_text(encoding="utf-8")

"""Contract checks for original Wilkins 2022 colony and stigma-stage audit.

The real statistical models run on the hash-checked original CSV via CI.
This test verifies the analysis contract, not any imagined field effect.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "scripts" / "check_wilkins_2022_colony_and_stigma_stages.R"
WORKFLOW = ROOT / ".github" / "workflows" / "wilkins-2022-architecture-reanalysis.yml"


def test_source_identity_observation_grain_and_columns_are_locked():
    text = ANALYSIS.read_text(encoding="utf-8")
    assert "0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62" in text
    assert "stopifnot(nrow(raw)==60L, !anyDuplicated(raw$BeeID)" in text
    assert "stopifnot(nrow(d)==59L" in text
    assert 'c("Blue","Orange","Red")' in text
    assert 'c("Cone","Sham")' in text
    assert 'all(raw$PollinatingPollen==raw$BodyPollen+raw$StigmaPollen)' in text


def test_three_source_stage_endpoints_are_separate_from_fitness():
    text = ANALYSIS.read_text(encoding="utf-8")
    assert 'd$log_body_basket <- log(d$BodyPollen/d$CorbiculaPollen)' in text
    assert 'd$log_stigma_body <- log(d$StigmaPollen/d$BodyPollen)' in text
    assert 'd$log_stigma_count <- log(d$StigmaPollen)' in text
    assert 'responses <- c("log_body_basket","log_stigma_body","log_stigma_count")' in text
    assert 'for (adjust in c(TRUE,FALSE))' in text
    assert 'Rscript scripts/check_wilkins_2022_colony_and_stigma_stages.R' in WORKFLOW.read_text(encoding="utf-8")


def test_fixed_adjustment_and_source_evidence_ceiling():
    text = ANALYSIS.read_text(encoding="utf-8")
    assert '"Treatment*width_centered + time_centered + ColonyID"' in text
    assert '"Treatment*width_centered + ColonyID"' in text
    assert 'reference_width <- mean(d$HeadWidth)' in text
    assert 'reference_time <- mean(d$VisitTime)' in text
    assert 'abs(replayed$free_minus_joined_size_beta_per_mm - 3.17546609)>0.002' in text
    assert 'not_V4_architecture_adjudication=TRUE' in text
    assert 'treatment_not_assured_random=TRUE' in text
    assert 'source_plant_identity_available=FALSE' in text


def test_colony_models_are_not_deduced_from_leave_one_colony_out():
    text = ANALYSIS.read_text(encoding="utf-8")
    assert 'for (colony in levels(d$ColonyID))' in text
    assert 'n_joined < 4L || n_free < 4L' in text
    assert 'log_body_basket ~ Treatment*width_centered + time_centered' in text
    assert 'observed_bees_in_overlap' in text
    assert 'valid_population_colony_inference=FALSE' in text
    assert 'nrow(within)==3L' in text
    assert 'pollen_stage_bee_hc3.csv' in text
    assert 'colony_specific_size_slopes.csv' in text

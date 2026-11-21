# Wilkins 2022 original-data reanalysis implementation plan

> **For agentic workers:** execute the assigned file ownership tasks and review their outputs before integration. Steps use checkboxes for the verification record.

**Goal:** authenticate the public 60-bee dataset, reproduce the published models, and determine how separating terminal body pollen from deposited stigma pollen changes the architecture-by-size result.

**Architecture:** a standard-library Python audit verifies source bytes, row identities, missingness and arithmetic before an R replay runs the source formulas. Published-composite and body-only sensitivity outcomes are both retained. The R run exports model diagnostics, coefficients, Type II tests and explicit conditional contrasts; a report interprets their biological scope.

**Tech stack:** Python >=3.10, pytest; R, glmmTMB, car, jsonlite on GitHub Actions. No new Python analysis dependency is required.

**Spec:** this plan's scientific contract below implements the ongoing BALANCE instruction to advance original empirical biology while preserving the frozen U2/U6/V4 sheets.

## Scientific contract fixed before fitting

- Source DOI: 10.1007/s00442-022-05246-0. Publisher supplement CSV SHA-256: `0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62` (5292 bytes). Original R SHA-256: `b89d1a1cea198bed16284c55fc941c5c217ca0501de4e530165cd3839a0ea16c` (29899 bytes).
- Unit: one bee/trial, four pooled donor/recipient flowers. Source records are 60 basket-collecting bees out of 67 recruited, across three colonies. Architecture assignment alternated; size was observed. Do not call assignment randomized or infer the seven excluded bees' outcomes.
- `BodyPollen = HeadPollen + ThoraxPollen + AbdomenPollen`; `PollinatingPollen = BodyPollen + StigmaPollen`; `TotalPollen = PollinatingPollen + CorbiculaPollen`. Verify these identities in every row.
- Replay the five archived models: Gaussian log remaining anther pollen; Gaussian log basket pollen; Gaussian log composite pollinating pollen; binomial composite versus basket counts with a bee-level random effect; Gaussian log stigma pollen including terminal body load. Preserve each formula, factor reference, ML and Type II test convention. Report convergence and positive-definite Hessian for every fit.
- Fit exactly two endpoint-definition sensitivities using the same respective predictors/random effects: replace the composite log response with log body-only pollen; replace the composite binomial numerator with body-only pollen and denominator with body plus basket pollen. No search across link functions, covariates or cutoffs.
- Head width and visit time are continuous. Do not dichotomize bees by a selected threshold. Treat time and terminal pollen as potentially post-treatment variables; all adjusted contrasts are conditional, not total causal effects.
- Report mean per-bee body-only and composite proportions separately. Use no artificial per-grain replication in interpretation and no genetic-paternity, seed-fitness or net structural-cost claims.
- Raw source files are fetched from the publisher and hash-checked; repository deliverables contain provenance, reproducible code and derived results rather than copies of the full article or author code.

## Task 1 — authenticated row audit

**Files:** `balance_domain/solanum_bee_architecture.py`, `scripts/audit_solanum_bee_architecture.py`, `tests/test_solanum_bee_architecture.py`, `data/BALANCE_WILKINS_2022_SOURCE_V1.json`.

**Interface:** CLI takes `--source-dir PATH`, optional `--download`, and `--out PATH`; downloads only the exact pinned CSV/R URLs when requested. Its receipt records hashes and sizes, row counts, endpoint-specific missingness, every-row identity checks, means/SE and support ranges. Export no p-values from this layer.

- [ ] Write tests that reject changed bytes even under the official filename, duplicated bee IDs, broken component sums and invalid counts; preserve allowed missing anther/head-width data and correct per-endpoint denominators.
- [ ] Implement the audit and fetch wrapper; run focused tests.
- [ ] Run against the authenticated source and verify 60 rows, 28 free/32 joined, three missing anther counts, one missing head width; reproduce source Table 1 means.

## Task 2 — source replay and fixed endpoint sensitivity

**Files:** `scripts/replay_wilkins_2022_architecture.R`, `.github/workflows/wilkins-2022-architecture-reanalysis.yml`.

**Interface:** R receives the verified CSV path and an output directory; writes `model_tests.csv`, `model_coefficients.csv`, `model_diagnostics.csv`, `conditional_contrasts.csv`, and `session_info.txt`. Workflow authenticates original sources before invoking R and uploads only derived artifacts/provenance.

- [ ] Implement the five exact model formulas and two fixed sensitivities above; retain the original Cone reference and map Sham to free architecture.
- [ ] Export model-specific sample counts and diagnostic failures explicitly; fail rather than claim a completed inferential result when a model is unusable.
- [ ] Compare replayed published Type II tests with the original R comments/tables using rounding-aware tolerances. Investigate discrepancies rather than choosing a better-fitting replacement.
- [ ] Export free-minus-joined contrasts on link scales at pooled mean visit time and prespecified 25th/75th percentiles of observed head width within common treatment support. These are conditional effect probes, not fitted optimal sizes. Export the stigma log-body slopes and their difference to adjudicate the prose/figure discrepancy.

## Task 3 — scientific synthesis and verification

**Files:** `docs/BALANCE_SOLANUM_BEE_ARCHITECTURE_REANALYSIS_20261121.md`, derived JSON/CSV files under `data/` or `results/`.

- [ ] Keep publication transcription, recomputed arithmetic, model replay and endpoint-definition sensitivity distinguishable.
- [ ] Explain that the published composite already contains the stigma outcome, preventing its use as independent corroboration of deposition.
- [ ] Distinguish an architecture-by-size result for basket/body allocation from an architecture-by-body-load result for stigma receipt; disclose the Results prose/Fig. 6 direction discrepancy.
- [ ] Review code and methods independently; run the repository test gate and the real-data R workflow; verify the exact pushed head before reporting success.

## Review focus

- Altered bytes under a correct filename must not qualify as original data.
- Missing endpoint values must change the correct model denominator only.
- Body-plus-stigma and body-only pollen must never silently share a label.
- Post-treatment adjustment and alternating allocation must not become a randomized total-effect claim.
- Source contradictions, boundary random-effect variance, poor convergence and limited common support must remain visible in the final readout.

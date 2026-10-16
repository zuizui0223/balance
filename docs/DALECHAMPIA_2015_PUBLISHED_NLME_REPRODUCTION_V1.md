# Dalechampia 2015: reproduce the published model family with R nlme

**Status: exact public Dryad files authenticated; six source-listed models successfully fitted in modern R nlme; published AICs not numerically reproduced; original analyst code and historical environment unavailable.**

## Motivation

Pélabon et al. (2015, Functional Ecology) reported a statistically resolved reduction in four-week seed mass after bract removal and whole-blossom foil covering. Earlier BALANCE reanalysis used the mother-paired or blossom-averaged treatment estimates and found larger uncertainty. Those are **different estimands**: the original paper treated **individual seed mass** as the response with the mother as a random factor, whereas the alternative sensitivity collapses seeds within the experimentally treated blossom and uses maternal-cluster-robust uncertainty.

The original article selected candidate models by **maximum-likelihood AIC** and estimated final fixed-effect coefficients under **REML**. Its reported computing environment was R 2.15.2, and the exact original analysis script was not deposited. The modern R reconstruction therefore tests the written model specification, not the entire historical analysis code.

Source article: [Pélabon et al., 2015](https://doi.org/10.1111/1365-2435.12427).
Public original dataset: [Dryad 10.5061/dryad.nb675](https://doi.org/10.5061/dryad.nb675).

## Biological and source unit verification

The original authenticated archived Dryad seed file contains 1,221 lines, including one missing seed weight. Its **117 numeric masses below 20 mg** match the authors' published count of morphologically aborted seeds by treatment, but do not independently recover their embryo and seed-coat diagnoses. The numerical ≥20-mg subset leaves **1,103 individual measured seeds**, belonging to **132 treated blossoms nested in 36 mothers**. The raw source-file SHA256s and six AIC targets are frozen in the registered contract.

All fitted models use the same included source records, original maternal identity and intact blossom treatment reference. The official source files are first checked against Dryad MD5 and byte-length records. We do not silently refit on a selected subset to force agreement.

## Independent R nlme run on the original files

Current R package: **nlme 3.1-169**, compared with an unspecified nlme version under the 2015 authors' R 2.15.2.

| Source Table 2 model, all with maternal random intercept | Published ML AIC | Recomputed R ML AIC | Difference |
|---|---:|---:|---:|
| Peduncle + seed set + treatment | 6006.35 | 6154.00 | +147.65 |
| Peduncle + treatment | 6005.72 | 6152.41 | +146.69 |
| Peduncle + seed set | 6070.67 | 6221.64 | +150.97 |
| Peduncle alone | 6070.15 | 6221.64 | +151.49 |
| Seed set alone | 6221.11 | 6375.33 | +154.22 |
| Intercept only | 6222.85 | 6373.46 | +150.61 |

**None of the six published absolute AICs is matched within the frozen ±1.0-unit tolerance.** Independent Python MixedLM earlier gave essentially identical AIC values. Thus the numerical discrepancy is not unique to one estimator implementation. It may reflect unknown data exclusions, transformed response, additional covariance modeling, historical package behavior or other unreported processing. It is not evidence of a fraudulent or biologically false study.

The original ranking of models with versus without the treatment remains broadly similar, and the modern R fit also favors the treatment model strongly over alternatives without treatment. This is **not a full replication** of the source effect sizes or absolute fit; it is a convergence of a narrower model-selection pattern.

### Published versus recomputed REML coefficients

| Term | Original reported | Modern R nlme source reconstruction | Modern R SE |
|---|---:|---:|---:|
| Whole-blossom foil cover vs intact | −2.03 mg | **−1.841 mg** | 0.318 mg |
| Bracts removed vs intact | −1.34 mg | **−1.177 mg** | 0.323 mg |
| Edge-cut control vs intact | +0.29 mg | **+0.713 mg** | 0.322 mg |
| Peduncle diameter | +13.77 mg/mm | **+14.228 mg/mm** | 1.009 mg/mm |

The estimated **standard errors** on the seed-level maternal-random model closely match the paper's roughly 0.32 mg errors; the point estimates do not exactly coincide. This convergence in standard errors is a **model-structure result**—it does not prove that the seeds inside one experimentally manipulated blossom are independent residual observations.

### Independent residual-heterogeneity check

The paper separately compared treatment-specific and homogeneous residual variance, reporting an AIC improvement from 6005.6 to 5987.3 (**ΔAIC −18.3**). The source-authenticated modern R models reproduced the *relative* preference for residual heterogeneity: 6152.41 to 6131.60 (**ΔAIC −20.81**). Their absolute AICs still differ from the original source.

Consequently, an empirical difference in seed-mass dispersion between treatment groups may be worth further testing; it is not the same as the origin of the source's AIC offset or proof of a causal bract-carbon mechanism.

## Main issue for biological inference

The random mother term accounts for similarity between seeds from the same maternal plant, but the experimentally randomized entity was a **blossom**. Multiple seeds from the same blossom share fruit development, gas environment and intervention history. Treating them as conditionally independent residual responses can yield smaller nominal standard errors than an analysis that explicitly models the nested blossom effect or resamples plants. The already-merged mother-clustered blossom-mean reanalysis showed broader uncertainty.

A **separate preregistered covariance sensitivity**, preserving the exact same source data and treatment formula, should compare a maternal-only random intercept with a maternal-plus-blossom nested random intercept and report the variance decomposition. This would not reproduce or overturn the historical author code; it would quantify the additional dependence at the actual manipulated unit.

## Scientific ceiling

The original published experiment manipulated **entire-blossom foil cover** or **physical bract removal**. It did not independently maintain fruit irradiation, protection, microclimate and bract-local photosynthesis. Six independent greenhouse plants in the physiology assay show an increase in area-based carbon fixation as bracts green, but were not matched to the 2015 seed-weight mothers.

No direct isotope-labelled carbon transfer to seeds, complete lifetime male-plus-female fitness, contemporary quantified SCH conflict L or matched structural architecture net-fitness alternative is identified. The results do not add another independent biological cluster to BALANCE, and no numerical parameter from the 2015 study should be inserted into its net structural Phi or K identity.

## Reproduce

Canonical source outputs:

- data/DALECHAMPIA_2015_PUBLISHED_NLME_REPLAY_CONTRACT_V1.json — frozen source article and AIC references;
- data/DALECHAMPIA_2015_PUBLISHED_NLME_REPLAY_VERIFIED_V1.json — actual archival source-run values and source provenance;
- scripts/replay_dalechampia_2015_source_nlme.R — R nlme six-model ML/REML replay and separate varIdent residual model;
- scripts/adjudicate_dalechampia_2015_nlme.py — all-source-AIC mismatch HOLD, original file SHA256 checks and neutral scientific claim ceilings;
- tests/test_dalechampia_2015_source_nlme_adjudication.py — synthetic schema and mismatch controls;
- .github/workflows/dalechampia-2015-source-nlme-replay.yml — authenticated source retrieval, R replay and short-lived artifact.

Run: [GitHub Actions 38920401664](https://github.com/zuizui0223/balance/actions/runs/38920401664); artifact 12054043845. Every source Table 2 AIC and the residual-variance comparison were produced in this successful source job. Success means the independent source replay ran correctly; the published-numeric comparison remains explicitly **HOLD**.

The practical research question after this audit is no longer a new algebraic middle-world theorem. It is **why an apparent organ-retention seed benefit has model-dependent precision and whether the original function-specific mechanism is physically identifiable**.

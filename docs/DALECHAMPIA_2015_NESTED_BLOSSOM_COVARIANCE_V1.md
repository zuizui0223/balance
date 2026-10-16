# Dalechampia 2015 — strong within-blossom seed dependence changes treatment precision

**Scientific status:** independent source-authenticated, retrospective hierarchical-covariance sensitivity; NOT the unpublished source R script, NOT carbon-allocation causality, NOT structural BALANCE occupancy.

## The actual biological unit

In Pélabon et al. (2015, Functional Ecology), each hand-pollinated Dalechampia scandens **blossom** was assigned one manipulation. Several seeds develop inside the same fruiting blossom, and several blossoms were treated on each maternal plant. Consequently the 1,103 qualifying individual seed weights are *measurements nested inside an experimentally assigned blossom*, not 1,103 independent randomized treatments.

The original paper describes a maternal plant random intercept, and its Table 2 reported AIC 6005.72 and foil/removal effects of −2.03 ± 0.32 / −1.34 ± 0.32 mg. As shown by the [original-R-family reproduction audit](DALECHAMPIA_2015_PUBLISHED_NLME_REPRODUCTION_V1.md), our modern R nlme and independent Python reconstructions have similar standard errors but **fail to reproduce the absolute source AIC and some coefficients**. The author scripts and original R 2.15.2 environment remain unavailable.

The new question does not ask which absolute AIC best matches the paper. It asks whether a random effect for the *treatment-assigned blossom* materially changes the covariance of seeds within mothers.

## Two models fitted to exactly the same original data

Both use the **same fixed-effects formula**: individual seed mass = intercept + mean blossom peduncle diameter + four-level treatment (intact reference), with ML for AIC and REML for treatment coefficients. No source rows, treatments, covariates, thresholds or contrasts change between models.

| R nlme random-effects structure | Source rows | ML AIC | Estimated seed-level variance structure |
|---|---:|---:|---|
| Mother only | 1,103 seeds / 132 blossoms / 36 mothers | **6152.41** | mother variance 19.175; residual 13.527 |
| Mother **plus nested blossom** | Same source rows and fixed effects | **5135.56** | mother variance 15.190; **blossom variance 14.500**; residual 3.809 |

Nested model minus maternal-only **ΔAIC = −1016.85**, a very large improvement in the Gaussian marginal likelihood for the same 1,103 observations. It measures the value of explicitly modeling shared seed variation within the same manipulated blossom. **It is not an architecture value, not a photosynthetic return and not a BALANCE reserve.**

### Source-derived correlation decomposition

In the nested random-intercept model, the three variance components are 15.190 (mother), 14.500 (blossom within mother) and 3.809 (remaining seed residual), all in squared seed-mass units.

- Two seeds in the **same blossom** have an implied correlation **0.886**.
- Two seeds in **different blossoms on the same mother** have implied correlation **0.453**.
- The extra blossom covariance is therefore substantial even after mother identity is accounted for.

These are model-implied correlations, not independently measured causal mechanisms. They can reflect shared fertilization, nutrition, local environment, genetic kinship or multiple unmeasured fruit-level processes.

## Consequences for measured treatment effects

Reported treatment–intact contrasts below are from the exact public seed records, restricted to numeric ≥20 mg (1,103 seeds). Coefficients are REML estimates; the intervals are **approximate normal Wald 95% intervals** from the fitted source models, not cluster-robust bootstrap intervals or the historical authors' model.

| Manipulation | Mother-only estimate ± SE (mg) | Mother + blossom estimate ± SE (mg) | Nested-model 95% interval (mg) |
|---|---:|---:|---:|
| Whole-blossom aluminium foil | −1.841 ± 0.318 | **−1.829 ± 0.991** | [−3.772, +0.114] |
| Both bracts removed | −1.177 ± 0.323 | **−1.119 ± 1.000** | [−3.080, +0.841] |
| Bract-edge-cut control | +0.713 ± 0.322 | **+0.575 ± 0.980** | [−1.346, +2.496] |

The fitted **effect sizes hardly change**, but adding the blossom random effect increases standard errors by approximately **3.05–3.12 times**. All three nested-model normal 95% intervals now include zero.

This is compatible with the independently implemented blossom-mean, mother-clustered sensitivity in [PR #234](https://github.com/zuizui0223/balance/pull/234), which also yielded wider intervals. Their interval methods differ (one fits a nested Gaussian random-effects model; the other uses maternal-cluster-robust regression), so agreement in the direction of wider uncertainty is useful but not two independent biological replications.

## What this does and does not show

**New, directly supported finding:** the published dataset has very strong *within-blossom dependence*, and a hierarchical model recognizing the true treated-blossom unit substantially reduces the apparent precision of early seed-mass treatment differences relative to a mother-only intercept model on the same seed-level data.

**Not established:** that the original authors' analysis code omitted a flower-level term, that a current alternative model is uniquely correct, that the experiment had inadequate biological randomization, that selection favoring bract persistence is absent, that green bract carbon entered seeds, or that a structural BALANCE middle-world state has been observed.

The original experiment includes **whole-blossom foil covering**, not bract-only suppression; cutting off bracts also alters protective and microclimatic conditions. A six-plant gas exchange assay supports stronger green-bract photosynthesis, but those plants are not directly linked to the maternal seed-mass cohort. The experiment measures early four-week seed mass, not lifetime maternal+paternal reproductive fitness. The source also used morphological observations to diagnose aborted seeds; our numeric <20 mg proxy is not a validated substitute for those diagnostics.

The strong within-blossom correlation should inform future experiment design and powering: allocate treatment at the blossom or independent plant level, maintain identifiable blossoms and maternal plants, and simulate covariance at both levels. **Counting seeds as independent replicates can substantially exaggerate effective sample size.**

## Exact source verification and computational audit

Original data: [Dryad 10.5061/dryad.nb675](https://doi.org/10.5061/dryad.nb675); article: [Pélabon et al. 2015](https://doi.org/10.1111/1365-2435.12427).

The independent [GitHub Actions run 38921890413](https://github.com/zuizui0223/balance/actions/runs/38921890413) retrieved both archived Dryad files, validated original MD5 and SHA256, re-fitted the two ML/REML models on the same source subset, and emitted the machine-checked covariance/interval comparison.

Canonical files:
- data/DALECHAMPIA_2015_NESTED_BLOSSOM_COVARIANCE_CONTRACT_V1.json — registered same-data model comparison;
- data/DALECHAMPIA_2015_NESTED_BLOSSOM_SOURCE_VERIFIED_V1.json — verified source outcome with archive artifact hashes;
- scripts/replay_dalechampia_2015_nested_nlme.R — original-source two-model fit, covariance decomposition and SE;
- scripts/adjudicate_dalechampia_nested_nlme.py — claim ceilings, original SHA256s, reference-model consistency and outcome parsing;
- tests/test_dalechampia_nested_nlme.py — synthetic failure gates, not source biological fixtures;
- .github/workflows/dalechampia-2015-nested-blossom-covariance.yml — original source download and exact-model replay.

No numerical evidence from the separate 2012 resin study or 2013 wild pollinator/predator selection study is merged into these seed data.

## Implication for the BALANCE paper

The finding **narrows** rather than weakens the scientific logic. The important question remains *when do genuinely conflicting functions favor retaining one multifunctional architecture?* The Dalechampia data identify a credible sequential reuse mechanism (visual advertisement followed by greening and carbon assimilation), but the early seed-mass treatment effect is insufficiently sharply determined under reasonable dependence models, and the bract-specific carbon pathway is not causally isolated.

Do not use this source to calculate SCH conflict load L, net differentiated architecture fitness, K, Phi, middle-world depth or the evolutionary transition rate. A genuine direct BALANCE worldline requires a **same-context, net-fitness comparison between actually distinct, accessible architectures** with joint uncertainty.

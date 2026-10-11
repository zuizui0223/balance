# Pedicularis rex 2013 — source bytes and 18/18 published seed ANOVA F reproduction

**Status: EXACT_SOURCE_BYTES_VERIFIED / PUBLISHED_FIXED_EFFECT_F_REPRODUCED / PATCH_LEVEL_INFERENCE_NOT_IDENTIFIABLE_FROM_PUBLIC_XLSX**

## Source and reproducibility

- Paper: Xia, Sun & Liu (2013), *Biology Letters* 9:20130387, DOI [10.1098/rsbl.2013.0387](https://doi.org/10.1098/rsbl.2013.0387).
- Source: Dryad [10.5061/dryad.6cv06](https://doi.org/10.5061/dryad.6cv06), version API ID `11193`.
- Original: `raw data.xlsx`, **89,597 bytes**, MD5 `10a98383677bbd2a01e19a86c350fdd3`, SHA256 `d1dab0ea6f4371370aacd13106eee57017abbccccb3cd12dea75b69bdfa60380`.
- Original ZIP SHA256 `e002c369ad864c2de22365b070c0551370c5d6c2cd6a10f80655865f0612f185`.
- The source bytes were retrieved from Dryad's published version ZIP through GitHub Actions, MD5-matched to the repository manifest, and independently inspected using `artifact_tool` at exactly the registered XLSX SHA256.
- The original workbook has exactly **three worksheets**:
  1. `pollination rate` — 2005/2011 × sparse/dense summary counts, **not individual patch observations**.
  2. `fruit set and fruit predation` — 74 biological spike/plant-level rows plus **two final legend rows**, with columns `year,density,size,flowers,fruit set,fruit predation`.
  3. `seed set and seed predatioin` — 2,930 biological flower/capsule-level rows plus **two final legend rows**, with columns `year,density,size,intial seed set,fianl seed set,seed predation`. Spelling reflects the **original** source, not transcription errors.

The two legend rows per sheet explicitly define: `1=2005`, `2=2011`; `1=sparse`, `2=dense`; `1=small`, `2=large`. These legend rows are **not** biological observations. Of 2,930 seed rows, **328 have missing initial seed set**, but their final seed set and seed predation columns are populated. Initial-seed models therefore use 2,602 records. Never interpret initial missing as zero or delete records with repeated numerical rates: repeated percentage values are plausible outcomes from discrete seed counts.

## Original group sizes

| Source rows | 2005 sparse | 2005 dense | 2011 sparse (small / large) | 2011 dense (small / large) |
| --- | ---: | ---: | ---: | ---: |
| Fruit set / fruit predation | 6 | 10 | 9 / 17 | 7 / 25 |
| Seed-related outcomes | 273 | 308 | 391 / 679 | 187 / 1092 |

The fruit sheet reproduces the source paper's harvested 16 spikes in 2005 and 58 in 2011. The seed sheet has 581 records in 2005 and 2,349 in 2011. The initial seed response has 328 missing records (not randomly distributed over year/density); complete-case support totals 2,602 for Table 1 and 2,051 for 2011 Table 2.

## Exact published numerical test: no invented patch effects

Using the original percentage measurements, fit ordinary least squares with two binary factors and their interaction, **sum-to-zero factor coding** `2*factor_code-3`. The original SPSS ANOVA's density/year and density/size F statistics emerge *to printed 3-decimal precision* from this unclustered row-level model.

| Source / seed response | n | Residual df | F for year or size | F for density | F interaction |
| --- | ---: | ---: | ---: | ---: | ---: |
| Table 1 / initial seed set | 2,602 | 2,598 | 0.507 | 3.767 | 1.241 |
| Table 1 / final seed set | 2,930 | 2,926 | 11.954 | **39.025** | 0.426 |
| Table 1 / seed predation | 2,930 | 2,926 | 46.571 | **166.220** | 4.250 |
| Table 2 / 2011 initial seed set | 2,051 | 2,047 | 41.221 | 27.348 | 44.556 |
| Table 2 / 2011 final seed set | 2,349 | 2,345 | 1.025 | 26.958 | 0.023 |
| Table 2 / 2011 seed predation | 2,349 | 2,345 | 45.029 | **317.878** | **106.270** |

**18/18 of these printed F statistics match** the article to 3 decimals. This is not an inference about the true number of independent density replicates: it is a reproducibility check that identifies a row-level statistical computation capable of recreating the published analysis.

Replication must not be presented as a second biological study. Fruit-related Table 1 covariate models are outside this 18/18 seed-only scope. The fruit-predation model lacks an independently recorded fruit-production covariate; the [separate fruit-set audit](PEDICULARIS_2013_FRUIT_SET_ANCOVA_PARTIAL_REPRODUCTION_V1.md) tests observed flower number as plant size and matches 3/4 F values. Neither this receipt nor the later completed 24F subset implies full-article reproduction.

## Source missingness: all missing initial rates are coded as 100% predation

**328/328 missing initial seed-rate rows** are coded as `seed predation = 100%` and `final seed set = 0%`. Original initial seed formation is unascertainable from these records. Missingness is associated with the recorded outcomes and differs by density/year; the file does not independently establish the cause of every missing value or a formal missing-data mechanism conditional on all relevant variables.

| Original cell | Initial rate missing | Missing fraction | Mean initial rate among measurable flowers | Conservative all-flower initial mean bound |
| --- | ---: | ---: | ---: | ---: |
| 2005 sparse | 17 / 273 | 6.2% | 25.32% | 23.74%–29.97% |
| 2005 dense | 13 / 308 | 4.2% | 24.64% | 23.60%–27.82% |
| 2011 sparse | 246 / 1,070 | **23.0%** | 25.65% | **19.75%–42.74%** |
| 2011 dense | 52 / 1,279 | **4.1%** | 23.13% | **22.19%–26.25%** |

The bounds are **not imputations**: they ask only what the overall mean would range over if each missing initial seed rate could lie anywhere from 0% to 100%. Under no further assumptions, 2011's dense-minus-sparse initial seed-mean contrast lies in **[-20.56,+6.50] percentage points**; its sign is **not identified**. The 2005 analogous interval is [-6.37,+4.08] points. These ranges are arithmetic outer bounds, not population confidence intervals and **do not** include patch-level sampling uncertainty.

The paper's methods count intact and recognizable predated seeds in **initial seed set**, but assign `seed predation = 100%` when no distinguishable seeds are found (Xia et al. 2013, Methods). The recorded code does not independently reveal the pre-attack seed count or establish complete destruction as the cause in every case. Replacing a missing initial value with **zero** would assume absence of initial seed formation even though later destruction is another possible explanation. Excluding these rows instead selects on whether initial seed formation remains ascertainable, with especially unequal missingness in sparse and dense 2011 patches.

This does not negate the measured **final seed-set** result (those rows have observed final zero and remain in the final outcome model). It does limit the statement "initial seed set is independent of density" to **the set of flowers for which initial seed count remained ascertainable**. To identify true early seed production separately from later predation would require a prospective seed-development measurement before enemy destruction or justified missing-value assumptions. The dataset alone does not identify pollination and predation as separable causal pathways.

The source-bound script includes `initial_seed_missingness_bounds` and a test for the recorded 100%-predation/zero-final-rate pattern. No biological values are filled in.

## Key inferential limitation now proven at the source-file level

**Neither the fruit worksheet nor the seed worksheet contains a `patch_id`, `plant_id`, geographical patch identifier, or seed-to-plant linking key.** Both provide only coarse group codes `year,density,size`. The 2013 paper's density exposure is a **patch-level variable**:
- 2005: **one sparse patch + one dense patch**.
- 2011: **five sparse patches + six dense patches**.

Thus 2,930 flower/capsule records cannot be treated as 2,930 independently sampled sparse/dense **patches**. The published ANOVA can be reproduced using per-record residual df 2,926, but **an actual patch-clustered standard error, patch-level leave-one-out validation and between-patch heterogeneity are not identifiable from these published bytes**. The true patch membership of each record cannot be reconstructed from a binary density category and a binary patch-size category.

This is stronger than a general concern about pseudoreplication: the source workbook has been checked and **does not preserve the grouping ID needed to test the claim at its stated patch scale**. It is not a demonstration that the ecological density association is false or that all analyses in the original paper are invalid. A request to the authors for original patch and plant IDs would make a proper hierarchical reanalysis possible.

### Scientific claim ceiling

**Established**:
- The author-deposited 2013 raw dataset is accessible, byte-verifiable and numerically reproduces the printed 18 seed ANOVA statistics.
- The analysis' reported degrees of freedom reflect capsule/flower records, not independent patch counts.
- The public workbook is insufficient for patch-level confidence intervals, patch-by-density variation or plant clustering.

**Not established**:
- A significant density effect after patch-level correction.
- A causal effect of **manipulating density** (density was observational).
- Any `density × water-treatment` result: the 2015 drainage experiment sampled dense patches only, and 2013 has no water treatment.
- A direct BALANCE structural-worldline fitness gap or architecture cost.

## Next data requirement

Request from the authors a **row-to-plant/inflorescence-to-patch crosswalk** with original patch IDs and plant IDs, including assignment of 2011 patch size/density and biological sampling dates. Do not substitute an invented grouping or assume that all flowers in a density × size code came from the same patch. Until such a crosswalk exists, the defensible outcome is `PATCH_CLUSTER_INFERENCE_NOT_IDENTIFIABLE_FROM_PUBLIC_XLSX`, even though the original F values are reproducible.

Reproducer: `scripts/adjudicate_pedicularis_2013_raw_workbook.py` (uses installed `artifact_tool` for XLSX import and standard-library fixed-effect OLS); raw-binary source receipt: `scripts/retrieve_pedicularis_2013_dryad_bytes.py`. Source test suite includes synthetic algebraic contrast oracles and digest/source-category guards.

Original article: https://pmc.ncbi.nlm.nih.gov/articles/PMC3971674/

## New fruit-denominator qualification (2026-10-11)

An independent **exact-XLSX percentage-arithmetic audit** (`docs/PEDICULARIS_2013_FRUIT_COUNT_DENOMINATOR_AUDIT_V1.md`) checked whether the original `fruit set (%)` could be inverted into a *unique integer fruit production count* using the deposited `flowers` count. With a conservative ±0.0051 percentage-point rounding allowance, **4/74** rows have no such fruit count. Among the other 70 rows, **16 more** have a fruit predation percentage incompatible with any integer damaged-fruit numerator out of the reconstructed fruit set count. Joint integer-chain support is therefore **54/74**, but these are conditional arithmetic tests, **not proven source errors**. The discrepancy is mainly in 2011.

The original 24/24 F-value reproduction **remains valid** because it uses observed percentages, never a reconstructed numerator. These incompatibilities reinforce the strict HOLD on reconstructed fruit-production covariates for the pooled Table 1 **fruit-predation** ANCOVA. The fruit-set ANCOVA has a separate 3/4 partial replay using recorded flowers. Original analysis code, field-count/censoring definitions and `flower→plant→patch` IDs remain needed to resolve the outstanding questions. No source correction or new biological inference is claimed.


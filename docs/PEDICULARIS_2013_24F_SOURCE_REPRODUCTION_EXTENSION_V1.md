# *Pedicularis rex* 2013 — extend seed ANOVA concordance from 18 to 24 published F statistics

**Status: EXACT_SOURCE_WORKBOOK / SOURCE-PRECISION F REPRODUCTION / PATCH-LEVEL INFERENCE STILL UNIDENTIFIABLE.**

## What is genuinely new relative to the existing 18/18 audit

The main branch's frozen source receipt already reproduces all **18 seed-related** F values in Xia, Sun & Liu (2013), *Biology Letters*, DOI 10.1098/rsbl.2013.0387, Tables 1 and 2, from Dryad [10.5061/dryad.6cv06](https://doi.org/10.5061/dryad.6cv06). This PR adds the **six 2011 fruit-related Table 2** F values on the same frozen source:

| 2011 source Table 2 | n | Residual df | Size F | Density F | Size × density F |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fruit set | 58 | 54 | 0.206 | 2.368 | 3.060 |
| Fruit predation | 58 | 54 | 4.573 | 26.314 | 10.605 |

Both models use exactly the 2011 fruit/inflorescence rows, **not** the seed-sheet flower/capsule observations. With source-original `year,density,size` codes and sum-to-zero ±1 coding, ordinary two-way OLS reproduces the six F statistics to the printed three decimals. The complete audited set is therefore **8 models × 3 F = 24/24** (18 seed + 6 fruit). This is not eight independent studies.

The source workbook is exact `raw data.xlsx`, **89,597 bytes**, SHA256 `d1dab0ea6f4371370aacd13106eee57017abbccccb3cd12dea75b69bdfa60380`, MD5 `10a98383677bbd2a01e19a86c350fdd3`, verified against Dryad version API ID 11193.

The existing `scripts/adjudicate_pedicularis_2013_raw_workbook.py` now reproduces all eight 2×2 models when supplied with the verified original XLSX. It preserves source-legend, row-count, source checksum and response completeness guards. The 18-seed-only frozen receipt remains intact under `data/PEDICULARIS_2013_SOURCE_SEED_ANOVA_CONCORDANCE_V1.json`; this extension's machine-readable frozen receipt is `data/PEDICULARIS_2013_ANOVA_24F_SOURCE_RECEIPT_V1.json`.

## What still does *not* reproduce

**The pooled 2005+2011 Table 1 fruit-set and fruit-predation ANCOVAs are not promoted as matched.** Their source paper includes plant-size and fruit-production covariates; the original XLSX has a `flowers` column and percentages, but does not provide an independent original fruit-production count nor an original analysis-script/missing-data specification. A post hoc reconstructed count from rounded percentages is not a verified covariate. Therefore the 24/24 claim is **explicitly restricted** to the six listed source models and two additional 2011 fruit-only models; it is **not full-article numerical reproduction**.

## Reproduction is not independent patch-level uncertainty

The verified workbook has **74 fruit/inflorescence rows**, **2,930 seed/capsule rows**, no `plant_id` or `patch_id` and no fruit-to-capsule join key. Published field methods report:
- 2005: 1 sparse and 1 dense patch.
- 2011: 5 sparse and 6 dense patches.

The model residual df of 2,926 and 2,345 reflect the source **flower/capsule-level** observations. Reproducing these tests does **not** establish that the density effect remains significant when **patch** is the unit supporting density variation. Patch-level standard errors, leave-one-patch-out estimates and joint density×patch-size uncertainty cannot be reconstructed without row-level patch membership; binary density and size classes are not patch identifiers.

This is an identifiability limit of the deposited workbook, not proof the published 2013 results were wrong. Do not fabricate a pseudo-patch assignment to produce a favourable or unfavourable revised p-value.

## Biological patterns, descriptive only

In 2011, row-weighted average seed predation in the original XLSX was:

| Density | Patch size (paper category) | Raw flower/capsule rows | Mean seed predation |
| --- | --- | ---: | ---: |
| Sparse | Small | 391 | **53.36%** |
| Sparse | Large | 679 | 22.98% |
| Dense | Small | 187 | 3.14% |
| Dense | Large | 1,092 | 9.56% |

These row-weighted rates show a sharp density × patch-size pattern that the source paper already reported. They are **not** averages of independently measured patches and have no patch-level confidence interval here.

The existing 18-F audit additionally found **328 missing initial seed-rate values**, all on source rows with final seed set 0 and seed predation 100%. This is outcome-related missingness, and initial seed-set comparisons among only ascertainable rows may be selected by predation intensity. The original report's *final seed set* uses those known zeros and is not changed by this note. The main-branch partial-identification bounds remain the appropriate evidence ceiling; this PR does not impute destroyed initial seeds.

## Next actual evidence required

Retrieve the original mapping `workbook record → plant/flower/capsule → patch` from the study authors before making any patch-clustered Allee-effect claim. The existing data cannot test density manipulation causality, and the 2015 water-drainage experiment deliberately used dense patches only; there is no sparse-patch water-treatment causal estimate here. No BALANCE `W_S^*/W_D^*` architecture-value gap is established.

### Reproduction command

```bash
python scripts/adjudicate_pedicularis_2013_raw_workbook.py \
    --workbook "raw data.xlsx" \
    --out "PEDICULARIS_2013_SOURCE_STRUCTURE_AND_ANOVA_V2.json"
```

The command requires the exact workbook checksum and the installed `artifact_tool` interface for XLSX import. Tests for the pure-standard-library effect-coded OLS and the frozen numerical source receipt run in baseline GitHub CI. **Do not count the 2011 fruit extension as an independent biological dataset from the 2013 seed analysis**.

Original source: https://pmc.ncbi.nlm.nih.gov/articles/PMC3971674/

# Pedicularis 2013: pooled fruit-set ANCOVA partially reproduced

**Status: 3/4 PRINTED F VALUES MATCH / INTERACTION UNRESOLVED / CONDITIONAL FLOWER-COVARIATE REPLAY.**

## The public-data question

Xia, Sun & Liu (2013), Table 1, assigns **plant size to the fruit-set model** and **fruit production to the fruit-predation model**, respectively. The absence of an independently recorded fruit-production count does not, by itself, prevent testing fruit set against the deposited flower count. The earlier documentation grouped these two limitations too broadly.

The present check fits one specified model to the exact deposited workbook, treating recorded `flowers` as the published plant-size covariate. That semantic mapping is an explicit assumption; numerical concordance is not independent access to the original SPSS syntax. This is a post-publication computational audit of an existing study, not a preregistered ecological test or a second field dataset.

Sources: [original article and Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC3971674/), DOI [10.1098/rsbl.2013.0387](https://doi.org/10.1098/rsbl.2013.0387); [Dryad source](https://doi.org/10.5061/dryad.6cv06).

## Fixed model and source support

- Original workbook: 89,597 bytes, MD5 `10a98383677bbd2a01e19a86c350fdd3`, SHA256 `d1dab0ea6f4371370aacd13106eee57017abbccccb3cd12dea75b69bdfa60380`.
- Fruit worksheet: all **74 biological spike/plant rows**, original Excel rows **2–75**, excluding only the two source legend rows.
- Response: recorded fruit-set **percentage**, without transformation, repair or imputation.
- Predictors: intercept, year, density, year × density, and mean-centered recorded flowers. Year and density use sum coding `2*code-3`.
- Five fitted coefficients, residual df **69**. Each F is the one-coefficient partial test conditional on the other four columns.
- One specification tested. No reconstructed fruit counts, patch assignments, or covariate interactions are introduced.

## All four published comparisons

| Table 1 fruit-set effect | Published F | Recomputed F | Difference | Match to printed precision |
|---|---:|---:|---:|---|
| Density | 2.945 | 2.945008437 | +0.000008437 | Yes |
| Year | 67.671 | 67.671420489 | +0.000420489 | Yes |
| Density × year | **0.355** | **0.080051129** | **−0.274948871** | **No** |
| Flowers, assumed plant size | 3.855 | 3.855458250 | +0.000458250 | Yes |

The fixed printed-precision tolerance is **0.0005 F units**. Three comparisons satisfy it. The interaction discrepancy is far beyond rounding. The machine-readable result is therefore `PARTIAL_REPRODUCTION_HOLD`, with **3 matches out of 4 attempted comparisons** and `all_F_reproduced=false`.

The existing eight-model **24/24 ANOVA receipt remains its own completed scope**. Combining scopes gives 27 matches across 28 attempted comparisons; the one mismatch must remain visible. Four other Table 1 fruit-predation ANCOVA entries are still outside these attempts. Neither 24/24 nor 27/28 means full-article reproduction.

## What the discrepancy establishes

The deposited observations permit a numerical fruit-set ANCOVA check without the missing fruit-production covariate. One clearly stated model reproduces the published year, density and plant-size F values, but it does not reproduce the interaction. The original interaction's analysis specification or table provenance remains unresolved.

This is not proof of a transcription error, an erroneous original model, or an ecological effect. Original SPSS syntax/output and confirmation of the plant-size variable are needed to distinguish possible explanations. Changing specifications until a preferred number appears would not establish that historical provenance.

Both the reported and recomputed interaction F values are small. The discrepancy is a reproducibility finding, not evidence for a newly discovered density-dependent biological interaction. No patch-clustered uncertainty is estimable without original patch membership. No causal density effect, water-defence interaction or BALANCE architecture-value comparison follows from this check.

The fruit-predation ANCOVA has a separate unresolved requirement: original fruit-production counts and their measurement definitions. The [integer-denominator audit](PEDICULARIS_2013_FRUIT_COUNT_DENOMINATOR_AUDIT_V1.md) explains why rounded inversions of the stored percentages cannot simply be substituted for that source variable.

## Reproduction and independent verification

From the repository root, with the exact original workbook:

```bash
python -m pip install -e '.[pedicularis]'
python -m scripts.audit_pedicularis_2013_fruit_set_ancova \
  --workbook /path/to/pedicularis_2013_raw_data.xlsx \
  --out /path/to/new-fruit-set-audit.json
```

The runner checks size, MD5, SHA256, sheet names, original headers, legend and category counts before fitting. It reads the workbook without editing it and refuses to overwrite a receipt. A successful command means the audit executed; its scientific status can remain a partial-reproduction HOLD.

The source result is retained in `data/PEDICULARIS_2013_FRUIT_SET_ANCOVA_AUDIT_V1.json`. Its calculation reuses the existing standard-library matrix inverse. An independent NumPy least-squares implementation and term-removal residual-sum-of-squares tests agreed with all four F values within `2e-12`. An orthogonal synthetic design separately checks the five-parameter formula against exact F expectations; these synthetic checks do not supply biological evidence.

The original 24 F values were also recomputed from the same workbook with the existing engine and independent NumPy fits, agreeing within `4e-12`. Independent rational arithmetic confirmed the denominator audit's 54/74 compatible rows, the identical 20 incompatible row identities at both 0.0051 and 0.1 percentage-point tolerances, and the minimum discrepancy values 0.2978947 and 0.1063830 percentage points. These checks strengthen the computational record while preserving all source and inferential limitations.

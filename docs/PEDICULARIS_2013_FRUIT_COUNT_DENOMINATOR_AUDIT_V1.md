# *Pedicularis rex* 2013 Dryad: integer fruit-count and predation-denominator audit

**Status:** EXACT_SOURCE_XLSX / PERCENTAGE_ARITHMETIC_SENSITIVITY / NO SOURCE DATA REPAIR / NO REVISED BIOLOGICAL F TEST.

## Why this is a new forensic question

Existing BALANCE source work reproduced **24/24** original Xia, Sun & Liu (2013) published Table 1 seed and Table 2 seed/fruit F statistics, and demonstrated that the 2013 XLSX has **no plant/patch identity**. The remaining 2005+2011 **Table 1 fruit ANCOVAs** use observed `flowers` (plant size) and **fruit production** covariates, but the deposited fruit worksheet gives only `flowers`, `fruit set (%)` and `fruit predation (%)`, not a separate exact fruit production count.

A tempting strategy is to reconstruct integer fruit production by `round(flowers * fruit_set / 100)`. **We tested whether this is licensed by the actual recorded percentages**, rather than postulating that a rounded value equals its originally measured count.

Original source: [Xia et al. (2013)](https://doi.org/10.1098/rsbl.2013.0387), Dryad [10.5061/dryad.6cv06](https://doi.org/10.5061/dryad.6cv06), raw workbook SHA256 `d1dab0ea6f4371370aacd13106eee57017abbccccb3cd12dea75b69bdfa60380` (89,597 bytes). The published Methods define fruit set as fruit count / flower count and fruit predation as damaged fruits / produced fruits. The source XLSX is not itself an original field book.

## Conditional integer consistency, no imputation

For each original biological row (Excel fruit-sheet rows **2–75**, 74 observations; source legend rows 76–77 are excluded), with registered flower count `N`, fruit-set percent `f`, fruit-predation percent `p`:

1. Collect all integers `F` between 0 and `N` that satisfy `abs(100*F/N - f) <= 0.0051` **percentage points**. This generous bound covers source values printed to two decimal places.
2. **Only if exactly one compatible positive `F` exists**, collect all integers `D` between 0 and `F` satisfying `abs(100*D/F - p) <= 0.0051` percentage points.
3. Do not replace, clip, round or impute original percentages. `F` and `D` are **candidate counts conditional on assumptions**, not independently observed fruit/damage counts.
4. A failure means the recorded values do not all satisfy that **single same-denominator integer chain** at the stated tolerance. It does **not** establish transcription error: field counts may come from different dates/eligible cohorts, or percentages may have been defined/processed differently from the deposited column labels.

### Results from original 74 source rows

| Year | Source rows | Jointly integer-compatible | Fruit-set incompatible with reported `flowers` | Fruit predation incompatible, conditional on a compatible fruit count |
|---|---:|---:|---:|---:|
| 2005 | 16 | 15 | **1** | 0 |
| 2011 | 58 | 39 | **3** | **16** |
| **Total** | **74** | **54** | **4** | **16** |

Therefore **20/74** recorded rows cannot support the full proposed nested integer reconstruction at ±0.0051 pp, with most of the disagreement in 2011. These are not 20 proven data errors and are not proof that the source ANOVA was miscomputed: the reproduced ANOVA uses the recorded percentages directly, without reconstructing counts.

The four *fruit-set* contradictions alone are particularly clear (Excel row indices, **not** 2013 patch IDs):

| Source Excel row | Year/density | Registered `flowers` | Fruit set (%) | Nearest integer `F` | Error from recorded percent (pp) |
|---|---|---:|---:|---:|---:|
| 16 | 2005 dense | 44 | 77.73 | 34 | 0.4573 |
| 57 | 2011 dense | 90 | 96.15 | 87 | 0.5167 |
| 68 | 2011 sparse | 95 | 62.86 | 60 | 0.2979 |
| 72 | 2011 sparse | 40 | 65.63 | 26 | 0.6300 |

Each minimum error is roughly **60–120 times** the rounding bound or greater. A simple two-decimal rounding explanation is ruled out for these particular same-denominator integer ratios.

An independent second-stage example: Excel row **19** has `flowers=40`, `fruit_set=90%` (exactly 36 candidate fruits), and `fruit_predation=5.128205128%`. That predation rate is close to **2/39**, not to *any integer damaged-fruit numerator out of 36*. The observation is incompatible with treating the numerator/denominator of the stored two rates as a single common cohort. Another plausible possibility is that the relevant at-risk fruit count was 39 at a distinct observation time; do not infer this from the file as a fact.

## Scientific conclusion and manuscript consequence

**What is established:** the raw source includes valid raw percentages that quantitatively reproduce the reported 24 F statistics; its fruit set/flower and fruit-predation/derived-fruit-rate chain is **not universally reconstructible as integer counts** from deposited columns under a normal rounding model. Neither true `fruit production` for all 74 stems nor a universally shared predation denominator can be independently recovered from this file.

**What is not established:** that 20 records have incorrect field values; that the original article's fruit ANCOVA is wrong; that any patch-level density effect is invalid; or that the source files measure different fruit cohorts. These are competing interpretations requiring field documentation.

**Hard gate:** do **not** present `round(flowers*fruit_set/100)` as an original verified covariate, do not use that synthetic series to declare Table 1 fruit predation ANCOVA reproduced, and do not treat 70 valid-looking inversions as a calibration of the remaining four discrepancies. The original fruit **Table 2** F reproduction is unaffected because it models the recorded percentages with their original rows, not reconstructed fruit counts.

For genuine completion, request the original `fruit production` count, count dates/censoring definitions, and a `flower/capsule → plant → patch` crosswalk. This is a different missing-data issue from the **328 missing initial seed-set percentages** already documented in the source audit. Both must be retained as separate evidence ceilings.

## Reproducibility

- `balance_domain/pedicularis_2013_fruit_denominators.py` — pure standard-library, frozen percentage integer-chain checker.
- `scripts/audit_pedicularis_2013_fruit_denominators.py` — exact-source-MD5/SHA256 and known sheet/legend identity, via installed `artifact_tool` as required to read original XLSX; emits original row-indexed machine-readable JSON with no data modification.
- `tests/test_pedicularis_2013_fruit_denominators.py` — synthetic tests for rounding, source codes, domain failures and claim ceiling.
- `data/PEDICULARIS_2013_FRUIT_INTEGER_DENOMINATOR_FREEZE_V1.json` — exact-original-source numeric case freeze.
- No independent patch-cluster uncertainty or biological mechanism estimate results from this arithmetic audit.

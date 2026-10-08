# Peucedanum 2025 R1 observation-grain and missingness audit

## Scope and evidence

This is a **pre-model input-support audit**, not a re-estimate of the published
selection gradient. It is based on the source-verified, SHA256-bound
`Kudo$Shibata_JEcol_Data.zip` from HUSCAP, DOI `10.14943/hu95572`.

The source archive was normalized with the frozen exact mapping and 685 rows
were verified by the GitHub Actions end-to-end ingest route. The output of
`scripts/audit_peucedanum_r1_support.py` is a derived receipt, not a
second, guessed source schema.

Machine-readable frozen expectations:
`empirical/peucedanum/PEUCEDANUM_2025_R1_ROW_SUPPORT_EXPECTATIONS_V1.json`.

The observation audit also requires exact SHA256 matches for the verified normalized
CSV and its normalization receipt, not merely the original ZIP's SHA256 and row
counts. Two independent successful ingests reproduced the same normalized
CSV bytes. A changed normalized value, even if missingness and total counts remain
identical, is therefore a versioned-provenance change and must fail closed.

## Observation support

The 685 recorded observations span **19** plot-by-year cells, not an assumed
complete 5-by-4 panel. The `HL` plot has no row in 2020.

| Plot | Raw rows | Fruit-complete, before global height exclusion | Original-source R1 candidate rows (differential and gradient) |
| --- | ---: | ---: | ---: |
| HA | 177 | 126 | 126 |
| HL | 95 | 88 | 88 |
| HC | 139 | 132 | 132 |
| KD | 135 | 135 | 135 |
| HD | 139 | 139 | 127 |
| **Total** | **685** | **620** | **608** |

The original archived R script filters `InitialFruitN` and `Height` globally
before **both** differential and gradient regressions and the female-gain
NLS fits. Its final-fruit models subsequently require `FinalFruitN`.
The 620 fruit-complete rows are therefore **not** 620 source-model
differential candidates: source-faithful differential **and** gradient
candidate counts are 608. These are still pre-fit eligible-row counts,
not proof of exact fitted N.

## Structured missingness

The source contains 65 missing `FinalFruitN` values:

- 2020 HA: 1 of 30;
- 2021 HA: **50 of 50**;
- 2022 HC: 7 of 40;
- 2022 HL: 7 of 40.

Other missing values are `InitialFruitN=6`, `Height=12`,
`OvipN=13`, and `PredationR=162`. The six missing initial-fruit
observations also have missing final fruit count. All 12 missing heights
occur in **2022 HD**, among records labelled `Dadd01`–`Dadd12`.
Thus 620 rows with both fruit counts become 608 after the source's global
height exclusion. For HD specifically, this changes the differential and
female-gain NLS input from 139 to 127 rows.

As a diagnostic of potentially informative missingness, the raw mean
`FinalFruitN/HflowerN` is 0.517 in the 12 excluded HD records versus
0.398 among the 127 retained HD records. This comparison is descriptive,
not an independently estimated selection effect. The missing Height must
not be imputed to recreate the original fitted coefficients.

A separate numerical NLS check of `Fitness = a * HflowerN^b` recovered
HD `b=1.5297` from all 139 fruit-complete records and `b=1.5452`
from the original global-height-complete 127 records, restoring the
published rounded `b=1.55`. The source R-script reproduction remains
the authority for regression and uncertainty verification.

Do not interpret the 2021 HA gap as zero reproductive success.
Do not use the available `PredationR` fraction to silently reconstruct
unobserved `FinalFruitN`.

## Biological identifier collisions

Two different source rows share the same reported year, plot, and plant ID:

| Year | Plot | ID | Distinct source-row numbers |
| --- | --- | --- | --- |
| 2022 | HC | C769 | 344, 366 |
| 2023 | KD | KD769 | 514, 516 |

Their floral and/or reproductive measurements are **not identical**.
These rows remain separate records, bound to the exact
`source_row_number`. They cannot automatically be declared either
duplicate measurements or independent biological individuals.

The eventual fitted source-model grain must be checked against the
original analysis script/README before handling biological ID reuse.

## R1 reproduction boundary

The first R1 reproduction attempt (before correcting the omitted global
height exclusion)
(<https://github.com/zuizui0223/balance/actions/runs/37645118381>)
produced five plot-level summaries but did **not** exactly reproduce every
published coefficient; in particular the HD multivariable selection
gradient was not recovered. That result is an audit target, not evidence
that the published model has been reproduced.

The next source-faithful comparison must report:

1. exact model-specific row inclusion and any additional exclusions;
2. plot/year factor levels and references;
3. whether within-plot standardization occurs before or after exclusions;
4. the original model formula, weights, optimizer and random effects;
5. contrasts on the original link and fitness scales with explicit
   uncertainty;
6. a published-table tolerance comparison with remaining discrepancies.

The regression tests in this module enforce **row and missingness
integrity**, without choosing a model after observing coefficient signs.

## Scientific interpretation ceiling

Local changes in floral sex expression and predation pressure are a
biological question, but the data do not by themselves measure both
optimized shared and differentiated architectures on a common
fitness scale. This audit establishes neither direct BALANCE occupancy
nor hysteresis nor historical causation.

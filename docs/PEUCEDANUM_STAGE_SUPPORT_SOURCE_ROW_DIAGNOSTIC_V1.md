# Peucedanum stage-support source-row diagnostic, 2026-10-08

## Exact observations

The verified 685-row normalized 2025 survey has three cases with FinalFruitN > InitialFruitN:

| Year | Plot | Plant ID | Source row | HflowerN | InitialFruitN | FinalFruitN | OvipN | PredationR |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 2022 | HC | C763 | 356 | 29 | 21 | 22 | 0 | 0 |
| 2022 | KD | K752 | 481 | 62 | 41 | 46 | 0 | 0 |
| 2022 | KD | K961 | 498 | 78 | 28 | 29 | 0 | 0.03 |

All values are from the source-verified normalized CSV; source-row identities refer to the original All_Plots_Data.csv. This is a violation of the simple nested-binomial assumption, **not** proof of a data-entry error. The archived author R code models PredationR as its own binomial response with InitialFruitN weights; it does not establish that every individual's FinalFruitN is a strictly nested count of the earlier InitialFruitN.

## Sample support and descriptive ratios

685 total rows; initial-rate support 679; final-rate support 620; conditional-ratio support 547; egg-and-conditional-ratio support 535. Three of the 547 conditional-ratio rows have FinalFruitN > InitialFruitN. The 544 remaining nonviolating rows yield these aggregate final/initial ratios, using the sums of fruit counts (not the mean of individual ratios):

| Plot | Nonviolating rows | Sum initial | Sum final | Ratio |
|---|---:|---:|---:|---:|
| HA | 108 | 1619 | 397 | 0.2452 |
| HL | 86 | 1808 | 1037 | 0.5736 |
| HC | 108 | 2126 | 1327 | 0.6242 |
| KD | 126 | 2701 | 2421 | 0.8963 |
| HD | 116 | 2229 | 2095 | 0.9399 |

These are descriptive, **conditioned on observed initial/final counts and exclusion of 3 impossible nested counts**. They are not causal predation effects, year-standardized rates, or selection gradients. The 2021 HA final-fruit cell is missing.

## Consequence for model design

Do not force a two-stage nested-binomial survival model on all observations. Before fitting, check source definitions and whether InitialFruitN and FinalFruitN are counts from a strictly nested cohort. Three possible routes must be distinguished prospectively:

1. If nested counts are indeed required by the field protocol, adjudicate the three discrepancies against original records and hold conditional survival modeling pending resolution.
2. If counts arise from nonnested repeated observations, use a model for separate initial and final rates with joint within-individual uncertainty, rather than claiming each final fruit survived from a fixed initial trial pool.
3. For sensitivity only, analyze a 544-row nonviolating complete-case subset, explicitly report the exclusion and missingness selection, and never treat this restricted subset as an unbiased full-survey population.

The biological hypothesis is stage-specific change in floral allocation's fitness association; no new stage-selection coefficient or causal mediation has yet been estimated. Published R1 reproduction remains unresolved under Issue #215.

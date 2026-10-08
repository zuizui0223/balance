# Peucedanum 2025: R1 source-model concordance and ecological claim ceiling

## Why this route exists

The public Kudo & Shibata (2025) HUSCAP archive is source verified. Source-row support is frozen at 685 recorded observations, 620 fruit-complete rows before global Height exclusion and 608 female-outcome candidates after removing missing InitialFruitN/Height. The original source R script uses a paired formula for each final-fruit selection quantity:

- \`glmerMR\` and \`glmerDMR\`: quadratic predictors written as \`I(x^2)\`, with predictions on the response scale and within-plot means of \`p(1-p)\` for Janzen–Stern adjustment;
- \`glmerMR_t\` and \`glmerDMR_t\`: named-square \`x_2\` predictors for \`emmeans::emtrends\` estimation.

The reanalysis must reconstruct **both** models, on the same 608 source-eligible observations, rather than using only the named-square form for both jobs. The separate script \`ops/peucedanum_r1_reproduce.R\` implements this source-specific operation without claiming the original source R script ran unchanged.

The original source script SHA256 is \`6efb3a5b619166e0eb3ce491a67112c0009164456508093f513f4bc5c3a19d64\`; the outer ZIP is \`07d9f718d58b795553d50c2cb2b33e9a7dd3df9e34b5c1757ed55d5674c777ca\`; and the primary survey CSV is \`7ea5669a44bd4ebbdf8df3c2addbb28f230a7e6f970ccb2117e6dfb031d9d69f\`.

## Last verified source-global-filter fits, before this paired-form audit

The corrected pre-audit wrapper (GitHub Actions run 37729229347, R 4.6.1) recovered 13/15 published-precision point estimates:

| Plot | S estimated | S published | beta estimated | beta published | b estimated | b published |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| HA | -0.028017 | -0.027 | -0.035237 | -0.035 | 0.630984 | 0.63 |
| HL | -0.050992 | -0.051 | -0.028630 | -0.029 | 0.450303 | 0.45 |
| HC | +0.035941 | +0.036 | +0.033875 | +0.034 | 1.152326 | 1.15 |
| KD | +0.020650 | +0.021 | +0.008502 | +0.008 | 1.256814 | 1.26 |
| HD | +0.024360 | +0.024 | +0.026301 | +0.026 | 1.545192 | 1.55 |

Two discrepancies remain: HA S and KD beta, notwithstanding the matching coarse negative/positive sign pattern across plots. A second R4.4.2 run of the *same unpaired wrapper* (run 37744388764) retained those two discrepancies. This argues against a simple R-version explanation; it does **not** eliminate package-version, fit-approximation, table rounding/transcription, or model-routing causes.

The archived source excludes missing \`InitialFruitN\` and \`Height\` globally before *either* the differential or multivariable-gradient model and the gain curve. Missing \`FinalFruitN\` further restricts the reproductive-outcome fit. The archive's 2021 HA plot-year cell has 50 source records, but zero observed final-fruit outcomes. The 12 excluded HD Height records all occur in 2022. Two repeated plot-year-plant keys are **not** automatically deduplicated.

## Exact numerical audit

\`scripts/adjudicate_peucedanum_r1.py\` is an external comparator, not a parameter fitting script. It requires:

1. cryptographic match of the public ZIP and original source R-script bytes;
2. a recorded R 4.4.2 session;
3. the exact registered five-plot target ordering, frozen published targets, and fitted N for all three metrics;
4. published-precision match of *each* of 15 point estimates **and** 15 standard errors;
5. transparent residuals for all 30 estimates, with no hidden post-hoc tolerance expansion.

If anything is inconsistent, it raises an error or declares \`R1_NOT_FULLY_REPRODUCED\`. Even all 30 matches would be \`NUMERICALLY_CONCORDANT_PENDING_SOURCE_MODEL_VERIFICATION\`, **not** a promoted ecological result. Source-script implementation details and the comparability of the published SEs must still be independently audited.

## Ecological questions this may eventually support

The primary biological contrast is a reversal of the relationship between perfect-flower allocation and final fruit production across snowmelt-related contexts, with context-dependent herbivore/predator pressure a candidate explanation. To test *why* the reversal occurs requires disaggregating initial fertilization success, egg deposition and fruit survival on matched observational units, and accounting for year and plot structure. This dataset is potentially informative about **stage-dependent selection and antagonistic-mediated selection**, but cannot itself establish the fitness ranking of a differentiated architecture relative to an optimized shared architecture.

After complete original-model reproduction, preregister a source-consistent extension comparing:

- the same floral-allocation predictor's gradient for \`InitialFruitN/HflowerN\` versus \`FinalFruitN/HflowerN\`, with joint uncertainty;
- whether changes between those gradients track directly measured predation (\`OvipN\` or source \`PredationR\`) rather than plot order alone;
- whether the reversal persists when omitting individual years and when adjusting for plant size, recognizing unbalanced cells and unmeasured confounders.

Do **not** interpret either a stage gradient difference or the HL–HC published bracket as direct \`W_S^*\` versus \`W_D^*\` evidence. These quantities answer a selection-mediated ecological question but cannot identify architecture cost \`K\`, recoverable load \`R\`, historical trait splitting, or BALANCE occupancy.

## Execution

\`.github/workflows/reproduce-peucedanum-r1-source-concordance.yml\` fetches and verifies the exact archived source bytes, runs the paired-model wrapper in R 4.4.2, calls the stand-alone numeric audit, and uploads model estimates, session information, and the complete residual receipt. A green workflow means the **audit ran**, not that the published values all matched.

This route is separate from the frozen observational critical-region claim and does not alter the confirmatory V4 plant outcome schema or SLK/BITA scientific ownership.

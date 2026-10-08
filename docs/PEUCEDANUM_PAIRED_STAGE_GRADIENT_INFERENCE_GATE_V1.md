# Paired stage-gradient inference gate (Peucedanum)

The 18 plot-year exploratory slopes include four sign reversals. These are not yet tests of a statistically significant reversal.

## Current diagnostic
The paired outcome difference is D_i = FinalFruitN_i/HflowerN_i - InitialFruitN_i/HflowerN_i on individuals with both measurements. For each plot-year cell, fit a perfect-flower-count-weighted linear probability association with x_i = HflowerN_i/(HflowerN_i + MflowerN_i). Its slope equals beta_final - beta_initial under identical weights and sample. The script now reports a heteroskedasticity-consistent HC3 standard error of that **difference**, using within-individual paired residuals.

HC3 does not resolve ecological pseudoreplication, plot-year dependence, nonrandom missingness, or confounding by plant size. In particular, HflowerN is present in both predictor and denominators: mathematical coupling may generate associations without causal selection. No HC3 z-value is a preregistered significance decision.

## Next required controls before biological interpretation

1. Compare the perfect-flower fraction proxy with a predictor that does not algebraically reuse the fruit-rate denominator (e.g. standardized male flower count with perfect flower count as an explicit covariate), using source-consistent covariate support.
2. Evaluate absolute flower production, height, and their interactions; test whether the paired delta persists after size adjustment.
3. Use year-aware or hierarchical uncertainty, not a naive independence assumption for all 685 records.
4. Repeat excluding the three FinalFruitN > InitialFruitN source rows, then include them in a separate nonnested two-response model to quantify sensitivity. Do not alter original counts.
5. Treat 2021 HA as missing final-outcome support rather than zero selection.
6. Compare egg-count associations only after confirming overlap and temporality. Predator eggs may be a mediator, confounder proxy or post-outcome correlate.
7. Avoid multiplicity-driven selection of the four sign-changing cells; report all 18 cells and a pooled heterogeneity analysis.

This is an exploratory ecological stage-allocation question, not a test of BALANCE architecture occupancy or a substitute for unresolved published-coefficient reproduction (Issue #215).

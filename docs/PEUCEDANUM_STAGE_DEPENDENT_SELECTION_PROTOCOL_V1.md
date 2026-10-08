# Peucedanum: stage-specific selection versus antagonistic mediation (prospective design)

## Biological question

Can a floral allocation strategy that increases initial fertilization become disfavoured at final fruit production because predator damage removes its advantage? This is a **stage-dependent selection** question, not a direct BALANCE architecture-value test.

## Source and scope

Kudo & Shibata (2025), HUSCAP DOI 10.14943/hu95572. Exact 2025 survey: 685 records, 608 eligible final-fruit observations after the original global InitialFruitN and Height exclusions. The original five-plot R1 published-coefficient replication remains NOT_FULLY_REPRODUCED (13/15 point estimates and 14/15 SEs at published precision); do not substitute approximate estimates as validated publication reproduction.

The natural survey has perfect-flower count HflowerN, male-flower count MflowerN, initial fruit count InitialFruitN, final intact fruit count FinalFruitN, predator egg count OvipN, predation rate PredationR, Height, Plot and Year. It does not have individual flowering dates. The separate HA experimental file is not merged into the natural survey.

## Estimands

Define per individual i, plot p, year t:

- F_i = InitialFruitN_i / HflowerN_i, fertilization rate.
- Y_i = FinalFruitN_i / HflowerN_i, surviving fruit-set rate.
- Q_i = (InitialFruitN_i - FinalFruitN_i) / InitialFruitN_i, conditional post-fertilization loss **only when InitialFruitN > 0 and source count consistency is verified**.
- X_i = standardized perfect-flower allocation, using a frozen within-plot scaling convention. Condition on male-flower count and plant height in multivariable analyses.

Primary descriptive quantity: D_p = beta_final,p - beta_initial,p, the difference between plot-specific gradients on the **same response-probability scale**. Estimating two independently standardized binomial GLMM coefficients and subtracting them is invalid if adjustment scales differ. Prefer joint simulation or bootstrap of the entire two-stage model, preserving within-individual dependence and resampling by year/plot where support allows. Do not claim a causal selection gradient from D_p alone.

Secondary: model the conditional survival fraction FinalFruitN/InitialFruitN among individuals with InitialFruitN > 0 using initial fruits as binomial trials, with predeclared handling of impossible counts and structural missingness. Compare association of X with stage-specific loss and with OvipN, keeping OvipN as a potential mediator **and** a potentially confounded, post-allocation variable. Do not condition on OvipN in the primary total association.

## Predictions with falsifiers

H1, post-fertilization reversal: D_p is negative in at least one plot with positive beta_initial,p, with uncertainty excluding zero. Falsified if the apparent sign change is explained by uncertainty or if gradients stay aligned.

H2, predator-mediated loss: among otherwise comparable individuals, higher OvipN predicts lower conditional survival and statistically accounts for part of the stage gradient difference. This is **associational** unless the intervention or identification assumptions justify causality. Falsified if OvipN is unrelated to survival, or the stage reversal remains unchanged under a prespecified decomposition with sufficient overlap.

H3, environmental heterogeneity: the stage difference varies across plots after controlling year and size, rather than being a uniform physiological cost. Falsified if plot interactions are unsupported or unstable under leave-one-year-out checks. Plot order is not itself a measured continuous predation gradient.

## Required gates before inference

1. Preserve source-byte hashes and verify all counts satisfy 0 <= FinalFruitN <= InitialFruitN <= HflowerN when all three are observed; report violations without silently clipping.
2. Tabulate by plot x year the denominator and missingness for initial fertilization, final fruit, eggs and conditional loss. The 2021 HA cell has zero observed final fruits; it must not be imputed or treated as a complete panel.
3. Reproduce the original published coefficients (Issue #215) separately; new stage-specific estimates have an independent exploratory label and cannot retrospectively repair R1.
4. Freeze the scaling, predictor basis, random effects, binomial weighting, bootstrap unit and multiplicity policy **before inspecting stage-specific signs**.
5. Compare stage-specific associations with uncertainty. Perform leave-one-year-out checks where estimable, influence diagnostics and alternative missingness scenarios. Do not present naive individual bootstrap as independent temporal replication.
6. Do not claim architectural differentiation, recoverable loss R, architecture cost K, W_S*, W_D*, hysteresis or BALANCE occupancy.

## Decision tree

- If stage gradients change sign and loss associates with egg load: **candidate stage-dependent antagonistic selection**, not proven mediation.
- If gradients change sign but egg load does not explain loss: investigate other post-fertilization mechanisms and measurement/selection bias.
- If no robust sign change: report stage selection stability; do not rescue the narrative by searching additional thresholds.
- If outcome support is insufficient or counts violate the source-defined process: **NOT_IDENTIFIED**.

The novel ecological target is not the algebraic BALANCE region; it is whether the *same investment strategy* changes its fitness consequences between fertilization and post-predation survival, and under which observed antagonist contexts.

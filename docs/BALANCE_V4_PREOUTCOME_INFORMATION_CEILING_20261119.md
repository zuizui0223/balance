# V4 predictor information ceiling and primary-source dependence (2026-11-19)

## Scientific status

**New quantitative pre-outcome design diagnostic. No architecture response data, outcome coefficients, posterior draws, or independent human coder returns were opened.** This is an extension of the exact deletion audit in draft PR #272, not a change to the registered V4 response, priors, outcome classes, source admissions or cross-universe generality gate.

The question is whether 29 source-screened groups (U2=8, U6=21) can realistically resolve moderately sized architecture associations **even if the nominal design matrix has rank five**.

### Bound and assumptions

Consider a *hypothetical* binary response for each source-screened group, with unpenalized logistic model and the exact registered V4 five-column design:
```
X = [intercept_U2, intercept_U6,
     module_MODULAR, temporal_ORDERED_OR_ALTERNATING, temporal_VARIABLE_CONTEXT]
```
For independent Bernoulli measurements, conditional Fisher information is
```
I(beta) = X' diag(p_i (1-p_i)) X
       <= (1/4) X'X
```
in the positive-semidefinite order, because each `p_i(1-p_i) <= 1/4`. Therefore the inverse-information asymptotic variance lower bound for an **unpenalized binary logistic** coefficient is
```
Var(beta_hat_j) >= 4 [(X'X)^-1]_{jj}
SE(beta_hat_j)  >= 2 sqrt([(X'X)^-1]_{jj}).
```
The Gram inverse is calculated exactly with rational Gaussian elimination (no data-dependent outcomes). The idealized two-sided 95% Wald coefficient-magnitude threshold `1.96 * SE_floor` and its exp transform are shown only to expose the scale of information.

| Hypothetical binary coefficient | Exact diag((X'X)^-1) | Optimistic SE lower bound | Illustrative 95% Wald odds-ratio magnitude |
|---|---:|---:|---:|
| Pooled universe-adjusted MODULAR | 33/56 | 1.53530 | >20.27 |
| Pooled ORDERED/ALTERNATING | 7/24 | 1.08012 | >8.31 |
| Pooled VARIABLE_CONTEXT | 33/56 | 1.53530 | >20.27 |
| U2-only MODULAR (U2 nuisance slopes retained) | 3/4 | 1.73205 | >29.81 |
| U2-only ORDERED/ALTERNATING | 7/6 | 2.16025 | >69.00 |
| U6-only ORDERED/ALTERNATING | 7/18 | 1.24722 | >11.53 |

**Important ceiling:** This is not a statement that a real effect of any size cannot reach significance, and not a power calculation. The displayed ORs are the minimum *coefficient magnitude benchmarks* that would produce `|beta_hat| / SE >= 1.96` under the most optimistic hypothetical Fisher information; actual p values, finite-sample separation, estimated effects and MLE standard errors are unknown. The ideal maximum information is generally unattainable for a nonzero coefficient across all predictor profiles.

**It is not a bound on V4's Bayesian four-class multinomial posterior**, which has different likelihood, priors, uncertainty structure, contrasts in probabilities rather than log-odds, and may share information across categories. It does not incorporate phylogenetic covariance, field sampling, common-source correlation or outcome-class sparsity. Posterior priors may numerically shrink uncertainty without creating empirical information.

### Primary source dependence beyond biological groups

Re-read original `source_id` values for every source-screened predictor group. Using only the *first frozen admitting-source segment* of each source ID (before explicitly appended additional-source evidence, separated with ` | `), the 29 groups represent **28 distinct source keys**. One original primary programme is repeated:

```
Kirk (1987), Ecological Entomology, DOI 10.1111/j.1365-2311.1987.tb00982.x
    Actinidia deliciosa
    Echium plantagineum
```

The 28 keys are **not proof of 28 statistically independent research programmes**, because the audit neither rebuilds the entire multi-paper citation graph nor adjudicates shared institutions/experimental contexts. It does demonstrate one specific dependence that a naive 29-independent-study interpretation would miss.

Exact leave-one-admitting-source-key-out screening removes both Kirk species together. Across all 28 distinct keys:
- **0/28** leave-one-source deletions collapse the full five-column rank;
- **0/28** cause a failure of the source-screened >=2-per-primary-level design support rule.

Again these source-key exclusions are *predictor design sensitivity only*, not leave-one-source-effect analyses.

### Consequences for the ecological question

The current source-screened data permit a rank-valid model but do not yet support small, precisely estimated cross-context architecture differences. With the frozen U2/V4 predictors, the strongest model statement that could eventually be made depends on **observed source-independent outcome coding**, not this information calculation.

The registered strict G1 temporal generality claim still has U2 SINGLE+SIMULTANEOUS=1 (<2), U2 SINGLE+ORDERED=2, U6 SINGLE+SIMULTANEOUS=18 and U6 SINGLE+ORDERED=3. The frozen 12-group/36-slot U2 V2 expansion remains the only authorized prospective widening before architecture unblinding. More rows sampled from the already abundant U6 SINGLE+SIMULTANEOUS category will not directly repair the common-support gap.

Two scientifically distinct additions should be tracked:
1. **Within-domain claim:** get genuine blinded architecture classifications and enough class-specific groups to estimate the preregistered probability contrasts; null and reversed associations are fully reportable.
2. **Stronger generality claim:** independently expand source-qualified U2 SINGLE+SIMULTANEOUS/ORDERED comparisons with no outcome-selective coding, preserving the exact existing G1 >=2 gate, then demonstrate within-universe directional concordance rather than only a pooled coefficient.

### Reproduce

```bash
python scripts/audit_plant_v4_preoutcome_information.py
python -m pytest -q tests/test_plant_v4_preoutcome_information.py
```

This reads only the frozen U2 conflict-screen and U2/U6 source-side predictor receipts. The exact rational upper-information computation is independently protected by tests for the Gram inverse, U2-only and U6-only contrasts, shared Kirk source-key pairing, singular-matrix rejection and premature-adjudication rejection.

**Claim ceiling:** source-side design geometry and an optimistic binary information bound, not an architecture result, evolutionary effect, direct BALANCE worldline or claim of power for the four-class model.

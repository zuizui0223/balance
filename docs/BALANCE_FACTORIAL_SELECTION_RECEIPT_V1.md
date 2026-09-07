# BALANCE factorial selection receipt v1

## Purpose

This receipt freezes the quantitative transform used by the Chapter-2 diffuse-factorial R layer. It is designed for experiments in which two selective agents are manipulated in a `2 × 2` factorial design and each agent-mediated selection effect may depend on the state of the other agent.

The motivating current example is the `Fragaria vesca` pollination × herbivory experiment, but the receipt is biological-system agnostic.

This is a quantitative R-layer receipt. It is **not** a direct BALANCE occupancy receipt and does not identify `W_S*`, `W_D*`, `rho`, `Phi`, `xi`, or `d_B`.

## Treatment-slope order

For one registered trait and one common fitness measure, write the four treatment-specific directional selection slopes as

```text
b = (
    beta_open_antagonist_present,
    beta_supplemented_antagonist_present,
    beta_open_antagonist_absent,
    beta_supplemented_antagonist_absent
)
```

The code freezes this order as `TREATMENT_ORDER`.

For the Fragaria mapping:

```text
open          = ambient/open pollination
supplemented  = supplemental hand pollination
antagonist    = herbivory
fitness       = common fertilized-seed output
```

## Registered mediated contrasts

The dependent agent-mediated contrast vector is

```text
theta = C b
```

with

```text
C = [ 1 -1  0  0 ]   pollinator | antagonist present
    [ 0  0  1 -1 ]   pollinator | antagonist absent
    [ 1  0 -1  0 ]   antagonist | open pollination
    [ 0  1  0 -1 ]   antagonist | supplemented pollination
```

The signs are treatment-difference conventions. Biological interpretation should therefore report the registered contrast label together with the estimate rather than relying on sign alone.

The code freezes the output order as `CONTRAST_ORDER`.

## Joint uncertainty

If the fitted model supplies the joint covariance matrix of the four treatment slopes,

```text
V = Var(b),
```

then the correct multicontrast covariance is

```text
Var(theta) = C V C^T.
```

The four mediated contrasts are statistically dependent. Their off-diagonal covariance is part of the estimand and must be retained in any synthesis.

A set of four marginal standard errors is **not** sufficient to reconstruct `V`. In particular, the following shortcut is prohibited:

```text
V := diag(SE_1^2, SE_2^2, SE_3^2, SE_4^2)
```

unless the off-diagonal zeros are genuinely supplied by the fitted joint model. Missing covariance is never silently set to zero.

## Accepted covariance provenance

`analyze_factorial_agent_selection` promotes a receipt to joint-multicontrast readiness only when the full covariance matrix is supplied with one of two registered provenance labels:

```text
joint_model
raw_bootstrap
```

Interpretation:

- `joint_model`: covariance recovered from the same fitted model / contrast system that generated the treatment slopes;
- `raw_bootstrap`: covariance estimated by refitting the registered analysis to raw-data bootstrap replicates.

A label such as `independent_standard_errors` is explicitly rejected.

## Interaction contrast

The `2 × 2` interaction contrast is

```text
I = beta_open,H
    - beta_supplemented,H
    - beta_open,A
    + beta_supplemented,A.
```

Equivalently,

```text
I = (pollinator | H) - (pollinator | A)
  = (antagonist | open) - (antagonist | supplemented).
```

Its uncertainty is propagated from the same joint covariance matrix. A non-zero interaction means that the mediated selection effect of one agent changes with the state of the other agent; that is exactly why such a study belongs in the diffuse-factorial Q1B stratum rather than being cherry-picked into one scalar simple-Q1 pair.

## Receipt states

### `POINT_ESTIMATES_ONLY_NOT_READY`

Returned when the four treatment slopes are available but no registered joint covariance is supplied.

The receipt may support a qualitative or point-estimate pattern statement, but it is not an effect-size-ready multicontrast object.

### `JOINT_MULTICONTRAST_READY`

Returned only when the treatment slopes and a valid full covariance matrix with registered provenance are supplied.

The receipt then carries:

```text
four treatment slopes
four mediated contrasts
full 4 × 4 contrast covariance
four contrast standard errors
interaction contrast
interaction standard error
covariance provenance
```

This state makes one study quantitatively usable inside the registered Q1B estimand. It does **not** make the Q1B meta-analytic stratum itself ready; the stratum separately requires independent replication according to `BALANCE_QUANTITATIVE_STRATA_V1.csv`.

## Fragaria current status

The merged Fragaria evidence supplies a high-confidence `CONFLICT_WITHOUT_SPLITTING` pattern and motivates one Q1B candidate. The publication and public supplement/raw-data sources support a full factorial analysis, but the repository has not yet recovered the exact joint covariance needed by this receipt.

Therefore the current registered state remains:

```text
DIFFUSE_FACTORIAL_AGENT_SELECTION
registered_pattern_candidates = 1
effect_size_ready_clusters    = 0
pooling_status                 = NOT_READY_FULL_MULTICONTRAST_COVARIANCE_REQUIRED
```

The next quantitative gate is:

1. recover the exact treatment-slope estimates from the registered supplement or reproduce them from Dryad raw data;
2. recover model-based joint covariance or estimate it by registered raw-data bootstrap;
3. pass those objects through `analyze_factorial_agent_selection`;
4. promote the study to effect-size-ready only if the returned state is `JOINT_MULTICONTRAST_READY`;
5. retain the entire dependent contrast vector in synthesis.

## Claim ceiling

This receipt quantifies context-dependent agent-mediated selection on one trait and one common fitness scale. It does not by itself identify a shared-versus-differentiated architecture worldline comparison, a BALANCE reserve, historical differentiation, or a critical architecture threshold.

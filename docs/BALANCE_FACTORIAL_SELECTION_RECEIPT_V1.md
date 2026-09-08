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

## Joint uncertainty from a fitted model or bootstrap

If the fitted model supplies the joint covariance matrix of the four treatment slopes,

```text
V = Var(b),
```

then

```text
Var(theta) = C V C^T.
```

The four mediated contrasts are statistically dependent. Their off-diagonal covariance is part of the estimand and must be retained in any synthesis.

A set of four marginal standard errors alone is **not** sufficient to reconstruct `V`. In particular, the shortcut

```text
V := diag(SE_1^2, SE_2^2, SE_3^2, SE_4^2)
```

is prohibited unless those off-diagonal zeros are actually supplied by the joint model.

`analyze_factorial_agent_selection` therefore accepts a full covariance only with registered provenance:

```text
joint_model
raw_bootstrap
```

and rejects labels such as `independent_standard_errors`.

## Reported sufficient-statistics route

A separate fail-closed route is now available for publications that report linearly dependent factorial contrasts rather than the treatment-slope covariance itself.

`reconstruct_reported_factorial_contrasts` in `balance_domain/reported_factorial.py` requires all of the following:

1. all four registered mediated contrasts;
2. all four marginal SEs;
3. a shared factorial diagonal contrast and its SE;
4. a positive one-degree-of-freedom interaction `F` statistic;
5. exact closure of the reported point estimates under the 2×2 factorial identities;
6. a reconstructed covariance that satisfies the factorial null direction and is positive semidefinite.

For registered contrasts `a,b,c,d`, the identities are

```text
a + d = b + c = y
a - b = c - d = q.
```

The four marginal variances, `Var(y)`, and `Var(q)=q^2/F` identify all pairwise covariances. This is algebraic identification from source-reported sufficient statistics, not an independence assumption.

The returned state is

`REPORTED_FACTORIAL_JOINT_COVARIANCE_READY`.

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

A non-zero interaction means that the mediated selection effect of one agent changes with the state of the other agent; this is why diffuse-factorial studies remain separate from the simple scalar Q1 stratum.

## Receipt states

### `POINT_ESTIMATES_ONLY_NOT_READY`

Four treatment slopes are available but no registered joint covariance is supplied.

### `JOINT_MULTICONTRAST_READY`

Treatment slopes plus a valid full covariance from a joint model or raw bootstrap are supplied.

### `REPORTED_FACTORIAL_JOINT_COVARIANCE_READY`

A complete set of source-reported factorial sufficient statistics identifies the same dependent multicontrast covariance without raw-data covariance output.

Both ready states make **one study** quantitatively usable inside the registered Q1B estimand. Neither makes the meta-analytic stratum pool-ready by itself.

## Fragaria current status

The public supplement now closes the reported-statistics route for `Fragaria vesca` inflorescence density. Table S2 provides the four mediated contrasts, their SEs, and the shared diagonal `OP - HA`; Table S3 provides the one-df interaction `F` statistic. The reconstructed full covariance is PSD, rank 3 as expected from the exact factorial identity, and contains substantial nonzero off-diagonal terms.

The frozen result is in:

- `data/BALANCE_FRAGARIA_Q1B_RECEIPT_V1.json`;
- `docs/BALANCE_FRAGARIA_Q1B_REPORTED_COVARIANCE_RECEIPT_V1.md`.

Current registered state:

```text
DIFFUSE_FACTORIAL_AGENT_SELECTION
registered_pattern_candidates = 1
reanalysis_candidates         = 1  # Trifolium negative control
effect_size_ready_clusters    = 1  # Fragaria
minimum positive clusters     = 3
pooling_status                 = NOT_READY_ONLY_ONE_EFFECT_READY_POSITIVE_CLUSTER
```

The next gate is independent positive factorial replication. A raw-data bootstrap of Fragaria remains useful as sensitivity analysis but is no longer a prerequisite for this source-reported receipt.

## Claim ceiling

This receipt quantifies context-dependent agent-mediated selection on one trait and one common fitness scale. It does not by itself identify a shared-versus-differentiated architecture worldline comparison, a BALANCE reserve, historical differentiation, or a critical architecture threshold.

# BALANCE Fragaria Q1B reported-covariance receipt v1

## Purpose

This receipt promotes the `Fragaria vesca` Egan et al. (2021) diffuse-factorial selection study from a qualitative Q1B candidate to the first **effect-size-ready Q1B cluster** without assuming independent contrasts or setting unreported covariance terms to zero.

The promotion remains in the Chapter-2 **R layer**. It is a quantitative selection-pattern receipt, not direct BALANCE occupancy and not a direct comparison of `W_S*` and `W_D*`.

## Source

Egan PA, Muola A, Parachnowitsch AL, Stenberg JA. 2021. *Pollinators and herbivores interactively shape selection on strawberry defence and attraction.* Evolution Letters 5:636–643. DOI `10.1002/evl3.262`.

Public data DOI: `10.5061/dryad.1rn8pk0vn`.

The source supplement was recovered through the public PMC article record as `EVL3-5-636-s001.docx`. No source table is copied into the repository; only the registered numerical sufficient statistics and the project reconstruction are retained.

## Registered trait and fitness scale

Trait: `inflorescence_density`.

Common fitness scale: total fertilized seed output.

The full-factorial design crossed pollination state with herbivory state. Q1B therefore retains all four context-specific agent-mediated contrasts rather than selecting one convenient pair.

## Source-reported sufficient statistics

Table S2 reports the following contrasts and marginal standard errors in registered order:

| Registered contrast | Estimate | SE |
|---|---:|---:|
| pollinator-mediated selection given herbivores present | -0.022 | 0.314 |
| pollinator-mediated selection given herbivores absent | 0.572 | 0.224 |
| herbivore-mediated selection under open / pollen-limited pollination | -0.391 | 0.125 |
| herbivore-mediated selection under supplemented pollination | 0.203 | 0.365 |

Table S2 also reports the shared diagonal contrast

`OP - HA = 0.181 ± 0.213`.

The two paths through the factorial square close exactly at the reported precision:

```text
-0.022 + 0.203 = 0.181
 0.572 - 0.391 = 0.181
```

The interaction contrast is likewise identified in two equivalent ways:

```text
q = -0.022 - 0.572 = -0.594
q = -0.391 - 0.203 = -0.594
```

Table S3 reports the `inflorescence density × pollination × herbivory` one-degree-of-freedom interaction test `F = 2.366`. Therefore

```text
Var(q) = q^2 / F
SE(q) = 0.3861704825451837
```

## Why the joint covariance is identified

Write the four registered contrasts as

```text
a = P | H present
b = P | H absent
c = H | open
 d = H | supplemented
```

The 2×2 factorial geometry gives the exact linear identities

```text
a + d = b + c = y
a - b = c - d = q
```

The four marginal variances, `Var(y)` from the reported diagonal SE, and `Var(q)` from the reported one-df interaction test identify four pairwise covariances directly:

```text
Cov(a,d) = [Var(y) - Var(a) - Var(d)] / 2
Cov(b,c) = [Var(y) - Var(b) - Var(c)] / 2
Cov(a,b) = [Var(a) + Var(b) - Var(q)] / 2
Cov(c,d) = [Var(c) + Var(d) - Var(q)] / 2
```

The null identity `a - b - c + d = 0` then identifies the remaining two covariances. No covariance is assigned zero by assumption.

The reconstructed covariance is

```text
[[ 0.098596,             -0.000177820794590014,  0.005547820794590035, -0.093226             ],
 [-0.000177820794590014,  0.050176,             -0.010216,              0.040137820794590016],
 [ 0.005547820794590035, -0.010216,              0.015625,             -0.00013882079459003743],
 [-0.093226,              0.040137820794590016, -0.00013882079459003743, 0.133225            ]]
```

Several off-diagonal terms are materially nonzero, especially `Cov(a,d) = -0.093226`, so the result is not equivalent to an independence shortcut.

The covariance is positive semidefinite and rank 3. Rank 3 is expected, not a defect: the four registered contrasts obey one exact factorial linear identity.

## Registered interpretation

The receipt state is

`EFFECT_SIZE_READY_REPORTED_FACTORIAL_RECONSTRUCTION`.

This means one positive Q1B cluster now has a fully registered dependent multicontrast estimate and joint uncertainty. It does **not** make the Q1B stratum pool-ready because the preregistered minimum is three independent positive clusters.

Current Q1B bookkeeping after this receipt:

```text
positive registered clusters = 1
negative/control reanalysis clusters = 1
positive effect-size-ready clusters = 1
minimum independent positive clusters for pooling = 3
pooling = NOT READY
```

`Trifolium repens` remains a design-matched negative control and does not enter the positive numerator.

## Claim ceiling

This receipt supports a quantitative, context-dependent pollinator-versus-herbivore selection pattern on one common reproductive-fitness scale.

It does not identify direct BALANCE quantities:

- `W_S*`;
- `W_D*`;
- `rho`;
- `Phi`;
- `xi`;
- `d_B`.

A raw-data bootstrap remains a useful sensitivity analysis if the deposited individual-level data can be recovered cleanly, but it is no longer required to establish the source-reported Q1B joint covariance because the published sufficient statistics already identify it.

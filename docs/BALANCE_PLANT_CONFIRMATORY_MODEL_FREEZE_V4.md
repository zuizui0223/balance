# BALANCE plant confirmatory model freeze v4

## Status

Frozen before U6 independent architecture coding and before any confirmatory routing fit.

V4 supersedes V3 because the pre-outcome cross-universe support audit showed that the
three primary literature universes are not exchangeable for routing inference.

## Programme roles

### U1 — broad specificity validation

The frozen U1 review universe is broad herbivory-pollination literature.

Current source screen:

```text
47 groups
0 strict conflict positive
46 no demonstrated conflict
1 aligned no conflict
```

U1 remains essential for testing the specificity of the BALANCE conflict definition.

It is **not** part of the V4 routing fit.

If independent U1 coding later produces conflict-positive cases, they are reported as
external validation/sensitivity cases rather than being injected post hoc into the V4
denominator.

### U2 — mechanism-targeted sexual interference

```text
8 source-screen conflict-positive groups
```

### U6 — conflict-first pollen theft

```text
21 frozen conflict-first groups
```

U2 and U6 are the two V4 primary routing universes.

## Why universe stratification is needed

Pre-outcome predictor support is:

```text
module opportunity
             U2   U6
SINGLE        5   21
MODULAR       3    0

temporal exposure
                         U2   U6
SIMULTANEOUS              3   18
ORDERED_OR_ALTERNATING    2    3
VARIABLE_CONTEXT          3    0

spatial exposure
             U2   U6
SAME_UNIT      7   21
DISTRIBUTED    1    0
```

Thus baseline architecture distributions from the two sampling universes must not be
silently absorbed into predictor slopes.

V4 uses a separate multinomial intercept for U2 and U6 while retaining common predictor
slopes.

## Primary response

Unchanged:

```text
SHARED
NONSTRUCTURAL_SEPARATION
STRUCTURAL_MODULE_DIVISION
MOSAIC
```

Reference class:

```text
SHARED
```

## Raw predictor coding

Unchanged and mandatory:

```text
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

## Primary predictor contrasts

### Module opportunity

```text
SINGLE
MODULAR
```

### Temporal exposure

```text
SIMULTANEOUS
ORDERED_OR_ALTERNATING
VARIABLE_CONTEXT
```

### Spatial exposure

Retained as a secondary axis because the pre-outcome support is 28 SAME_UNIT versus
1 DISTRIBUTED dependence block.

## V4 primary model

For row (i) in sampling universe (u_i):

```text
architecture_class4_i
~ multinomial_logit(
    alpha[universe_i]
    + beta_module * module_opportunity2_i
    + beta_ordered * temporal_ORDERED_i
    + beta_variable * temporal_VARIABLE_i
  )
```

There are separate non-reference intercept vectors for U2 and U6.

Common slopes are used for the primary model.

## Priors

```text
universe-specific non-reference intercepts:
  Normal(0, 1.5)

common slopes:
  Normal(0, 0.75)
```

Prior sensitivity:

```text
common slopes:
  Normal(0, 1.5)
```

## Parameter budget at the frozen two-universe design

Four response classes imply three non-reference logits.

```text
U2 intercepts                       3
U6 intercepts                       3
module slope                        3
ORDERED temporal slope              3
VARIABLE_CONTEXT temporal slope     3
--------------------------------------
total                              15
```

This remains far below the V1 raw-category model and directly controls sampling-frame
baseline differences.

## Estimability gate

Before fitting:

```text
U2 present with >= 2 licensed dependence blocks
U6 present with >= 2 licensed dependence blocks

every architecture response class
  >= 2 independent dependence blocks overall

module SINGLE and MODULAR
  each >= 2 independent dependence blocks overall

temporal SIMULTANEOUS
temporal ORDERED_OR_ALTERNATING
temporal VARIABLE_CONTEXT
  each >= 2 independent dependence blocks overall

common-slope design matrix
  full rank

full U2/U6-intercept + common-slope design matrix
  full rank
```

This second rank check prevents a predictor that is perfectly determined by sampling
universe from masquerading as an estimable common biological slope.

Failure action:

```text
DO_NOT_FIT_OR_DROP_TERMS_POST_HOC
```

## Generality hierarchy

### Cross-universe replicated candidate

Only one current two-level contrast has both sides represented independently in U2 and U6:

```text
SIMULTANEOUS
vs
ORDERED_OR_ALTERNATING
```

Marginally, both timing levels occur in U2 and U6. That is not sufficient for a
generality test because module opportunity is distributed differently across the two
universes.

The frozen stricter gate requires at least one **shared module-opportunity stratum** with:

```text
>= 2 SIMULTANEOUS blocks in U2
>= 2 ORDERED_OR_ALTERNATING blocks in U2
>= 2 SIMULTANEOUS blocks in U6
>= 2 ORDERED_OR_ALTERNATING blocks in U6
```

At the current source-screen freeze the only shared module stratum is `SINGLE`:

```text
             U2   U6
SIMULTANEOUS  1   18
ORDERED       2    3
```

Therefore the strict cross-universe temporal generality sensitivity is **not yet
estimable prospectively**, even though the marginal timing contrast is represented in both
universes.

A future generality statement requires the common-support gate to pass after independent
adjudication, reporting the contrast separately in U2 and U6, and checking that a pooled
interpretation is not contradicted by a practically large universe-by-timing interaction.

### U2-anchored candidate

```text
module SINGLE vs MODULAR
VARIABLE_CONTEXT timing contrasts
```

These are estimable from U2 variation but cannot currently support a cross-universe
generality claim because U6 lacks the second level.

### Support-limited

```text
spatial SAME_UNIT vs DISTRIBUTED
```

This remains secondary.

## Registered interaction extension

```text
universe-stratified intercept
+ module_opportunity2 * temporal_exposure3
```

At two universes:

```text
21 coefficients
```

The interaction is fit only if required cells are supported.

## U1 external-validation rule

U1 independent coding remains required for the specificity claim.

However:

```text
U1 adjudicated positive cases
!= automatic V4 model rows
```

Any such cases are reported as prospective external validation of the U2/U6 result under
the same codebook and claim ceiling.

This rule is frozen before independent U1 coding is completed.

## Spatial reporting

Mandatory even though secondary:

1. raw spatial-geometry support table;
2. architecture class by spatial exposure;
3. U2/U6 spatial support separately;
4. spatial-only sensitivity only if final DISTRIBUTED support reaches at least two
   independent blocks.

## Claim ceiling

V4 can support comparative routing associations in two independently defined
conflict-focused plant literature universes.

Only the temporal simultaneous-versus-ordered contrast is currently positioned for a
cross-universe generality test.

V4 does not identify causal historical transitions, natural angiosperm prevalence, or
theoretical BALANCE parameters.

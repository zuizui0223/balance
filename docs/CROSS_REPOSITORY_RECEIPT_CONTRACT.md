# Cross-repository receipt contract

## Purpose

The three chapters must be able to analyse the same biological context without silently changing outcome scale, population, treatment window, or meaning of the architecture comparison.

The minimal matched receipt therefore freezes:

```text
context_id
fitness_scale_id
```

before any chapter-specific inference.

## Required SCH-facing fields

```text
conflict_load.lower
conflict_load.upper
```

The interval must be on the same registered reproductive-fitness scale used for the architecture comparison. Chapter 2 calls conflict identified only when the entire interval is above zero.

State-specific optima such as `z_P*`, `z_G*`, and `z_C*` can accompany the receipt, but they are not silently relabelled as pure function optima.

## Required direct BALANCE fields

```text
shared_optimum_fitness.lower
shared_optimum_fitness.upper

differentiated_optimum_fitness.lower
differentiated_optimum_fitness.upper
```

The direct architecture-gap interval is

```text
Delta_W = W_D* - W_S*.
```

Strong Chapter-2 classifications are:

```text
L.lower > 0 and Delta_W.upper < 0
    -> BALANCE_IDENTIFIED

L.lower > 0 and Delta_W.lower > 0
    -> BITA_SIDE_IDENTIFIED

L.lower > 0 and Delta_W contains 0
    -> ARCHITECTURE_ORDER_UNRESOLVED.
```

Thus uncertainty is not collapsed to a point estimate merely to assign a chapter state.

## Optional BITA decomposition fields

```text
decoupling.lower
decoupling.upper
architecture_cost.lower
architecture_cost.upper
```

These generate a bounded decomposed gap

```text
Phi = sL-K
```

and the bridge residual

```text
delta_parallel = Delta_W-Phi.
```

If the residual interval contains zero, the direct and decomposed views remain compatible. If it excludes zero, the mismatch is retained explicitly.

## Interpretation of a non-zero bridge residual

A non-zero residual is not automatically biological evidence for a new parallel world. Audit, in order:

1. outcome/fitness-scale mismatch;
2. unmatched population, season, life stage, or generation;
3. different architecture-cost definitions;
4. omitted direct/background or ecological channels;
5. estimation or optimization mismatch;
6. only then, a genuine change in the effective fitness landscape between the shared and differentiated architecture states.

## Recommended biological chain

```text
SCH
context_id + fitness_scale_id
+ positive conflict receipt
+ shared optimum geometry
        ↓
BALANCE
direct matched W_S* versus W_D*
+ state / domain / reserve / topology
        ↓
BITA
s,K decomposition
+ dimensional release
+ mechanism identification
        ↓
BALANCE concordance audit
direct Delta_W versus decomposed sL-K
+ same versus parallel critical-point test.
```

The flow is intentionally not one-way: Chapter 2 is the reconciliation layer between the two worldline definitions as well as the middle ecological regime between them.

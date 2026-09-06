# Cross-repository receipt contract

## Purpose

The three chapters must be able to analyse the same biological context without silently changing outcome scale, population, treatment window, or meaning of the architecture comparison.

The implemented SCH-facing interface is now:

```text
THREE_WORLD_CONFLICT_HANDOFF_V1
```

SCH exports it, BALANCE validates it, and BITA's stronger projection wrapper requires an exact match before evaluating `sL-K`.

The minimal matched identity is:

```text
context_id
system
population_id
season_id
fitness_scale_id
```

before any chapter-specific inference. The same `context_id` and `fitness_scale_id` must survive unchanged across all three chapters.

## Required SCH-facing fields

The handoff carries:

```text
conflict_load.point
conflict_load.lower_95
conflict_load.upper_95
```

The interval must be on the same registered reproductive-fitness scale used for the architecture comparison. Chapter 2 calls conflict identified only when the entire interval is above zero.

State-specific optima such as `z_P*`, `z_G*`, and `z_C*` can accompany upstream SCH provenance, but they are not silently relabelled as pure function optima.

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

## Implemented ownership

```text
SCH
scripts/export_three_world_conflict_handoff.py
-> exports context-locked THREE_WORLD_CONFLICT_HANDOFF_V1

BALANCE
balance_domain/handoff.py
-> validates context, scale, provenance and L interval

BITA
scripts/project_three_world_handoff_into_bita.py
-> requires exact context + scale before reusing the registered sL-K projection
```

The legacy `SCH_COMPONENT_CONFLICT_BUDGET_V1` and BITA projection remain intact; the three-world handoff is an additive stronger interface.

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
context-locked THREE_WORLD_CONFLICT_HANDOFF_V1
+ positive conflict receipt
+ shared optimum geometry
        ↓
BALANCE
direct matched W_S* versus W_D*
+ state / domain / reserve / topology
        ↓
BITA
same context_id + fitness_scale_id
+ s,K decomposition
+ dimensional release
+ mechanism identification
        ↓
BALANCE concordance audit
direct Delta_W versus decomposed sL-K
+ same versus parallel critical-point test.
```

The flow is intentionally not one-way: Chapter 2 is the reconciliation layer between the two worldline definitions as well as the middle ecological regime between them.

## End-to-end regression fixture

`empirical/interface/THREE_WORLD_SYNTHETIC_FIXTURE_V1.json` fixes one synthetic Pedicularis context and demonstrates that:

```text
SCH conflict interval
+ BALANCE direct worldline gap
+ BITA-compatible s,K decomposition
```

can produce the same negative architecture margin without changing context or scale. This fixture is a software contract only and is not an empirical Pedicularis result.

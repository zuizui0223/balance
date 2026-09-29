# BALANCE plant confirmatory model freeze v3

> **Superseded before architecture coding by v4.** The pre-outcome cross-universe audit showed that module MODULAR and temporal VARIABLE_CONTEXT support are U2-only, whereas SIMULTANEOUS-vs-ORDERED timing is replicated in U2 and U6. V4 fixes the primary routing fit to conflict-focused U2+U6 and adds sampling-universe-stratified multinomial intercepts. See `docs/BALANCE_PLANT_CONFIRMATORY_MODEL_FREEZE_V4.md`.

## Status

Frozen before U6 independent architecture coding and before any confirmatory plant model fit.

V3 supersedes V2 for one pre-outcome reason: the frozen source-screened predictor surface
contains only one `DISTRIBUTED` spatial-exposure dependence group across the current
conflict-positive U2+U6 evidence surface.

The four-class response and all raw predictor coding remain unchanged.

## Pre-outcome support audit

Current source-screened conflict-positive groups:

```text
U2   8
U6  21
total 29
```

Frozen primary-contrast support:

```text
module_opportunity2
  SINGLE   26
  MODULAR   3

temporal_exposure3
  SIMULTANEOUS             21
  ORDERED_OR_ALTERNATING    5
  VARIABLE_CONTEXT          3

spatial_exposure2
  SAME_UNIT                28
  DISTRIBUTED               1
```

No architecture outcome was used to obtain these counts.

The spatial axis is therefore under-supported for a joint primary coefficient. Keeping it
in the V2 primary model would make one dependence block carry the entire distributed-side
contrast.

## Primary scientific question

V3 focuses the confirmatory model on two preregistered causal-opportunity axes:

> Does pre-existing module opportunity and the temporal geometry of conflict exposure
> predict whether conflict remains shared, separates nonstructurally, divides labour
> structurally, or remains mosaic?

Spatial exposure remains scientifically recorded and is reported as a secondary support
axis rather than silently discarded.

## Response

Unchanged:

```text
SHARED
NONSTRUCTURAL_SEPARATION
STRUCTURAL_MODULE_DIVISION
MOSAIC
```

## Raw predictors

Unchanged:

```text
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

Raw categories remain source-auditable and are not overwritten by the primary contrasts.

## Primary contrasts

### Module opportunity

```text
SINGLE
  SINGLE_OR_CONTINUOUS

MODULAR
  SERIAL_WITHIN_FLOWER
  REPEATED_FLOWERS
  PREEXISTING_SEPARATE_ORGANS
  MULTILEVEL
```

### Temporal exposure

```text
SIMULTANEOUS
  SIMULTANEOUS

ORDERED_OR_ALTERNATING
  SEQUENTIAL_WITHIN_UNIT
  SEASONALLY_ALTERNATING

VARIABLE_CONTEXT
  CONTEXT_DEPENDENT
  MIXED
```

## Secondary spatial contrast

```text
SAME_UNIT
  SAME_UNIT

DISTRIBUTED
  BETWEEN_MODULES
  AMONG_INDIVIDUALS
  AMONG_POPULATIONS
  ENVIRONMENTAL_MOSAIC
  MIXED
```

Spatial coding is mandatory, but it is not a primary joint fixed effect under the frozen
current support.

A separate spatial sensitivity can run only if final independently adjudicated data contain
at least two independent `DISTRIBUTED` dependence blocks.

## Parameter budget

### Historical V1 raw joint model

```text
42 fixed coefficients before conflict-family adjustment
```

### V2 low-dimensional three-axis model

```text
15 fixed coefficients
```

### V3 primary model

```text
intercept                    1
module_opportunity2          1
temporal_exposure3           2
------------------------------
columns per logit            4

4 columns x 3 non-reference logits = 12 fixed coefficients
```

### Registered interaction

```text
module_opportunity2 x temporal_exposure3

6 columns/logit x 3 logits = 18 fixed coefficients
```

## Primary model

```text
regularized Bayesian multinomial logit

architecture_class4
~ module_opportunity2
+ temporal_exposure3
```

Reference response:

```text
SHARED
```

Priors remain:

```text
slope coefficients:
  Normal(0, 0.75)

non-reference intercepts:
  Normal(0, 1.5)
```

Sensitivity:

```text
slope coefficients:
  Normal(0, 1.5)
```

## Estimability gate

Before fitting:

```text
every response class
  >= 2 independent dependence blocks

every level of module_opportunity2
  >= 2 independent dependence blocks

every level of temporal_exposure3
  >= 2 independent dependence blocks

primary design matrix
  full rank
```

Failure action:

```text
DO_NOT_FIT_OR_DROP_TERMS_POST_HOC
```

This prevents a sparse predictor from being deleted because its coefficient is inconvenient.

## Registered primary contrasts

### Module opportunity

```text
P(STRUCTURAL_MODULE_DIVISION | MODULAR)
-
P(STRUCTURAL_MODULE_DIVISION | SINGLE)
```

### Temporal exposure

```text
P(NONSTRUCTURAL_SEPARATION | ORDERED_OR_ALTERNATING)
-
P(NONSTRUCTURAL_SEPARATION | SIMULTANEOUS)
```

### Module x timing

The registered interaction asks whether the structural-routing contrast for
`MODULAR - SINGLE` differs among temporal-exposure states.

The interaction is reported only where the required cells have empirical support.

## Spatial result under V3

Spatial exposure is not erased.

Mandatory outputs are:

1. raw `conflict_spatial_geometry` support table;
2. `spatial_exposure2` support by architecture class;
3. `spatial_exposure2` support by sampling universe;
4. a separate spatial-only regularized sensitivity only if at least two independent
   `DISTRIBUTED` blocks survive final adjudication.

If distributed support remains one block, the ecological conclusion is that spatial
generality is under-sampled in the registered literature surface.

## Conflict family

Conflict family remains a mandatory stratified / leave-universe-out sensitivity rather than
a primary sparse fixed effect.

## Primary denominator

Only:

```text
U1_HAAS_LORTIE_2020
U2_BARRETT_2002
U6_POLLEN_THEFT_HARGREAVES_2009
```

U3/U4/U5 do not enter the primary denominator.

## Claim ceiling

A successful V3 fit supports comparative association of module opportunity and temporal
conflict geometry with architecture routing in the frozen conflict-positive literature
surfaces.

It does not identify evolutionary transition probabilities, causal historical origins,
natural angiosperm prevalence, or theoretical BALANCE quantities.

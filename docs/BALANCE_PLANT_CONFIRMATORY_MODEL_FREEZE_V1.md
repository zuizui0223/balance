# BALANCE plant confirmatory model freeze v1

## Status

Frozen before any confirmatory plant model is fit.

This document supersedes the data-dependent "full nominal if adequate, four-class if sparse"
fallback logic. The primary response is fixed now so that response coarsening cannot depend
on which model gives a cleaner coefficient or smaller p-value.

Executable/specification surfaces:

- `balance_domain/plant_macro.py`
- `balance_domain/plant_confirmatory.py`
- `data/BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V1.json`
- `data/BALANCE_PLANT_CONFIRMATORY_PREDICTOR_RECEIPT_TEMPLATE_V1.csv`

## Scientific question

> Given independently established reproductive functional conflict, which pre-existing
> architectural and conflict-geometry features predict whether the system remains shared,
> separates functions without structural module division, divides labour structurally, or
> remains polymorphic/mosaic?

The algebraic BALANCE coordinates do not answer this question by definition.

## Primary population

A row enters the primary analysis only when all of the following are closed:

```text
unit_type in {SPECIES, SPECIES_CONTEXT}
adjudication_status = ADJUDICATED
conflict_status = POSITIVE
architecture_mode resolved
module_substrate independently adjudicated from an outcome-independent receipt
conflict_timing_geometry independently adjudicated from an outcome-independent receipt
conflict_spatial_geometry independently adjudicated from an outcome-independent receipt
```

A value written in the macro ledger is not sufficient by itself. The receipt value must
exist and match.

## Primary response: frozen four-class architecture routing

```text
SHARED
  SHARED_INTEGRATED

NONSTRUCTURAL_SEPARATION
  TEMPORAL_SEPARATION
  SPATIAL_SEPARATION
  SIGNAL_SEPARATION
  TEMPORAL_AND_SPATIAL_SEPARATION

STRUCTURAL_MODULE_DIVISION
  WITHIN_FLOWER_DIVISION_OF_LABOUR
  AMONG_FLOWER_MODULE_DIVISION

MOSAIC
  POLYMORPHIC_OR_MOSAIC
```

Two corrections are intentional.

First, `SIGNAL_SEPARATION` is explicitly retained in the nonstructural class; the previous
fallback table accidentally omitted it.

Second, `POLYMORPHIC_OR_MOSAIC` is primary-outcome eligible even though the derived binary
`structural_module_division` field is unresolved. The binary field is secondary and cannot
gate the nominal primary response.

## Primary predictors

Raw predictor categories are retained.

### Module substrate

```text
SINGLE_OR_CONTINUOUS
SERIAL_WITHIN_FLOWER
REPEATED_FLOWERS
PREEXISTING_SEPARATE_ORGANS
MULTILEVEL
```

### Timing geometry

```text
SIMULTANEOUS
SEQUENTIAL_WITHIN_UNIT
SEASONALLY_ALTERNATING
CONTEXT_DEPENDENT
MIXED
```

### Spatial geometry

```text
SAME_UNIT
BETWEEN_MODULES
AMONG_INDIVIDUALS
AMONG_POPULATIONS
ENVIRONMENTAL_MOSAIC
MIXED
```

`UNRESOLVED` is never promoted to the confirmatory model.

### Exposure geometry rule

For timing and spatial predictors, code the geometry in which the conflict is **expressed
before the focal resolution is credited**. Admissible evidence comes from an integrated
baseline or an experimental challenge that exposes the conflicting functions.

Examples:

- self pollen applied before or together with compatible pollen on the same stigma can
  identify sequential/mixed timing and same-unit spatial exposure;
- geitonogamy among simultaneously hermaphroditic flowers can identify between-flower
  exposure in the integrated baseline;
- observed protandry, herkogamy, flexistyly, or sexual segregation cannot by themselves
  define the timing/spatial predictor because those traits may be the response.

If no independent baseline/challenge geometry is available, the predictor stays
`UNRESOLVED`.

## Predictor independence rule

Predictor evidence can come from the same publication as the outcome, but it must be
logically independent of the focal architecture state.

Allowed evidence can include direct pre-outcome measurement, integrated-state experiments
or descriptions, developmental mechanism evidence, ancestral reconstruction, and
outcome-blinded sister-lineage evidence.

Forbidden shortcut:

```text
observed architecture
=> predictor value
```

Examples:

```text
heteranthery observed
!=>
SERIAL_WITHIN_FLOWER substrate was independently established

dichogamy observed
!=>
SEQUENTIAL_WITHIN_UNIT conflict timing was independently established

spatially separated organs observed
!=>
the competing demands were independently shown to act BETWEEN_MODULES
```

Outcome-derived receipts remain visible but must be marked
`outcome_independence=FALSE` and cannot license model entry.

## Primary model

The frozen primary model is:

```text
hierarchical multinomial

architecture_class4
~ module_substrate
+ conflict_timing_geometry
+ conflict_spatial_geometry
+ conflict_family
```

Biological dependency groups are not counted as independent replication. Repeated rows from
one dependency group require clustered/varying-intercept treatment or one frozen
representative row, depending on the final dependence ledger.

There is no significance-triggered fallback to a binary structural model.

If one primary response class is absent or nearly uninformative, that is reported as an
estimability limitation. The response is not recoded after seeing the fit.

## Registered interaction extensions

Interactions answer biologically distinct questions and are fit separately so the primary
model does not become an unidentifiable coefficient forest.

### I1 — module substrate x timing geometry

```text
architecture_class4
~ module_substrate * conflict_timing_geometry
+ conflict_spatial_geometry
+ conflict_family
```

Target: does pre-existing modularity route conflict differently when the competing demands
are simultaneous versus temporally structured?

Prospective directional contrast: the association between serial/repeated/multilevel
substrate and `STRUCTURAL_MODULE_DIVISION` should be stronger under simultaneous demand
than when a temporal partition is already available.

### I2 — module substrate x spatial geometry

```text
architecture_class4
~ module_substrate * conflict_spatial_geometry
+ conflict_timing_geometry
+ conflict_family
```

Target: does pre-existing modularity route conflict differently when demands act on the
same unit versus across modules, individuals, populations, or environmental mosaics?

Prospective directional contrasts:

- distributed conflict geometry should shift probability away from `SHARED`;
- among-population/environmental-mosaic geometry should particularly enrich `MOSAIC`;
- pre-existing separate organs plus between-module demand should enrich
  `NONSTRUCTURAL_SEPARATION` rather than being automatically called structural division.

I1 and I2 are both reported. Neither is selected because it gives a stronger result.

## Primary planned contrasts

The multinomial coefficients are not themselves the biological endpoint. Report predicted
probability contrasts on the observed predictor support.

1. temporally structured versus simultaneous demand:
   `P(NONSTRUCTURAL_SEPARATION) - P(SHARED)`;
2. serial/repeated/multilevel versus single/continuous substrate under simultaneous demand:
   `P(STRUCTURAL_MODULE_DIVISION) - P(SHARED)`;
3. population/environmental-mosaic versus same-unit spatial geometry:
   `P(MOSAIC) - P(SHARED)`;
4. pre-existing separate organs under between-module versus same-unit demand:
   `P(NONSTRUCTURAL_SEPARATION) - P(SHARED)`.

Contrasts unsupported by observed predictor overlap are reported as non-estimable rather
than extrapolated.

## Secondary analyses

### Binary structural model

`structural_module_division` is secondary and only uses rows coded true/false. It cannot
replace the four-class primary result.

### Full nominal architecture detail

The raw architecture categories remain available for descriptive or regularized secondary
analysis. This analysis can show whether temporal, spatial, signal, or combined separation
differ, but it does not replace the frozen primary estimand.

## Falsifiers and downgrade conditions

The programme is weakened, rather than rescued by recoding, if:

- independent coders cannot reproduce the three predictors at the registered reliability gate;
- outcome-independent receipts are unavailable for most conflict-positive systems;
- architecture routing shows no reproducible association with module substrate or conflict
  geometry;
- directional planned contrasts reverse consistently across independent conflict families;
- estimates depend entirely on one review universe or one dependency block;
- predictor overlap is too poor to support the planned contrasts.

A null or imprecise association is a scientific result under the frozen design, not a reason
to invent a new architecture ordering.

## Claim ceiling

The design supports comparative associations within the screened conflict-positive plant
literature universe.

It does not identify historical transition probabilities, causal evolutionary routes,
natural angiosperm prevalence, or theoretical `R`, `K`, `Phi`, `rho`, `xi`, or
`d_B`.

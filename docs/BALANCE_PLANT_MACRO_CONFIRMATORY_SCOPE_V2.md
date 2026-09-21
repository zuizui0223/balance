# BALANCE plant macro confirmatory scope v2

## Decision update

The first confirmatory BALANCE macro study remains focused on flowering-plant reproductive systems.

Version 2 changes the **primary response**, not the biological scope.

The first two outcome-blind review universes show that reducing conflict resolution to

```text
structural split = yes / no
```

would discard recurrent and directly measured temporal and spatial solutions.

The primary comparative object is therefore the nominal `architecture_mode`.

## Central question

> When reproductive functions conflict, what predicts whether plants remain integrated, separate functions in time, separate them in space, combine temporal and spatial separation, or divide labour among modules?

## Primary analysis population

Only records satisfying all of the following can enter the confirmatory response model:

```text
dependency group frozen
source provenance closed
conflict_status = POSITIVE
architecture_mode resolved
core predictors independently coded
independent-coder/adjudication gate closed
```

Conflict-negative, aligned and unresolved systems remain essential screening controls but do not enter the conflict-resolution response model.

## Primary response

Use the nominal architecture categories:

```text
SHARED_INTEGRATED
TEMPORAL_SEPARATION
SPATIAL_SEPARATION
TEMPORAL_AND_SPATIAL_SEPARATION
WITHIN_FLOWER_DIVISION_OF_LABOUR
AMONG_FLOWER_MODULE_DIVISION
POLYMORPHIC_OR_MOSAIC
```

Do not impose an ordinal progression.

Where cell counts require pooling, any coarsening must be preregistered before the confirmatory fit. Preferred biologically interpretable coarsenings are:

```text
SHARED

TEMPORAL_OR_SPATIAL
  = TEMPORAL_SEPARATION
  + SPATIAL_SEPARATION
  + TEMPORAL_AND_SPATIAL_SEPARATION

STRUCTURAL_MODULE_DIVISION
  = WITHIN_FLOWER_DIVISION_OF_LABOUR
  + AMONG_FLOWER_MODULE_DIVISION

MOSAIC
  = POLYMORPHIC_OR_MOSAIC
```

Coarsening is a sample-size accommodation, not an evolutionary ordering.

## Secondary response

`structural_module_division` remains a secondary binary estimand:

```text
true:
  WITHIN_FLOWER_DIVISION_OF_LABOUR
  AMONG_FLOWER_MODULE_DIVISION

false:
  SHARED_INTEGRATED
  TEMPORAL_SEPARATION
  SPATIAL_SEPARATION
  TEMPORAL_AND_SPATIAL_SEPARATION
```

The binary analysis asks one narrower question:

> when is conflict resolved by structural division of labour rather than without structural module division?

It does not represent all biologically important conflict-resolution modes.

## Why this changed

### U1 broad herbivory-pollination universe

The provisional first 20 source-ready U1 records show that a broad interaction literature has low yield for the strict shared-reproductive-coordinate estimand:

```text
20 source-ready records
13 excluded at S0 for no shared reproductive coordinate
0 conflict-positive promotions
1 aligned no-conflict control
5 no-demonstrated-conflict retained cases
```

U1 is therefore currently strongest as an estimand-specificity universe.

### U2 sexual-interference universe

The source-closed U2 universe contains 22 dependency groups.

The conservative provisional screen recovered:

```text
7 POSITIVE
2 NO_DEMONSTRATED_CONFLICT
13 UNRESOLVED
```

The seven positive records occupy multiple nonstructural modes:

```text
SHARED_INTEGRATED                 2
TEMPORAL_SEPARATION               1
SPATIAL_SEPARATION                1
TEMPORAL_AND_SPATIAL_SEPARATION   2
UNRESOLVED                        1
```

Thus the available empirical signal itself argues against treating structural differentiation as the sole primary response.

These counts are development diagnostics, not prevalence estimates.

## Primary predictors

Retain predictors that can be coded before reference to the outcome:

### Module substrate

```text
SINGLE_OR_CONTINUOUS
SERIAL_WITHIN_FLOWER
REPEATED_FLOWERS
PREEXISTING_SEPARATE_ORGANS
MULTILEVEL
```

### Conflict timing geometry

```text
SIMULTANEOUS
SEQUENTIAL_WITHIN_UNIT
SEASONALLY_ALTERNATING
CONTEXT_DEPENDENT
MIXED
```

### Conflict spatial geometry

```text
SAME_UNIT
BETWEEN_MODULES
AMONG_INDIVIDUALS
AMONG_POPULATIONS
ENVIRONMENTAL_MOSAIC
MIXED
```

The predictor receipt / independent-coding rules remain unchanged.

## Revised confirmatory hypotheses

### PH1 — module-opportunity hypothesis

Pre-existing serial, repeated or already separated reproductive modules alter the probability distribution across architecture modes relative to a single/continuous shared structure.

The primary prediction is not only “more structural differentiation”; module substrate may redirect conflict toward spatial, temporal or structural solutions.

### PH2 — temporal-geometry hypothesis

Sequential functional demands increase the relative probability of temporal or combined temporal-spatial separation versus a permanently shared architecture.

### PH3 — simultaneous repeated-module hypothesis

Simultaneous competing demands on serial/repeated modules increase the relative probability of module-level division of labour, conditional on conflict family.

### PH4 — spatial-mosaic hypothesis

Among-population or environmental-mosaic conflict geometry increases the relative probability of `POLYMORPHIC_OR_MOSAIC` architecture compared with a single fixed mode.

### PH5 — retained-integration hypothesis

When conflict is positive but module substrate is single/continuous and demands occur on the same unit, `SHARED_INTEGRATED` remains a legitimate predicted outcome rather than a failed transition.

## Statistical plan

### Primary model family

If category counts are adequate:

```text
hierarchical multinomial architecture model

architecture_mode
~ module_substrate
+ conflict_timing_geometry
+ conflict_spatial_geometry
+ conflict_family
+ phylogenetic / taxonomic dependence
```

Reference-category choice is a parameterization detail, not a biological ranking.

### Sparse-cell fallback

If the full nominal model is unstable, use the preregistered four-class coarsening:

```text
SHARED
TEMPORAL_OR_SPATIAL
STRUCTURAL_MODULE_DIVISION
MOSAIC
```

If that remains too sparse, do not collapse post hoc until a coefficient becomes significant. Freeze a smaller estimand before fitting.

### Secondary binary model

```text
structural_module_division
~ module_substrate
+ conflict_timing_geometry
+ conflict_spatial_geometry
+ conflict_family
+ phylogenetic / taxonomic dependence
```

This is secondary even if it is statistically easier.

## Universe structure

The confirmatory data are built as the union of independently defined literature universes after biological deduplication.

Current roles:

```text
U1 herbivory-pollination:
  broad interaction specificity / shared-coordinate gate

U2 sexual interference:
  mechanism-targeted conflict and nonstructural separation

U3 heteranthery / pollen fate:
  structural division-of-labour enrichment universe

U4 pollinator-prey:
  pre-existing separate-organ / spatial-temporal separation universe

U5 aligned / abiotic controls:
  specificity controls
```

The different universes are not interchangeable sampling frames. `conflict_family` and source universe must remain visible in sensitivity analyses.

## Independent reliability gate

U2 is currently the first source-closed review universe eligible for the formal independent-coder reliability exercise.

The deterministic sample uses the first 20 frozen U2 record IDs:

```text
U2_001 ... U2_020
```

Coders receive only the blinded source packet and codebook, not the provisional U2 screening calls.

The confirmatory freeze still requires acceptable agreement and adjudication.

## Claim ceiling

The study can support comparative associations between conflict geometry, module substrate and observed architecture mode within the screened plant literature universe.

It cannot from this design alone identify:

- the historical probability of any transition;
- theoretical `R`, `K`, `Phi`, `rho`, `xi`, or `d_B`;
- natural prevalence across angiosperms;
- the SLK accessibility/invasion/fixation chain.

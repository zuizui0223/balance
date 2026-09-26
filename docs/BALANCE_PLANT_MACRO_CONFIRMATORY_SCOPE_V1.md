# BALANCE plant macro confirmatory scope v1

## Decision

The first confirmatory BALANCE macro study will be developed within flowering-plant reproductive systems.

The 55-system cross-domain pilot remains a generality and measurement-invariance stress test.

This decision is methodological, not taxonomic: the theory remains general, but the first comparative test uses a domain in which the predictors and outcomes can be coded without equating gene duplication, paired claws and floral modules on an artificial common scale.

## Central question

> When reproductive functions conflict, what determines whether plants retain a shared compromise, separate the functions in time or space, or divide labour among reproductive modules?

## Comparative sequence

```text
multifunctional reproductive system
-> conflict screen
-> conflict-positive system
-> resolution mode
```

Conflict-negative and aligned multifunctional systems remain in the screening denominator and specificity controls.

## Discovery families

The outcome-blind search frame will be assembled from at least five literature families.

### F1 — pollinator versus antagonist / herbivore conflict

Examples include floral display, phenology, colour, shape, scent and inflorescence traits jointly affecting pollination and antagonist damage.

The current literature base is large: the updated plant-herbivore/pollinator meta-analysis contains 171 studies and 1348 study cases. Most of these are not automatically BALANCE-eligible; the dataset is a discovery frame.

### F2 — sexual interference between male and female function

Hermaphroditic flowers can experience interference or antagonistic selection between male and female function.

Candidate resolution modes include:

- dichogamy;
- herkogamy;
- movement herkogamy;
- unisexual flowers;
- gender polymorphism;
- retained simultaneous hermaphroditism.

Anti-selfing and sexual-interference explanations must be separated where possible.

### F3 — pollen reward versus pollen export

In pollen-reward flowers, pollen serves as both food for pollinators and male gametes.

Candidate states include:

- homanthery / shared stamens;
- heteranthery;
- other stamen division-of-labour states.

### F4 — pollination versus prey capture

Carnivorous plants provide flower/trap systems in which insects can serve as pollinators and prey.

Resolution may occur through:

- flower-trap spatial separation;
- temporal separation;
- visual or chemical signal partition;
- selfing or pollinator-independence that reduces the fitness cost of conflict;
- little/no demonstrated conflict.

### F5 — aligned or weak-conflict controls

Include multifunctional reproductive traits for which the two functions favour the same state or for which conflict has not been demonstrated.

Examples include some flower-orientation / rain-protection systems.

These rows protect the denominator and stop 'multifunctionality' from becoming synonymous with conflict.

## Plant-specific analysis unit

Primary unit:

```text
species
x homologous reproductive structure/module
x declared function pair
x biologically distinct context when context changes the conflict or resolution state
```

Repeated contexts from one species receive a common dependency-group identifier and cannot be treated as independent species.

Comparative radiation papers are not flattened into one pseudo-independent row per species unless species-level predictor and response information is independently recoverable.

## Plant-specific architecture modes

Use a nominal architecture variable rather than assuming a universal evolutionary ladder. Only conflict-positive rows are interpreted as conflict-resolution outcomes; negative and unresolved conflict rows retain architecture state without causal language.

```text
SHARED_INTEGRATED
TEMPORAL_SEPARATION
SPATIAL_SEPARATION
TEMPORAL_AND_SPATIAL_SEPARATION
WITHIN_FLOWER_DIVISION_OF_LABOUR
AMONG_FLOWER_MODULE_DIVISION
POLYMORPHIC_OR_MOSAIC
UNRESOLVED
```

Examples:

```text
shared corolla under pollinator/ant conflict -> SHARED_INTEGRATED
dichogamy -> TEMPORAL_SEPARATION
herkogamy or flower/trap separation -> SPATIAL_SEPARATION
combined dichogamy + herkogamy -> TEMPORAL_AND_SPATIAL_SEPARATION
heteranthery -> WITHIN_FLOWER_DIVISION_OF_LABOUR
male-only + bisexual flowers -> AMONG_FLOWER_MODULE_DIVISION
context-dependent morph/state turnover -> POLYMORPHIC_OR_MOSAIC
```

A secondary binary estimand is:

```text
structural_module_division =
  true  for WITHIN_FLOWER_DIVISION_OF_LABOUR or AMONG_FLOWER_MODULE_DIVISION
  false for SHARED_INTEGRATED / TEMPORAL_SEPARATION / SPATIAL_SEPARATION / TEMPORAL_AND_SPATIAL_SEPARATION
```

This binary outcome is a statistical simplification, not a claim that temporal/spatial separation is biologically unimportant.

## Outcome-independent opportunity variables

Replace the generic cross-domain accessibility score with observable plant architecture.

### P1 — pre-existing module substrate

Code before using the resolution outcome:

```text
SINGLE_OR_CONTINUOUS
SERIAL_WITHIN_FLOWER
REPEATED_FLOWERS
PREEXISTING_SEPARATE_ORGANS
MULTILEVEL
UNRESOLVED
```

Examples:

- corolla-shape conflict -> SINGLE_OR_CONTINUOUS;
- pollen fates across several stamens -> SERIAL_WITHIN_FLOWER;
- sex-function divergence among flowers -> REPEATED_FLOWERS;
- flowers versus carnivorous traps -> PREEXISTING_SEPARATE_ORGANS.

This is a structural opportunity measure, not an inferred historical probability of differentiation.

### P2 — conflict timing geometry

```text
SIMULTANEOUS
SEQUENTIAL_WITHIN_UNIT
SEASONALLY_ALTERNATING
CONTEXT_DEPENDENT
MIXED
UNRESOLVED
```

### P3 — conflict spatial geometry

```text
SAME_UNIT
BETWEEN_MODULES
AMONG_INDIVIDUALS
AMONG_POPULATIONS
ENVIRONMENTAL_MOSAIC
MIXED
UNRESOLVED
```

These variables describe where/when the competing functions make demands; they do not use the observed resolution mode as evidence.

## Confirmatory hypotheses

### PH1 — module-opportunity hypothesis

Among conflict-positive systems, pre-existing repeated or separable reproductive modules increase the probability of structural division of labour relative to a single/continuous shared structure.

This is the within-plant operationalization of the original architecture-accessibility idea.

### PH2 — temporal-geometry hypothesis

Sequential or seasonally alternating functional demands are more likely to be resolved by temporal separation than by fixed structural division, conditional on module substrate.

### PH3 — simultaneous-conflict hypothesis

Simultaneous competing demands on repeated modules increase the probability of within- or among-module division of labour.

### PH4 — spatial-mosaic hypothesis

Conflict that varies primarily among populations or environmental contexts is more likely to produce polymorphic/context-dependent states than a single fixed resolution mode.

PH4 requires repeated-context data and is secondary until enough independent species contribute such data.

## Important moderators

Register when extractable:

- self compatibility;
- autonomous selfing capacity;
- pollinator dependence;
- life history;
- floral longevity;
- flower number / display size;
- antagonist type;
- abiotic versus biotic second function;
- mating system;
- latitude / biome only if they are available without selective missingness.

Do not turn missing literature descriptions into biological zeros.

## Statistical plan

### Primary model

Among adjudicated conflict-positive species with resolved binary outcome:

```text
structural_module_division
~ module_substrate
+ conflict_timing_geometry
+ conflict_spatial_geometry
+ conflict_family
+ phylogenetic / taxonomic dependence
```

Exact parameterization is frozen only after the plant pilot shows adequate cells.

### Resolution-mode model

If cell counts are adequate, fit a hierarchical multinomial model for:

```text
SHARED
TEMPORAL
SPATIAL
STRUCTURAL
MOSAIC
```

Do not force the nominal modes into an ordinal model unless an independently justified ordering is registered.

### Within-family sensitivity

Repeat the relevant contrasts separately for:

- sexual-interference systems;
- pollinator-antagonist systems;
- pollen-reward systems;
- carnivorous-plant systems.

A general result must not be driven by one literature family.

## Search-frame construction

Start from review/meta-analysis universes rather than named positive examples.

Initial discovery anchors include:

- the 2026 updated herbivory-pollinator meta-analysis;
- sexual-interference reviews;
- heteranthery / pollen division-of-labour literature;
- carnivorous-plant pollinator-prey reviews.

Backward and forward citation chaining is frozen prospectively.

A source is retained even when it yields:

- aligned/no conflict;
- unresolved conflict;
- shared compromise;
- nonstructural separation;
- structural division.

## Evidence ceiling

The plant macro study can identify comparative associations between conflict geometry, pre-existing modular opportunity and observed resolution architecture.

It cannot by itself identify:

- theoretical `R`, `K`, `Phi`, `rho`, `xi`, or `d_B`;
- a unique historical causal route;
- natural prevalence unless the search denominator supports that estimand;
- SLK accessibility, invasion, fixation or long-run occupancy.

## Promotion criterion

The plant lane replaces the cross-domain model as the first confirmatory macro target only after:

1. an outcome-blind plant screening universe is frozen;
2. at least two coders independently apply the plant codebook to a pilot subset;
3. conflict and resolution modes show acceptable agreement;
4. module substrate and conflict-geometry predictors can be coded independently of outcome;
5. the phylogenetic/taxonomic grain is made explicit.

Until then, this file defines the development target rather than a completed analysis.

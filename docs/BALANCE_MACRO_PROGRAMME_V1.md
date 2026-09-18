# BALANCE comparative macro programme v1

## Status

This document opens a new comparative-macro lane for BALANCE without changing the frozen DOI-module claim ceiling or the SLK ownership split.

The macro lane asks a different question from the SLK flagship:

```text
SLK:
when does differentiation have positive architecture value and clear downstream evolutionary gates?

BALANCE macro:
given multifunctionality and an identified or adjudicated functional conflict,
what predicts persistence of an integrated compromise versus functional/structural decoupling?
```

The primary comparative target is therefore the **resolution of conflict**, not the existence of `Phi=0` itself.

## Core question

> Why are some functional conflicts tolerated inside a shared architecture whereas others are resolved by differentiation?

The target comparative sequence is

```text
multifunctional system
-> conflict screen
-> conflict-positive system
-> shared compromise / non-structural separation / structural differentiation
```

The screening universe must begin upstream of the outcome. Existing BALANCE pattern-positive systems may seed discovery, but they cannot define the sampling denominator.

## Unit of analysis

The primary unit is one independent biological cluster:

```text
taxon or lineage
x homologous shared structure/coordinate
x declared pair of functions
x biologically distinct context when the architecture state or conflict state changes
```

Rules:

1. Multiple papers on the same biological cluster are evidence sources, not independent rows.
2. A new row is permitted when a population, environment, life stage, or evolutionary lineage has a genuinely different conflict/architecture state that is part of the estimand.
3. Closely related taxa are not assumed independent. Taxonomic and, where available, phylogenetic dependence is retained for modelling.
4. One publication may contribute multiple rows only when the rows satisfy the cluster-independence rule above.

## Sampling frame

The current 17-cluster reality-pattern ledger is a recurrence map and is intentionally enriched for informative cases. It is **not** the macro sampling frame.

The macro study will build an explicit screened universe from broad multifunctionality searches and source chaining. Candidate systems are retained even when they show:

- aligned function optima and therefore no conflict;
- multifunctionality without demonstrated conflict;
- conflict with shared persistence;
- partial separation;
- complete structural differentiation;
- unresolved architecture state.

This prevents the macro denominator from being constructed only from positive BALANCE examples.

A versioned search protocol should freeze, before the main analysis:

1. databases and search date;
2. search strings by biological domain;
3. backward/forward citation-chaining rule;
4. duplicate-cluster merge rule;
5. stopping rule for each domain;
6. exclusion reasons.

## Two-stage inferential design

### Stage 1 — conflict screen

All screened multifunctional systems retain a conflict state:

```text
POSITIVE
ALIGNED_NO_CONFLICT
NO_DEMONSTRATED_CONFLICT
UNRESOLVED
```

This stage protects the denominator and allows negative/aligned controls to remain visible.

It is not the primary BALANCE macro outcome and should not be interpreted as an SCH replacement.

### Stage 2 — conflict resolution

The primary BALANCE macro analysis is conditional on adjudicated positive conflict.

Architecture states are coded as:

```text
SHARED_INTEGRATED
REGULATORY_TEMPORAL_SEPARATION
SPATIAL_COMPARTMENTALIZATION
PARTIAL_STRUCTURAL_DIFFERENTIATION
SEPARATE_MODULES
POLYMORPHIC
UNRESOLVED
```

The primary binary response is:

```text
structural_differentiation = false
    SHARED_INTEGRATED
    REGULATORY_TEMPORAL_SEPARATION
    SPATIAL_COMPARTMENTALIZATION

structural_differentiation = true
    PARTIAL_STRUCTURAL_DIFFERENTIATION
    SEPARATE_MODULES
```

`POLYMORPHIC` and `UNRESOLVED` are excluded from the primary binary response but retained for secondary analysis.

A secondary ordinal resolution level may be derived as:

```text
0 shared integrated
1 regulatory / temporal separation
2 spatial compartmentalization
3 partial structural differentiation
4 separate modules
```

This ordinal encoding is a comparative convenience, not a claim that every biological transition must traverse all five states.

## Registered macro hypotheses

### H1 — architecture-accessibility hypothesis

Among conflict-positive systems, greater accessibility of an alternative architecture predicts structural differentiation.

```text
alternative accessibility up
-> P(structural differentiation) up
```

Accessibility is coded from biological/developmental evidence, not inferred from the observed outcome alone.

### H2 — functional-coupling hypothesis

Strong coordination or coupling between the two functions predicts persistence of an integrated architecture.

```text
functional coupling up
-> P(structural differentiation) down
```

The coding must refer to the biological dependence between functions, not merely shared location.

### H3 — temporal-switching hypothesis

When the same lineage/individual repeatedly experiences opposing functional regimes through time, rapidly switching temporal heterogeneity predicts retention of generalist/shared solutions relative to stable one-sided environments.

Spatial heterogeneity is coded separately because among-population mosaics can generate a different prediction.

### H4 — alternative-envelope hypothesis

With other predictors held fixed, systems with multiple biologically credible alternative architectures are predicted to have lower persistence of the shared solution than systems with no or one credible alternative.

This is the macro analogue of the BALANCE multi-alternative envelope theorem. Because alternative counts are vulnerable to study-effort bias, this hypothesis requires citation-intensity / evidence-effort sensitivity analysis.

### H5 — conflict-by-accessibility hypothesis

Conflict magnitude alone should be an incomplete predictor of structural differentiation. The association between conflict strength and differentiation should increase when alternative accessibility is high and/or functional coupling is weak.

This is the key comparative translation of:

```text
conflict != automatic differentiation.
```

## Predictor codebook

Primary predictors:

- `conflict_strength_proxy`
- `alternative_accessibility`
- `functional_coupling`
- `temporal_heterogeneity`
- `spatial_heterogeneity`
- `alternative_repertoire`

Design / bias variables:

- biological domain;
- taxonomic group;
- study design;
- evidence quality;
- publication year;
- number of evidence sources;
- adjudication status;
- sampling frame.

No macro proxy is to be relabelled as theoretical `rho`, `Phi`, `xi`, or `d_B`.

## Primary model

The first confirmatory model is a hierarchical logistic model among adjudicated conflict-positive systems with resolved binary architecture state:

```text
structural_differentiation
~ alternative_accessibility
+ functional_coupling
+ temporal_heterogeneity
+ spatial_heterogeneity
+ alternative_repertoire
+ conflict_strength_proxy
+ conflict_strength_proxy:alternative_accessibility
+ domain / taxonomic dependence
```

The exact random-effect or phylogenetic structure is frozen only after the pilot reveals which clades/domains have adequate replication.

Preferred hierarchy:

1. domain-level varying intercept;
2. taxonomic-cluster varying intercept where repeated related systems exist;
3. clade-specific phylogenetic covariance sensitivity analysis when a defensible phylogeny is available.

Do not pool domains with radically different coding semantics until cross-domain measurement invariance is audited.

## Secondary analyses

1. ordinal resolution-level model;
2. conflict-positive transition/mosaic subset;
3. within-domain models for floral systems, feeding structures, molecular/gene architecture, and other sufficiently replicated groups;
4. sensitivity to excluding low-evidence systems;
5. sensitivity to alternative architecture-state coding;
6. source-count / citation-intensity adjustment for H4;
7. matched or stratified comparisons for strong confounders when sample size permits.

## Pilot and expansion gates

### Pilot

Goal: approximately 40 independently screened systems spanning at least three domains, including negative/aligned controls.

Pilot outputs:

- coder agreement;
- missingness map;
- predictor separability;
- architecture-state frequency;
- domain-specific semantic failures;
- estimate of how many systems can enter the primary model.

The pilot is for codebook repair, not final hypothesis testing.

### Freeze gate

Before the first confirmatory model:

- freeze sampling protocol;
- freeze inclusion/exclusion rules;
- freeze primary outcome mapping;
- freeze predictor definitions;
- freeze duplicate-cluster rule;
- freeze primary model formula;
- document every post-pilot change.

### Full comparative target

Expand toward roughly 150-300 screened systems if the literature supports it. Sample size is evidence-limited rather than quota-driven; the stopping rule belongs to the versioned search protocol.

## Relationship to the existing BALANCE ledgers

`data/BALANCE_PATTERN_LEDGER_V1.csv` remains the source-adjudicated recurrence ledger.

It is **not overwritten**.

The macro lane has a separate schema because its denominator and purpose differ:

```text
pattern ledger:
Does BALANCE-compatible geometry recur?

macro ledger:
Across a defined screened universe, what predicts conflict resolution architecture?
```

Existing rows may be migrated only after re-adjudication under the macro codebook. Migration does not automatically make a row primary-model eligible.

## Claim ceiling

The macro study may support statements such as:

- structural differentiation is associated with architecture accessibility;
- strong functional coupling is associated with persistent integration;
- temporal heterogeneity moderates conflict resolution;
- conflict strength alone is a poor predictor relative to conflict x accessibility.

It may not claim from comparative proxies alone that:

- `K`, `R`, `Phi`, `rho`, `xi`, or `d_B` were measured;
- a particular historical transition was caused by BALANCE;
- current architecture state reveals the historical path uniquely;
- the screened literature estimates natural prevalence without a defensible sampling frame;
- association establishes the SLK evolutionary transport chain.

## Immediate implementation sequence

1. register the macro codebook;
2. create a seed registry from existing BALANCE cases and negative controls;
3. implement a fail-closed macro-ledger validator;
4. build a pilot search frame across at least three domains;
5. double-code the first pilot subset;
6. freeze the confirmatory protocol only after pilot codebook repair.

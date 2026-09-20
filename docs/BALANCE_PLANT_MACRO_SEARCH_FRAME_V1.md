# BALANCE plant macro outcome-blind search frame v1

## Purpose

Construct a plant comparative denominator without starting from named BALANCE-positive examples.

The screening frame is assembled from broad literature universes that were created for questions adjacent to, but not conditioned on, the focal architecture outcome.

## Seed universes

### U1 — herbivory / pollination interaction universe

Use the updated herbivory-pollinator meta-analysis as a discovery universe.

The 2026 update reports:

```text
171 studies
1348 study cases
```

covering natural and simulated herbivory, floral traits, pollinator attraction and reproductive success.

These records are discovery candidates only. Most will not establish opposing selection on one shared coordinate and will therefore remain negative, unresolved or excluded at the conflict gate.

### U2 — sexual-interference universe

Start from reviews of sexual interference in cosexual flowers and forward/backward citation chaining.

Retain studies of:

- dichogamy;
- herkogamy;
- movement herkogamy;
- unisexual flowers;
- gender polymorphism;
- experimental manipulation of self-interference.

Do not admit a species simply because it is dichogamous or herkogamous. The source must independently address male/female functional interference or enter as an unresolved architecture-only candidate.

### U3 — heteranthery / pollen-fate universe

Start from heteranthery and pollen division-of-labour reviews plus cited primary systems.

Retain both:

- homantherous / undifferentiated comparators;
- heterantherous systems;
- systems where function partition among stamens is disputed or unresolved.

### U4 — carnivorous-plant pollinator/prey universe

Start from pollinator-prey conflict reviews and primary studies.

Retain systems with:

- demonstrated pollinator capture / pollen limitation;
- little overlap between prey and pollinators;
- flower-trap spatial separation;
- temporal separation;
- chemical/visual signal partition;
- autonomous selfing / pollinator independence;
- unresolved conflict.

### U5 — multifunctional aligned / abiotic controls

Use flower-orientation, rain-protection and related literature to retain multifunctional systems where the two functions have aligned optima or conflict is not demonstrated.

This prevents the screening frame from equating multifunctionality with conflict.

## Search logic

Each universe receives its own versioned search query and date.

The final confirmatory dataset is the union after duplicate clustering, not a simple concatenation of publication counts.

### U1 starting search

The 2026 meta-analysis reports the combined Web of Science logic used for its update. Reuse that search family as a reproducibility anchor and update forward from the last covered year.

### U2 starting concepts

```text
("sexual interference" OR "male female interference" OR "pollen interference")
AND
(flower* OR floral OR plant*)
AND
(dichogam* OR herkogam* OR stamen movement OR unisexual* OR monoec* OR gynodioec*)
```

### U3 starting concepts

```text
(heteranther* OR "stamen dimorphism" OR "division of labour" OR "division of labor")
AND
(pollen)
AND
(feeding OR reward OR pollinat* OR gamete*)
```

### U4 starting concepts

```text
("pollinator prey conflict" OR "pollinator-prey conflict")
OR
((carnivorous plant* OR Drosera OR Pinguicula OR Nepenthes OR Sarracenia)
 AND (pollinat* AND prey))
```

### U5 starting concepts

```text
(multifunction* OR "multiple function*" OR "flower orientation")
AND
(pollinat*)
AND
(rain OR water OR protection OR temperature OR abiotic)
```

These strings are pilot starts, not yet the final database-specific syntax.

## Screening gates

### S0 — plant reproductive multifunctionality

Does one declared reproductive structure/module/system contribute to both focal functions?

```text
NO -> exclude
YES -> S1
UNCLEAR -> retain unresolved
```

### S1 — conflict evidence

```text
POSITIVE
ALIGNED_NO_CONFLICT
NO_DEMONSTRATED_CONFLICT
UNRESOLVED
```

Do not screen on architecture outcome at this stage.

### S2 — architecture mode

Code the observed architecture independently of whether conflict is positive:

```text
SHARED_INTEGRATED
TEMPORAL_SEPARATION
SPATIAL_SEPARATION
TEMPORAL_AND_SPATIAL_SEPARATION
WITHIN_FLOWER_DIVISION_OF_LABOUR
AMONG_FLOWER_MODULE_DIVISION
POLYMORPHIC_OR_MOSAIC
UNRESOLVED
NA
```

The label `SHARED_INTEGRATED` is retained for compatibility, but in negative-conflict rows it means only shared/integrated architecture and is not interpreted as compromise caused by conflict.

A later schema version may rename this state to `SHARED_INTEGRATED` if that improves semantic clarity.

### S3 — outcome-independent predictors

Code:

- module substrate;
- conflict timing geometry;
- conflict spatial geometry;

from source evidence that does not use the resolution mode as its justification.

### S4 — moderator extraction

Extract mating system, self-compatibility, autonomous selfing, pollinator dependence and life history when reported.

Missing description is `UNRESOLVED`, never biological absence.

## Duplicate clustering

One publication can map to several species.

One species can map to several publications.

The final unit is biological, not bibliographic.

Rules:

1. identical species × function pair × context -> one dependency group;
2. multiple sources strengthen one record rather than create replication;
3. biologically distinct contexts may create multiple records but retain one dependency group;
4. comparative-clade papers remain discovery sources until species-level extraction is possible;
5. hybrids/cultivars are treated explicitly and not silently merged with wild species.

## Search-flow reporting

Freeze and report:

```text
records retrieved
duplicates removed
candidate biological systems
full-text screened systems
excluded systems by reason
screened dependency groups
conflict-positive groups
resolved architecture groups
primary-model eligible groups
```

The PRISMA-style flow describes the screened literature universe. It does not imply that the final systems are an unbiased sample of all flowering plants.

## Stop rule

The confirmatory search stops by protocol, not when a desired coefficient becomes significant.

For each universe:

1. freeze database/date window;
2. screen all returned records up to the declared query;
3. complete backward/forward chaining for registered anchor reviews using one predefined generation;
4. update only by a separately versioned search.

## Claim ceiling

The search frame supports inference within the screened literature universe.

It does not estimate the natural frequency of each architecture mode across all angiosperms unless an independent species-sampling design is added.

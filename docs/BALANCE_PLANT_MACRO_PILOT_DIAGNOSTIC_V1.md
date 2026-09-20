# BALANCE plant macro pilot diagnostic v1

## Status

This diagnostic summarizes the first plant-specific codebook stress test.

The pilot is assembled partly from existing BALANCE cases and deliberately added resolution-mode examples. It is **not outcome-blind** and therefore cannot be used for confirmatory effect estimation.

Its job is to test whether the proposed plant architecture variables are observable and whether the screening grain can be made explicit.

## Current plant pilot

```text
29 records
28 dependency groups

SPECIES / SPECIES_CONTEXT dominate;
1 comparative-clade row is retained but cannot enter a species-level primary model.
```

Conflict screen:

```text
POSITIVE                  16
NO_DEMONSTRATED_CONFLICT   8
ALIGNED_NO_CONFLICT        1
UNRESOLVED                 4
```

Conflict families:

```text
POLLINATOR_ANTAGONIST   10
POLLINATOR_PREY          8
SEXUAL_INTERFERENCE      5
POLLEN_REWARD_GAMETE     3
POLLINATION_ABIOTIC      2
OTHER                     1
```

Observed architecture modes:

```text
SHARED_INTEGRATED                   15
TEMPORAL_SEPARATION                  1
SPATIAL_SEPARATION                   4
TEMPORAL_AND_SPATIAL_SEPARATION      1
WITHIN_FLOWER_DIVISION_OF_LABOUR     3
AMONG_FLOWER_MODULE_DIVISION         1
POLYMORPHIC_OR_MOSAIC                3
UNRESOLVED                           1
```

All intended architecture modes are therefore represented in the stress test.

## Important semantic repair

The field is named `architecture_mode`, not `resolution_mode`.

Reason:

```text
observed architecture
!=
identified historical resolution of conflict
```

A spatially separated flower/trap system can exist even when the current study does not demonstrate active pollinator-prey conflict. Likewise, shared architecture in an aligned-optimum control is not evidence of persistent compromise.

Only rows with `conflict_status=POSITIVE` may be interpreted as observed candidate conflict-resolution states.

## Conflict-positive subset

The 16 positive-conflict pilot records contain:

```text
SHARED_INTEGRATED                    7
TEMPORAL_SEPARATION                  1
SPATIAL_SEPARATION                   1
TEMPORAL_AND_SPATIAL_SEPARATION      1
WITHIN_FLOWER_DIVISION_OF_LABOUR     3
AMONG_FLOWER_MODULE_DIVISION         1
POLYMORPHIC_OR_MOSAIC                2
```

For the coarse binary architecture estimand:

```text
nonstructural / shared    10
structural division        4
binary unresolved          2
```

This is sufficient for codebook stress testing, not for a confirmatory regression.

## Pre-existing module substrate

Among conflict-positive pilot records:

```text
SINGLE_OR_CONTINUOUS            3
MULTILEVEL                      4
SERIAL_WITHIN_FLOWER            6
REPEATED_FLOWERS                2
PREEXISTING_SEPARATE_ORGANS     1
```

The first-pass records qualitatively show why module substrate may be more operational than the cross-domain `alternative_accessibility` score:

- continuous corolla/display systems can be coded before seeing whether the focal system split;
- stamens are serial reproductive modules regardless of whether a species is homantherous or heterantherous;
- repeated flowers exist before one asks whether sex function diverges among flowers;
- flower and trap organs are pre-existing separate modules.

This is exactly the type of predictor evidence needed to avoid outcome-derived accessibility.

No association is estimated from the current counts because the pilot deliberately targeted missing architecture classes.

## Conflict geometry is observable

Among positive-conflict rows, timing geometry already spans:

```text
SIMULTANEOUS             8
SEQUENTIAL_WITHIN_UNIT   3
SEASONALLY_ALTERNATING   1
CONTEXT_DEPENDENT        2
MIXED                    2
```

Spatial geometry spans:

```text
SAME_UNIT             11
BETWEEN_MODULES        2
AMONG_INDIVIDUALS      1
AMONG_POPULATIONS      1
ENVIRONMENTAL_MOSAIC   1
```

Thus the proposed question

> does the spatiotemporal geometry of conflict predict how functions are separated?

is empirically codable rather than purely conceptual.

## Pseudoreplication gate works

The Mexico and Costa Rica `Dalechampia scandens` contexts occupy two records but one `dependency_group`.

A confirmatory analysis must therefore use the dependency group or species-level random/clustered structure and cannot count these contexts as two independent species.

The same rule will apply when one paper reports several populations, years, morphs or environmental treatments.

## Main problems still open

### 1. Search denominator

The current plant pilot was assembled for codebook stress testing.

The next dataset must be recreated from an outcome-blind search frame based on review/meta-analysis universes and registered citation chaining.

### 2. Phylogeny

Taxonomic dependence is not yet represented by a plant phylogeny.

A confirmatory analysis should either:

- build a species phylogeny for the screened set;
- or freeze a taxonomic hierarchical approximation before fitting the primary model.

### 3. Mixed evidence grain

Comparative-clade sources such as the current `Senna` row are useful discovery evidence but cannot enter a species-level model without species-specific extraction.

### 4. Causal attribution

An architecture mode remains descriptive unless positive conflict and the relevant function pair are independently established.

### 5. Sexual-interference ambiguity

Traits such as herkogamy and dichogamy can reflect anti-selfing, pollen transfer efficiency, sexual interference or combinations of these processes.

The plant macro study must retain mechanism-attribution uncertainty rather than coding every spatial or temporal separation as a sexual-conflict adaptation.

## Immediate next gate

The plant macro lane is ready to move from **codebook stress test** to **outcome-blind screening-frame construction**.

Do not fit the primary model yet.

The next evidence task is:

```text
review/meta-analysis universe
-> title/abstract candidate screen
-> species/context deduplication
-> full-text conflict + architecture adjudication
-> frozen dependency groups
-> only then confirmatory model
```

# BALANCE plant U3 matched-control audit v4

## Status

U3 is now a source-audited matched heteranthery lane with three distinct unresolved problems that must not be collapsed:

1. control-selection closure;
2. conflict-measurement closure after matching;
3. broader architecture closure after matching.

Canonical surfaces include:

```text
data/BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv
data/BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv
data/BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv
data/BALANCE_PLANT_U3_SENNA_CONTROL_SEARCH_V1.csv
balance_domain/plant_u3_controls.py
balance_domain/plant_u3_adjudication.py
balance_domain/plant_u3_matched_extraction.py
balance_domain/plant_u3_senna_controls.py
```

## Current primary-pair state

The six source-resolved U3 cases currently have:

```text
PASS / adjudicated controls         2
OPEN / screened controls            2
REJECTED controls needing replacement 2
```

### PASS

- `Solanum rostratum -> Solanum lycocarpum`
- `Melastoma malabathricum -> Osbeckia chinensis`

### OPEN

- `Monochoria korsakowii -> Monochoria australasica`
- `Monochoria vaginalis -> Monochoria australasica`

### replacement required

- `Senna alata`
- `Senna bicapsularis`

The original Senna control `S. surattensis` remains rejected because source audit showed heteromorphic stamen sets rather than source-secure absence of heteranthery.

## Monochoria correction

The pair registry previously stored:

```text
animal_pollination_eligible = true
```

for `Monochoria australasica`.

That was too strong.

The cited Amegilla source documents male territorial behaviour over aquatic vegetation including `M. australasica`; it is not a source-secure direct flower-visitation or effective-pollination observation for the plant.

The registry now uses a tri-state field and records:

```text
animal_pollination_eligible = unresolved
```

for both Monochoria pairs.

This change does not weaken a previously adjudicated pair: both pairs were already OPEN in the adjudication ledger because direct animal-pollination evidence and nearest-eligible-control search were not closed.

The repair makes the pair registry semantically consistent with that OPEN decision.

## Monochoria remaining gates

The proposed control remains biologically attractive because:

- it is congeneric;
- modern phylogeny places `M. australasica` sister to the remaining Monochoria;
- source-resolved morphology lacks the distinct pollinating-anther differentiation of the two heterantherous cases.

But promotion requires both:

```text
DIRECT_EFFECTIVE_ANIMAL_POLLINATION
CLOSEST_ELIGIBLE_NONHETERANTHEROUS_CONGENER_SEARCH
```

Comparative statements that enantiostylous Monochoria are animal-pollinated do not substitute for species-specific effective-pollination evidence under the current contract.

## Senna replacement search

The rejected `S. surattensis` control has not been replaced by a convenient distant species.

A separate search ledger now records ten candidate-control evaluations.

### Close relatives that fail the negative-architecture gate

For `S. alata`:

- `S. siamea` is phylogenetically close but has strong stamen differentiation.

For `S. bicapsularis`:

- `S. corymbosa` is recovered as a very close/sister candidate but has direct nutritional-versus-reproductive stamen division;
- `S. occidentalis` is close but heterantherous;
- `S. siamea` is also close and heterantherous.

These are retained as explicit exclusions rather than disappearing from the search history.

### Homantherous / weakly differentiated candidates still open

For both Senna cases the current open set is:

```text
Senna racemosa
Senna pumilio
Senna villosa
```

Their negative architecture is source-secure enough for candidate status, but two gates remain open:

1. relative phylogenetic distance within the case-specific candidate set;
2. source-secure effective animal-pollination evidence for the exact control species.

Pollen-resource records alone do not satisfy the second gate.

No replacement Senna control is currently promoted.

## Why the Senna failure is informative

The closest well-supported relatives around the focal cases are themselves frequently heterantherous.

That means a naive analysis could manufacture a desired case-control contrast simply by widening until it found a homantherous species.

The frozen protocol does the opposite:

```text
close but architecture-positive -> exclude
farther architecture-negative -> keep OPEN until distance and pollination gates close
```

This preserves phylogenetic comparability at the cost of smaller matched sample size.

## Matched extraction among the two PASS pairs

### Solanum pair

```text
CASE:    Solanum rostratum
         heteranthery = present
         pollen-fate conflict = POSITIVE
         architecture = WITHIN_FLOWER_DIVISION_OF_LABOUR

CONTROL: Solanum lycocarpum
         heteranthery = absent
         pollen-fate conflict = POSITIVE
         broader architecture = AMONG_FLOWER_MODULE_DIVISION
```

This control is especially informative because absence of heteranthery does not equal absence of conflict or global integration.

### Melastoma pair

```text
CASE:    Melastoma malabathricum
         heteranthery = present
         pollen-fate conflict = POSITIVE

CONTROL: Osbeckia chinensis
         heteranthery = absent
         pollen-fate conflict = UNRESOLVED
         broader architecture = UNRESOLVED
```

The historical Osbeckia pollination source identifies hymenopteran visitor handling but not the registered quantitative pollen-reward versus gamete-transfer estimand.

No quantitative pollen-fate experiment has yet been recovered, so the control remains unresolved.

## Current matched-estimand state

Among adjudicated pairs:

```text
case conflict positive        2 / 2
control conflict resolved     1 / 2
control conflict unresolved   1 / 2

shared-integrated controls    0 / 2
alternative architecture      1 / 2
architecture unresolved       1 / 2
```

Therefore:

```text
matched_conflict_estimand_ready = false
matched_integrated_control_contrast_ready = false
```

U3 currently supports a source-secure heteranthery-present versus heteranthery-absent matched design, not yet a complete conflict-resolution effect estimate.

## Current bottleneck order

Priority is now:

1. recover a matched pollen-fate experiment for `Osbeckia chinensis`, if one exists;
2. close direct effective-pollination and nearest-eligible search for `Monochoria australasica`;
3. rank the open Senna homantherous candidates on a common phylogenetic framework and recover exact-species effective-pollination evidence;
4. only then enlarge the matched extraction.

Do not add easier heteranthery cases merely to increase n while these registered pairs remain unresolved.

## Claim ceiling

U3 can presently support:

- source-audited matched-control methodology;
- heteranthery-present versus heteranthery-absent comparisons for two closed pairs;
- demonstration that conflict can persist without heteranthery;
- discovery of alternative conflict-routing architecture;
- explicit documentation of why candidate negative controls fail.

It cannot presently support:

- a matched estimate of heteranthery as a function of conflict strength;
- a structural-division-versus-shared-integration effect;
- heteranthery prevalence;
- historical causal transition probabilities;
- theoretical BALANCE quantities or downstream SLK evolutionary realization.

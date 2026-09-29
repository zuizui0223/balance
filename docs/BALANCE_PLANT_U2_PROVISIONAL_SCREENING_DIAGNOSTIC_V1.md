# BALANCE plant U2 provisional screening diagnostic v1

## Scope

This diagnostic applies the plant macro codebook to the 22 dependency groups in the Barrett (2002) sexual-interference discovery universe after its 37-reference source map was closed.

The U2 source universe is review-defined and source-resolved, but the present coding is still:

```text
SCREENED
!=
independently double-coded
!=
ADJUDICATED
!=
confirmatory-model eligible
```

Canonical screen:

```text
data/BALANCE_PLANT_U2_SCREENING_PROVISIONAL_V1.csv
```

## Conflict screen

First-pass conservative result:

```text
POSITIVE                     7
NO_DEMONSTRATED_CONFLICT     2
UNRESOLVED                  13
TOTAL                       22
```

The seven positive systems are:

```text
Campsis radicans
Asclepias exaltata
Mimulus aurantiacus
Polemonium viscosum
Eichhornia paniculata
Pontederia sagittata
Ipomopsis aggregata
```

No row is marked primary-model eligible.

## Positive systems are not one architecture class

Among the seven conflict-positive rows:

```text
TEMPORAL_SEPARATION               1
SPATIAL_SEPARATION                1
TEMPORAL_AND_SPATIAL_SEPARATION   2
SHARED_INTEGRATED                 2
UNRESOLVED                        1
```

Thus a binary structural-differentiation outcome would discard most of the biological resolution signal recovered by this universe.

All resolved positive U2 architectures are currently nonstructural:

```text
structural_module_division = false
```

This is not a claim that structural division never resolves sexual interference. It reflects the particular review-defined empirical systems in U2.

## High-information positive cases

### Campsis radicans

Timed self-plus-cross pollinations show that self pollen applied before or with cross pollen sharply reduces fruit production.

The same literature explicitly links marked protandry to avoidance of that interference.

Pilot call:

```text
conflict_status  = POSITIVE
architecture_mode = TEMPORAL_SEPARATION
```

### Asclepias exaltata

In 1,380 hand pollinations, prior or simultaneous self pollen strongly reduces fruit and seed success of cross pollen.

The focal experiment identifies the interference but does not itself establish a separate avoidance architecture.

Pilot call:

```text
POSITIVE
SHARED_INTEGRATED
```

### Mimulus aurantiacus

Experimental stigma-closure manipulation shows that dynamic stigma movement reduces male-female interference and improves subsequent pollen export.

Pilot call:

```text
POSITIVE
TEMPORAL_AND_SPATIAL_SEPARATION
```

### Polemonium viscosum

Incompatible self pollen can inhibit compatible pollen germination and seed production. The species has spatial and temporal segregation of pollen and stigma presentation.

Pilot call:

```text
POSITIVE
TEMPORAL_AND_SPATIAL_SEPARATION
```

### Eichhornia paniculata

Manipulating floral display size shows a direct trade-off: larger displays attract pollinators but increase geitonogamy and reduce outcrossed siring success.

Pilot call:

```text
POSITIVE
SHARED_INTEGRATED
```

The row deliberately represents the experimentally manipulated shared display, rather than inferring historical differentiation.

### Pontederia sagittata

Prior self pollen reduces later outcrossed seed set in a style-morph- and timing-dependent manner.

Pilot call:

```text
POSITIVE
SPATIAL_SEPARATION
```

### Ipomopsis aggregata

The source establishes reproductive costs of self pollination/ovule usurpation.

The architecture is left unresolved rather than inferred from the conflict alone.

## Explicit null/specificity cases

### Pontederia cordata

A direct test found little/no significant reduction in compatible pollen receipt under the focal physical-interference manipulation.

Pilot call:

```text
NO_DEMONSTRATED_CONFLICT
SPATIAL_SEPARATION
```

### Turnera ulmifolia

Barrett's review likewise reports little influence of prior self/incompatible pollen on seed set.

Pilot call:

```text
NO_DEMONSTRATED_CONFLICT
SPATIAL_SEPARATION
```

These controls are important because spatial sexual-organ separation is not, by itself, proof that current sexual interference is large.

## Unresolved architecture-rich cases

The remaining 13 rows are deliberately not promoted merely because they possess striking reproductive architectures.

Examples include:

- stigma-height polymorphism in *Narcissus*;
- flexistyly in *Alpinia kwangsiensis*;
- enantiostyly in the four *Wachendorfia* species;
- historical heteranthery observations in *Solanum rostratum* and *Chamaecrista fasciculata*.

This implements:

```text
architecture exists
!=
conflict mechanism identified
```

## U1 versus U2

The provisional screens now expose a useful methodological contrast.

### U1

A broad herbivory-pollination review universe produced:

```text
20 source-ready provisional records
13 S0 exclusions for no shared reproductive coordinate
0 promoted conflict-positive rows
```

### U2

A mechanism-targeted sexual-interference review universe produced:

```text
22 source-resolved dependency groups
7 direct conflict-positive rows
2 explicit null rows
13 unresolved rows
```

This is **not a prevalence comparison**.

The review inclusion criteria differ radically. The licensed conclusion is that mechanism-targeted literature has a higher *estimand yield* for direct conflict identification than a broad ecological-interaction literature.

## Consequence for the macro response variable

The U2 screen provides empirical support for keeping `architecture_mode` as a primary comparative object.

A structural yes/no model may remain a secondary simplification, but it cannot be the only confirmatory analysis because temporal and spatial separation are recurrent conflict-positive outcomes.

A later confirmatory freeze should therefore prioritize a nominal hierarchical model across:

```text
SHARED_INTEGRATED
TEMPORAL_SEPARATION
SPATIAL_SEPARATION
TEMPORAL_AND_SPATIAL_SEPARATION
STRUCTURAL_MODULE_DIVISION
POLYMORPHIC_OR_MOSAIC
```

only if cell counts in the outcome-blind combined universes support that model.

## Next gate

U2 should now enter the independent-coder workflow.

The first independent reliability sample must be selected deterministically from the frozen U2 dependency-group registry and coded without access to this provisional first-pass screen.

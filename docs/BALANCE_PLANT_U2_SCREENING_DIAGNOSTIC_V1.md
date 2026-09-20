# BALANCE plant U2 source-screening diagnostic v1

## Status

U2 is the source-closed Barrett (2002) sexual-interference discovery universe.

The discovery layer contains:

```text
22 biological dependency groups
37 review references classified
0 unresolved primary-source groups
```

All 22 groups have now received a conservative primary-source screen in:

```text
data/BALANCE_PLANT_U2_SCREENING_V1.csv
```

Every row remains:

```text
adjudication_status      = SCREENED
primary_model_eligible   = false
```

Independent double coding and disagreement adjudication remain open.

## Conflict screen

```text
POSITIVE                   8
NO_DEMONSTRATED_CONFLICT   2
UNRESOLVED                12
```

This is a key result of the screening workflow.

Membership in a sexual-interference review is not being converted into a positive BALANCE conflict receipt.

More than half of the source-defined groups remain unresolved at the mechanism level.

## Explicit specificity controls

### Pontederia cordata

The primary experiment tested two proposed forms of interference in a tristylous system.

It found:

- no meaningful reduction of legitimate pollen capture from the presence of stamens;
- no marked seed-set cost after prior incompatible-pollen application.

The source therefore remains:

```text
conflict_status = NO_DEMONSTRATED_CONFLICT
```

despite conspicuous floral polymorphism.

### Turnera ulmifolia

Most compatible/incompatible pollen-mixture treatments did not reduce seed set.

A clogging effect occurred only under an extreme long-styled treatment, and the authors concluded that pollen clogging was unlikely to have played a major role in the evolution and maintenance of distyly.

This row therefore also remains a specificity control.

## Direct positive conflict cases

The first-pass positive set contains eight dependency groups.

### Campsis radicans

Self pollen supplied with or before cross pollen markedly reduces fruit production.

Marked protandry is interpreted in the primary source as at least partly avoiding the negative effect.

First-pass architecture:

```text
TEMPORAL_SEPARATION
```

### Asclepias exaltata

Prior or simultaneous self pollen strongly reduces fruit and seed set after cross pollen in a self-incompatible milkweed.

The cited experiment does not establish a separate resolution architecture.

First-pass architecture:

```text
SHARED_INTEGRATED
```

### Mimulus aurantiacus

Experimental prevention of stigma closure reduces pollen export.

Natural closure creates movement herkogamy, and closed flowers export more than twice as much pollen while self-pollination changes little.

First-pass architecture:

```text
SPATIAL_SEPARATION
```

### Polemonium viscosum

Prior/self pollen reduces compatible-pollen performance and sometimes seed set.

The source explicitly reports both spatial and temporal separation of pollen and stigma presentation.

This exposed a codebook problem: temporal and spatial separation are not biologically exclusive.

The plant architecture codebook was therefore expanded with:

```text
TEMPORAL_AND_SPATIAL_SEPARATION
```

rather than forcing the system into one arbitrary category.

### Eichhornia paniculata

Manipulating sex-role segregation among repeated flowers changes geitonogamy and outcross siring.

The focal natural flowers in the experiment are simultaneously hermaphroditic/adichogamous.

Therefore the natural architecture is retained as:

```text
SHARED_INTEGRATED
```

while the manipulation demonstrates that a repeated-flower separation route is experimentally available.

### Pontederia sagittata

Prior self pollen can reduce outcross seed set in morph- and timing-dependent ways.

The observed tristylous state is retained as:

```text
POLYMORPHIC_OR_MOSAIC
```

and is not forced into the structural binary.

### Epilobium obcordatum

Pollen-chase experiments show that prior or simultaneous self pollen can reduce seed set.

No source-level differentiated architecture is established.

### Ipomopsis aggregata

Self pollen germinates and penetrates ovules; combined self + outcross pollen reduces seed set substantially relative to outcross pollen alone.

The cited source therefore identifies a reproductive cost of self pollen without establishing a separated architecture.

## Unresolved cases are intentionally retained

Examples include:

- stigma-height dimorphism in *Narcissus assoanus* and *N. dubius*;
- self-sterility/stylar polymorphism in *N. triandrus*;
- flexistyly in *Alpinia kwangsiensis*;
- enantiostyly across four *Wachendorfia* species;
- segregation of pollen and stigmas in *Wahlenbergia albomarginata*;
- the historical heteranthery observations of Todd (1882).

These are not discarded.

They remain useful for the architecture map, but the primary source does not by itself identify the focal sexual-interference mechanism strongly enough for a positive conflict call.

## Architecture modes after screening

```text
POLYMORPHIC_OR_MOSAIC                10
SHARED_INTEGRATED                     4
TEMPORAL_SEPARATION                   2
SPATIAL_SEPARATION                    2
TEMPORAL_AND_SPATIAL_SEPARATION       1
UNRESOLVED                            3
```

Coarse structural-module outcome:

```text
nonstructural / shared    9
binary unresolved        13
structural division       0
```

The absence of a structural-division-positive U2 row is not evidence that such resolution is absent in nature.

It reflects the evidence family defined by the source review and the conservative rule that historical heteranthery observations are not promoted to functional division of labour without modern source-level support.

## Why U2 matters to the macro programme

U2 independently validates three design principles.

1. **Morphological separation is not sufficient evidence of conflict.**
2. **Review membership is not sufficient evidence of the focal mechanism.**
3. **Resolution modes are not mutually exclusive in time and space.**

U2 therefore acts as a strong mechanism-specificity and codebook-repair universe, not merely as extra sample size.

## Next gate

The source-closed first 20 dependency groups already have a blinded primary-source packet.

The next inferential operation is:

```text
20 source packets
-> independent coder A
-> independent coder B
-> raw agreement + Cohen kappa + Gwet AC1
-> disagreement adjudication
-> codebook repair if raw agreement < 0.80
```

No synthetic second coder is to be generated.

Until that gate closes, the current U2 screen remains a programme-level first pass, not the final adjudicated dataset.
